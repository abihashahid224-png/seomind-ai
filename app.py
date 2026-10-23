import streamlit as st
from agents import AGENTS
from orchestrator import run_pipeline

st.set_page_config(page_title="SEOmind AI", page_icon="🔍")
st.title("SEOmind AI")
st.caption("Paste your blog content. 6 AI agents suggest keywords, titles, fixes and a rewrite. Powered by Gemma 4.")

content = st.text_area("Blog content", height=250)
selected = st.multiselect("Agents", list(AGENTS), default=list(AGENTS))

if st.button("Analyze"):
    if not content.strip():
        st.warning("Paste content first.")
    else:
        with st.spinner("Gemma 4 is analyzing..."):
            try:
                results = run_pipeline(content, selected)
            except Exception as e:
                st.error(f"Error: {e}. Try again shortly.")
                st.stop()
        for name, output in results.items():
            st.subheader(name.replace("_", " ").title())
            if "raw" in output:
                st.write(output["raw"])
            else:
                st.json(output)