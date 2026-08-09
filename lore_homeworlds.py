"""Lore homeworld names for trade seeding / galaxy labels.

Drawn from conventional-species-history-c.md (kids-to-feed table + entries).
`map_label` is what appears on the galactic map; `world` is the system/world name.
"""

from __future__ import annotations

from typing import TypedDict


class LoreHomeworld(TypedDict):
    key: str
    map_label: str
    culture: str
    world: str


# Parents first, then moderate / drastic abductees — matches the lore roster.
LORE_HOMEWORLDS: list[LoreHomeworld] = [
    {"key": "sol", "map_label": "Sol", "culture": "Humans", "world": "Sol"},
    {
        "key": "thalass",
        "map_label": "Thalass",
        "culture": "Tidecloth Compact",
        "world": "Thalass",
    },
    {
        "key": "mycorr",
        "map_label": "Mycorr",
        "culture": "Rootward Compact",
        "world": "Mycorr",
    },
    {
        "key": "keth_orum",
        "map_label": "Keth-Orum",
        "culture": "Veyri",
        "world": "Keth-Orum",
    },
    {
        "key": "coldfold",
        "map_label": "Coldfold",
        "culture": "Second Pack",
        "world": "Coldfold",
    },
    {
        "key": "inkden",
        "map_label": "Inkden",
        "culture": "Brand-Pack",
        "world": "Inkden",
    },
    {
        "key": "sillin",
        "map_label": "Sillin",
        "culture": "Sillin Chorus-Weavers",
        "world": "Sillin",
    },
    {
        "key": "umbral",
        "map_label": "Umbral",
        "culture": "Deepglow Court",
        "world": "Umbral",
    },
    {
        "key": "whitecut",
        "map_label": "Whitecut",
        "culture": "Flense-Shore",
        "world": "Whitecut",
    },
    {
        "key": "drannock",
        "map_label": "Drannock",
        "culture": "Drannock Clades",
        "world": "Drannock",
    },
    {
        "key": "karst",
        "map_label": "Karst",
        "culture": "Stonehex",
        "world": "Karst",
    },
    {
        "key": "roargrid",
        "map_label": "Roargrid",
        "culture": "Spectacle Hex",
        "world": "Roargrid",
    },
    {
        "key": "moru",
        "map_label": "Moru",
        "culture": "Moru Binders",
        "world": "Moru",
    },
    {
        "key": "windlash",
        "map_label": "Windlash",
        "culture": "Highspan Kin",
        "world": "Windlash",
    },
    {
        "key": "facetflow",
        "map_label": "Facetflow",
        "culture": "Glass-Barge",
        "world": "Facetflow",
    },
    {
        "key": "hecate",
        "map_label": "Hecate",
        "culture": "Hecate Line",
        "world": "Hecate",
    },
    {
        "key": "nullspire",
        "map_label": "Nullspire",
        "culture": "Mirror-Alone",
        "world": "Nullspire",
    },
    {
        "key": "crowdwell",
        "map_label": "Crowdwell",
        "culture": "Crowdwell Seed",
        "world": "Crowdwell",
    },
    {
        "key": "ylth",
        "map_label": "Ylth",
        "culture": "Ylth Swarm-Kin",
        "world": "Ylth",
    },
    {
        "key": "glarecap",
        "map_label": "Glarecap",
        "culture": "Sunspill Farms",
        "world": "Glarecap",
    },
    {
        "key": "schedulecap",
        "map_label": "Schedulecap",
        "culture": "Rail-Spore",
        "world": "Schedulecap",
    },
    {
        "key": "ukari",
        "map_label": "Ukari",
        "culture": "Brazen Ukari",
        "world": "Ukari",
    },
    {
        "key": "windscar",
        "map_label": "Windscar",
        "culture": "Highsteppe Remnant",
        "world": "Windscar",
    },
    {
        "key": "stillsteppe",
        "map_label": "Stillsteppe",
        "culture": "Quiet Banner",
        "world": "Stillsteppe",
    },
    {
        "key": "ix",
        "map_label": "Ix",
        "culture": "Soft-Lattice Ix",
        "world": "Ix",
    },
    {
        "key": "abyssroot",
        "map_label": "Abyssroot",
        "culture": "Deeper-Still",
        "world": "Abyssroot",
    },
    {
        "key": "clickcrust",
        "map_label": "Clickcrust",
        "culture": "Market Lattice",
        "world": "Clickcrust",
    },
    {
        "key": "pellagra",
        "map_label": "Pellagra",
        "culture": "Pellagra Singers",
        "world": "Pellagra",
    },
    {
        "key": "resound",
        "map_label": "Resound",
        "culture": "Echo-Nation",
        "world": "Resound",
    },
    {
        "key": "redactsound",
        "map_label": "Redactsound",
        "culture": "Cah'Zee",
        "world": "Redactsound",
    },
    {
        "key": "khar",
        "map_label": "Khar",
        "culture": "Khar Dentate",
        "world": "Khar",
    },
    {
        "key": "gloamdrift",
        "map_label": "Gloamdrift",
        "culture": "Night-Caravan",
        "world": "Gloamdrift",
    },
    {
        "key": "softbite",
        "map_label": "Softbite",
        "culture": "Moss-Dent",
        "world": "Softbite",
    },
    {
        "key": "nuun",
        "map_label": "Nuun",
        "culture": "Nuun Mirror-Polities",
        "world": "Nuun",
    },
    {
        "key": "triune",
        "map_label": "Triune",
        "culture": "Triple-Fault",
        "world": "Triune",
    },
    {
        "key": "driftpair",
        "map_label": "Driftpair",
        "culture": "Herd-Mirror",
        "world": "Driftpair",
    },
    {
        "key": "threnn",
        "map_label": "Threnn",
        "culture": "Threnn Bell-Divers",
        "world": "Threnn",
    },
    {
        "key": "brightwell",
        "map_label": "Brightwell",
        "culture": "Shallow-Tone",
        "world": "Brightwell",
    },
    {
        "key": "windshaft",
        "map_label": "Windshaft",
        "culture": "Dry-Chime",
        "world": "Windshaft",
    },
    {
        "key": "vael",
        "map_label": "Vael",
        "culture": "Vael of the Second Skin",
        "world": "Vael",
    },
    {
        "key": "closeglen",
        "map_label": "Closeglen",
        "culture": "Nearskin Compact",
        "world": "Closeglen",
    },
    {
        "key": "noavatar",
        "map_label": "Noavatar",
        "culture": "Hidebound",
        "world": "Noavatar",
    },
    {
        "key": "orth",
        "map_label": "Orth",
        "culture": "Orth of the Brief Dark",
        "world": "Orth",
    },
    {
        "key": "milknight",
        "map_label": "Milknight",
        "culture": "Softnight Kin",
        "world": "Milknight",
    },
    {
        "key": "brightstep",
        "map_label": "Neverdark / Brightstep",
        "culture": "Neverdark",
        "world": "Brightstep",
    },
]


def lore_by_key(key: str) -> LoreHomeworld:
    for entry in LORE_HOMEWORLDS:
        if entry["key"] == key:
            return entry
    raise KeyError(key)
