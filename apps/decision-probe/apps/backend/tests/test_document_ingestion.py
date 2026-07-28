import pytest
import os
import tempfile
from services.document_parser import DocumentParser
from services.embedding_service import EmbeddingService

def test_chunk_text():
    text = "A" * 1500
    chunks = DocumentParser.chunk_text(text, chunk_size=1000, chunk_overlap=200)
    assert len(chunks) == 2
    assert len(chunks[0]) == 1000
    assert len(chunks[1]) == 700

def test_extract_text_txt():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as temp:
        temp.write("Hello world, this is decision probe testing.")
        temp_path = temp.name

    try:
        content = DocumentParser.extract_text(temp_path, "txt")
        assert content == "Hello world, this is decision probe testing."
    finally:
        os.unlink(temp_path)

@pytest.mark.asyncio
async def test_embedding_generation():
    service = EmbeddingService()
    vector = await service.get_embedding("Test sentence")
    assert len(vector) == 768
    assert isinstance(vector, list)
    assert all(isinstance(val, float) for val in vector)
