import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from services.models import ReasoningContext
from datetime import datetime, timezone
import os

# Set dummy key for test so InferenceClient initializes without error
os.environ["GEMINI_API_KEY"] = "dummy"

from inference.client import InferenceClient, LLMResponse

@pytest.fixture
def dummy_context():
    return ReasoningContext(
        workspace_id="ws1",
        workspace_title="Test",
        user_prompt="Add a new decision block",
        timestamp=datetime.now(timezone.utc)
    )

@pytest.mark.asyncio
async def test_inference_client_success(dummy_context):
    client = InferenceClient()
    
    mock_response = MagicMock()
    # Mocking the JSON response from Gemini
    mock_response.text = json.dumps({
        "operations": [
            {
                "op": "append_block",
                "payload": {
                    "type": "decision",
                    "content": {"text": "I made a decision"}
                }
            }
        ]
    })
    
    with patch('google.genai.models.AsyncModels.generate_content', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response
        
        result = await client.generate(dummy_context)
        
        assert isinstance(result, LLMResponse)
        assert len(result.operations) == 1
        assert result.operations[0].op == "append_block"
        assert result.operations[0].payload.type == "decision"
        mock_generate.assert_called_once()

@pytest.mark.asyncio
async def test_inference_client_retry_logic(dummy_context):
    client = InferenceClient()
    
    invalid_response = MagicMock()
    invalid_response.text = "this is not json"
    
    valid_response = MagicMock()
    valid_response.text = json.dumps({
        "operations": [
            {
                "op": "append_block",
                "payload": {
                    "type": "evidence",
                    "content": {"text": "Found some data"}
                }
            }
        ]
    })
    
    with patch('google.genai.models.AsyncModels.generate_content', new_callable=AsyncMock) as mock_generate:
        # First call fails, second succeeds
        mock_generate.side_effect = [invalid_response, valid_response]
        
        result = await client.generate(dummy_context)
        
        assert isinstance(result, LLMResponse)
        assert len(result.operations) == 1
        assert mock_generate.call_count == 2
