# _VA Helper_
A Retrieval-Augmented Generation (RAG) prototype assistant combining official VA policy documents with community insights for veterans navigating tinnitus claims.

## Purpose
Many veterans are overwhelmed by the vague eligibility rules, unclear instructions, or lack of timely advice. This assistant bridges the gap between policy text and practical insights. VA Helper combines official policy information from the U.S. Department of Veterans Affairs (VA) with practical insights shared by the veteran communities from Reddit. The tool generates structured, side-by-side answers to common questions veterans have about filing tinnitus claims.

## Tech Stack
- **Languages**: Python 3.11+
- **Frameworks & Libraries**:
  - LangChain — Document ingestion, splitting, and pipeline orchestration
  - Ollama — Local large language model (LLM) inference and embedding generation
  - Streamlit — Interactive web interface for user Q&A
- **Vector Database**: Custom embedding-based retrieval pipeline of relevant policy and community text
- **Models**:
  - Embedding: `bge-base-en-v1.5-gguf`
  - LLM Response Generation: `Llama-3.2-1B-Instruct-GGUF`

## Setup
1. **Install dependencies**
   - Python 3.11+
   - See `./requirements.txt` for dependencies:
   ```
   pip install -r requirements.txt
   ```
   - This project requires Ollama and specific models:
     - [Ollama](https://ollama.com/)
     - [Embedding model: bge-base-en-v1.5-gguf](https://huggingface.co/CompendiumLabs/bge-base-en-v1.5-gguf)
     - [Language model: Llama-3.2-1B-Instruct-GGUF](https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF)

For Ollama installation, see the [Official Ollama Documentation](https://github.com/ollama/ollama/tree/main/docs) for more information.

2. **Clone this repository into a local directory of your choice**
3. **Data**
   - This repo includes sample data in `./pdf_data/` and `./community_data/`. 

## How To Run
Navigate to the `./VA-Helper` directory and run:
```
python load_data.py
```
and
```
python pipeline.py
```
to preprocess and build the vector database. Then run:
```
streamlit run app.py
```
to launch the app. 

If the app loads and you can submit a question, you’re good to go!

## Example Questions
- Can I apply for tinnitus benefits without a formal diagnosis?
- How do I file a VA disability claim for tinnitus?
- My claim got denied, what do I do?
- Does my MOS matter?

## Current Limitations
- **Manual Reddit Integration**: Community insights from Reddit are manually reviewed and added due to challenges with automatic filtering (sarcasm, irrelevant content, data integrity issues).
- **URL Handling**: External links within community insights are currently replaced with [link] placeholders, limiting traceability.

## Future Considerations
- Integrate the VA’s Letter 10-35 MOS Noise Exposure Listing by building automated Excel ingestion and normalization tools to standardize multi-sheet, inconsistently structured data, allowing end users to directly search their MOS within VA Helper.
- Automate and enhance Reddit data ingestion with advanced NLP techniques:
  - Employ upvote ratios and other engagement signals to algorithmically promote the most relevant and useful community advice
  - Use sentiment and toxicity lexicons (VADER, Hatebase) to filter out hostile or non-informative comments
  - Integrate sarcasm and humor detection to reduce the influence of joke or low-value high-engagement posts
- Expand to additional VA benefit areas:
  - Other Disability Claims
  - Education & Training Benefits
  - Veteran Readiness & Employment (VRE)

## References
See ./references.md for full list

## _Disclaimer_
This is an experimental project and is not affiliated with or endorsed by the U.S. Department of Veterans Affairs. 

Always verify information with official VA.gov resources or consult with a Veterans Service Officer (VSO).
