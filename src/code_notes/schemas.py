from pydantic import BaseModel, Field

last_id: int = 0


class CodeNote(BaseModel):
    id: int = Field(title="note id", default_factory=lambda: CodeNote.generate_id())
    name: str = Field(title="note name")
    code_block: str = Field(title="note code block")

    @staticmethod
    def generate_id() -> int:
        global last_id  # noqa: PLW0603
        last_id += 1
        return last_id
