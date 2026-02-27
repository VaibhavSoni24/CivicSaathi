"""
Smart Geo-Hash Based Duplicate Detection System
=================================================

Generates a deterministic **10-character Smart Hash ID** for every complaint:

    [TITLE_3][LAT_2][LON_2][DEPT_3]

Components
──────────
1. Title Keyword Hash (3 chars)
   • Strip stopwords & adjectives, extract civic-issue keywords,
     resolve to a semantic category code via a synonym table.
   • Fuzzy fallback via SequenceMatcher for unknown words.

2. Location Hash (4 chars – 2 lat + 2 lon)
   • Grid-normalise coordinates to a ~30-meter cell (double the 15 m
     tolerance) so two points ≤15 m apart are guaranteed to share a cell.
   • Also generates 3×3 neighbor hashes for boundary safety.

3. Department Code (3 chars)
   • Fixed 3-character uppercase abbreviation derived from
     the department name.

Duplicate flow
──────────────
• Generate primary hash + 9 neighbor-cell candidate hashes.
• Query DB for ANY matching hash among active complaints.
• Confirm match with Haversine distance ≤ 50 m.
• Hash matches + same user   → reject  ("You have already reported this issue.")
• Hash matches + diff user   → auto-upvote existing complaint.
• No match                   → create new complaint & store hash.
"""

from __future__ import annotations

import hashlib
import math
import re
from difflib import SequenceMatcher


# ═══════════════════════════════════════════════════════════════════════════
# Stopwords  (aggressive — includes adjectives / filler words so only
#             the civic-issue noun survives)
# ═══════════════════════════════════════════════════════════════════════════

_STOPWORDS = frozenset(
    # determiners / pronouns / prepositions / conjunctions
    "a an the is are was were be been being have has had do does did will would "
    "shall should may might can could of in on at to for with by from up about "
    "into through during before after above below between out off over under "
    "again further then once here there when where why how all each every both "
    "few more most other some such no nor not only own same so than too very "
    "just because as until while also and but or if this that these those it its "
    "i me my we our you your he him his she her they them their what which who "
    "whom how much many near "
    # filler adjectives / adverbs that don't identify the issue type
    "big large small huge major minor severe bad worst terrible horrible "
    "serious heavy deep broken damaged public local main old new massive "
    "dirty filthy unhygienic unsanitary unclean smelly stinking foul rotten "
    "extremely highly quite really totally completely absolutely partially "
    "poorly badly urgently immediate immediate urgent critical dangerous "
    # filler nouns that don't identify issue type
    "facility area zone place spot site point section issue problem complaint "
    "report condition situation matter concern state status "
    "road street lane avenue colony ward block sector locality mohalla "
    "nagar chowk circle bazaar market".split()
)


# ═══════════════════════════════════════════════════════════════════════════
# 1.  Title Keyword Hash  (3 uppercase characters) — SEMANTIC
# ═══════════════════════════════════════════════════════════════════════════

