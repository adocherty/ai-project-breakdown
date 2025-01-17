# LangChain functions to take a project description and create structured tasks

import os
import tomllib

from langchain_core.prompts import ChatPromptTemplate
from langchain_core import output_parsers
from langchain_ollama import ChatOllama

from jinja2 import Template

from pydantic import BaseModel, Field
from enum import Enum, IntEnum


class Size(str, Enum):
    small = "Small"
    medium = "Medium"
    large = "Large"


class Priority(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


class ToolEnum(IntEnum):
    spanner = 1
    wrench = 2


# Stage 1 output structure


class CategoryCritique(BaseModel):
    critique: str = Field(
        description="A critique of the project description with relation to the given category (200-300 words)"
    )
    score: int = Field(
        description="A score of how the description covers the category, as an integer between 0 and 10"
    )
    improvement: str = Field(
        description="Suggestions for how to improve the description in the category (200-300 words)"
    )


class ProjectObjectives(CategoryCritique):
    """Are the research objectives specific, measurable, achievable, relevant, and time-bound (SMART)?"""

    category: str = "Project Objectives"


class ResearchMethodology(CategoryCritique):
    """Does the proposal clearly outline the steps to be taken to acheive the project objectives?"""

    category: str = "Research Questions"


class ResearchQuestions(CategoryCritique):
    """Does the proposal clearly articulate a compelling and focused research question?"""

    category: str = "Research Questions"


class Evaluation(CategoryCritique):
    """How will the software's effectiveness and usability be evaluated?"""

    category: str = "Evaluation"


class ProjectCritique(BaseModel):
    """A critique of the project description in multiple categories."""

    objectives: ProjectObjectives
    questions: ResearchQuestions
    methodology: ResearchMethodology
    evaluation: Evaluation


# Stage 2 output structure


class ProjectSpecification(BaseModel):
    """A detailed description of a research project"""

    name: str = Field(description="A short and descriptive project name")
    summary: str = Field(description="A summary of the project (100-200 words)")
    problem: str = Field(
        description="A description of the research problem the project aims to solve (200-300 words)."
    )
    impact: str = Field(
        description="What contributions could this project have in my personal processes (200-300 words)?"
    )
    objectives: list[str] = Field(
        description="A list of most important project objectives (200-300 words)."
    )
    methodology: str = Field(
        description="A clear statement for how the project objectives can be achieved and evaluated (200-300 words)."
    )
    questions: list[str] = Field(
        description="A list of most important research questions to be answered (200-300 words)."
    )


# "Detailed information about a task within a project.
# Format as Markdown with sections Context, Outcome, Subtasks, and Priority and size."
# "Include an explanation of the context for the task, the reason why the task is estimated
# to have the size and priority that it does, and a list of the goals for the task.",
class TaskSpecification(BaseModel):
    """A single task of a research project"""

    name: str = Field(description="A short and descriptive task name")
    summary: str = Field(description="A summary of the task in 100 words or less")
    priority: Priority = Field(description="The priority of the tasl.")
    size: Size = Field(description="The relative size of the task.")
    description: str = Field(
        description="Let's think step by step. Write a description of the task formatted in markdown and including all required context, explanation of the priority and size, and description of outcome. Aim for 300-400 words."
    )
    outcome: str = Field(
        description="A description of the required outcome of the task in 200-300 words."
    )
    evaluation: str = Field(
        description="A clear statement for how the task objectives can be measured in 200-300 words."
    )
    steps: list[str] = Field(description="A list of steps to complete the task.")


class TaskBreakdown(BaseModel):
    tasks: list[TaskSpecification] = Field(
        description="A breakdown of the given project into multiple tasks."
    )


def load_prompts_from_file(file_name: str = "prompts.toml"):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, file_name)
    with open(file_path, "rb") as f:
        data = tomllib.load(f)
    return data


class StagedLLMProcess:
    def __init__(self, prompt_key: str, model_name: str):
        prompts_data = load_prompts_from_file()
        self.prompts = prompts_data.get(prompt_key)
        self.model = ChatOllama(model=model_name, temperature=0.2, format="json")

    def run_stage_structured(
        self, user_input: str, output_object: object, stage_key: str = "stage1"
    ) -> dict:
        print(f"LLM inference: {stage_key}")

        if self.prompts is None:
            raise RuntimeError("Prompt not found")
        prompt_text = self.prompts[stage_key]
        prompt_stage_1 = ChatPromptTemplate.from_messages(
            [
                ("system", prompt_text["system"]),
                ("user", prompt_text["user"]),
            ]
        )

        output_parser = output_parsers.JsonOutputParser(pydantic_object=output_object)

        llm_json_chain = prompt_stage_1 | self.model | output_parser
        stage_output = llm_json_chain.invoke(
            {
                "json_schema": output_parser.get_format_instructions(),
                "user_input": user_input,
            }
        )

        return stage_output

    def output_to_markdown(self, stage_key: str, data: dict):

        if self.prompts is None:
            raise RuntimeError("Prompt not found")
        prompt_text = self.prompts[stage_key]
        jinja_template = Template(prompt_text["display_template"])
        return jinja_template.render(data)

    def stage_output_to_next_input(self, stage_key: str, data: dict):

        if self.prompts is None:
            raise RuntimeError("Prompt not found")
        prompt_text = self.prompts[stage_key]
        jinja_template = Template(prompt_text["next_prompt_template"])
        return jinja_template.render(data)
