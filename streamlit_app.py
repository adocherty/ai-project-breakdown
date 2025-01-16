import streamlit as st

OPENROUTER_MODEL_LIST = ["llama3-groq-tool-use", "gemma2", "llama3", "llama3.1"]

# This must be the first Streamlit command in the script.
st.set_page_config(
    page_title="AD's streamlit test",
    page_icon=":material/bug_report:",
)


def set_state(i: int):
    st.session_state["stage"] = i


# Using the staging pattern documented here
# https://docs.streamlit.io/develop/concepts/design/buttons#buttons-to-continue-or-control-stages-of-a-process

if "stage" not in st.session_state:
    set_state(0)

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
    st.stop()

# All states: Show form with model parameters and input text
if st.session_state.stage >= 0:
    with st.form("project_description_form"):
        model_choice = st.selectbox("Model", OPENROUTER_MODEL_LIST)
        text_input = st.text_area("Project description", key="input_text", height=200)

        generate_button = st.form_submit_button(
            "Go", on_click=st.switch_page, args=("ai-project-breakdown/page1.py",)
        )

    st.session_state["form_main"] = dict(
        model_choice=model_choice, text_input=text_input
    )
    st.write("End of stage 0")


# Set up pages
generate_page = st.Page(
    "ai-project-breakdown/page1.py",
    title="Generate Project",
    icon=":material/handyman:",
)
feedback_page = st.Page(
    "ai-project-breakdown/page2.py",
    title="Critique Project",
    icon=":material/handyman:",
)
pg = st.navigation({"Pages": [generate_page, feedback_page]})
pg.run()
