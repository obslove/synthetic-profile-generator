from __future__ import annotations

import csv
import gzip
import html
import json
import re
import unicodedata
import urllib.request
from io import StringIO
from pathlib import Path

OUT = (
    Path(__file__).resolve().parent.parent
    / "synthetic_profiles"
    / "locales"
    / "countries"
    / "city_catalog.json"
)

BR_CAPITALS = {
    "AC": "Rio Branco",
    "AL": "Maceió",
    "AP": "Macapá",
    "AM": "Manaus",
    "BA": "Salvador",
    "CE": "Fortaleza",
    "DF": "Brasília",
    "ES": "Vitória",
    "GO": "Goiânia",
    "MA": "São Luís",
    "MT": "Cuiabá",
    "MS": "Campo Grande",
    "MG": "Belo Horizonte",
    "PA": "Belém",
    "PB": "João Pessoa",
    "PR": "Curitiba",
    "PE": "Recife",
    "PI": "Teresina",
    "RJ": "Rio de Janeiro",
    "RN": "Natal",
    "RS": "Porto Alegre",
    "RO": "Porto Velho",
    "RR": "Boa Vista",
    "SC": "Florianópolis",
    "SP": "São Paulo",
    "SE": "Aracaju",
    "TO": "Palmas",
}

US_CAPITALS = {
    "AL": "Montgomery",
    "AK": "Juneau",
    "AZ": "Phoenix",
    "AR": "Little Rock",
    "CA": "Sacramento",
    "CO": "Denver",
    "CT": "Hartford",
    "DE": "Dover",
    "FL": "Tallahassee",
    "GA": "Atlanta",
    "HI": "Urban Honolulu",
    "ID": "Boise",
    "IL": "Springfield",
    "IN": "Indianapolis",
    "IA": "Des Moines",
    "KS": "Topeka",
    "KY": "Frankfort",
    "LA": "Baton Rouge",
    "ME": "Augusta",
    "MD": "Annapolis",
    "MA": "Boston",
    "MI": "Lansing",
    "MN": "Saint Paul",
    "MS": "Jackson",
    "MO": "Jefferson City",
    "MT": "Helena",
    "NE": "Lincoln",
    "NV": "Carson City",
    "NH": "Concord",
    "NJ": "Trenton",
    "NM": "Santa Fe",
    "NY": "Albany",
    "NC": "Raleigh",
    "ND": "Bismarck",
    "OH": "Columbus",
    "OK": "Oklahoma City",
    "OR": "Salem",
    "PA": "Harrisburg",
    "RI": "Providence",
    "SC": "Columbia",
    "SD": "Pierre",
    "TN": "Nashville",
    "TX": "Austin",
    "UT": "Salt Lake City",
    "VT": "Montpelier",
    "VA": "Richmond",
    "WA": "Olympia",
    "WV": "Charleston",
    "WI": "Madison",
    "WY": "Cheyenne",
    "DC": "Washington",
    "AS": "Pago Pago",
    "GU": "Hagatna",
    "MP": "Capitol Hill",
    "PR": "San Juan",
    "VI": "Charlotte Amalie",
}

US_GAZETTEER_FIPS = {
    "HI": "15",
    "PR": "72",
}

US_GUAM_VILLAGES = [
    "Agana Heights",
    "Agat",
    "Asan-Maina",
    "Barrigada",
    "Chalan Pago-Ordot",
    "Dededo",
    "Hagatna",
    "Inarajan",
    "Mangilao",
    "Merizo",
    "Mongmong-Toto-Maite",
    "Piti",
    "Santa Rita-Sumai",
    "Sinajana",
    "Talofofo",
    "Tamuning-Tumon-Harmon",
    "Umatac",
    "Yigo",
    "Yona",
]


def normalize_ascii(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return " ".join(without.casefold().split())


def fetch_text(url: str, *, timeout: int = 60) -> str:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        raw = response.read()
    try:
        raw = gzip.decompress(raw)
    except OSError:
        pass
    return raw.decode("utf-8", "ignore")


def add_entries(
    bucket: dict[str, dict[str, list[dict[str, object]]]],
    country: str,
    subdivision: str,
    names: list[str],
    capital_name: str | None,
) -> None:
    seen: set[str] = set()
    items: list[dict[str, object]] = []
    capital_norm = normalize_ascii(capital_name) if capital_name else None
    for name in sorted(names, key=normalize_ascii):
        normalized_name = normalize_ascii(name)
        if normalized_name in seen:
            continue
        seen.add(normalized_name)
        items.append(
            {
                "name": name,
                "is_capital": capital_norm == normalized_name,
            }
        )
    bucket.setdefault(country, {})[subdivision] = items


def fetch_br() -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for uf in BR_CAPITALS:
        text = fetch_text(
            f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
        )
        result[uf] = [item["nome"] for item in json.loads(text)]
    return result


def fetch_us() -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for code in US_CAPITALS:
        if code == "GU":
            result[code] = list(US_GUAM_VILLAGES)
            continue

        names = fetch_us_incplace(code)
        if names:
            result[code] = names
            continue

        fips = US_GAZETTEER_FIPS.get(code)
        if fips is None:
            result[code] = []
            continue
        result[code] = fetch_us_gazetteer_places(fips)
    return result


def fetch_us_incplace(code: str) -> list[str]:
    text = fetch_text(
        f"https://tigerweb.geo.census.gov/tigerwebmain/Files/bas26/"
        f"tigerweb_bas26_incplace_{code.lower()}.html"
    )
    row_re = re.compile(r"<tr>(.*?)</tr>", re.I | re.S)
    cell_re = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.I | re.S)
    tag_re = re.compile(r"<[^>]+>")
    headers: list[str] = []
    names: list[str] = []

    for row in row_re.findall(text):
        cells = [
            html.unescape(tag_re.sub("", cell)).strip()
            for cell in cell_re.findall(row)
        ]
        if not cells:
            continue
        if not headers and "BASENAME" in cells:
            headers = cells
            continue
        if headers and len(cells) == len(headers):
            record = dict(zip(headers, cells))
            name = record.get("BASENAME") or record.get("NAME")
            if name:
                names.append(name)
    return names


def fetch_us_gazetteer_places(fips: str) -> list[str]:
    text = fetch_text(
        "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/"
        f"2025_Gazetteer/2025_gaz_place_{fips}.txt"
    )
    reader = csv.DictReader(StringIO(text), delimiter="|")
    return [
        _normalize_us_place_name(row["NAME"])
        for row in reader
        if row.get("NAME")
    ]


def _normalize_us_place_name(name: str) -> str:
    suffixes = (
        " CDP",
        " city",
        " town",
        " village",
        " borough",
        " municipality",
        " comunidad",
        " zona urbana",
        " urbanizacion",
        " barrio-pueblo",
    )
    for suffix in suffixes:
        if name.endswith(suffix):
            return name[: -len(suffix)].strip()
    return name.strip()

def build_catalog() -> dict[str, dict[str, list[dict[str, object]]]]:
    catalog: dict[str, dict[str, list[dict[str, object]]]] = {}

    br = fetch_br()
    for code, names in br.items():
        add_entries(catalog, "BR", code, names, BR_CAPITALS.get(code))

    us = fetch_us()
    for code, names in us.items():
        add_entries(catalog, "US", code, names, US_CAPITALS.get(code))

    return catalog


def main() -> None:
    catalog = build_catalog()
    OUT.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"BR/SP {len(catalog['BR']['SP'])}")
    print(f"US/CA {len(catalog['US']['CA'])}")


if __name__ == "__main__":
    main()
