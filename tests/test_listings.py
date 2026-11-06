"""Tests for CSV parsing -- the part most likely to meet a surprising file."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rep.listings import (  # noqa: E402
    Listing, apply_filter, build_mapping, classify_deal, load_csv,
    normalise_header, parse_int, parse_number, sniff_delimiter, split_multi,
)


class TestParseNumber:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("4500000", 4_500_000.0),
            ("4,500,000", 4_500_000.0),
            ("฿ 4,500,000", 4_500_000.0),
            ("THB 2,950,000.00", 2_950_000.0),
            ("78.5", 78.5),
            ("1 890 000", 1_890_000.0),
            ("45,000 /month", 45_000.0),
            ("3,5", 3.5),          # decimal comma: 2 digits after, not 3
            ("", None),
            ("   ", None),
            (None, None),
            ("POA", None),
            ("Ask", None),
        ],
    )
    def test_parses(self, raw, expected):
        assert parse_number(raw) == expected

    def test_int_truncates(self):
        assert parse_int("3.9") == 3
        assert parse_int("") is None


class TestHeaders:
    def test_normalise(self):
        assert normalise_header("  Price (THB) ") == "pricethb"
        assert normalise_header("Ref No.") == "refno"
        assert normalise_header("Area / District") == "areadistrict"

    def test_exact_alias_wins(self):
        mapped, unmapped = build_mapping(["Bedrooms", "Price", "Agent"])
        assert mapped["bedrooms"] == "Bedrooms"
        assert mapped["price"] == "Price"
        assert unmapped == ["Agent"]

    def test_longest_alias_wins_on_fuzzy_match(self):
        # "Area / District" must go to location (alias "district", 8 chars),
        # not size_sqm (alias "area", 4 chars).
        mapped, _ = build_mapping(["Area / District"])
        assert mapped.get("location") == "Area / District"
        assert "size_sqm" not in mapped

    def test_type_means_property_type(self):
        # Property exports use "Type" for Condo/Villa, not for sale-vs-rent.
        mapped, _ = build_mapping(["Type", "For Sale / Rent"])
        assert mapped["property_type"] == "Type"
        assert mapped["deal_type"] == "For Sale / Rent"

    def test_short_aliases_do_not_fuzzy_match(self):
        # "br" must not claim "Brochure Link".
        mapped, unmapped = build_mapping(["Brochure Link"])
        assert "bedrooms" not in mapped
        assert unmapped == ["Brochure Link"]

    def test_field_claimed_only_once(self):
        mapped, unmapped = build_mapping(["Price", "Price (THB)"])
        assert mapped["price"] == "Price"
        assert "Price (THB)" in unmapped or len(mapped) > 1


class TestDealType:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("For Sale", "sale"),
            ("Rent", "rent"),
            ("Sale & Rent", "both"),
            ("Monthly Rental", "rent"),
            ("ขาย", "sale"),
            ("เช่า", "rent"),
            ("Condo", ""),
        ],
    )
    def test_classify(self, text, expected):
        assert classify_deal(text) == expected


class TestSplitMulti:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("a.jpg|b.jpg", ["a.jpg", "b.jpg"]),
            ("Pool; Gym; Parking", ["Pool", "Gym", "Parking"]),
            ("Pool, Garden", ["Pool", "Garden"]),
            ("one\ntwo", ["one", "two"]),
            ("", []),
            (None, []),
            ("  ,  ,  ", []),
        ],
    )
    def test_splits(self, raw, expected):
        assert split_multi(raw) == expected


class TestDelimiter:
    def test_semicolon(self):
        assert sniff_delimiter("a;b;c\n1;2;3\n") == ";"

    def test_tab(self):
        assert sniff_delimiter("a\tb\tc\n1\t2\t3\n") == "\t"

    def test_comma_default(self):
        assert sniff_delimiter("a,b,c\n1,2,3\n") == ","


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    path = tmp_path / "listings.csv"
    path.write_text(
        "Ref No.,Property Name,Type,For Sale / Rent,Price (THB),Rent Per Month,"
        "Bedrooms,Bathrooms,Size (Sqm),Area / District,Photos,Amenities,Agent\n"
        'CP-001,"Sea View Condo",Condo,Sale,"฿ 4,500,000",,2,2,78.5,Pratumnak,'
        '"https://x/a.jpg|https://x/b.jpg","Pool;Gym",Nok\n'
        'CP-002,,Villa,Rent,,"45,000",3,3.5,210,Jomtien,https://x/c.jpg,"Garden",Som\n'
        ",,,,,,,,,,,,\n",
        encoding="utf-8",
    )
    return path


class TestLoadCsv:
    def test_round_trip(self, sample_csv):
        listings, report = load_csv(sample_csv)

        assert report.looks_like_listings
        assert report.row_count == 2          # the blank row is dropped
        assert report.unmapped == ["Agent"]

        first, second = listings
        assert first.reference == "CP-001"
        assert first.price == 4_500_000
        assert first.deal_type == "sale"
        assert first.property_type == "Condo"
        assert first.location == "Pratumnak"
        assert first.images == ["https://x/a.jpg", "https://x/b.jpg"]
        assert first.features == ["Pool", "Gym"]
        assert first.extra == {"Agent": "Nok"}

        # Row 2 has no title, so one is synthesised from the other columns.
        assert second.title
        assert "Villa" in second.title
        assert second.deal_type == "rent"
        assert second.rent_price == 45_000

    def test_column_override(self, sample_csv):
        listings, report = load_csv(sample_csv, overrides={"reference": "Agent"})
        assert report.mapped["reference"] == "Agent"
        assert listings[0].reference == "Nok"
        assert "Agent" not in report.unmapped

    def test_utf8_bom(self, tmp_path):
        path = tmp_path / "bom.csv"
        path.write_bytes("﻿Title,Price\nHouse,100\n".encode("utf-8"))
        listings, report = load_csv(path)
        assert report.encoding == "utf-8-sig"
        assert listings[0].title == "House"

    def test_semicolon_file(self, tmp_path):
        path = tmp_path / "semi.csv"
        path.write_text("Title;Price;Bedrooms\nVilla;1000000;3\n", encoding="utf-8")
        listings, report = load_csv(path)
        assert report.delimiter == ";"
        assert listings[0].price == 1_000_000
        assert listings[0].bedrooms == 3

    def test_empty_file_raises(self, tmp_path):
        path = tmp_path / "empty.csv"
        path.write_text("", encoding="utf-8")
        with pytest.raises(ValueError, match="empty"):
            load_csv(path)

    def test_non_listing_csv_is_flagged(self, tmp_path):
        path = tmp_path / "invoices.csv"
        path.write_text("Invoice No,Customer,Due Date\n1,Acme,2026-01-01\n", encoding="utf-8")
        _, report = load_csv(path)
        assert not report.looks_like_listings


class TestFilter:
    def test_filters_case_insensitively(self):
        rows = [
            Listing(title="A", location="Jomtien", deal_type="sale"),
            Listing(title="B", location="Pratumnak", deal_type="rent"),
        ]
        assert [x.title for x in apply_filter(rows, {"location": "jomtien"})] == ["A"]
        assert [x.title for x in apply_filter(rows, {"deal_type": "RENT"})] == ["B"]

    def test_multiple_rules_are_and(self):
        rows = [
            Listing(title="A", location="Jomtien", deal_type="sale"),
            Listing(title="B", location="Jomtien", deal_type="rent"),
        ]
        out = apply_filter(rows, {"location": "jomtien", "deal_type": "sale"})
        assert [x.title for x in out] == ["A"]

    def test_no_rules_returns_everything(self):
        rows = [Listing(title="A"), Listing(title="B")]
        assert apply_filter(rows, {}) == rows
