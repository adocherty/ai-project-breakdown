import streamlit as st

OPENROUTER_MODEL_LIST = ["nemotron-mini", "llama3.2", "gemma2"]

# This must be the first Streamlit command in the script.
st.set_page_config(
    page_title="AD's streamlit test",
    page_icon=":material/bug_report:",
)

# Using the staging pattern documented here
# https://docs.streamlit.io/develop/concepts/design/buttons#buttons-to-continue-or-control-stages-of-a-process

if "model_list" not in st.session_state:
    st.session_state["model_list"] = OPENROUTER_MODEL_LIST

# Main page - these are shown on every page
st.title("AI Project Breakdown")

# Setup sidebar with parameters
with st.sidebar:
    st.subheader("API Keys")
    openai_api_key = st.text_input("OpenRouter API Key", type="password")
    notion_api_key = st.text_input("Notion API Key (optional)", type="password")

if not openai_api_key:
    st.info("Please add your OpenRouter API key to continue.", icon="🗝️")
    # st.stop()

# Keep the values of these widgets persistent
if "input_text" in st.session_state:
    st.session_state.input_text = st.session_state.input_text
if "model_select" in st.session_state:
    st.session_state.model_select = st.session_state.model_select

# Set up pages
generate_page = st.Page(
    "ai_project_breakdown/page1.py",
    title="Generate Project",
    icon=":material/handyman:",
)
feedback_page = st.Page(
    "ai_project_breakdown/page2.py",
    title="Critique Project",
    icon=":material/handyman:",
)
pg = st.navigation({"Pages": [generate_page, feedback_page]})
pg.run()
