# Sandbox Benchmark — 2026-05-27

3 models × 3 chunks, LightRAG extraction prompt, every model completed every chunk at correct token caps.

## Chunks

| Chunk | Source | Size |
|-------|--------|------|
| 1 | Lecture 1 - Framework Intro | ~1384 chars |
| 2 | Lecture 20 - Question Generation | ~1480 chars |
| 3 | Lecture 60 - Information Extraction Points | ~1430 chars |

## Raw Results

| Model | Chunk | Time | Entities | Relations | Tokens | Completed |
|-------|-------|------|----------|-----------|--------|-----------|
| gemma4:31b-cloud | 1 | 7s | 13 | 6 | 573 | ✓ |
| gemma4:31b-cloud | 2 | 6s | 16 | 17 | 1017 | ✓ |
| gemma4:31b-cloud | 3 | 24s | 15 | 12 | 855 | ✓ |
| deepseek-v4-flash:cloud | 1 | 126s | 12 | 6 | 2478 | ✓ |
| deepseek-v4-flash:cloud | 2 | 168s | 17 | 16 | 2360 | ✓ |
| deepseek-v4-flash:cloud | 3 | 136s | 22 | 17 | 3754 | ✓ |
| deepseek-v4-pro:cloud | 1 | 68s | 16 | 14 | 3801 | ✓ |
| deepseek-v4-pro:cloud | 2 | 102s | 19 | 24 | 5513 | ✓ |
| deepseek-v4-pro:cloud | 3 | 95s | 24 | 22 | 5387 | ✓ |

## Token Caps Used

| Model | num_predict | Why |
|-------|------------|-----|
| gemma4 | 4096 | Never hits cap — efficient output |
| flash | 16384 | 4096 truncated to zero relations on chunk 1 |
| pro | 8192 | 4096 truncated; 8192 allows full entity+relation output |

## Quality Findings

### Gemma4 31B
- Clean output, zero hallucinations
- Weakest type accuracy (Country→Location, Hot Water→NaturalObject)
- Misses domain concepts: Source Context, Entity Type, Semantic Content Network
- No bidirectional relations

### DeepSeek v4 Flash
- Needs 16384 output cap (4096 = truncated with zero relations)
- Low noise (3 vague entities across 3 chunks)
- Better types than Gemma4
- Still misses bidirectional relations

### DeepSeek v4 Pro
- Richest graph — 40% more relations than Gemma4
- Required num_predict=8192
- Best type accuracy (Country→Concept, Context Vectors→Method)
- Bidirectional edges (Friendship↔Benefit, Friendship↔Duration)
- 2 harmless noise entities across 3 chunks
- Only model capturing full domain vocabulary (Source Context, Entity Type, Semantic Content Network)

## Decision

**Pro selected for 8014 Koray Lectures.** Permanent quality gain (40% richer graph, bidirectional edges) outweighs 7× time cost for one-time ingestion.
