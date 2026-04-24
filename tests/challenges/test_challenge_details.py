from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "challenges" / "catalog.yaml"
DETAILS_PATH = ROOT / "challenges" / "details.yaml"
REQUIRED_LOCALES = {"en", "zh"}
REQUIRED_DETAIL_FIELDS = {
    "background",
    "objective",
    "input_contract",
    "output_contract",
    "scoring",
    "example_input",
    "example_output",
    "common_pitfalls",
    "stretch_goal",
}


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    assert isinstance(data, dict)
    return data


def runnable_catalog_ids() -> set[str]:
    catalog = load_yaml(CATALOG_PATH)
    entries = catalog.get("challenges")
    assert isinstance(entries, list)
    return {
        entry["id"]
        for entry in entries
        if entry.get("status") == "runnable"
    }


def test_runnable_challenges_have_rich_bilingual_details() -> None:
    details = load_yaml(DETAILS_PATH)

    assert set(details) == runnable_catalog_ids()

    for challenge_id, localized_details in details.items():
        assert set(localized_details) == REQUIRED_LOCALES, challenge_id

        for locale, detail in localized_details.items():
            assert REQUIRED_DETAIL_FIELDS <= set(detail), (challenge_id, locale)

            for field in REQUIRED_DETAIL_FIELDS - {"example_input", "example_output", "common_pitfalls"}:
                assert isinstance(detail[field], str), (challenge_id, locale, field)
                assert len(detail[field].strip()) >= 40, (challenge_id, locale, field)

            assert isinstance(detail["example_input"], dict), (challenge_id, locale)
            assert isinstance(detail["example_output"], dict), (challenge_id, locale)

            pitfalls = detail["common_pitfalls"]
            assert isinstance(pitfalls, list), (challenge_id, locale)
            assert len(pitfalls) >= 3, (challenge_id, locale)
            assert all(isinstance(item, str) and len(item.strip()) >= 20 for item in pitfalls)
