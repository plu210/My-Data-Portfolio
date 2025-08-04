import streamlit as st
import pipeline
from pipeline import (
    load_clean_texts,
    chunk_texts_with_source,
    build_vector_db,
    retrieve_both,
    generate_response,
)

st.caption(f"⚙️ Pipeline version: {pipeline.PIPELINE_VERSION}")

# ── Initialize the pipeline (runs once at startup) ────────────────────────────────────
@st.cache_resource
def get_db():
    pdf_texts = load_clean_texts("clean_pdf")
    community_texts = load_clean_texts("clean_community")
    entries = (
        [{"text": t, "source": "official"}  for t in pdf_texts] +
        [{"text": t, "source": "community"} for t in community_texts]
    )
    docs = chunk_texts_with_source(entries)
    return build_vector_db(docs)
db = get_db()

#Debug Check - Reading db
#st.write("DEBUG: db has", len(db), "chunks")

# ── Streamlit UI ───────────────────────────────────────────────────────────
st.title("VA Helper")
st.subheader("Tinnitus Claims Assistant")

st.markdown(
    "Get side-by-side guidance on filing tinnitus disability claims—"
    "official VA policy plus community tips."
)

st.markdown(
    "1. Type your question below (e.g., “Can I apply for tinnitus benefits without a formal diagnosis?”)\n"
    "2. Click **Submit**\n"
    "3. See **Official Policy** and **Community Insights** side by side."
)

query = st.text_input(
    "Ask a question:",
    placeholder="e.g. Can I apply for tinnitus benefits without a formal diagnosis?"
)

if st.button("Submit"):
    with st.spinner("Looking up VA policy and community tips…"):
        # Debug Check - Show context being used in generation
        #import inspect
        # Unpack generate_response internals
        #from pipeline import retrieve_both
        #results = retrieve_both(db, query)
        #st.write("DEBUG: Official context:")
        #st.write("\n\n".join([txt for txt, _ in results["official"]]))
        #st.write("DEBUG: Community context:")
        #st.write("\n\n".join([txt for txt, _ in results["community"]]))

        answer = generate_response(db, query)
    st.write(answer)

with st.expander("Disclaimer"):
    st.write(
        "This is a personal, experimental project and is not affiliated with or endorsed by the U.S. Department of Veterans Affairs. Content may be incomplete or inaccurate.\n\n"
        "Please always verify information with official VA.gov resources or consult with a Veterans Service Officer (VSO)."
    )
