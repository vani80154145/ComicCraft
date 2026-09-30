from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from pydantic import ValidationError

from app.config import get_settings
from app.schemas import PromptRequest

from app.services.gemini_flash import (
    generate_outline
)

from app.services.gemini_pro import (
    generate_story
)

from app.services.image_generator import (
    generate_image,
    test_image,
)

from app.services.layout_builder import (
    build_comic_layout
)

from app.services.exporters import (
    save_pdf
)


router = APIRouter()

settings = get_settings()

templates = Jinja2Templates(
    directory=str(
        settings.templates_dir
    )
)


def validate_form(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> PromptRequest:

    try:

        return PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

    except ValidationError as exc:

        raise HTTPException(
            status_code=422,
            detail=exc.errors()
        ) from exc


def generate_complete_comic(
    data: PromptRequest
):

    # Generate 5-panel outline using Gemini Flash
    outline = generate_outline(
        story_prompt=data.story_prompt,
        character_name=data.character_name,
        setting=data.setting,
        tone=data.tone,
        art_style=data.art_style,
    )

    # Generate complete story and dialogue
    story = generate_story(
        data,
        outline
    )

    image_urls = []

    # Generate image for every panel
    for panel in story.panels:

        image_url = generate_image(
            panel.image_prompt,
            panel.panel_number
        )

        image_urls.append(
            image_url
        )

    # Build comic layout
    layout = build_comic_layout(
        story,
        image_urls
    )

    # Export comic as PDF
    pdf_url = save_pdf(
        layout
    )

    return layout, pdf_url


@router.get(
    "/",
    response_class=HTMLResponse
)
async def home(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "ComicCraft"
        }
    )


@router.post(
    "/generate",
    response_class=HTMLResponse
)
async def generate(
    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...),
):

    try:

        data = validate_form(
            story_prompt,
            character_name,
            setting,
            tone,
            art_style
        )

        layout, pdf_url = (
            generate_complete_comic(data)
        )

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "title": "Comic Preview",
                "layout": layout,
                "pdf_url": pdf_url,
                "request_data":
                    data.model_dump(),
            }
        )

    except HTTPException:

        raise

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "title": "ComicCraft",
                "error": str(exc),
                "form": {
                    "story_prompt":
                        story_prompt,

                    "character_name":
                        character_name,

                    "setting":
                        setting,

                    "tone":
                        tone,

                    "art_style":
                        art_style,
                }
            },
            status_code=500
        )


@router.post(
    "/generate-comic/json"
)
async def generate_comic_json(
    data: PromptRequest
):

    try:

        layout, pdf_url = (
            generate_complete_comic(
                data
            )
        )

        return {
            "success": True,
            "layout": layout,
            "pdf_url": pdf_url,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc


@router.get(
    "/export-success",
    response_class=HTMLResponse
)
async def export_success(
    request: Request,
    pdf: str = ""
):

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "title":
                "Export Complete",

            "pdf_url":
                pdf
        }
    )


@router.get(
    "/test-image"
)
async def test_image_route(
    prompt: str =
        "A friendly fox in an "
        "enchanted forest, "
        "comic book art"
):

    try:

        image_url = test_image(
            prompt
        )

        return {
            "success": True,
            "image_url": image_url
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc