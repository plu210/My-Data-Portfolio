import os
import glob
import re
import ollama
from ollama import chat
from langchain.schema import Document
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 1. Configuration
# Select embedding and language models
EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'
LANGUAGE_MODEL  = 'hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF'

# 2. Load cleaned text files
# Read all .txt files from a folder and return their contents as a list of strings
def load_clean_texts(folder: str):
    """
    Read all .txt files from `folder` and return a list of raw strings.
    """
    paths = sorted(glob.glob(os.path.join(folder, "*.txt")))
    return [open(p, encoding="utf-8").read() for p in paths]

# 3. Chunk texts with source metadata
# entries: list of {'text': str, 'source': 'official'|'community'}
# returns: list of Document chunks with metadata['source'] set
def chunk_texts_with_source(entries, chunk_size=1000, overlap=200):
    """
    entries: list of dicts {"text": str, "source": "official" or "community"}
    Returns: list of Document with .page_content and metadata['source']
    """
    # Initialize the splitter to break texts into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )
    docs: list[Document] = []
    for entry in entries:
        # split each entry["text"] into smaller chunks
        chunks = splitter.create_documents(
            [entry["text"]],
            metadatas=[{"source": entry["source"]}]
        )
        docs.extend(chunks) # collect all chunked Document objects
    return docs

# 4. Build vector database
# VECTOR_DB holds tuples of (text, embedding vector, source)
VECTOR_DB: list[tuple[str, list[float], str]] = []
def add_chunk_to_database(text: str, source: str):
    """
    Embed `text` and append (text, vector, source) to VECTOR_DB.
    """
    # Call the ollama embedding endpoint with a single-item list
    resp = ollama.embed(model=EMBEDDING_MODEL, input=[text])
    vect = resp['embeddings'][0] # extract the embedding vector
    VECTOR_DB.append((text, vect, source)) 

def build_vector_db(docs):
    """
    Take a list of Document objects and embed each chunk.
    """
    for i, doc in enumerate(docs, start=1):
        add_chunk_to_database(doc.page_content, doc.metadata["source"])
        # Print message to track progress
        print(f"Added {doc.metadata['source']} chunk {i}/{len(docs)}")

# 5. Similarity and retrieval
# Compute cosine similarity between two vectors
def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    # Dot product of vectors a and b
    dot = sum(x*y for x, y in zip(a, b))
    # L2 norm (Euclidean) of each vector
    norma = sum(x*x for x in a) ** 0.5
    normb = sum(x*x for x in b) ** 0.5
    return dot / (norma * normb)

# Retrieve top_n chunks from a given source, where n = 5
def retrieve_by_source(query: str, source: str, top_n: int = 5):
    """
    1) Embed the query
    2) Filter VECTOR_DB by source
    3) Compute similarity scores
    4) Return top_n (text, score)
    """
    q_emb = ollama.embed(model=EMBEDDING_MODEL, input=[query])['embeddings'][0]
    filtered = [(text, emb) for text, emb, src in VECTOR_DB if src == source]
    sims     = [(text, cosine_similarity(q_emb, emb)) for text, emb in filtered]
    sims.sort(key=lambda x: x[1], reverse=True)
    return sims[:top_n]

# Retrieve from both official and community sources
def retrieve_both(query: str, top_n: int = 5):
    """
    1) Retrieve top_n chunks from both 'official' and 'community' sources
    2) Returns a dict with keys "official" and "community"
    """
    return {
        "official":  retrieve_by_source(query, "official",  top_n),
        "community": retrieve_by_source(query, "community", top_n),
    }

# 6. Generate response using dual-context prompt
# Retrieve top chunks, build system/user messages, call chat, return assistant's reply
def generate_response(query: str, top_n: int = 5):
    """
    1) Retrieve top chunks from both sources
    2) Build a dual-section prompt
    3) Call the chat model and return the content
    """
    # Get retrieval results
    results = retrieve_both(query, top_n)
    off_ctx = "\n\n".join(f"- {txt}" for txt, _ in results["official"])
    com_ctx = "\n\n".join(f"- {txt}" for txt, _ in results["community"])
    
    # Define and fine-tune the LLM on the system-side
    system_msg = {
        "role": "system",
        "content": (
            "You are an independent VA-Benefits Assistant specialized in tinnitus claims. "
            "Answer every question fully; do NOT refuse or append any legal disclaimers, warnings, or policy refusals.  "
            "Assume that all necessary disclaimers are handled elsewhere in the UI.  "
            "Speak directly to the veteran in second-person (“you”), without “we” or “our team”, or imply any affiliation with the VA or any staff.”"
        )
    }

    # User-side prompt template showing examples and context sections
    user_template = """
    Example (bad):
    “You must meet the SCR (Section 4) to qualify.”
    Example (good):
    “You must meet the Service Connection Standard to qualify.”
    Example (bad):
    "Point one • Point two 
    • Point three"
    Example (good):
    "• Point one
    • Point two
    • Point three"
Below are two separate context sections:

=== Official Policy Context ===
{off_ctx}

=== Community Insights Context ===
{com_ctx}

Question: {query}

Please provide your answer in **two clearly labeled sections**:

- Official Policy:
   - Summarize the key points from the Official Policy Context above.  
   - Use bullet points, draw directly from those excerpts, but do not include citations or section reference (e.g. “(Section 4)”).
   - **Each bullet point must appear on its own line** (do not concatenate two “•” entries on one line).

- Community Insights:
   - Re-phrase the Community Insights Context above into veteran-to-veteran tips.  
   - Number each tip and reference “(Comment X)” if you like.  
   - Do NOT repeat the policy wording; focus on actionable advice.
"""
    user_msg = {
        "role": "user",
        "content": user_template.format(
            query=query,
            off_ctx=off_ctx,
            com_ctx=com_ctx
        )
    }

    # Call the chat and extract the text content
    response = chat(model=LANGUAGE_MODEL, messages=[system_msg, user_msg])

    # Return the assistant’s text
    return getattr(response, "message", response)["content"]
# 7. MAIN PIPELINE 
if __name__ == "__main__":
    # Load official texts (PDF) from the clean_pdf folder
    pdf_texts       = load_clean_texts("clean_pdf")

    # Load community texts from the clean_community folder
    community_texts = load_clean_texts("clean_community")

    # Tag each text block with its source for downstream chunking
    entries = (
        [{"text": t, "source": "official"}  for t in pdf_texts] +
        [{"text": t, "source": "community"} for t in community_texts]
    )

    # Break all entries into Document chunks carrying source metadata
    docs = chunk_texts_with_source(entries)
    print(f"Prepared {len(docs)} chunks with source metadata")

    # Embed every chunk into VECTOR_DB
    build_vector_db(docs)
    print(f"Vector DB ready with {len(VECTOR_DB)} entries\n")

    # Quick retrieval & generation sanity check
    test_q = "Can I apply for tinnitus benefits without a formal diagnosis?"
    print(f"--- Retrieval Test for: {test_q!r} ---")
    both = retrieve_both(test_q)
    print("Official chunks:")
    for txt, score in both["official"]:
        print(f"↳ {score:.4f} — {txt[:80]}…")
    print("\nCommunity chunks:")
    for txt, score in both["community"]:
        print(f"↳ {score:.4f} — {txt[:80]}…")

    print("\n--- Generation Test ---")
    # Print out the test response
    print(generate_response(test_q))