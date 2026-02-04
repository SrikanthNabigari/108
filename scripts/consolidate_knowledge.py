#!/usr/bin/env python3
"""
Consolidate yoga and dosha JSON files into master databases.
"""

import json
from pathlib import Path


def consolidate_yogas():
    """Merge all yoga detection JSON files into one master file."""
    rules_dir = Path(__file__).parent.parent / "knowledge" / "rules"

    # Collect all yoga files
    yoga_files = [
        rules_dir / "yoga_detection_expanded.json",
        rules_dir / "yoga_detection_part2.json",
        rules_dir / "yoga_detection_part3.json",
        rules_dir / "yoga_detection_part4.json",
        rules_dir / "yoga_detection_part5.json",
        rules_dir / "yoga_detection_part6.json",
        rules_dir / "yoga_detection_part7.json",
    ]

    # Master yoga dictionary
    master_yogas = {
        "metadata": {
            "version": "2.0.0",
            "total_yogas": 0,
            "sources": [
                "Brihat Parashara Hora Shastra (BPHS)",
                "Phaladeepika by Mantreswara",
                "Brihat Jataka by Varahamihira",
                "Jataka Parijata by Vaidyanatha",
                "Saravali by Kalyana Varma",
                "Uttara Kalamrita by Kalidasa",
                "Chamatkara Chintamani by Bhatt Narayana",
                "Hora Sara by Prithuyasas",
                "Jataka Tattva by Mahadeva",
                "Sarvarth Chintamani",
            ],
            "categories": {
                "pancha_mahapurusha": "Five great person yogas (Mars, Mercury, Jupiter, Venus, Saturn)",
                "chandra": "Moon-based yogas",
                "surya": "Sun-based yogas",
                "raja": "Kingly/royal yogas for power and authority",
                "dhana": "Wealth and prosperity yogas",
                "arishta": "Misfortune and health affliction yogas",
                "daridra": "Poverty and struggle yogas",
                "nabhas": "Sky/pattern yogas based on planetary distribution",
                "parivartana": "Exchange/mutual reception yogas",
                "neecha_bhanga": "Debilitation cancellation yogas",
                "viparita_raja": "Reversal of fortune yogas",
                "sanyasa": "Renunciation and spiritual yogas",
                "special": "Special combination yogas",
                "nakshatra": "Lunar mansion based yogas",
            },
        },
        "yoga_rules": {},
    }

    # Merge all yoga files
    for yoga_file in yoga_files:
        if yoga_file.exists():
            print(f"Loading: {yoga_file.name}")
            with yoga_file.open(encoding="utf-8") as f:
                data = json.load(f)
                if "yoga_rules" in data:
                    master_yogas["yoga_rules"].update(data["yoga_rules"])
                    print(f"  Added {len(data['yoga_rules'])} yogas")

    # Update count
    master_yogas["metadata"]["total_yogas"] = len(master_yogas["yoga_rules"])

    # Write master file
    master_file = rules_dir / "yoga_master.json"
    with master_file.open("w", encoding="utf-8") as f:
        json.dump(master_yogas, f, indent=2, ensure_ascii=False)

    print(f"\nCreated master yoga file: {master_file}")
    print(f"Total yogas: {master_yogas['metadata']['total_yogas']}")

    # Print category breakdown
    categories = {}
    for _yoga_id, yoga in master_yogas["yoga_rules"].items():
        cat = yoga.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    print("\nCategory breakdown:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    return master_yogas


def consolidate_doshas():
    """Copy expanded dosha file as master."""
    rules_dir = Path(__file__).parent.parent / "knowledge" / "rules"

    expanded_file = rules_dir / "dosha_detection_expanded.json"
    master_file = rules_dir / "dosha_master.json"

    if expanded_file.exists():
        with expanded_file.open(encoding="utf-8") as f:
            data = json.load(f)

        with master_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\nCreated master dosha file: {master_file}")
        print(f"Total doshas: {data['metadata']['total_doshas']}")

        # Print category breakdown
        categories = {}
        for _dosha_id, dosha in data["dosha_rules"].items():
            cat = dosha.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1

        print("\nCategory breakdown:")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            print(f"  {cat}: {count}")

        return data

    return None


def main():
    print("=" * 60)
    print("108 Knowledge Base Consolidation")
    print("=" * 60)

    print("\n--- Consolidating Yogas ---")
    yogas = consolidate_yogas()

    print("\n--- Consolidating Doshas ---")
    doshas = consolidate_doshas()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Yogas: {yogas['metadata']['total_yogas'] if yogas else 0}")
    print(f"Total Doshas: {doshas['metadata']['total_doshas'] if doshas else 0}")
    print("=" * 60)


if __name__ == "__main__":
    main()
