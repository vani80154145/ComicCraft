from app.schemas import (
    ComicStory,
    PanelStory,
)

from app.services.layout_builder import (
    build_comic_layout,
)


def make_story():

    panels = []

    for number in range(1, 6):

        panels.append(
            PanelStory(
                panel_number=number,

                title=f"Panel {number}",

                scene_description=(
                    f"Scene description "
                    f"for panel {number}."
                ),

                caption=(
                    f"Caption {number}"
                ),

                narration=(
                    f"Narration {number}"
                ),

                dialogue=(
                    f"Dialogue {number}"
                ),

                image_prompt=(
                    f"Image prompt {number}"
                ),
            )
        )

    return ComicStory(
        panels=panels
    )


def test_build_comic_layout():

    story = make_story()

    image_urls = [
        f"/static/panels/panel_{number}.png"
        for number in range(1, 6)
    ]

    layout = build_comic_layout(
        story,
        image_urls
    )

    assert len(layout) == 5

    assert layout[0]["panel_number"] == 1

    assert (
        layout[0]["image_url"]
        == "/static/panels/panel_1.png"
    )

    assert (
        layout[4]["panel_number"]
        == 5
    )


def test_layout_requires_one_image_per_panel():

    story = make_story()

    image_urls = [
        "/static/panels/panel_1.png"
    ]

    try:

        build_comic_layout(
            story,
            image_urls
        )

        assert False, (
            "Expected ValueError"
        )

    except ValueError as exc:

        assert (
            "exactly one image"
            in str(exc)
        )