import time

from google import genai
from google.genai import types

from app.config import get_settings
from app.schemas import ComicOutline


def generate_with_retry(
    client,
    model,
    prompt,
    config,
    max_retries=4,
):
    """
    Gemini API temporary 503 errors-ku automatic retry.
    """

    for attempt in range(max_retries):
        try:
            return client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )

        except Exception as e:
            error_text = str(e)

            # 503 / UNAVAILABLE mattum retry pannum
            if "503" not in error_text and "UNAVAILABLE" not in error_text:
                raise

            # Last attempt-na error-a throw pannum
            if attempt == max_retries - 1:
                raise

            # 2, 4, 8 seconds wait
            wait_time = 2 ** attempt

            print(
                f"Gemini temporarily unavailable. "
                f"Retrying in {wait_time} seconds..."
            )

            time.sleep(wait_time)


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> ComicOutline:

    settings = get_settings()

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Please add your Gemini API key to the .env file."
        )

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    prompt = f"""
You are the story outline generator for ComicCraft,
an AI comic creation application.

Create a comic story outline with EXACTLY 5 panels.

User's story idea:
{story_prompt}

Main character:
{character_name}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}

Requirements:

1. Create exactly 5 panels.
2. The story must have a clear beginning, middle, and ending.
3. Keep the same main character throughout the story.
4. Make every panel visually interesting.
5. Each panel must contain:
   - panel_number
   - title
   - scene_description
   - image_prompt
6. The image_prompt must describe the visual scene clearly.
7. Keep the story suitable for a comic.
8. Make the events flow naturally from panel 1 to panel 5.
9. Do not create more or fewer than 5 panels.

Return ONLY valid JSON matching the requested schema.
"""

    response = generate_with_retry(
        client=client,
        model=settings.gemini_outline_model,
        prompt=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ComicOutline,
        ),
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return ComicOutline.model_validate_json(
        response.text
    )