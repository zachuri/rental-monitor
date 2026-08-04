#!/usr/bin/env python3
"""Build a city-grouped rental digest with durable property lookup links."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlencode, urlsplit


def load_json_array(path: Path, label: str) -> list:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a JSON array")
    return value


def markdown_text(value: object, fallback: str = "N/A") -> str:
    text = str(value if value not in (None, "") else fallback)
    for char in "\\`*_{}[]<>#|":
        text = text.replace(char, f"\\{char}")
    return text


def valid_listing_url(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    parsed = urlsplit(value.strip())
    return value.strip() if parsed.scheme in {"http", "https"} and parsed.netloc else None


def build_digest(listings: list[dict], new_ids: list, today: str) -> str:
    wanted = {str(item) for item in new_ids}
    selected = [item for item in listings if isinstance(item, dict) and str(item.get("id")) in wanted]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for listing in selected:
        city = str(listing.get("city") or "Unknown area").strip() or "Unknown area"
        grouped[city].append(listing)

    lines = [f"# Rental Digest — {markdown_text(today)}", "", f"**{len(selected)} new matching listing(s)**", ""]
    for city in sorted(grouped, key=str.casefold):
        city_listings = sorted(
            grouped[city],
            key=lambda item: (
                item.get("price") if isinstance(item.get("price"), (int, float)) else float("inf"),
                str(item.get("addressLine1") or "").casefold(),
            ),
        )
        lines.extend([f"## {markdown_text(city)} ({len(city_listings)})", ""])
        for listing in city_listings:
            original_url = valid_listing_url(listing.get("listingUrl"))
            search_terms = " ".join(
                part
                for part in [
                    str(listing.get("addressLine1") or "").strip(),
                    str(listing.get("city") or "").strip(),
                    "rent",
                ]
                if part
            )
            search_url = "https://google.com/search?" + urlencode({"q": search_terms})
            property_url = original_url or search_url
            address_heading = markdown_text(listing.get("addressLine1"), "Unknown address")
            price = listing.get("price")
            rent = f"${price:,.0f}" if isinstance(price, (int, float)) else "$N/A"
            beds = markdown_text(listing.get("bedrooms"))
            baths = markdown_text(listing.get("bathrooms"))
            sqft = markdown_text(listing.get("squareFootage"))
            lines.append(
                f"- [{address_heading}]({property_url}) | {rent} | {beds}bd/{baths}ba | {sqft}sf"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    if len(sys.argv) != 5:
        print("Usage: build-digest.py LISTINGS_JSON NEW_IDS_JSON OUTPUT_MD DATE", file=sys.stderr)
        return 2
    listings_path, ids_path, output_path = map(Path, sys.argv[1:4])
    today = sys.argv[4]
    try:
        listings = load_json_array(listings_path, "listings")
        new_ids = load_json_array(ids_path, "new IDs")
        Path(output_path).write_text(build_digest(listings, new_ids, today), encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
