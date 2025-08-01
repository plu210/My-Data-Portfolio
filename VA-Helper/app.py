import streamlit as st
from pipeline import generate_response

# Page header
st.title("VA Helper") # Main title
st.subheader("Tinnitus Claims Assistant")

# Explanation/Purpose
st.markdown(
    "Get side-by-side guidance on filing tinnitus disability claims—"
    "official VA policy plus community tips."
)

# Instruction
st.markdown(
    "1. Type your question below (e.g., “Can I apply for tinnitus benefits without a formal diagnosis?”)\n"
    "2. Click **Submit**\n"
    "3. See **Official Policy** and **Community Insights** side by side."
)

# User Input
query = st.text_input(
    "Ask a question:", # Label for the text input box
    placeholder="e.g. Can I apply for tinnitus benefits without a formal diagnosis?"
)

# Submit
if st.button("Submit"):
    # Show a spinner while waiting for the pipeline to run
    with st.spinner("Looking up VA policy and community tips…"):
        answer = generate_response(query) # Call the pipeline LLM
    # Display the result under an “Answer” heading
    st.markdown("### Answer")
    st.write(answer)

# Disclaimer
with st.expander("Disclaimer"):
    st.write(
        "This is a personal, experimental project and is not affiliated with or endorsed by the U.S. Department of Veterans Affairs. Content may be incomplete or inaccurate.\n\n"
        
        "Please always verify information with official VA.gov resources or consult with a Veterans Service Officer (VSO)."
    )