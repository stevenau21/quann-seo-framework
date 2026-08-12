"""
seo-methodology server — thin config wrapper around the shared nexus engine.
One notebook in the multi-bot architecture: SEO research chatbot.
"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, "/home/steve/lightrag-env/lib/python3.11/site-packages")
sys.path.insert(0, "/home/steve/lightrag-apps")

import nexus_shared
from nexus_shared import NotebookConfig, create_app

SEO_SYSTEM_PROMPT = """You are an expert SEO research assistant drawing from holisticseo.digital.
You answer in-depth questions about SEO methodology, content strategy, entity-based SEO,
topical maps, and technical SEO concepts.

## How to respond
- Be thorough but clear — explain concepts, don't just list definitions
- Connect ideas across different SEO disciplines when relevant
- Use concrete examples from the knowledge base
- Structure longer answers with clear sections when helpful
- If the context doesn't fully answer a question, be honest about the gap

""" + nexus_shared.CONFLICT_RESOLUTION_INSTRUCTION + """

## RESEARCH CONTEXT:
{context}"""

config = NotebookConfig(
    name="seo-methodology",
    title="SEO Methodology",
    workspace="/home/steve/lightrag-apps/seo-methodology/workspace",
    fallback_workspace="/home/steve/lightrag-apps/seo-methodology/workspace_old",
    llm_model="deepseek-v4-pro:cloud",
    top_k_retrieve=40,
    top_n_rerank=5,
    max_context_chars=6000,
    llm_temperature=0.3,
    llm_max_tokens=1500,
    route_path="/ask",
    route_method="ask",
    system_prompt_template=SEO_SYSTEM_PROMPT,
)

app = create_app(config)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8002, log_level="warning")
