import pytest
import json
from sqlmodel import Session, SQLModel, create_engine
from storage.models import Workspace, Document, DocumentChunk
from retrieval.document import DocumentRetrievalAdapter
from services.embedding_service import EmbeddingService

@pytest.fixture(name="db_session")
def db_session_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.mark.asyncio
async def test_document_retrieval(db_session: Session):
    # 1. Setup Workspace
    ws = Workspace(title="Retrieval Test Workspace")
    db_session.add(ws)
    db_session.commit()
    db_session.refresh(ws)

    # 2. Setup Document metadata
    doc = Document(
        id="doc-123",
        workspace_id=ws.id,
        filename="test_logs.log",
        file_type="log",
        file_path="/dummy/test_logs.log",
        status="indexed",
        chunk_count=2
    )
    db_session.add(doc)
    db_session.commit()

    # 3. Create Chunks with deterministic mock vectors
    service = EmbeddingService()
    vector1 = service._generate_deterministic_mock_vector("Database connection failed timeout")
    vector2 = service._generate_deterministic_mock_vector("Successful login user Maya")

    chunk1 = DocumentChunk(
        id="chunk-1",
        document_id=doc.id,
        workspace_id=ws.id,
        chunk_index=0,
        content="Database connection failed timeout error database",
        embedding_json=json.dumps(vector1)
    )
    chunk2 = DocumentChunk(
        id="chunk-2",
        document_id=doc.id,
        workspace_id=ws.id,
        chunk_index=1,
        content="Successful login user Maya to server dashboard",
        embedding_json=json.dumps(vector2)
    )
    db_session.add_all([chunk1, chunk2])
    db_session.commit()

    # 4. Perform Retrieval
    adapter = DocumentRetrievalAdapter(session=db_session)
    
    # Query matching chunk 1
    results = await adapter.retrieve(
        query="database timeout fail",
        context={"workspace_id": ws.id, "limit": 1}
    )
    assert len(results) == 1
    assert results[0]["id"] == "chunk-1"
    assert "timeout" in results[0]["snippet"]

    # Query matching chunk 2
    results2 = await adapter.retrieve(
        query="user Maya login successful",
        context={"workspace_id": ws.id, "limit": 1}
    )
    assert len(results2) == 1
    assert results2[0]["id"] == "chunk-2"
    assert "Maya" in results2[0]["snippet"]