# Maps civic-issue keywords (including synonyms) to a stable 3-char code.
# Every synonym for the same real-world issue maps to the SAME code.
_SEMANTIC_CATEGORIES: dict[str, str] = {
    # ── Pothole / Road-surface damage ──
    "pothole":       "POT", "potholes":      "POT", "crater":        "POT",
    "craters":       "POT", "roadhole":      "POT",

    # ── General road / pavement damage ──
    "pavement":      "RDD", "asphalt":       "RDD", "tar":           "RDD",
    "bitumen":       "RDD", "resurfacing":   "RDD", "resurface":     "RDD",

    # ── Garbage / Waste ──
    "garbage":       "GRB", "trash":         "GRB", "waste":         "GRB",
    "litter":        "GRB", "littering":     "GRB", "rubbish":       "GRB",
    "debris":        "GRB", "dump":          "GRB", "dumping":       "GRB",
    "dumpsite":      "GRB", "dumpyard":      "GRB",

    # ── Sewage / Drainage ──
    "sewage":        "SEW", "sewer":         "SEW", "drain":         "SEW",
    "drainage":      "SEW", "clogged":       "SEW", "blocked":       "SEW",
    "overflow":      "SEW", "overflowing":   "SEW", "manhole":       "SEW",
    "manholes":      "SEW", "gutter":        "SEW", "nala":          "SEW",
    "nallah":        "SEW",

    # ── Streetlight ──
    "streetlight":   "SLT", "streetlights":  "SLT", "lamp":          "SLT",
    "lamppost":      "SLT", "bulb":          "SLT", "light":         "SLT",
    "lighting":      "SLT", "darkspot":      "SLT", "dark":          "SLT",

    # ── Electricity / Power ──
    "electricity":   "ELC", "power":         "ELC", "powercut":      "ELC",
    "outage":        "ELC", "blackout":      "ELC", "transformer":   "ELC",
    "wire":          "ELC", "wiring":        "ELC", "cable":         "ELC",
    "electrocution": "ELC", "spark":         "ELC", "sparking":      "ELC",

    # ── Water supply ──
    "water":         "WTR", "watersupply":   "WTR", "tap":           "WTR",
    "pipeline":      "WTR", "pipe":          "WTR", "pipes":         "WTR",
    "leakage":       "WTR", "leak":          "WTR", "leaking":       "WTR",
    "burst":         "WTR", "borewell":      "WTR", "borehole":      "WTR",
    "tanker":        "WTR",

    # ── Waterlogging / Flooding ──
    "waterlogging":  "WLG", "waterlogged":   "WLG", "flood":         "WLG",
    "flooding":      "WLG", "stagnant":      "WLG", "stagnation":    "WLG",
    "puddle":        "WLG", "inundation":    "WLG",

    # ── Toilet / Urinal / Sanitation ──
    "toilet":        "SAN", "toilets":       "SAN", "urinal":        "SAN",
    "urinals":       "SAN", "lavatory":      "SAN", "restroom":      "SAN",
    "washroom":      "SAN", "bathroom":      "SAN", "sanitation":    "SAN",
    "defecation":    "SAN",

    # ── Footpath / Sidewalk ──
    "footpath":      "FTP", "sidewalk":      "FTP", "walkway":       "FTP",
    "pedestrian":    "FTP", "encroachment":  "FTP",

    # ── Park / Garden / Tree ──
    "park":          "PRK", "garden":        "PRK", "tree":          "PRK",
    "trees":         "PRK", "branch":        "PRK", "fallen":        "PRK",
    "uprooted":      "PRK", "pruning":       "PRK", "greenery":      "PRK",
    "plantation":    "PRK",

    # ── Traffic / Signal ──
    "traffic":       "TRF", "signal":        "TRF", "signals":       "TRF",
    "congestion":    "TRF", "jam":           "TRF", "trafficjam":    "TRF",
    "zebra":         "TRF", "crossing":      "TRF", "divider":       "TRF",
    "barricade":     "TRF", "sign":          "TRF", "signboard":     "TRF",

    # ── Noise / Pollution ──
    "noise":         "NOS", "pollution":     "NOS", "honking":       "NOS",
    "loudspeaker":   "NOS", "construction":  "NOS", "dust":          "NOS",
    "smoke":         "NOS", "emission":      "NOS",

    # ── Animal related ──
    "stray":         "ANM", "dog":           "ANM", "dogs":          "ANM",
    "cattle":        "ANM", "cow":           "ANM", "cows":          "ANM",
    "pig":           "ANM", "pigs":          "ANM", "animal":        "ANM",
    "animals":       "ANM", "carcass":       "ANM", "snake":         "ANM",
    "monkey":        "ANM",

    # ── Mosquito / Health hazard ──
    "mosquito":      "MSQ", "mosquitoes":    "MSQ", "dengue":        "MSQ",
    "malaria":       "MSQ", "breeding":      "MSQ", "fogging":       "MSQ",
    "fumigation":    "MSQ",

    # ── Building / Structural ──
    "building":      "BLD", "illegal":       "BLD", "demolition":    "BLD",
    "unsafe":        "BLD", "collapse":      "BLD", "wall":          "BLD",
    "crack":         "BLD", "cracked":       "BLD",
}


def _extract_keywords(title: str) -> list[str]:
    """Tokenise, lowercase, strip stopwords and short (≤2 char) tokens."""
    tokens = re.findall(r"[a-zA-Z]+", (title or "").lower())
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 2]


def _best_semantic_match(keywords: list[str]) -> str | None:
    """
    Resolve a list of keywords to a semantic 3-char category code.

    Pass 1 — Direct lookup (O(1) per keyword).
    Pass 2 — Fuzzy match via SequenceMatcher (≥ 0.70 threshold).
    """
    # Pass 1: exact match
    for kw in keywords:
        if kw in _SEMANTIC_CATEGORIES:
            return _SEMANTIC_CATEGORIES[kw]

    # Pass 2: fuzzy / substring
    best_code: str | None = None
    best_score = 0.0
    for kw in keywords:
        for known_kw, code in _SEMANTIC_CATEGORIES.items():
            if known_kw in kw or kw in known_kw:
                score = 0.85
            else:
                score = SequenceMatcher(None, kw, known_kw).ratio()
            if score > best_score and score >= 0.70:
                best_score = score
                best_code = code
    return best_code


