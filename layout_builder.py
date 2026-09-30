from typing import Any

from app.schemas import ComicStory


def build_comic_layout(
    story: ComicStory,
    image_urls: list[str]
) -> list[dict[str, Any]]:

    if len(story.panels) != len(image_urls):

        raise ValueError(
            "Every panel must have exactly one image."
        )

    layout = []

    for panel, image_url in zip(
        story.panels,
        image_urls
    ):

        layout.append(
            {
                "panel_number":
                    panel.panel_number,

                "title":
                    panel.title,

                "image_url":
                    image_url,

                "scene_description":
                    panel.scene_description,

                "caption":
                    panel.caption,

                "narration":
                    panel.narration,

                "dialogue":
                    panel.dialogue,

                "image_prompt":
                    panel.image_prompt,
            }
        )

    return layout