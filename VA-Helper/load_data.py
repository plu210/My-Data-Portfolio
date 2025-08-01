from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

import os
import re

# 1. LOAD source documents (PDFs and community text)
# Define folders containing source files
pdf_folder = "pdf_data"
community_folder = "community_data"

# List all PDF filenames in the pdf_folder
pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith(".pdf")]

# Initialize a list to collect Document-like objects
all_docs = []

# Load each PDF into LangChain Document objects
for filename in pdf_files:
    path = os.path.join(pdf_folder, filename)
    print(f"Loading → {path}")
    loader = PyPDFLoader(path)
    docs = loader.load()
    all_docs.extend(docs)

# Identify all community text files (.txt) in community_folder
comment_files = [
    f for f in os.listdir(community_folder)
    if f.lower().endswith(".txt")
]

# Load each community text file and wrap it
for filename in comment_files:
    path = os.path.join(community_folder, filename)
    print(f"Loading → {path}")
    # Read the raw comment text
    text = open(path, encoding="utf-8").read()
    # Create a minimal object with .page_content and .metadata attributes
    class C: 
        pass
    doc = C()
    doc.page_content = text # Raw text of the comment
    doc.metadata     = {"source": filename} # Store original filename as metadata
    all_docs.append(doc) # Add to combined list

print(f"\nTotal pieces loaded: {len(all_docs)}")

# 2. EXPORT raw text to raw_txt
os.makedirs("raw_txt", exist_ok=True)
for idx, doc in enumerate(all_docs, start=1):
    # Pull raw source string
    raw_src = doc.metadata.get("source", "")
    # Strip out any path segments, keep only the filename
    file_only = os.path.basename(raw_src)
    # Decide if source is PDF or community text
    kind = "pdf" if file_only.lower().endswith(".pdf") else "community"
    # Build flat filename by combining kind and original filename
    base = f"{kind}_{file_only}"
    safe_base = base.replace(" ", "_")
    #Final filename
    fname    = f"{idx:03}_{safe_base}.txt"
    out_path = os.path.join("raw_txt", fname)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc.page_content)

# 3) DEFINE cleaning functions
def clean_text(text: str) -> str:
    """
    1) Merge hyphenated line breaks: "exam-\nples" → "examples"
    2) Collapse newlines to spaces and collapse extra spaces
    3) Preserve punctuation & casing
    """
    # Merge hyphenated line breaks
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)
    # Collapse to spaces
    text = text.replace("\n", " ")
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

def clean_community_urls(text: str) -> str:
    """
    1) Remove URL query parameters (utm_*)
    2) Replace URLs with '[link]'
    """
    # Remove query parameters but keep the base URL
    text = re.sub(r"(\bhttps?://\S+?)(?:\?[^\s]*)", r"\1", text)
    # Replace any leftover bare URLs with [link]
    text = re.sub(r"\bhttps?://\S+", "[link]", text)
    return text

# 4) CLEAN raw files and save to respective folders
# Create clean_pdf and clean_community folders
os.makedirs("clean_pdf", exist_ok=True)
os.makedirs("clean_community", exist_ok=True)

# Iterate through each raw exported file
for fname in os.listdir("raw_txt"):
    raw_path = os.path.join("raw_txt", fname)
    raw      = open(raw_path, encoding="utf-8").read()

    # Determine target folder
    if "_community_" in fname:
        # clean community text (URL handling)
        cleaned = clean_community_urls(raw)
        target = "clean_community"
    else:
        # clean PDF-derived text (whitespace & hyphens)
        cleaned = clean_text(raw)
        target = "clean_pdf"

    # Write out the cleaned text to its folder
    out_path = os.path.join(target, fname)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(cleaned)
print("Cleaned text exported to clean_pdf/ & clean_community/")

# 5) INGEST: chunk the cleaned text
# Use RecursiveCharacterTextSplitter to break text into ~1k-char chunks with overlap
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs = []

# Process official (PDF-derived) chunks
for fname in os.listdir("clean_pdf"):
    path = os.path.join("clean_pdf", fname)
    text = open(path, encoding="utf-8").read()
    # Split into Document chunks with the 'official' tag
    chunks = splitter.create_documents(
        [text],
        metadatas=[{"source": "official"}]
    )
    docs.extend(chunks)

# Process community-derived chunks
for fname in os.listdir("clean_community"):
    path = os.path.join("clean_community", fname)
    text = open(path, encoding="utf-8").read()
    # Split into Document chunks with the 'community' tag
    chunks = splitter.create_documents(
        [text],
        metadatas=[{"source": "community"}]
    )
    docs.extend(chunks)

# Report total number of chunks ready for pipeline
print(f"Total chunks ready for embedding: {len(docs)}")