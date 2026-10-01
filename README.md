# TokenLab Python SDK

Lightweight Python client for TokenLab discovery, OpenAI-compatible APIs, and native endpoint families.

Install from PyPI:

```bash
pip install tokenlab-ai
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
    "model": "claude-sonnet-5",
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

## System One decisions

Discover `tokenlab.list_models(category="decision")` and inspect the selected model with `get_model()` first. Decision models declare the `systemone` public operation, not a chat format.

```python
with TokenLabClient(timeout=60.0) as tokenlab:
    decision = tokenlab.evaluate_decisions({
        "model": "jev-1.13",
        "state": {"ticket": "Please refund my duplicate charge."},
        "questions": {"refund": {"type": "noul", "instructions": "Is a refund requested?"}},
    })
    print(decision["answers"], decision["usage"])
```

The client reads `TOKENLAB_API_KEY` from the environment. This synchronous `/v1/systemone` call preserves typed answers, probabilities, optional confidence, and usage. It is not Chat, streaming, or Batch. A decision does not authorize a refund or another side effect. Errors are returned without automatic resubmission. Available in SDK 0.1.2+.

## Base URLs

- API: `https://api.tokenlab.sh`
- OpenAI-compatible SDK base URL: `https://api.tokenlab.sh/v1`
- OpenAPI: `https://tokenlab.sh/docs/openapi.json`
