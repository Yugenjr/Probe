import os
import json
import logging
from sqlmodel import Session, select
import storage.database
from storage.models import Document, DocumentChunk
from services.document_parser import DocumentParser
from services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

async def process_document_task(workspace_id: str, document_id: str):
    """
    Asynchronous background task to parse, chunk, embed, and index an uploaded document.
    """
    logger.info(f"Starting background processing for document {document_id} in workspace {workspace_id}")
    
    # We open a new session for the background task
    with Session(storage.database.engine) as session:
        doc = session.get(Document, document_id)
        if not doc:
            logger.error(f"Document {document_id} not found in database.")
            return

        doc.status = "processing"
        session.add(doc)
        session.commit()
        session.refresh(doc)

        try:
            # 1. Extract text content
            text = DocumentParser.extract_text(doc.file_path, doc.file_type)
            
            # 2. Chunk text content
            chunks = DocumentParser.chunk_text(text, chunk_size=1000, chunk_overlap=200)
            doc.chunk_count = len(chunks)
            session.add(doc)
            session.commit()

            if not chunks:
                logger.warning(f"No text extracted or chunks generated for document {document_id}")
                doc.status = "indexed"
                session.add(doc)
                session.commit()
                return

            # 3. Embedding Generation and Chunk Storage
            embedding_service = EmbeddingService()
            for idx, chunk_text in enumerate(chunks):
                # Generate embedding
                vector = await embedding_service.get_embedding(chunk_text)
                
                # Save chunk record
                chunk_record = DocumentChunk(
                    document_id=doc.id,
                    workspace_id=workspace_id,
                    chunk_index=idx,
                    content=chunk_text,
                    embedding_json=json.dumps(vector)
                )
                session.add(chunk_record)
                
            doc.status = "indexed"
            session.add(doc)
            session.commit()
            logger.info(f"Document {document_id} successfully parsed, embedded, and indexed with {len(chunks)} chunks.")

        except Exception as e:
            logger.exception(f"Failed to process document {document_id}: {str(e)}")
            doc.status = "failed"
            doc.error_message = str(e)
            session.add(doc)
            session.commit()
