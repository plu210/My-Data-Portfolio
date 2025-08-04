import os
import glob
import re
import ollama
from ollama import chat
from langchain.schema import Document
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# VERSION
PIPELINE_VERSION = "v4.1"  # bump this every time prompt change occured

# 1. Configuration
# Select embedding and language models
EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'
LANGUAGE_MODEL  = 'hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF'

# 2. Load cleaned text files
# Read all .txt files from a folder and return their contents as a list of strings
def load_clean_texts(folder: str):
    """
    folder: path to directory containing .txt files of cleaned VA policy or community excerpts.
    returns: List[str] where each entry is the full text of one file.
    """
    paths = sorted(glob.glob(os.path.join(folder, "*.txt")))
    return [open(p, encoding="utf-8").read() for p in paths]

# 3. Chunk texts with source metadata
# Splits each text into smaller "Document" chunks, tagging each with its source.
def chunk_texts_with_source(entries):
    """
    entries: List[dict] where each dict has keys:
      - 'text': the raw string
      - 'source': either 'official' or 'community'
    returns: List[Document], each with .page_content and metadata['source']
    """
    docs = []
    for entry in entries:
        if entry["source"] == "official":
            splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=70)
        else:
            splitter = RecursiveCharacterTextSplitter(chunk_size=950, chunk_overlap=100)
        docs.extend(
            splitter.create_documents([entry["text"]], metadatas=[{"source": entry["source"]}])
        )
    return docs

# 4. Build vector database
# Embeds each chunk and builds an in-memory list of tuples.
def build_vector_db(docs):
    """
    docs: list of Document objects with .page_content and metadata['source']
    returns: db: list of tuples (text, vector, source)
    """
    db = []
    for i, doc in enumerate(docs, start=1):
        # Call embedding API on the chunk
        resp = ollama.embed(model=EMBEDDING_MODEL, input=[doc.page_content])
        vect = resp['embeddings'][0]
        db.append((doc.page_content, vect, doc.metadata["source"]))
        print(f"Added {doc.metadata['source']} chunk {i}/{len(docs)}") # progress log
    return db

# 5. Similarity and retrieval
# Cosine similarity for ranking embeddings
def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    # Dot product of vectors a and b
    dot = sum(x*y for x, y in zip(a, b))
    # L2 norm (Euclidean) of each vector
    norma = sum(x*x for x in a) ** 0.5
    normb = sum(x*x for x in b) ** 0.5
    return dot / (norma * normb)

# Retrieve top_n chunks from a given source, where n = 3
def retrieve_by_source(db, query: str, source: str, top_n: int = 3):
    """
    db: list of (text, embedding, source) tuples
    query: user query string
    source: 'official' or 'community'
    top_n: how many top results to return
    returns: list of (text, similarity_score)
    """
    # Embed the query
    q_emb = ollama.embed(model=EMBEDDING_MODEL, input=[query])['embeddings'][0]
    # Filter by source
    filtered = [(text, emb) for text, emb, src in db if src == source]
    # Score all
    sims     = [(text, cosine_similarity(q_emb, emb)) for text, emb in filtered]
    # Sort descending by similarity
    sims.sort(key=lambda x: x[1], reverse=True)
    return sims[:top_n]

# Retrieve from both official and community sources
def retrieve_both(db, query: str, top_n: int = 5):
    """
    returns: {'official': [...], 'community': [...]} with top_n each
    """
    return {
        "official":  retrieve_by_source(db, query, "official",  top_n),
        "community": retrieve_by_source(db, query, "community", top_n),
    }

