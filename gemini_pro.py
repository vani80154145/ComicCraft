from google import genai
from google.genai import types

from app.config import get_settings
from app.schemas import (
    ComicOutline,
    ComicStory,
    PromptRequest,
)


def get_client() -> genai.Client:

    settings = get_settings()

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def generate_story(
    request: PromptRequest,
    outline: ComicOutline
) -> ComicStory:

    settings = get_settings()

    outline_json = outline.model_dump_json(
        indent=2
    )

    prompt = f"""
Expand the following five-panel comic outline
into a complete comic story.

Original story:
{request.story_prompt}

Main character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Comic outline:
{outline_json}

Create exactly five panels.

For every panel provide:

- panel_number
- title
- scene_description
- caption
- narration
- dialogue
- image_prompt

Rules:

1. Keep the story coherent.
2. Keep the character consistent.
3. Keep the requested tone.
4. Keep the requested art style.
5. Scene description should be 1-2 vivid sentences.
6. Caption should be short.
7. Narration should be concise.
8. Dialogue should sound natural.
9. If dialogue is unnecessary, use an empty string.
10. Image prompts should describe only visual content.
11. Do not put written dialogue or captions inside image prompts.
12. Do not add markdown.
"""

    client = get_client()

    response = client.models.generate_content(
        model=settings.gemini_story_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.9,
            response_mime_type="application/json",
            response_schema=ComicStory,
        ),
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty story."
        )

    return ComicStory.model_validate_json(
        response.text
    )