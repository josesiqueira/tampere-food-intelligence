# Lesson 1: OpenAI Responses API with cURL

## Basic Request (without tools)

```bash
curl https://api.openai.com/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_OPENAI_API_KEY" \
  -d '{
    "model": "gpt-5.2",
    "input": "What are the best rated lunch restaurants near Tampere train station?"
  }'
```

Copy and paste in terminal, change the YOUR_OPENAI_API_KEY first
```
curl https://api.openai.com/v1/responses -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_KEY" -d '{"model": "gpt-5.2", "input": "What are the best rated lunch restaurants near Tampere train station?"}'
```

### Response

```json
{
  "id": "resp_...",
  "object": "response",
  "created_at": 1767883405,
  "status": "completed",
  "model": "gpt-5.2-2025-12-11",
  "output": [
    {
      "id": "msg_...",
      "type": "message",
      "status": "completed",
      "content": [
        {
          "type": "output_text",
          "annotations": [],
          "text": "Here are some of the best rated lunch restaurants near Tampere train station..."
        }
      ],
      "role": "assistant"
    }
  ],
  "usage": {
    "input_tokens": 19,
    "output_tokens": 85,
    "total_tokens": 104
  }
}
```

## With Web Search Tool Enabled

```bash
curl https://api.openai.com/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_OPENAI_API_KEY" \
  -d '{
    "model": "gpt-5.2",
    "tools": [
        { "type": "web_search" }
    ],
    "input": "What are the best rated lunch restaurants near Tampere train station?"
  }'
```

Copy and paste in terminal, change the YOUR_OPENAI_API_KEY first
```
curl https://api.openai.com/v1/responses -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_KEY" -d '{"model": "gpt-5.2", "tools": [{"type": "web_search"}], "input": "What are the best rated lunch restaurants near Tampere train station?"}'
```

### Response

```json
{
  "id": "resp_...",
  "object": "response",
  "created_at": 1767885697,
  "status": "completed",
  "model": "gpt-5.2-2025-12-11",
  "output": [
    {
      "id": "ws_...",
      "type": "web_search_call",
      "status": "completed",
      "action": {
        "type": "search",
        "queries": [
          "best rated lunch restaurants near Tampere train station",
          "top lunch places Tampere rautatieasema"
        ],
        "query": "best rated lunch restaurants near Tampere train station"
      }
    },
    {
      "id": "msg_...",
      "type": "message",
      "status": "completed",
      "content": [
        {
          "type": "output_text",
          "annotations": [
            {
              "type": "url_citation",
              "title": "Tampere Restaurants - Google Maps",
              "url": "https://www.google.com/maps/..."
            }
          ],
          "text": "Here are some of the best-rated lunch restaurants near Tampere train station (Rautatieasema):\n\n1. **Ravintola Näsinneula** — Finnish fine dining in the observation tower (4.5 stars)\n2. **Plevna** — Brewpub with hearty Finnish and international dishes (4.4 stars)\n..."
        }
      ],
      "role": "assistant"
    }
  ],
  "tools": [
    {
      "type": "web_search"
    }
  ],
  "usage": {
    "input_tokens": 8483,
    "output_tokens": 182,
    "total_tokens": 8665
  }
}
```