# 6. Generate response using dual-context prompt
# Orchestrates retrieval + prompt construction + model call.
def generate_response(db, query: str, top_n: int = 5):
    """
    db: vector database from build_vector_db
    query: user-input question
    top_n: number of chunks to retrieve per source
    returns: string, the LLM's reply
    """
    # Retrieve relevant chunks
    results = retrieve_both(db, query, top_n)
    official_chunks = results["official"]
    community_chunks = results["community"]

    # Official: join paragraphs with blank lines
    off_ctx = "\n\n".join(txt.strip("-• ").strip() for txt, _ in official_chunks)
    # Community: same treatment
    com_ctx = "\n\n".join(txt.strip("-• ").strip() for txt, _ in community_chunks) 
    
    # Clean the question mark to improve LLM response accuracy
    clean_query = query.rstrip('?').strip()

    # Define and fine-tune the LLM on the system-side
    system_msg = {
    "role": "system",
    "content": f"""
    You are an independent VA-Benefits Assistant for tinnitus claims.
    Use ONLY the provided contexts. Do NOT invent or infer.

    Follow these steps for every response:   
    1. Chain-of-Thought
    - Begin with **### Reasoning**  
    - Show your thought-process step by step as a numbered list.

    2. Final Answer
    - After reasoning, use **### Answer**  
    - Under this, include exactly two sub-headings **once each**:
        ## Official Policy
        ## Community Insights

    3. Official Policy (under ## Official Policy)
    - If this is a yes/no question, start with “Yes, …” or “No, …”.  
    - If the Official Policy Context is empty or irrelevant, write exactly:
        - I’m sorry, I don’t have information on that topic. Please consult the VA.gov website or a Veterans Service Officer for guidance.
    - Otherwise:
        - Open with one empathetic sentence (e.g., “I know this can feel overwhelming, but…”).  
        - Summarize the Official Policy Context into concise bullets (`- `), one per line.  
        - Do NOT include citations or section references.

    4. Community Insights (under ## Community Insights)
    - Summarize the Community Insights Context into actionable tips.  
    - Begin each tip with an action verb (Consider…, Ask…, Gather…, Contact…).  
    - Use `- ` bullets, one per line.  
    - Do NOT repeat any Official Policy phrasing.  
    - If empty, write exactly:
        - No relevant community insights available at this time, please try again.

    5. Tone & Style
    - Speak directly to **you**; never use “we,” “our team,” “I,” or add disclaimers (UI handles those).  
    - Discard all original bullets or formatting; rewrite every point from scratch.  
    - Do NOT include meta-statements (e.g. “As you requested…”).
"""
}

    # USER prompt with plain contexts and question
    user_msg = {
    "role": "user",
    "content": f"""
    Example (yes/no Question: "Can I apply for tinnitus benefits without a formal diagnosis?"):
    ## Reasoning
    1. The Service Connection Standard focuses on linking tinnitus to noise exposure.
    2. A formal diagnosis is helpful but not strictly required if other evidence is strong.
    3. Community tips often emphasize gathering lay statements and service records.
    
    ## Answer
    ### Official Policy
    - Yes, you can apply without a formal diagnosis under the Service Connection Standard.

    ### Community Insights
    - Consider collecting lay statements from fellow service members about your noise exposure.
    - Ask your audiologist to document symptom frequency and severity even without a formal diagnosis.
    
    ---

    Example (open-ended Question:"My claim got denied, what do I do?"):
    ### Reasoning
    1. When a VA disability claim is denied, official policy allows you to appeal the decision or submit new evidence.
    2. The appeals process has several options: Supplemental Claim, Higher-Level Review, or Board Appeal.
    3. Community members often recommend reviewing your denial letter to understand the reasons, gathering additional supporting documents, and seeking help from a Veterans Service Officer (VSO) or accredited representative.

    ### Answer
    ## Official Policy
    - You have several options after a denial, including filing a Supplemental Claim with new evidence, requesting a Higher-Level Review, or submitting a Board Appeal.
    - Carefully review your denial letter for the specific reasons and what evidence may be missing or insufficient.
    - Timelines apply, so pay attention to deadlines for each type of appeal.

    ## Community Insights
    - Contact a Veterans Service Officer (VSO) or an accredited representative—they can guide you through the appeal or review process at no cost.
    - Gather any new medical records, lay statements, or other documents that address the reasons for denial.
    - Consider reaching out to local veterans’ organizations for additional resources or advice from peers who have appealed before.
    ———
    Now, given these raw contexts and your question, follow that exact format:

    **Official Policy Context:**  
    {off_ctx}

    **Community Insights Context:**  
    {com_ctx}

    Question: {clean_query}

    Begin with **### Reasoning**, then **### Answer**, then **## Official Policy** and **## Community Insights**.
    """
    }
    # Call the chat and extract the text content
    response = chat(
        model=LANGUAGE_MODEL,
        messages=[system_msg, user_msg],
        options={"temperature": 0.55}
    )
    answer = response["message"]["content"]

    #Test
    print(f"[Pipeline version {PIPELINE_VERSION}] Generating response…")

    # Return the assistant’s text
    return getattr(response, "message", response)["content"]

# 7. MAIN PIPELINE 
if __name__ == "__main__":
    pdf_texts       = load_clean_texts("clean_pdf")
    community_texts = load_clean_texts("clean_community")
    entries = (
        [{"text": t, "source": "official"}  for t in pdf_texts] +
        [{"text": t, "source": "community"} for t in community_texts]
    )
    docs = chunk_texts_with_source(entries)
    db = build_vector_db(docs)

    # Test query
    test_q = "Can I apply for tinnitus benefits without a formal diagnosis?"
    print("\n--- Retrieval Test ---")
    both = retrieve_both(db, test_q)
    print("Official chunks:")
    for txt, score in both["official"]:
        print(f"↳ {score:.4f} — {txt[:80]}…")
    print("\nCommunity chunks:")
    for txt, score in both["community"]:
        print(f"↳ {score:.4f} — {txt[:80]}…")

    print("\n--- Generation Test ---")
    print(generate_response(db, test_q))