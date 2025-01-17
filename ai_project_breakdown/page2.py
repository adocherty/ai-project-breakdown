import streamlit as st
from ai_project_breakdown.project_dummy import (
    StagedLLMProcess,
    ProjectCritique,
    ProjectSpecification,
    TaskBreakdown,
)

st.divider()
st.subheader("Stage 2 - Detailed project description")

# Create LLM object (should this be cached?)
if "form_main" in st.session_state:
    model_choice = st.session_state["form_main"]["model_choice"]
    text_input = st.session_state["form_main"]["text_input"]
    llm_process = StagedLLMProcess(prompt_key="default", model_name=model_choice)

# Get feedback
if "critique_data" not in st.session_state:
    st.info("Please complete the previous stage to continue.", icon="🚧")
else:
    critique_data = st.session_state["critique_data"]

    # Display improvements, allow selections, and run LLM
    with st.form("improvements_form"):
        st.subheader("Suggested improvements")
        improvements_select = [
            st.checkbox(item["improvement"], value=True)
            for category, item in critique_data.items()
        ]

        improve_button = st.form_submit_button("Go")

    if improve_button:
        critique_data_select = dict(
            improvements=[
                item["improvement"]
                for select, item in zip(improvements_select, critique_data.values())
                if select
            ],
        )

        next_input = llm_process.stage_output_to_next_input(
            "stage1", critique_data_select
        )

        with st.spinner("Generating project outline..."):
            project_spec_detailed = llm_process.run_stage_structured(
                next_input, ProjectSpecification, "stage2"
            )

        project_spec_detailed["markdown_content"] = llm_process.output_to_markdown(
            "stage2", project_spec_detailed
        )

        st.session_state["project_spec_detailed"] = project_spec_detailed

    # Display output and request to proceed to next stage
    if "project_spec_detailed" in st.session_state:
        project_data = st.session_state["project_spec_detailed"]

        with st.container():
            st.subheader(f"Project: {project_data['name']}")
            st.write(project_data["summary"])

            with st.expander("Research Problem"):
                st.write(project_data["problem"])

            with st.expander("Methodology"):
                st.write(project_data["methodology"])

            with st.expander("Research Questions"):
                questions_select = st.markdown(
                    "\n".join(f" * {item}" for item in project_data["questions"])
                )

            with st.expander("Objectives"):
                goals_select = st.markdown(
                    "\n".join(f" * {item}" for item in project_data["objectives"])
                )

        next_page = st.button("Next")

        if next_page:
            st.switch_page("ai_project_breakdown/page2.py")
