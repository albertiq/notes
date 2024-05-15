from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastui import AnyComponent, FastUI, prebuilt_html
from fastui import components as c
from fastui.components.display import DisplayLookup
from fastui.events import BackEvent, GoToEvent

from schemas import CodeNote
from service import get_notes

router = APIRouter()
notes = get_notes()


@router.get("/api/", response_model=FastUI, response_model_exclude_none=True)
def notes_table() -> list[AnyComponent]:
    return [
        c.Page(
            components=[
                c.Heading(text="Code notes", level=2),
                c.Table(
                    data=notes,
                    data_model=CodeNote,
                    columns=[
                        DisplayLookup(field="id"),
                        DisplayLookup(field="name", on_click=GoToEvent(url="/note/{id}/")),
                    ],
                ),
            ],
        ),
    ]


@router.get("/api/note/{note_id}/", response_model=FastUI, response_model_exclude_none=True)
def note_details(note_id: int) -> list[AnyComponent]:
    note: CodeNote | None = notes[note_id - 1] if note_id <= len(notes) else None
    return [
        c.Page(
            components=[
                c.Heading(text=note.name, level=2),
                c.Button(text="Back", on_click=BackEvent()),
                c.Code(text=note.code_block, language="python"),
            ],
        ),
    ]


@router.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title="FastUI Demo"))
