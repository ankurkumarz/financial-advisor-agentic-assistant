# Claude Code Session Notes

## Session Date: 2025-11-21

### Project: Financial Advisor Agentic Assistant

---

## Issues Fixed: Enterprise Docs Agent

### Location
`/app/financial_advisor_agent/sub_agents/enterprise_docs_agent/`

### Problems Identified

#### 1. Pydantic Validation Error (prompt.py)
**Error:**
```
pydantic_core._pydantic_core.ValidationError: 5 validation errors for LlmAgent
instruction.str
```

**Root Cause:**
- Trailing comma after `ENTERPRISE_DOCS_AGENT_PROMPT` string definition
- Made the variable a tuple instead of a string
- Located at: `prompt.py:19`

**Fix:**
```python
# Before (incorrect - tuple)
ENTERPRISE_DOCS_AGENT_PROMPT="""...""",

# After (correct - string)
ENTERPRISE_DOCS_AGENT_PROMPT = """..."""
```

#### 2. Empty Search Implementation (vector_search_tool.py)
**Issue:**
- The `search()` method was not implemented (just had `pass`)
- No documents were being retrieved from ChromaDB
- Tool was registered but non-functional

**Fix:**
Implemented complete search functionality:
```python
async def search(self, query: str, top_k: Optional[int] = None) -> Dict[str, Any]:
    """
    Search for relevant documents using semantic similarity.

    Returns:
        {
            "found": bool,
            "query": str,
            "total_results": int,
            "results": [
                {
                    "rank": int,
                    "content": str,
                    "source": str,
                    "chunk_index": int,
                    "relevance_score": float  # 1 - distance
                }
            ]
        }
    """
```

**Features:**
- ChromaDB semantic search using embeddings
- Formatted results with relevance scores (converted from distances)
- Source tracking with filename and chunk index
- Error handling with graceful fallbacks

#### 3. Tool Definition Issues (vector_search_tool.py)
**Problems:**
- Tool name mismatch: code used "vector_search", prompt referenced "search_documents"
- Vague description
- Missing handler reference

**Fix:**
```python
def get_tool_definition(self) -> Dict[str, Any]:
    return {
        "name": "search_documents",  # Match prompt reference
        "description": (
            "Search internal financial documents using semantic similarity. "
            "Returns relevant document chunks with source information and relevance scores. "
            "Use this tool to find information about financial products, policies, regulations, and company guidelines."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find relevant documents. Use specific terms and questions."
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of document chunks to return (default: 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        },
        "handler": self.search  # Link to actual search method
    }
```

#### 4. Prompt Enhancement (prompt.py)
**Improvements:**
- Added explicit output format documentation
- Added citation format guidance: `[source_filename, chunk_index]`
- Documented the search results structure
- Added instructions for handling edge cases (no results, multiple chunks)

---

## System Architecture

### Enterprise Docs Agent
**Purpose:** Knowledge retrieval using ChromaDB vector search

**Components:**
1. **agent.py** - Agent definition and initialization
2. **prompt.py** - System prompt with instructions
3. **vector_search_tool.py** - ChromaDB integration and search

**Flow:**
1. PDFs loaded from `docs/pdfs/` into ChromaDB on startup
2. Documents chunked (1000 chars, 100 char overlap)
3. Embedded using Google's `text-embedding-004` model
4. Agent uses `search_documents` tool to query vector DB
5. Returns formatted results with sources and relevance scores

**Key Settings:**
- Collection: `settings.chroma_collection_name`
- DB Path: `settings.chroma_persist_directory`
- Model: `settings.vertex_ai_model`
- Temperature: `settings.retriever_temperature`
- Top K Results: 5 (configurable)

---

## ChromaDB Vector Search Details

### Embedding Configuration
```python
embedding_fn = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
    api_key=os.getenv("GEMINI_API_KEY"),
    model_name="models/text-embedding-004",
    task_type="RETRIEVAL_DOCUMENT"
)
```

### Document Chunking Strategy
- Chunk Size: 1000 characters
- Overlap: 100 characters
- Method: Sliding window

### Metadata Structure
```python
{
    "source": "filename.pdf",
    "chunk_index": 0
}
```

### Search Result Format
```python
{
    "found": True,
    "query": "user query",
    "total_results": 5,
    "results": [
        {
            "rank": 1,
            "content": "document text...",
            "source": "filename.pdf",
            "chunk_index": 0,
            "relevance_score": 0.95  # Higher = more relevant
        }
    ]
}
```

---

## Best Practices for RAG Implementation

### 1. Tool Definition
- Use descriptive tool names that match prompt references
- Include detailed descriptions of what the tool does
- Document expected input/output formats
- Always include the `handler` reference

### 2. Search Results
- Convert distances to similarity scores for intuitive interpretation
- Include source citations for transparency
- Rank results by relevance
- Handle empty results gracefully

### 3. Agent Prompts
- Document the exact format of tool outputs
- Provide examples of how to use tools
- Specify citation formats
- Include edge case handling instructions

### 4. Error Handling
- Catch ChromaDB exceptions
- Return structured error responses
- Log errors for debugging
- Provide fallback messages to agents

---

## Testing Checklist

- [ ] Agent imports without Pydantic errors
- [ ] ChromaDB collection initializes
- [ ] PDF documents load on startup
- [ ] Search returns relevant results
- [ ] Results include proper citations
- [ ] Relevance scores calculated correctly
- [ ] Agent follows citation format in responses
- [ ] Error handling works for missing documents

---

## Future Improvements

### Potential Enhancements
1. **Multi-query retrieval**: Generate multiple search queries for complex questions
2. **Reranking**: Add cross-encoder reranking for better precision
3. **Hybrid search**: Combine semantic + keyword search
4. **Query expansion**: Use synonyms and related terms
5. **Metadata filtering**: Filter by document type, date, etc.
6. **Caching**: Cache frequent queries
7. **Relevance threshold**: Filter low-scoring results
8. **Document summaries**: Store and return document-level summaries

---

## Common Issues & Solutions

### Issue: "Collection not found"
**Solution:** Ensure `initialize_knowledge_base()` runs before agent creation

### Issue: "Embedding API key not set"
**Solution:** Set `GEMINI_API_KEY` environment variable

### Issue: "No results returned"
**Solution:** Check if documents are loaded (`collection.count() > 0`)

### Issue: "Relevance scores too low"
**Solution:** Adjust chunking strategy or use query expansion

---

## Files Modified (2025-11-21)

1. `app/financial_advisor_agent/sub_agents/enterprise_docs_agent/prompt.py`
   - Fixed trailing comma bug
   - Enhanced prompt with output format documentation

2. `app/financial_advisor_agent/sub_agents/enterprise_docs_agent/vector_search_tool.py`
   - Implemented `search()` method
   - Updated tool definition
   - Added proper error handling

---

## References

- [Google ADK Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/adk)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Google Embedding Models](https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/get-text-embeddings)

---

*Session completed by Claude Code on 2025-11-21*
