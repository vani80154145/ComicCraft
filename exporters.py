from pathlib import Path
from uuid import uuid4

from fpdf import FPDF
from PIL import Image

from app.config import get_settings


def get_image_path(
    image_url: str
) -> Path:

    settings = get_settings()

    prefix = "/static/panels/"

    if not image_url.startswith(prefix):

        raise ValueError(
            "Invalid panel image URL."
        )

    filename = Path(
        image_url[len(prefix):]
    ).name

    path = (
        settings.panels_dir /
        filename
    )

    if not path.exists():

        raise FileNotFoundError(
            f"Panel image not found: {filename}"
        )

    return path


def save_pdf(
    layout: list[dict]
) -> str:

    settings = get_settings()

    pdf = FPDF()

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    for panel in layout:

        image_path = get_image_path(
            panel["image_url"]
        )

        with Image.open(image_path) as image:

            width, height = image.size

            if width <= 0 or height <= 0:

                raise ValueError(
                    "Invalid image dimensions."
                )

        pdf.add_page()

        pdf.set_font(
            "Helvetica",
            "B",
            18
        )

        pdf.multi_cell(
            0,
            10,
            (
                f"Panel "
                f"{panel['panel_number']}: "
                f"{panel['title']}"
            )
        )

        pdf.ln(3)

        usable_width = 180

        with Image.open(image_path) as image:

            ratio = (
                image.height /
                image.width
            )

        image_height = min(
            120,
            usable_width * ratio
        )

        pdf.image(
            str(image_path),
            x=15,
            y=None,
            w=usable_width,
            h=image_height
        )

        pdf.ln(6)

        pdf.set_font(
            "Helvetica",
            "I",
            10
        )

        pdf.multi_cell(
            0,
            6,
            panel["scene_description"]
        )

        pdf.ln(2)

        if panel.get("caption"):

            pdf.set_font(
                "Helvetica",
                "B",
                11
            )

            pdf.multi_cell(
                0,
                6,
                "Caption: "
                + panel["caption"]
            )

        if panel.get("narration"):

            pdf.set_font(
                "Helvetica",
                "",
                11
            )

            pdf.multi_cell(
                0,
                6,
                "Narration: "
                + panel["narration"]
            )

        if panel.get("dialogue"):

            pdf.multi_cell(
                0,
                6,
                "Dialogue: "
                + panel["dialogue"]
            )

    filename = (
        f"comic_"
        f"{uuid4().hex[:12]}"
        f".pdf"
    )

    output = (
        settings.exports_dir /
        filename
    )

    pdf.output(str(output))

    return f"/exports/{filename}"