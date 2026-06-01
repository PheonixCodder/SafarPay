from location.maps.query_detection import is_coordinate_formatted, parse_coordinates_query


def test_parse_coordinates_query_accepts_lat_lng() -> None:
    parsed = parse_coordinates_query("31.53723, 74.42631")
    assert parsed is not None
    assert parsed.latitude == 31.53723
    assert parsed.longitude == 74.42631


def test_parse_coordinates_query_rejects_place_name() -> None:
    assert parse_coordinates_query("Gulberg, Lahore") is None


def test_is_coordinate_formatted_detects_fallback_label() -> None:
    assert is_coordinate_formatted("31.52040, 74.35870")
