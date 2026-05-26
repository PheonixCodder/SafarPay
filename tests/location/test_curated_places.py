from __future__ import annotations

from pathlib import Path

from location.maps.curated_importer import read_curated_places
from location.maps.normalization import normalise_search_query


def test_read_curated_places_parses_aliases_and_builds_stable_keys(tmp_path: Path) -> None:
    seed_file = tmp_path / "lahore_seed.csv"
    seed_file.write_text(
        "\n".join(
            [
                "name,formatted,place_type,city,district,region,latitude,longitude,popularity,aliases",
                '"DHA Phase 5","DHA Phase 5, Lahore, Pakistan",neighbourhood,Lahore,Lahore,Punjab,31.4670,74.4100,950,"D.H.A Phase 5|Defence Phase V|Phase 5 DHA Lahore"',
            ]
        ),
        encoding="utf-8",
    )

    places = read_curated_places(seed_file)

    assert len(places) == 1
    assert places[0].source_key == "curated:lahore:dha-phase-5"
    assert places[0].aliases == {
        "D.H.A Phase 5",
        "Defence Phase V",
        "Phase 5 DHA Lahore",
    }
    assert normalise_search_query(places[0].name) == "dha phase 5"
