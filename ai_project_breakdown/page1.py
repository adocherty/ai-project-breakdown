import streamlit as st
from time import sleep
from ai_project_breakdown.project_dummy import (
    StagedLLMProcess,
    ProjectCritique,
    ProjectSpecification,
    TaskBreakdown,
)

st.divider()
st.subheader("Stage 1 - Enter project description")


def process_input(text: str, stage: str):
    sleep(2)
    return text.lower()


def set_state_1(v: bool):
    st.session_state["stage_1_process"] = v


def get_state_1():
    if "stage_1_process" in st.session_state:
        return st.session_state["stage_1_process"]
    else:
        return False


OPENROUTER_MODEL_LIST = st.session_state["model_list"]

# Input model parameters and text
with st.form("project_description_form"):
    model_choice = st.selectbox(
        "Model", options=OPENROUTER_MODEL_LIST, key="model_select"
    )
    text_input = st.text_area("Project description", key="input_text", height=200)

    generate_button = st.form_submit_button(
        "Go", use_container_width=True, on_click=set_state_1, args=(True,)
    )

st.session_state["form_main"] = dict(model_choice=model_choice, text_input=text_input)

# Create LLM object (should this be cached?)
if model_choice:
    llm_process = StagedLLMProcess(prompt_key="default", model_name=model_choice)


# Don't rerun this step unless required
if get_state_1():
    # LLM Stage 1 - Critique the description
    with st.spinner("Processing..."):
        critique_data = llm_process.run_stage_structured(
            text_input, ProjectCritique, "stage1"
        )

    st.session_state["critique_data"] = critique_data
    set_state_1(False)

elif "critique_data" in st.session_state:
    critique_data = st.session_state["critique_data"]

else:
    critique_data = None


if critique_data is not None:
    st.subheader("Feedback on project description")
    st.markdown(llm_process.output_to_markdown("stage1", critique_data))

    next_page = st.button("Next")

    if next_page:
        st.switch_page("ai_project_breakdown/page2.py")
