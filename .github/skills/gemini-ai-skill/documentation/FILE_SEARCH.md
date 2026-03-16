# Gemini File Search (Managed RAG) API - Complete Documentation

## Table of Contents

1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Core Concepts](#core-concepts)
4. [API Reference](#api-reference)
5. [Usage Examples](#usage-examples)
6. [Advanced Features](#advanced-features)
7. [Performance & Cost Optimization](#performance--cost-optimization)
8. [Comparison With Alternatives](#comparison-with-alternatives)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Quick Reference](#quick-reference)
12. [Glossary](#glossary)

---

## Overview

Google File Search is a fully managed Retrieval-Augmented Generation (RAG) system built directly into the Gemini API. It eliminates the need for external vector databases, embedding pipelines, and chunking infrastructure by handling document indexing, semantic search, and citation tracking in a single integrated workflow.

### Key Capabilities

- **Managed RAG**: No external vector databases (Pinecone, ChromaDB) required
- **Automatic Chunking**: Documents are split and embedded automatically during upload
- **Semantic Search**: Finds relevant passages by meaning, not keyword matching
- **Built-in Citations**: Grounding metadata traces answers back to source documents
- **Persistent Stores**: Index documents once, query thousands of times
- **Multi-Document Synthesis**: Query across multiple documents in a single request
- **Metadata Filtering**: Narrow retrieval scope with custom key-value metadata
- **Custom Chunking**: Configure chunk size and overlap for different document types
- **Multiple Stores**: Up to 10 stores per project for logical document separation
- **Structured Output**: Combine File Search with JSON schema for typed responses (Gemini 3+)
- **150+ File Formats**: PDF, DOCX, TXT, code files, and more

### How It Works

File Search operates in two phases:

1. **Indexing (once)**: Upload documents to a File Search Store. Files are automatically chunked and converted to embeddings using `gemini-embedding-001`.
2. **Querying (repeatedly)**: Pass a user query with the File Search tool configured. The system retrieves semantically relevant chunks and provides them as context to the Gemini model, which generates a grounded response with citations.

**Two indexing paths**:

- **Direct upload**: Use `upload_to_file_search_store()` to upload and index in one step. The temporary File object is deleted after 48 hours, but the indexed data in the store persists indefinitely.
- **Upload then import**: First upload via `client.files.upload()`, then import into a store via `import_file()`. Useful when the same file needs to be imported into multiple stores.

---

## Installation & Setup

### Required Imports

```python
import time
from google import genai
from google.genai import types
```

### Initialize Client

```python
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
```

---

## Core Concepts

### File Search Stores

A File Search Store is a persistent container for indexed documents. Unlike temporary file uploads that expire after 48 hours, stores persist indefinitely until manually deleted.

Each store:

- Holds chunked and embedded documents ready for semantic retrieval
- Has a unique identifier (e.g., `fileSearchStores/fda-drug-labels-abc123`)
- **Store names are globally scoped** — each name must be unique across all projects
- Can be queried from any session using its name
- Supports up to 20GB of data (including embeddings)

**Data lifecycle**: There is no Time To Live (TTL) for embeddings and store data — they persist until manually deleted or the model is deprecated. Raw File objects uploaded via `client.files.upload()` expire after 48 hours, but data already imported into a store is unaffected.

### Chunking and Embeddings

During upload, File Search:

1. Splits each document into chunks based on the configured strategy
2. Converts chunks to numerical embeddings using `gemini-embedding-001`
3. Stores embeddings alongside metadata linking back to the source document and position

Embeddings capture semantic meaning, enabling retrieval of relevant passages even when the query wording differs from the document text.

### Grounding and Citations

Every response includes grounding metadata containing:

- **Source document title**: Which document informed each part of the answer
- **Retrieved text**: The exact passage used for grounding
- **Relevance ordering**: Chunks ordered by semantic similarity to the query

This creates a verification path from the generated response back to your original documents.

---

## API Reference

### Store Management

#### Create a Store

```python
store = client.file_search_stores.create(
    config={"display_name": "my-document-store"}
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `config.display_name` | `string` | Human-readable name for the store |

**Returns**: Store object with a `name` property containing the unique identifier.

#### List Stores

```python
for store in client.file_search_stores.list():
    print(store)
```

#### Get a Store

```python
store = client.file_search_stores.get(name="fileSearchStores/my-store-name")
```

#### Delete a Store

```python
client.file_search_stores.delete(name="fileSearchStores/my-store-name", config={"force": True})
```

**Note**: Use `force=True` to delete a store even if it still contains documents.

#### Upload and Index a Document

```python
operation = client.file_search_stores.upload_to_file_search_store(
    file="document.pdf",
    file_search_store_name=store.name,
    config={
        "display_name": "document-label",
        "chunking_config": {},       # Optional: custom chunking
        "custom_metadata": []        # Optional: metadata for filtering
    }
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `file` | `string` | Path to the file to upload |
| `file_search_store_name` | `string` | Store identifier from `store.name` |
| `config.display_name` | `string` | Label for the uploaded document |
| `config.chunking_config` | `dict` | Optional chunking configuration (see [Custom Chunking](#custom-chunking-configuration)) |
| `config.custom_metadata` | `list[dict]` | Optional metadata key-value pairs (see [Metadata Filtering](#metadata-filtering)) |

**Returns**: An asynchronous operation object. Poll until `operation.done` is `True`.

#### Import an Existing File

Alternatively, upload a file first via the Files API, then import it into a store:

```python
# Step 1: Upload file
sample_file = client.files.upload(
    file="sample.txt",
    config={"name": "display_file_name"}
)

# Step 2: Import into store
operation = client.file_search_stores.import_file(
    file_search_store_name=store.name,
    file_name=sample_file.name
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_search_store_name` | `string` | Store identifier |
| `file_name` | `string` | File name from `client.files.upload()` |
| `custom_metadata` | `list[dict]` | Optional metadata (passed as direct parameter, not nested in config) |

**Returns**: An asynchronous operation object. Poll until `operation.done` is `True`.

**When to use import vs direct upload**: Use `import_file()` when you need to import the same file into multiple stores, or when you want to manage the file lifecycle separately from indexing.

### Document Management

Manage individual documents within a store:

#### List Documents in a Store

```python
for doc in client.file_search_stores.documents.list(
    parent="fileSearchStores/my-store-name"
):
    print(doc)
```

#### Get a Document

```python
doc = client.file_search_stores.documents.get(
    name="fileSearchStores/my-store-name/documents/my_doc"
)
print(doc)
```

#### Delete a Document

```python
client.file_search_stores.documents.delete(
    name="fileSearchStores/my-store-name/documents/my_doc"
)
```

### Querying With File Search

#### `generate_content()` with File Search Tool

```python
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Your query here",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[store.name],
                    metadata_filter=""  # Optional: filter expression
                )
            )
        ]
    )
)
```

#### File Search Tool Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_search_store_names` | `list[string]` | One or more store identifiers to query |
| `metadata_filter` | `string` | Optional filter expression (e.g., `"category=diabetes"`). Syntax follows [AIP-160 filtering](https://google.aip.dev/160) |

#### Response Structure

| Field | Path | Description |
|-------|------|-------------|
| Response text | `response.text` | The generated answer grounded in your documents |
| Grounding chunks | `response.candidates[0].grounding_metadata.grounding_chunks` | Array of retrieved passages with source info |
| Source title | `chunk.retrieved_context.title` | Document display name |
| Source text | `chunk.retrieved_context.text` | The exact text passage retrieved |

### Chunking Configuration

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `chunking_config.white_space_config.max_tokens_per_chunk` | `int` | Maximum tokens per chunk | Model default |
| `chunking_config.white_space_config.max_overlap_tokens` | `int` | Token overlap between consecutive chunks | Model default |

### Metadata Configuration

Each metadata entry in `custom_metadata` accepts:

| Field | Type | Description |
|-------|------|-------------|
| `key` | `string` | Metadata key name |
| `string_value` | `string` | Text value (use for categories, types, labels) |
| `numeric_value` | `number` | Numeric value (use for years, versions, counts) |

---

## Usage Examples

### 1. Create a Store and Index Documents

Set up a File Search Store and upload documents for indexing:

```python
import time
from google import genai
from google.genai import types

client = genai.Client()

# Create a store
file_search_store = client.file_search_stores.create(
    config={"display_name": "fda-drug-labels"}
)
print(f"Created store: {file_search_store.name}")

# Upload and index documents
pdf_files = ["metformin.pdf", "atorvastatin.pdf", "lisinopril.pdf"]

for pdf_file in pdf_files:
    operation = client.file_search_stores.upload_to_file_search_store(
        file=pdf_file,
        file_search_store_name=file_search_store.name,
        config={"display_name": pdf_file.replace(".pdf", "")},
    )

    # Wait for indexing to complete
    while not operation.done:
        time.sleep(3)
        operation = client.operations.get(operation)

    print(f"{pdf_file} indexed")
```

**Notes**:

- Indexing is asynchronous. Large documents take longer to process.
- Each chunk preserves metadata linking it back to its source document and position.
- For production systems, add timeout logic to prevent infinite polling loops.

---

### 2. Query for Single-Document Information

Ask a question that targets content from a specific document:

```python
from google import genai
from google.genai import types

client = genai.Client()

query = "What are the contraindications for metformin?"

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=query,
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[file_search_store.name]
                )
            )
        ]
    ),
)

print(response.text)
```

The `tools` array tells the model to use File Search during generation. File Search retrieves the most semantically similar chunks and provides them as context to `gemini-3-flash-preview`, which generates the grounded answer.

---

### 3. Access Citations and Grounding Metadata

Extract which documents informed the answer for verification:

```python
from google import genai
from google.genai import types

client = genai.Client()

query = "What are the contraindications for metformin?"

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=query,
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[file_search_store.name]
                )
            )
        ]
    ),
)

print(response.text)

# Extract source citations
print("Sources used:")
grounding_chunks = response.candidates[0].grounding_metadata.grounding_chunks
for i, chunk in enumerate(grounding_chunks, 1):
    source_name = chunk.retrieved_context.title
    print(f"  [{i}] {source_name}")
```

The `grounding_chunks` array contains all retrieved passages ordered by relevance. Each chunk includes the source document title and the specific text passage that informed the answer.

---

### 4. Query Across Multiple Documents

Ask questions that require synthesizing information from several documents:

```python
from google import genai
from google.genai import types

client = genai.Client()

query = "Can a patient take both atorvastatin and metformin together? Are there any drug interactions?"

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=query,
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[file_search_store.name]
                )
            )
        ]
    ),
)

print(response.text)

# Inspect sources with text excerpts
print("Sources used:")
grounding_chunks = response.candidates[0].grounding_metadata.grounding_chunks
for i, chunk in enumerate(grounding_chunks, 1):
    source_name = chunk.retrieved_context.title
    source_text = chunk.retrieved_context.text[:100] + "..."
    print(f"  [{i}] {source_name}")
    print(f"      {source_text}")
```

File Search retrieves relevant sections from multiple documents and the model synthesizes them into a coherent answer. The `retrieved_context.text` attribute gives you the exact passage used, letting you verify the model did not hallucinate information.

---

### 5. Cross-Document Comparisons

Ask analytical questions that require comparing content across all indexed documents:

```python
from google import genai
from google.genai import types

client = genai.Client()

query = "Which medications have muscle-related side effects?"

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=query,
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[file_search_store.name]
                )
            )
        ]
    ),
)

print(response.text)

# Verify which documents were consulted
metadata = response.candidates[0].grounding_metadata
for i, chunk in enumerate(metadata.grounding_chunks, 1):
    print(f"  [{i}] {chunk.retrieved_context.title}")
```

File Search consults all indexed documents to answer comparison questions, identifying relevant information across the entire store.

---

### 6. Upload With Custom Chunking

Configure chunk size and overlap for specific document types:

```python
import time
from google import genai

client = genai.Client()

operation = client.file_search_stores.upload_to_file_search_store(
    file="metformin.pdf",
    file_search_store_name=file_search_store.name,
    config={
        "display_name": "metformin",
        "chunking_config": {
            "white_space_config": {
                "max_tokens_per_chunk": 200,
                "max_overlap_tokens": 20
            }
        }
    }
)

while not operation.done:
    time.sleep(3)
    operation = client.operations.get(operation)

print("Indexed with custom chunking")
```

**Chunking guidelines**:

| Document Type | Recommended Chunk Size | Rationale |
|---------------|----------------------|-----------|
| Technical docs with clear sections | 150–250 tokens | Precise retrieval of specific facts |
| Narrative documents (reports, papers) | 400–600 tokens | Preserves argument flow and context |

The `max_overlap_tokens` parameter ensures information spanning chunk boundaries is not lost during retrieval.

---

### 7. Upload With Metadata for Filtering

Attach metadata to documents during upload to enable filtering at query time:

```python
import time
from google import genai

client = genai.Client()

operation = client.file_search_stores.upload_to_file_search_store(
    file="metformin.pdf",
    file_search_store_name=file_search_store.name,
    config={
        "display_name": "metformin",
        "custom_metadata": [
            {"key": "category", "string_value": "diabetes"},
            {"key": "year", "numeric_value": 2017},
            {"key": "drug_class", "string_value": "biguanide"}
        ]
    }
)

while not operation.done:
    time.sleep(3)
    operation = client.operations.get(operation)

print("Indexed with metadata")
```

---

### 8. Query With Metadata Filtering

Restrict retrieval to documents matching specific metadata criteria:

```python
from google import genai
from google.genai import types

client = genai.Client()

query = "What are the common side effects?"

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=query,
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[file_search_store.name],
                    metadata_filter="category=diabetes"
                )
            )
        ]
    )
)

print(response.text)
```

The `metadata_filter` runs first to select candidate documents, then semantic search finds the most relevant passages within those documents. This is critical when stores contain heterogeneous document types.

---

### 9. Query Across Multiple Stores

Search across separate stores in a single request:

```python
from google import genai
from google.genai import types

client = genai.Client()

# Create specialized stores
diabetes_store = client.file_search_stores.create(
    config={"display_name": "diabetes-medications"}
)

cardio_store = client.file_search_stores.create(
    config={"display_name": "cardiovascular-medications"}
)

# Query both stores at once
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="What medications treat both diabetes and heart disease?",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[
                        diabetes_store.name,
                        cardio_store.name
                    ]
                )
            )
        ]
    )
)

print(response.text)
```

File Search retrieves from all specified stores and synthesizes results. The grounding metadata identifies which store each citation came from, maintaining full traceability.

---

### 10. Import an Existing File Into a Store

Upload a file via the Files API first, then import it into a store. Useful when the same file needs to be indexed in multiple stores:

```python
import time
from google import genai
from google.genai import types

client = genai.Client()

# Step 1: Upload file via Files API
sample_file = client.files.upload(
    file="sample.txt",
    config={"name": "display_file_name"}
)

# Step 2: Create a store
file_search_store = client.file_search_stores.create(
    config={"display_name": "my-document-store"}
)

# Step 3: Import the file into the store
operation = client.file_search_stores.import_file(
    file_search_store_name=file_search_store.name,
    file_name=sample_file.name
)

while not operation.done:
    time.sleep(5)
    operation = client.operations.get(operation)

print("File imported and indexed")
```

You can also attach metadata during import:

```python
operation = client.file_search_stores.import_file(
    file_search_store_name=file_search_store.name,
    file_name=sample_file.name,
    custom_metadata=[
        {"key": "author", "string_value": "Robert Graves"},
        {"key": "year", "numeric_value": 1934}
    ]
)
```

**Note**: With `import_file()`, `custom_metadata` is passed as a direct parameter, not nested inside a config dict.

---

### 11. Manage Stores and Documents

List, inspect, and delete stores and their documents:

```python
from google import genai

client = genai.Client()

# List all stores
for store in client.file_search_stores.list():
    print(store)

# Get a specific store
my_store = client.file_search_stores.get(
    name="fileSearchStores/my-store-name"
)

# List documents in a store
for doc in client.file_search_stores.documents.list(
    parent="fileSearchStores/my-store-name"
):
    print(doc)

# Get a specific document
doc = client.file_search_stores.documents.get(
    name="fileSearchStores/my-store-name/documents/my_doc"
)
print(doc)

# Delete a document from a store
client.file_search_stores.documents.delete(
    name="fileSearchStores/my-store-name/documents/my_doc"
)

# Delete an entire store (force=True deletes even if documents remain)
client.file_search_stores.delete(
    name="fileSearchStores/my-store-name",
    config={"force": True}
)
```

---

### 12. Structured Output With File Search

Combine File Search with structured JSON output using Pydantic models (Gemini 3+ models):

```python
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

client = genai.Client()

class Money(BaseModel):
    amount: str = Field(description="The numerical part of the amount.")
    currency: str = Field(description="The currency of amount.")

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="What is the minimum hourly wage in Tokyo right now?",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[file_search_store.name]
                )
            )
        ],
        response_mime_type="application/json",
        response_schema=Money.model_json_schema()
    )
)

result = Money.model_validate_json(response.text)
print(result)
```

**Requirements**: Structured output with File Search requires Gemini 3+ models. Pass `response_mime_type="application/json"` and provide a schema via `response_schema`.

---

## Advanced Features

### Custom Chunking Configuration

Fine-tune how documents are split during indexing.

**Trade-offs**:

- **Smaller chunks** (150–250 tokens): More precise retrieval but may miss broader context. Best for structured documents with clear sections (tables, lists, technical specs).
- **Larger chunks** (400–600 tokens): Retain more meaning and argument flow but may include irrelevant information. Best for narrative documents (research papers, reports).

**Overlap** (`max_overlap_tokens`): Ensures information at chunk boundaries is not lost. A typical value is 10–20% of the chunk size.

### Metadata Filtering

Narrow retrieval scope before semantic search runs. Useful when stores contain documents of different types, categories, or time periods.

**Supported value types**:

- `string_value`: Text metadata (categories, labels, document types)
- `numeric_value`: Numeric metadata (years, versions, priority levels)

**Filter syntax**: `"key=value"` (e.g., `"category=diabetes"`, `"year=2017"`). For advanced filter syntax, see the [AIP-160 filtering standard](https://google.aip.dev/160).

### Multiple Stores

Each Google Cloud project supports up to 10 File Search Stores. Use multiple stores to:

- Separate documents by access control or domain
- Isolate performance-sensitive collections
- Organize by logical category or time period

Stores persist indefinitely and require manual deletion when no longer needed.

### Combining File Search With Other Tools

File Search can be combined with other tools in the same `generate_content()` request:

```python
config=types.GenerateContentConfig(
    tools=[
        types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[store.name]
            )
        ),
        types.Tool(google_search=types.GoogleSearch())
    ]
)
```

This allows the model to ground answers in both your private documents and real-time web information.

---

## Performance & Cost Optimization

### Store Size Limits

- Keep individual stores under **20GB** for optimal retrieval latency.
- Embeddings require approximately **3x** the size of original files. A 7GB collection generates ~21GB of stored data.
- When approaching the limit, create separate stores organized by category or access pattern.

### Pricing

File storage and embedding generation at query time are **free of charge**. You only pay for creating embeddings when you first index files and the standard Gemini model input/output token costs.

| Operation | Cost |
|-----------|------|
| Indexing (embedding creation) | Applicable embedding model cost |
| File storage | Free |
| Query-time embedding generation | Free |
| Querying | Standard Gemini model input/output token pricing |

This pricing model favors **read-heavy workloads** where you query the same documents repeatedly.

### Model Selection for Queries

| Model | Latency | Cost | Best For |
|-------|---------|------|----------|
| `gemini-3-flash-preview` | 1–2 seconds | Low | Most queries, high-volume applications |
| `gemini-2.5-pro` | Higher | Higher | Deep reasoning across multiple sources, complex synthesis |

Use `gemini-3-flash-preview` for most File Search queries. Reserve `gemini-2.5-pro` for queries requiring deep multi-source reasoning.

---

## Comparison With Alternatives

| Feature | Google File Search | OpenAI File Search | Custom RAG (LangChain) |
|---------|-------------------|-------------------|----------------------|
| **Pricing Model** | Free storage; pay for indexing embeddings + model tokens | $0.10/GB daily storage | Infrastructure + development costs |
| **Chunking Control** | Automated with basic config | Configurable (800 tokens default, 400 overlap) | Full control over strategy |
| **Search Type** | Semantic (vector only) | Hybrid (vector + keyword) | Any method you implement |
| **File Formats** | 150+ types | 6 types (TXT, MD, HTML, DOCX, PPTX, PDF) | Depends on parsers used |
| **Setup Time** | Minutes | Minutes | Days to weeks |
| **Citations** | Built-in with grounding metadata | Built-in | Must implement yourself |
| **Best For** | High query volume, quick deployment | Keyword-heavy queries, moderate control | Complex requirements, full customization |

### When to Use Google File Search

- Building prototypes or proofs-of-concept where speed matters
- Standard patterns: Q&A over documents, knowledge bases, documentation search
- Teams lacking deep RAG expertise
- Predictable costs and minimal operational overhead

### When to Build Custom RAG

- Advanced chunking or specialized retrieval methods required
- Working with structured data or unusual file formats
- Agentic RAG systems combining multiple strategies
- Compliance requires specific infrastructure or model control
- Scale justifies the engineering investment

---

## Best Practices

### Store Organization

1. ✅ Use **descriptive display names** for stores and documents
2. ✅ **Separate stores** by domain, access pattern, or document type
3. ✅ Add **metadata** during upload to enable filtering at query time
4. ✅ **Monitor store size** and split before reaching the 20GB limit
5. ✅ **Save store names** for cross-session access

### Chunking Strategy

1. ✅ Use **smaller chunks** (150–250 tokens) for structured, technical documents
2. ✅ Use **larger chunks** (400–600 tokens) for narrative documents
3. ✅ Set **overlap** at 10–20% of chunk size to preserve boundary context
4. ✅ **Test retrieval quality** with different chunk sizes for your document types

### Querying

1. ✅ Use `gemini-3-flash-preview` for **most queries** (cost and latency)
2. ✅ **Verify citations** by checking `grounding_metadata.grounding_chunks`
3. ✅ Use **metadata filtering** to narrow scope in large, heterogeneous stores
4. ✅ **Validate grounding metadata exists** before accessing citations

### Production Safeguards

1. ✅ Add **timeout logic** to upload polling loops to prevent infinite waits
2. ✅ Wrap API calls in **error handling** (try-except blocks)
3. ✅ **Validate grounding metadata** before accessing citation fields
4. ✅ **Test with domain experts** to catch plausible but incorrect answers
5. ✅ Consider **data privacy** when uploading sensitive documents to Google servers

### Anti-Patterns to Avoid

1. ❌ Indexing all documents in a single store without logical separation
2. ❌ Skipping metadata when stores contain heterogeneous document types
3. ❌ Using `gemini-2.5-pro` for simple retrieval queries (unnecessary cost)
4. ❌ Trusting generated answers without verifying grounding metadata
5. ❌ Polling upload operations without a timeout safeguard
6. ❌ Re-uploading documents to a store that already contains them
7. ❌ Exceeding the 20GB store limit without splitting into multiple stores

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Upload hangs indefinitely | Large document or network issue | Add timeout logic to polling loop |
| Empty grounding metadata | No relevant chunks found | Verify documents are indexed; check query relevance |
| Irrelevant retrieval results | Chunks too large or too small | Adjust `max_tokens_per_chunk` for your document type |
| Store creation fails | Project limit reached (10 stores) | Delete unused stores or consolidate documents |
| Metadata filter returns no results | Typo in filter key or value | Verify metadata keys and values match exactly |
| Slow retrieval | Store exceeds 20GB | Split into multiple smaller stores |

### Polling Pattern With Timeout

```python
import time

TIMEOUT_SECONDS = 300
start_time = time.time()

while not operation.done:
    if time.time() - start_time > TIMEOUT_SECONDS:
        raise TimeoutError("Document indexing exceeded timeout")
    time.sleep(3)
    operation = client.operations.get(operation)
```

---

## Quick Reference

### File Search Workflow

```
1. Create Store          → client.file_search_stores.create(config={...})
2a. Upload & Index Docs  → client.file_search_stores.upload_to_file_search_store(...)
2b. Or Upload + Import   → client.files.upload(...) then client.file_search_stores.import_file(...)
3. Poll Until Done       → while not operation.done: ...
4. Query With Tool       → client.models.generate_content(model=..., tools=[FileSearch])
5. Read Response         → response.text
6. Verify Citations      → response.candidates[0].grounding_metadata.grounding_chunks
```

### Store & Document Management

```
List stores              → client.file_search_stores.list()
Get store                → client.file_search_stores.get(name=...)
Delete store             → client.file_search_stores.delete(name=..., config={"force": True})
List documents           → client.file_search_stores.documents.list(parent=...)
Get document             → client.file_search_stores.documents.get(name=...)
Delete document          → client.file_search_stores.documents.delete(name=...)
```

### Parameter Quick Reference

| Parameter | Location | Purpose |
|-----------|----------|----------|
| `display_name` | Store/upload config | Human-readable label |
| `file_search_store_names` | `FileSearch` tool | Which stores to query |
| `metadata_filter` | `FileSearch` tool | Filter documents before retrieval |
| `max_tokens_per_chunk` | `chunking_config` | Maximum chunk size |
| `max_overlap_tokens` | `chunking_config` | Overlap between consecutive chunks |
| `custom_metadata` | Upload/import config | Key-value pairs for filtering |
| `response_mime_type` | `GenerateContentConfig` | Set to `"application/json"` for structured output |
| `response_schema` | `GenerateContentConfig` | JSON schema for typed responses |

### Supported File Formats

File Search supports **150+ file types** including:

- **Documents**: PDF, DOCX, TXT, RTF, ODT
- **Code**: Python, JavaScript, Java, C++, and more
- **Web**: HTML, CSS, XML, JSON
- **Other**: Markdown, LaTeX, CSV (limited)

---

## Glossary

- **RAG (Retrieval-Augmented Generation)**: A technique that retrieves relevant information from external documents before generating a response, grounding answers in actual data
- **File Search Store**: A persistent container for indexed documents, holding chunked embeddings ready for semantic retrieval
- **Chunking**: The process of splitting documents into smaller pieces for embedding and retrieval
- **Embeddings**: Numerical vector representations of text that capture semantic meaning
- **Grounding**: Linking generated answers to specific source passages in your documents
- **Grounding Metadata**: Response metadata containing retrieved passages, source titles, and citation information
- **Metadata Filtering**: Restricting retrieval to documents matching specified key-value criteria before semantic search runs
- **Semantic Search**: Finding relevant content by meaning rather than exact keyword matching
- **Indexing**: The process of uploading, chunking, and embedding documents into a File Search Store
- **File Import**: An alternative indexing path where files are uploaded via the Files API and then imported into a store
- **Structured Output**: Combining File Search with JSON schema enforcement to produce typed, parseable responses
- **AIP-160**: Google's standard filtering syntax used for metadata filter expressions

---

*End of Documentation*
