# Nexus LightRAG Bots

**Multi-bot architecture — one engine, many notebooks.**

All chatbots share a single engine (`nexus_shared.py`) via thin config wrappers. Each "notebook" is a workspace directory with its own graph data + a config dict specifying LLM model, system prompt, and retrieval parameters.

## Running Bots

| Bot | Port | Model | Route |
|-----|------|-------|-------|
| quann-chat | 8001 | gemma4:31b-cloud | `/chat` |
| seo-methodology | 8002 | deepseek-v4-pro:cloud | `/ask` |

## Adding a New Bot

Create a ~50-line `server.py`:

```python
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, "/home/steve/lightrag-env/lib/python3.11/site-packages")
sys.path.insert(0, "/home/steve/lightrag-apps")

from nexus_shared import NotebookConfig, create_app

config = NotebookConfig(
    name="my-bot",
    title="My Bot",
    workspace="/home/steve/lightrag-apps/my-bot/workspace",
    llm_model="gemma4:31b-cloud",
    top_k_retrieve=20,
    top_n_rerank=5,
    route_path="/chat",
    route_method="chat",
    system_prompt_template="You are a helpful assistant.\n\nCONTEXT:\n{context}",
)

app = create_app(config)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8003)
```

## Architecture

```
nexus_shared.py         ← Shared engine (NotebookConfig + create_app + reranker + classifier)
    │
    ├── quann-chat/server.py   ← 53-line config wrapper
    ├── seo-methodology/server.py  ← 49-line config wrapper
    └── your-bot/server.py     ← future notebooks
```

- **Query classifier**: Auto-detects local/global/hybrid retrieval mode
- **Shared reranker**: mxbai-rerank-base-v1, CPU-only, loaded once
- **Conflict resolution**: System prompt instructs LLM to resolve contradictory sources
- **Citations**: Up to 20 `[ref:N]` citations per response

## Setup

```bash
git clone <this-repo>
cd lightrag-apps
./scripts/setup.sh
```

## Requirements

- Python 3.11+
- Ollama Cloud API access
- ~2GB RAM (for embedding + reranker models)
