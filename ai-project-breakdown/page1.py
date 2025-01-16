import streamlit as st


def process_input(text: str, stage: str):
    return text.lower()


st.write("Now on page 1")

text_input = st.session_state["form_main"]["text_input"]

# LLM Stage 1 - Critique the description
with st.spinner("Generating suggestions..."):
    critique_data = process_input(text_input, "stage1")

st.session_state["critique_data"] = critique_data

st.write(critique_data)


print("Output prompt 1:")
print(critique_data)
print("-" * 80)
