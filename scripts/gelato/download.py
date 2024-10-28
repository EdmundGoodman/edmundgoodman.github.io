#!/usr/bin/env python3
"""A script to download and markdownify the Jack's Gelato menu."""

from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import gdown
import dateutil.parser

NOW = datetime.now(timezone.utc)
DATE = datetime.strftime(NOW, "%y_%m_%d")

BASE_RAW_DIRECTORY = Path("../../static/files/gelato/raw_menus")
BASE_MARKDOWN_DIRECTORY = Path("../../content/gelato")

HEADER = f"""---
title: "Jack's Gelato Menus"
author: "Edmund Goodman"
date: {NOW}
---

All menu information is property of Jack's Gelato. See my [blog post]({{{{< ref "/posts/a_faster_gelato" >}}}}) for why
I made this website.

"""
MENU_LOCATIONS: dict[str, str] = {
    "Bene't Street": "https://docs.google.com/uc?id=1dVYB7lnBgWE0bPhc9SFz0aLrkDfSCulrMctW1gDfCA8",
    "All Saints": "https://docs.google.com/uc?id=1kDBSxPb8X4L2TKXWUmm2A-VGuPVTyxmfbq9iwUQQ2nc",
}


@dataclass
class Menu:
    """Dataclass containing the menu date and items."""

    location: str
    date: datetime
    items: list[str]


class MenuParseState(Enum):
    """Enum containing parser states for the menu."""

    Date = auto()
    Items = auto()
    Done = auto()


def get_jacks_menu(location: str, url: str, output_file: Path | None = None) -> Menu:
    """Get the Jack's Gelato menu from the Google Docs url.

    Args:
        location: The name of the menu's restaurant.
        url: The URL of the Google doc containing the menu.
        output_file: The file path to cache the downloaded text menu to.

    Returns:
        A dataclass containing the contents of the menu.
    """
    if output_file is None:
        location_sanitised = location.replace(" ", "_").replace("'", "").lower()
        output_file = BASE_RAW_DIRECTORY / f"{DATE}__{location_sanitised}.txt"

    if not output_file.exists():
        gdown.download(url, str(output_file), quiet=False, format="txt")

    with output_file.open() as menu:
        lines = [line.strip() for line in menu]

    date: datetime | None = None
    items: list[str] = []
    menu_parse_state = MenuParseState.Date

    for line in lines:
        if menu_parse_state == MenuParseState.Date:
            try:
                date = dateutil.parser.parse(line)
                menu_parse_state = MenuParseState.Items
            except dateutil.parser._parser.ParserError:  # noqa: SLF001
                pass
        elif menu_parse_state == MenuParseState.Items:
            if line in {"-", ""}:
                continue
            if line.startswith("Single Scoop"):
                menu_parse_state = MenuParseState.Done
                break
            items.append(line)

    assert date is not None
    # `assert date.day == NOW.day
    assert len(items) > 0
    return Menu(location, date, items)


def menu_to_markdown(menu: Menu) -> str:
    """Convert a menu dataclass to its markdown representation.

    Args:
        menu: The parse menu dataclass.

    Returns:
        A markdown representation of the menu.
    """
    date_string = datetime.strftime(menu.date, "%A, %d/%m/%Y")
    title = f"## {menu.location} ({date_string})\n\n"
    contents = "\n".join(f"- {item}" for item in menu.items)
    return title + contents + "\n\n"


def get_markdown_doc(header: str, menu_locations: dict[str, str]) -> str:
    """Get the markdown document containing the menus.

    Args:
        header: The header for the markdown file.
        menu_locations: The restaurant locations and their respective menu URLs.

    Returns:
        The markdown document containing the scraped menus.
    """
    menu_markdowns = [
        menu_to_markdown(get_jacks_menu(*values)) for values in menu_locations.items()
    ]
    return header + "\n\n".join(menu_markdowns)


if __name__ == "__main__":
    output_file = BASE_MARKDOWN_DIRECTORY / f"{DATE}.md"
    with output_file.open("w+") as file_handle:
        file_handle.write(HEADER)
        for values in MENU_LOCATIONS.items():
            file_handle.write(menu_to_markdown(get_jacks_menu(*values)))