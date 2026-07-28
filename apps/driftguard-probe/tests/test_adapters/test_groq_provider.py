import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from pydantic import BaseModel, Field
from typing import List
from probe.llm.providers.groq import GroqProvider


class MockResponse(BaseModel):
    """Schema for test structured validation."""
    items: List[str] = Field(...)


@pytest.mark.anyio
@patch("httpx.AsyncClient.post")
async def test_groq_provider_generate_text(mock_post):
    """Verify unstructured text generation on Groq compatible endpoints."""
    mock_resp = AsyncMock()
    mock_resp.json = MagicMock(return_value={
        "choices": [
            {
                "message": {
                    "content": "Hello from Llama 3 on Groq"
                }
            }
        ]
    })
    mock_resp.raise_for_status = MagicMock()
    mock_post.return_value = mock_resp

    provider = GroqProvider(api_key="mock-groq-key")
    res = await provider.generate_text("sys", "user")
    assert res == "Hello from Llama 3 on Groq"
    assert mock_post.called


@pytest.mark.anyio
@patch("httpx.AsyncClient.post")
async def test_groq_provider_generate_structured(mock_post):
    """Verify structured response schema parsing on Groq endpoints."""
    mock_resp = AsyncMock()
    mock_resp.json = MagicMock(return_value={
        "choices": [
            {
                "message": {
                    "content": '{"items": ["drift_stats", "latency_metrics"]}'
                }
            }
        ]
    })
    mock_resp.raise_for_status = MagicMock()
    mock_post.return_value = mock_resp

    provider = GroqProvider(api_key="mock-groq-key")
    res = await provider.generate_structured(MockResponse, "sys", "user")
    assert res.items == ["drift_stats", "latency_metrics"]
    assert mock_post.called
