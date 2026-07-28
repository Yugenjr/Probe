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
    
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps({
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
    
    mock_create = AsyncMock()
    mock_create.return_value.choices = [mock_choice]
    
    with patch.object(client.client.chat.completions, 'create', mock_create):
        result = await client.generate(dummy_context)
        
        assert isinstance(result, LLMResponse)
        assert len(result.operations) == 1
        assert result.operations[0].op == "append_block"
        assert result.operations[0].payload.type == "decision"
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_inference_client_retry_logic(dummy_context):
    client = InferenceClient()
    
    # Mocking first call throwing JSON Decode error, second succeeding
    mock_choice_valid = MagicMock()
    mock_choice_valid.message.content = json.dumps({
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
    
    mock_choice_invalid = MagicMock()
    mock_choice_invalid.message.content = "this is not json"
    
    mock_create = AsyncMock()
    # First returns invalid response (will throw json.JSONDecodeError), second returns valid
    mock_resp_invalid = MagicMock()
    mock_resp_invalid.choices = [mock_choice_invalid]
    mock_resp_valid = MagicMock()
    mock_resp_valid.choices = [mock_choice_valid]
    
    mock_create.side_effect = [mock_resp_invalid, mock_resp_valid]
    
    with patch.object(client.client.chat.completions, 'create', mock_create):
        result = await client.generate(dummy_context)
        
        assert isinstance(result, LLMResponse)
        assert len(result.operations) == 1
        assert mock_create.call_count == 2

