import os
import pytest

# Inject dummy API keys for testing environment to prevent validation and initialization errors
os.environ["GROQ_API_KEY"] = "dummy_key_for_testing"
os.environ["GEMINI_API_KEY"] = "dummy"
