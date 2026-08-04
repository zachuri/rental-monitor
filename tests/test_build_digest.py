#!/usr/bin/env python3
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build-digest.py"


class DigestBuilderTest(unittest.TestCase):
    def test_groups_by_city_and_adds_property_links(self):
        listings = [
            {
                "id": "irvine-1",
                "addressLine1": "123 Main St",
                "city": "Irvine",
                "state": "CA",
                "zipCode": "92614",
                "bedrooms": 2,
                "bathrooms": 2,
                "price": 3500,
                "squareFootage": 1000,
            },
            {
                "id": "anaheim-1",
                "addressLine1": "456 Center St",
                "city": "Anaheim",
                "state": "CA",
                "zipCode": "92805",
                "bedrooms": 3,
                "bathrooms": 2,
                "price": 4800,
                "listingUrl": "https://example.com/original-listing",
            },
        ]

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            listings_path = tmp / "listings.json"
            ids_path = tmp / "ids.json"
            output_path = tmp / "digest.md"
            listings_path.write_text(json.dumps(listings))
            ids_path.write_text(json.dumps(["irvine-1", "anaheim-1"]))

            subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    str(listings_path),
                    str(ids_path),
                    str(output_path),
                    "August 04, 2026",
                ],
                check=True,
            )
            digest = output_path.read_text()

        self.assertIn("## Anaheim (1)", digest)
        self.assertIn("## Irvine (1)", digest)
        self.assertLess(digest.index("## Anaheim"), digest.index("## Irvine"))
        self.assertIn("[456 Center St](https://example.com/original-listing)", digest)
        self.assertIn(
            "[123 Main St](https://google.com/search?q=123+Main+St+Irvine+rent)",
            digest,
        )
        self.assertIn("$3,500 | 2bd/2ba | 1000sf", digest)

    def test_full_rentcast_page_fits_github_issue_limit(self):
        listings = [
            {
                "id": f"listing-{index}",
                "addressLine1": f"{1000 + index} Example Apartment Way",
                "city": ["Anaheim", "Garden Grove", "Irvine", "Tustin"][index % 4],
                "bedrooms": 2 + index % 2,
                "bathrooms": 2,
                "price": 3200 + index,
                "squareFootage": 1000 + index,
            }
            for index in range(500)
        ]
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            listings_path = tmp / "listings.json"
            ids_path = tmp / "ids.json"
            output_path = tmp / "digest.md"
            listings_path.write_text(json.dumps(listings))
            ids_path.write_text(json.dumps([item["id"] for item in listings]))
            subprocess.run(
                ["python3", str(SCRIPT), str(listings_path), str(ids_path), str(output_path), "August 04, 2026"],
                check=True,
            )
            self.assertLess(len(output_path.read_bytes()), 65_536)


if __name__ == "__main__":
    unittest.main()
