from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class File(BaseModel):
    path: str = Field(description="Path to the file. E.g., 'index.html', 'style.css', 'script.js', 'README.md'")
    purpose: str = Field(description="Purpose of the file, e.g., 'Main HTML structure', 'Styling for the application'")


class Plan(BaseModel):
    name: str = Field(description="App name")
    description: str = Field(description="One-line description")
    techstack: str = Field(description="HTML5, CSS3 (modern design), Vanilla JS")
    features: list[str] = Field(description="2-4 key features list")
    files: list[File] = Field(description="List of files to be created. Should include index.html, style.css, script.js, and README.md.")


class ImplementationTask(BaseModel):
    filepath: str = Field(description="The path to the file to be modified")
    task_description: str = Field(description="A detailed description of the task to be performed on")


class TaskPlan(BaseModel):
    implementation_steps: list[ImplementationTask] = Field(description="List of implementation tasks, one per file")
    plan: Optional['Plan'] = Field(default=None, description="Original plan")
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class CoderState(BaseModel):
    task_plan: TaskPlan = Field(description="The plan for the task to be implemented")
    current_step_idx: int = Field(default=0, description="The index of the current step in the implementation steps")
    current_file_content: Optional[str] = Field(default=None, description="The content of the file currently being edited or created")
    retry_count: int = Field(default=0, description="Number of retries for current task")
    feedback: Optional[str] = Field(default=None, description="Feedback from the reviewer to be addressed by the coder")


class Review(BaseModel):
    approved: bool = Field(description="Whether the code is approved or not.")
    feedback: str = Field(description="Detailed feedback and required changes if not approved.")


class ReviewerState(BaseModel):
    review: Review = Field(description="The review of the generated code.")
    coder_state: CoderState = Field(description="The state of the coder agent.")