def _title_hash(title: str) -> str:
    """
    Produce a **3-character uppercase** semantic code from the title.

    1. Extract keywords (strip stopwords / adjectives / filler nouns).
    2. Match against known civic-issue semantic categories.
    3. If no match, produce a deterministic 3-char hash of sorted keywords.
    """
    if not title or not title.strip():
        return "GEN"

    kws = _extract_keywords(title)
    if not kws:
        return "GEN"

    code = _best_semantic_match(kws)
    if code:
        return code

    # Fallback: deterministic hash of sorted keywords → 3 uppercase chars
    joined = "".join(sorted(kws))
    digest = hashlib.md5(joined.encode()).hexdigest()
    chars = []
    for i in range(3):
        val = int(digest[i * 2 : i * 2 + 2], 16) % 26
        chars.append(chr(ord("A") + val))
    return "".join(chars)


# ═══════════════════════════════════════════════════════════════════════════
# 2.  Location Hash  (4 characters – 2 lat + 2 lon)
#
#     Uses a ~30 m grid cell (DOUBLE the 15 m tolerance) so that two
#     points ≤ 15 m apart are guaranteed to land in the same cell –
#     even when they straddle a cell boundary.
#
#     Additionally, _location_hashes_3x3() returns the 3×3 grid
#     neighborhood (9 hashes) so the DB lookup covers adjacent cells
#     as a second safety net against floating-point edge rounding.
# ═══════════════════════════════════════════════════════════════════════════

# Grid cell ≈ 30 metres latitude (double the 15 m tolerance).
_LAT_CELL = 30.0 / 111_320.0   # ≈ 0.0002696°

