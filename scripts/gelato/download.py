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

"""

FOOTER = """All menu information is property of Jack's Gelato. This page is
updated daily at 10:20am -- see my
[blog post]({{< ref "/posts/a_faster_gelato" >}}) for why I made it.
"""

MENU_LOCATIONS: dict[str, tuple[str, str]] = {
    "Bene't Street": (
        "https://docs.google.com/uc?id=1dVYB7lnBgWE0bPhc9SFz0aLrkDfSCulrMctW1gDfCA8",
        "https://www.jacksgelato.com/bene-t-street-menu"
    ),
    "All Saints": (
        "https://docs.google.com/uc?id=1kDBSxPb8X4L2TKXWUmm2A-VGuPVTyxmfbq9iwUQQ2nc",
        "https://www.jacksgelato.com/all-saints-menu"
    ),
}

NAMED_DATES: set[str] = {
    "Halloween",
}


@dataclass
class Menu:
    """Dataclass containing the menu date and items."""

    location: str
    web: str
    date: datetime | str
    items: list[str]

    def __repr__(self) -> str:
        """Convert a menu dataclass to its markdown representation.

        Returns:
            A markdown representation of the menu.
        """
        date_string = (
            self.date if isinstance(self.date, str)
            else datetime.strftime(self.date, "%A, %d/%m/%Y")
        )
        title = f"## [{self.location}]({self.web}) ({date_string})\n\n"
        contents = "\n".join(f"- {item}" for item in self.items)
        return title + contents + "\n\n"


class MenuParseState(Enum):
    """Enum containing parser states for the menu."""

    Date = auto()
    Items = auto()
    Done = auto()


def get_jacks_menu(location: str, doc: str, web: str, output_file: Path | None = None) -> Menu:
    """Get the Jack's Gelato menu from the Google Docs url.

    Args:
        location: The name of the menu's restaurant.
        doc: The URL of the Google doc containing the menu.
        web: The URL of the Jack's website with the canonical menu.
        output_file: The file path to cache the downloaded text menu to.

    Returns:
        A dataclass containing the contents of the menu.
    """
    if output_file is None:
        location_sanitised = location.replace(" ", "_").replace("'", "").lower()
        output_file = BASE_RAW_DIRECTORY / f"{DATE}__{location_sanitised}.txt"

    if not output_file.exists():
        gdown.download(doc, str(output_file), quiet=False, format="txt")

    with output_file.open() as menu:
        lines = [line.strip() for line in menu]

    date: datetime | str | None = None
    items: list[str] = []
    menu_parse_state = MenuParseState.Date

    for line in lines:
        print(line, date)
        if menu_parse_state == MenuParseState.Date:
            try:
                date = (
                    line if line.split(",")[0] in NAMED_DATES else
                    dateutil.parser.parse(line)
                )
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

    if not isinstance(date, str):
        assert date.day == NOW.day
    assert len(items) > 0
    return Menu(location, web, date, items)


if __name__ == "__main__":
    output_file = BASE_MARKDOWN_DIRECTORY / f"{DATE}.md"
    with output_file.open("w+") as file_handle:
        file_handle.write(HEADER)
        for (name, (doc, web)) in MENU_LOCATIONS.items():
            file_handle.write(str(get_jacks_menu(name, doc, web)))
        file_handle.write(FOOTER)
