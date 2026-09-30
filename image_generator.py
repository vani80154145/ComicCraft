from pathlib import Path

from PIL import Image

from app.config import get_settings
from app.utils.storage import safe_filename


def generate_huggingface_image(
    prompt: str
) -> Image.Image:

    from huggingface_hub import InferenceClient

    settings = get_settings()

    if not settings.hf_token:
        raise RuntimeError(
            "HF_TOKEN is not configured."
        )

    client = InferenceClient(
        provider="auto",
        api_key=settings.hf_token,
    )

    image = client.text_to_image(
        prompt=prompt,
        model=settings.hf_image_model,
    )

    return image.convert("RGB")


def generate_diffusers_image(
    prompt: str
) -> Image.Image:

    try:
        import torch

        from diffusers import DiffusionPipeline

    except ImportError as exc:

        raise RuntimeError(
            "Diffusers mode requires torch, diffusers, "
            "transformers and accelerate."
        ) from exc

    settings = get_settings()

    if torch.cuda.is_available():
        device = "cuda"
        dtype = torch.float16
    else:
        device = "cpu"
        dtype = torch.float32

    pipe = DiffusionPipeline.from_pretrained(
        settings.diffusers_model,
        torch_dtype=dtype,
    )

    pipe = pipe.to(device)

    result = pipe(
        prompt=prompt,
        num_inference_steps=settings.diffusers_steps,
        width=settings.image_width,
        height=settings.image_height,
    )

    return result.images[0].convert("RGB")


def generate_image(
    prompt: str,
    panel_number: int
) -> str:

    settings = get_settings()

    enhanced_prompt = f"""
{prompt}

Comic illustration.
Clear composition.
Expressive characters.
Consistent character appearance.
Detailed background.
Cinematic lighting.
High quality.
No text.
No watermark.
"""

    provider = settings.image_provider.lower()

    if provider == "huggingface":

        image = generate_huggingface_image(
            enhanced_prompt
        )

    elif provider == "diffusers":

        image = generate_diffusers_image(
            enhanced_prompt
        )

    else:

        raise RuntimeError(
            "IMAGE_PROVIDER must be either "
            "'huggingface' or 'diffusers'."
        )

    filename = safe_filename(
        f"panel_{panel_number}"
    )

    path: Path = (
        settings.panels_dir / filename
    )

    image.save(
        path,
        format="PNG"
    )

    return f"/static/panels/{filename}"


def test_image(
    prompt: str
) -> str:

    return generate_image(
        prompt,
        panel_number=0
    )