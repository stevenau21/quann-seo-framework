"""
Extraction prompts for Koray Gubur architect analysis.
Each prompt targets a specific extraction phase.
"""

# ── Phase 1: Entity Classification ──────────────────────────────

CLASSIFY_ENTITIES = """You are analyzing a knowledge graph of Koray Gubur's content from holisticseo.digital. 
Koray is a deep SEO practitioner who builds frameworks from patent analysis, IR theory, and NLP research.

Below is a list of entity names extracted from his content. Classify each one into exactly ONE category:

CATEGORIES:
- framework: A named system or methodology for doing SEO (e.g., "Topical Authority", "Semantic SEO", "Query-Entity Mapping")
- mental_model: A way of thinking or conceptual lens (e.g., "Search Engine as Information Retrieval System", "Entity-First Indexing")
- method: A specific technique or process (e.g., "Semantic Role Labeling for SEO", "Contextual Vector Analysis")
- concept: A key idea or term that's important but not a full framework (e.g., "Frame Semantics", "Lexical Units")
- tool: A specific tool or technology mentioned
- person: A person or organization
- noise: Not relevant to SEO methodology (dates, generic terms, etc.)

Return JSON array:
[{{"name": "exact entity name", "category": "framework", "confidence": 0.9, "reason": "one sentence why"}}]

Only classify entities that are clearly identifiable. Skip ambiguous ones.
Prioritize frameworks and mental models — these are our primary targets.

Entities to classify:
{entity_names}"""

# ── Phase 2: Framework Extraction ────────────────────────────────

EXTRACT_FRAMEWORK = """You are extracting Koray Gubur's SEO frameworks from his own writing on holisticseo.digital.

FRAMEWORK TO EXTRACT: {framework_name}

Below are relevant passages from his articles. Read them carefully and extract:

1. DEFINITION: What is this framework? (2-3 sentences, in Koray's own framing)
2. PROBLEM IT SOLVES: What was broken that this framework fixes?
3. EVOLUTION: How has it changed over time? (v1 → v2 → current)
4. DEPENDS_ON: What other concepts or frameworks does it require?
5. CONTRADICTS: What conventional SEO wisdom does it challenge?
6. UNIQUE_POSITION: What makes Koray's version different from others?
7. RAW_SOURCES: What patents, papers, or official docs does he cite?
8. NEGATIVE_SPACE: What does this framework NOT address? What questions are unanswered?

Return JSON:
{{
  "name": "{framework_name}",
  "type": "framework",
  "confidence": "core|secondary|emerging",
  "definition": "...",
  "problem_solved": "...",
  "evolution": ["v1: ...", "v2: ..."],
  "depends_on": ["..."],
  "contradicts": ["..."],
  "unique_position": "...",
  "raw_sources_cited": [
    {{"type": "patent|paper|official_doc|api_doc", "name": "...", "description": "..."}}
  ],
  "negative_space": {{
    "topics_avoided": ["..."],
    "questions_unanswered": ["..."],
    "blind_spots": ["..."]
  }},
  "source_docs": []  // I will fill this
}}

CONTEXT PASSAGES:
{passages}"""

# ── Phase 3: Mental Model Extraction ─────────────────────────────

EXTRACT_MENTAL_MODEL = """You are extracting Koray Gubur's mental models — how he THINKS about search, not what he DOES.

MENTAL MODEL TO EXTRACT: {model_name}

A mental model is a conceptual lens or way of seeing the problem. It shapes everything else.

Extract:
1. DESCRIPTION: How does Koray frame this? What's the core insight?
2. ORIGIN: Where does this mental model come from? (patent, IR theory, linguistics, etc.)
3. IMPLICATIONS: What does this mental model lead Koray to do differently?
4. CITATIONS: What sources does he cite to support this way of thinking?

Return JSON:
{{
  "name": "{model_name}",
  "type": "mental_model",
  "description": "...",
  "origin": "...",
  "implications": ["..."],
  "raw_sources_cited": [{{"type": "...", "name": "..."}}],
  "source_docs": []
}}

CONTEXT PASSAGES:
{passages}"""

# ── Phase 4: Signal Hierarchy ────────────────────────────────────

EXTRACT_SIGNAL_HIERARCHY = """You are analyzing Koray Gubur's content to understand what ranking signals he believes matter most.

Based on these passages from his articles, rank the signals/factors Koray considers important for SEO, from MOST important to LEAST important.

For each signal, provide:
- name: short label
- description: how Koray describes its importance
- source: what evidence he cites (patent, paper, observation)
- confidence: how certain he seems about this (high|medium|speculative)

Return JSON:
{{
  "signal_hierarchy": [
    {{"rank": 1, "name": "...", "description": "...", "source": "...", "confidence": "high"}}
  ]
}}

Rank at least 8 signals. Only include what's explicitly discussed in the passages.

PASSAGES:
{passages}"""

# ── Phase 5: Negative Space ──────────────────────────────────────

EXTRACT_NEGATIVE_SPACE = """You are analyzing Koray Gubur's entire body of work to find what's MISSING.

Read these representative passages from across his articles and identify:

1. TOPICS_AVOIDED: What significant SEO topics does Koray notably NOT discuss?
2. QUESTIONS_UNANSWERED: What questions does he raise but never resolve?
3. CONTRADICTIONS: Where does he say things that conflict with his other statements?
4. BLIND_SPOTS: What approaches/paradigms does he dismiss or overlook?
5. AEO_GEO_GAP: Does he address AI Overviews, ChatGPT, Perplexity? If not, that's a major gap.

Return JSON:
{{
  "topics_avoided": ["topic 1 (why notable)"],
  "questions_unanswered": ["question 1"],
  "contradictions": ["contradiction 1"],
  "blind_spots": ["blind spot 1"],
  "aeo_geo_coverage": "extensive|partial|minimal|none - one sentence assessment"
}}

PASSAGES:
{passages}"""

# ── Phase 6: Breadcrumb Tracing ───────────────────────────────────

EXTRACT_BREADCRUMBS = """You are tracing Koray Gubur's intellectual influences by scanning his writing for citations.

Read these passages and extract every reference to:
- PATENTS (USPTO numbers, patent titles, "Patent #...")
- RESEARCH PAPERS (arXiv, academic conferences: SIGIR, WWW, ECIR, ACL, EMNLP, etc.)
- API DOCUMENTATION (Google NLP API, Cloud APIs, Schema.org references)
- OFFICIAL DOCUMENTATION (Google Search Central, W3C specs, Schema.org)
- BOOKS (Information Retrieval textbooks, named authors)
- OTHER PRACTITIONERS (other SEOs he cites or references)

Return JSON:
{{
  "patents": [{{"id": "...", "title": "...", "why_cited": "..."}}],
  "papers": [{{"title": "...", "authors": "...", "venue": "...", "why_cited": "..."}}],
  "api_docs": [{{"name": "...", "why_cited": "..."}}],
  "official_docs": [{{"name": "...", "why_cited": "..."}}],
  "books": [{{"title": "...", "author": "...", "why_cited": "..."}}],
  "practitioners": [{{"name": "...", "context": "..."}}]
}}

PASSAGES:
{passages}"""
