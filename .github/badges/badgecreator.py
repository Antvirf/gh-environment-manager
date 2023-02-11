"""
Python script to get ratings and downloads from Garmin Marketplace, and create repo badges for both.
"""
import sys

import requests


def create_badge(badge_text: str, badge_value: str):
    """Given a text and a number, generate an .svg badge"""
    url = f"https://img.shields.io/badge/{badge_text}-{badge_value}-brightgreen"
    svg_text = requests.get(url).text

    with open(".github/badges/"+badge_text+".svg", "w") as writer:
        writer.write(svg_text)


if __name__ == "__main__":
    # take value from first arg
    for line in sys.stdin:
        coverage_value = str(line).strip()
        create_badge(
            badge_text="coverage",
            badge_value=coverage_value
        )
        break
