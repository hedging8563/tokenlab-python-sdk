# TokenLab Python SDK

Lightweight Python client for TokenLab discovery, OpenAI-compatible APIs, and native endpoint families.

The package is prepared for PyPI as `tokenlab`. Until PyPI publishing is complete, install from GitHub:

```bash
pip install git+https://github.com/hedging8563/tokenlab-python-sdk.git
```

## Usage

```python
from tokenlab import TokenLabClient

with TokenLabClient(api_key="YOUR_TOKENLAB_API_KEY") as tokenlab:
    models = tokenlab.list_models(category="chat")
    response = tokenlab.create_response({
        "model": "gpt-5.5",
        "input": "Hello from TokenLab",
    })
```

## Native Endpoints

```python
tokenlab.create_anthropic_message({
    "model": "claude-sonnet-5.5",
    "max_tokens": 512,
    "messages": [{"role": "user", "content": "Hello"}],
})

tokenlab.create_gemini_content("gemini-3.5-flash", {
    "contents": [{"role": "user", "parts": [{"text": "Hello"}]}],
})
```

## Discovery Helpers

```python
tokenlab.get_models_json()
tokenlab.get_pricing_json()
tokenlab.get_integrations_json()
```

## Base URLs

- API: `https://api.tokenlab.sh`
- OpenAI-compatible SDK base URL: `https://api.tokenlab.sh/v1`
- OpenAPI: `https://docs.tokenlab.sh/openapi.json`