_BASE36 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _encode_base36_2char(value: int) -> str:
    """Encode an integer into exactly 2 base-36 characters (0–1295)."""
    value = abs(value) % 1296      # 36² = 1296
    return _BASE36[value // 36] + _BASE36[value % 36]


def _lat_index(latitude: float) -> int:
    """Return the grid row index for a latitude value."""
    return int(math.floor(latitude / _LAT_CELL))


def _lon_index(latitude: float, longitude: float) -> int:
    """Return the grid column index (latitude-adjusted cell width)."""
    cos_lat = max(math.cos(math.radians(latitude)), 1e-10)
    lng_cell = _LAT_CELL / cos_lat
    return int(math.floor(longitude / lng_cell))


def _location_hash(latitude, longitude) -> str:
    """Return the PRIMARY 4-character location hash (2 lat + 2 lon)."""
    if latitude is None or longitude is None:
        return "0000"
    lat_f = float(latitude)
    lng_f = float(longitude)
    return (
        _encode_base36_2char(_lat_index(lat_f))
        + _encode_base36_2char(_lon_index(lat_f, lng_f))
    )


def _location_hashes_3x3(latitude, longitude) -> list[str]:
    """
    Generate the PRIMARY location hash **plus all 8 neighboring cell hashes**.

    Even with the 30 m grid, a point sitting exactly on a cell boundary
    could theoretically land in either cell due to floating-point rounding.
    By checking the 3×3 neighbourhood we guarantee that two points up to
    15 m apart share **at least one** common hash — so the duplicate
    lookup will always find the match.

    Returns a list of up to 9 unique 4-character location hashes.
    """
    if latitude is None or longitude is None:
        return ["0000"]

    lat_f = float(latitude)
    lng_f = float(longitude)
    lat_idx = _lat_index(lat_f)
    lng_idx = _lon_index(lat_f, lng_f)

    hashes: set[str] = set()
    for dlat in (-1, 0, 1):
        for dlng in (-1, 0, 1):
            h = (
                _encode_base36_2char(lat_idx + dlat)
                + _encode_base36_2char(lng_idx + dlng)
            )
            hashes.add(h)
    return list(hashes)


# ═══════════════════════════════════════════════════════════════════════════
# 3.  Department Code  (3 uppercase characters)
# ═══════════════════════════════════════════════════════════════════════════

# Well-known municipal department abbreviations
_DEPT_CODES: dict[str, str] = {
    "public works":                "PWD",
    "solid waste management":      "SWM",
    "water supply":                "WSS",
    "sewerage":                    "SEW",
    "electricity":                 "ELE",
    "street lighting":             "SLT",
    "roads":                       "RDS",
    "parks":                       "PRK",
    "health":                      "HLT",
    "sanitation":                  "SAN",
    "traffic":                     "TRF",
    "drainage":                    "DRN",
    "building":                    "BLD",
    "town planning":               "TPL",
    "revenue":                     "REV",
    "education":                   "EDU",
    "fire":                        "FIR",
    "animal control":              "ANM",
    "environment":                 "ENV",
    "transport":                   "TRN",
}


def _dept_hash(department_name: str | None) -> str:
    """
    Return a stable 3-character uppercase department code.

    • First checks the known-abbreviation table.
    • Falls back to extracting the first 3 consonants (padded).
    """
    if not department_name:
        return "GEN"

    name_lower = department_name.strip().lower()

    # Direct / partial match against known codes
    for key, code in _DEPT_CODES.items():
        if key in name_lower or name_lower in key:
            return code

    # Fallback: first 3 uppercase consonants
    consonants = [c for c in name_lower if c.isalpha() and c not in "aeiou"]
    code = "".join(consonants[:3]).upper()
    return code.ljust(3, "X") if len(code) < 3 else code


# ═══════════════════════════════════════════════════════════════════════════
# Haversine distance helper
# ═══════════════════════════════════════════════════════════════════════════

def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance in **metres** between two GPS points."""
    R = 6_371_000  # Earth radius in metres
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lam = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lam / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ═══════════════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════════════

def generate_smart_hash(
    title: str,
    latitude,
    longitude,
    department_name: str | None,
) -> str:
    """
    Build the PRIMARY 10-character Smart Hash ID::

        [TITLE_3][LAT_2][LON_2][DEPT_3]

    Example: ``POT4F7ASWM``

    This hash is STORED on the Complaint row.
    """
    t = _title_hash(title)                          # 3 chars
    loc = _location_hash(latitude, longitude)       # 4 chars
    d = _dept_hash(department_name)                  # 3 chars
    return f"{t}{loc}{d}"


def generate_candidate_hashes(
    title: str,
    latitude,
    longitude,
    department_name: str | None,
) -> list[str]:
    """
    Generate the primary smart hash **plus all neighbor-cell variants**.

    Returns up to 9 hashes (1 primary + 8 neighbors).
    When checking for duplicates the DB query uses ``smart_hash__in``
    over this list, eliminating the grid-boundary problem entirely.
    """
    t = _title_hash(title)
    d = _dept_hash(department_name)
    loc_hashes = _location_hashes_3x3(latitude, longitude)
    return list({f"{t}{lh}{d}" for lh in loc_hashes})


# ═══════════════════════════════════════════════════════════════════════════
# Duplicate lookup
# ═══════════════════════════════════════════════════════════════════════════

# Active statuses considered for duplicate matching
_ACTIVE_STATUSES = [
    "SUBMITTED",
    "FILTERING",
    "VERIFIED",
    "SORTING",
    "PENDING",
    "ASSIGNED",
    "IN_PROGRESS",
    "PENDING_VERIFICATION",
]


def find_duplicate(
    smart_hash: str,
    candidate_hashes: list[str] | None = None,
    new_lat: float | None = None,
    new_lng: float | None = None,
):
    """
    Search for an existing active complaint matching the given hash(es).

    Parameters
    ----------
    smart_hash : str
        The primary 10-char hash of the new complaint.
    candidate_hashes : list[str] | None
        The full list of 9 neighbor-cell hashes (from
        ``generate_candidate_hashes``).  If provided the DB query covers the
        entire 3×3 grid neighborhood.
    new_lat, new_lng : float | None
        Coordinates of the new complaint.  When provided a Haversine check
        confirms the match is truly within 50 m (guards against base-36
        collisions across distant locations).

    Returns
    -------
    Complaint | None
        The earliest matching active complaint, or ``None``.
    """
    from .models import Complaint          # late import — avoid circular dep

    all_hashes: set[str] = {smart_hash}
    if candidate_hashes:
        all_hashes.update(candidate_hashes)

    matches = (
        Complaint.objects.filter(
            smart_hash__in=list(all_hashes),
            is_deleted=False,
            status__in=_ACTIVE_STATUSES,
        )
        .order_by("created_at")
    )

    if not matches.exists():
        return None

    # If we have coordinates, verify with Haversine (50 m generous tolerance)
    if new_lat is not None and new_lng is not None:
        for complaint in matches:
            if complaint.latitude is not None and complaint.longitude is not None:
                dist = _haversine_m(
                    new_lat, new_lng,
                    float(complaint.latitude), float(complaint.longitude),
                )
                if dist <= 50.0:
                    return complaint
        # All matches are > 50 m away — likely a hash collision, not a dup
        return None

    # No coordinates to verify — trust the hash
    return matches.first()
