"""
Filter B: AI-Assisted Complaint Authenticity & Intelligence Classification
Uses Gemini Vision API to:
  1. Verify whether the submitted image supports the complaint description.
  2. Dynamically determine SLA hours based on severity.
  3. Assign a priority level (1-5).
  4. Flag emergencies for immediate attention.

NOTE: AI is used as a classification assistant, not a sole decision-maker.
All AI decisions are logged for transparency and audit.
"""

import json
import logging
from google import genai
from google.genai import types
from django.conf import settings
from PIL import Image

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default / fallback values when structured parsing fails
# ---------------------------------------------------------------------------
_DEFAULTS = {
    'genuine': 'YES',
    'sla_hours': 48,
    'priority': 1,
    'emergency': False,
}


def classify_complaint(image_path: str, description: str) -> dict:
    """
    AI-assisted verification **and** severity classification of a complaint.

    Sends the complaint image + description to Gemini Vision and asks it to
    return a structured JSON object with genuineness, SLA, priority, and
    emergency flag.

    Returns:
        dict with keys:
            genuine   (str)  – 'YES' or 'NO'
            sla_hours (int)  – recommended SLA in hours (2-48)
            priority  (int)  – 1=Minimal, 2=Low, 3=Medium, 4=High, 5=Emergency
            emergency (bool) – True when immediate attention is needed

    Raises:
        Exception – caller must handle and apply fail-safe logic
    """
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    image = Image.open(image_path)

    prompt = f"""
You are a STRICT authenticity checker AND severity classifier for CivicSaathi, a Smart City civic complaints platform.

Your job is TWO-FOLD:
  A) Decide whether the image is a legitimate photo of a real, visible civic infrastructure problem.
  B) If genuine, assess HOW SEVERE the issue is and recommend SLA / priority.

=== COMPLAINT DESCRIPTION ===
"{description}"

=== THE 14 VALID MUNICIPAL DEPARTMENTS AND THEIR ACCEPTED ISSUE TYPES ===
1. Engineering / Public Works Department (Urban)
   - Potholes, broken/damaged roads, caved-in footpaths, damaged bridges, collapsed walls/fencing, construction debris blocking roads
2. Solid Waste Management Department
   - Overflowing or damaged dustbins, uncleared garbage heaps, illegal dumping sites, scattered waste on roads/public areas
3. Municipal Health Department
   - Dead animals on roads, public health hazards, disease outbreak sites, unhygienic conditions in public spaces
4. Electrical / Street Lighting Department
   - Broken or non-functional street lights, exposed/dangling electrical wires, damaged electrical poles/boxes
5. Water Supply & Sewerage Department
   - Burst/leaking water pipes, contaminated water supply, overflowing water tanks, sewage leak/mixing with drinking water
6. Drainage / Storm Water Department
   - Blocked/clogged drains, waterlogged roads or streets, overflowing stormwater drains, broken drain covers
7. Sanitation & Public Toilet Department
   - Damaged, dirty, or non-functional public toilets, open defecation areas, blocked/overflowing public sewage
8. Municipal Enforcement / Vigilance Department
   - Illegal encroachments on roads or footpaths, unauthorized hoardings/banners, illegal constructions on public land
9. Animal Husbandry / Cattle Nuisance Department
   - Stray cattle/livestock on roads, injured or dead stray animals blocking public areas
10. Municipal HR / Establishment Department
    - Municipal staff misbehaviour at public service points (photo evidence required)
11. IT / e-Governance Department
    - Damaged or non-functional government digital kiosks, broken e-governance service terminals
12. Finance & Accounts Department
    - Publicly visible fraudulent notices/boards by municipal bodies
13. Swachh Bharat Mission (Urban)
    - Open defecation, public urination areas, extremely filthy public spaces
14. Smart City SPV
    - Damaged smart city infrastructure: broken sensors, non-functional smart benches/lights/bus shelters

=== HARD REJECT — genuine = "NO" FOR ANY OF THESE ===
- Human faces, selfies, portraits, or photos where a person is the main subject
- Animals that are pets or indoor animals (not stray cattle on public roads)
- Food, beverages, or kitchen/household items
- Indoor rooms, homes, offices, private property interiors
- Personal belongings: phones, wallets, clothes, vehicles (unless the vehicle is blocking a public road)
- Screenshots, memes, digital artwork, documents, or text-only images
- Nature scenes with no civic infrastructure (forests, mountains, empty fields)
- Images that are blurry, pitch-black, or contain no identifiable subject
- Any image where the civic problem described is NOT CLEARLY VISIBLE
- Any image unrelated to the 14 departments listed above

=== GENUINENESS RULES ===
1. The image MUST clearly and visibly show the civic infrastructure problem described.
2. The problem MUST fall under one of the 14 departments listed above.
3. If the image shows a person as the main subject (even near a civic issue) → NO
4. If you cannot clearly see the reported civic problem → NO
5. If there is any reasonable doubt → NO
6. If both rules 1 and 2 are satisfied → YES

=== SEVERITY / SLA LOGIC (only when genuine = "YES") ===
Use the following guidelines to set sla_hours and priority:

🚨 EMERGENCY (priority 5, sla_hours 2-6, emergency true):
   - Live / exposed electrical wires on public roads
   - Major water main burst flooding a road
   - Road cave-in / sinkhole posing immediate accident risk
   - Sewage overflow contaminating drinking water supply
   - Collapsed bridge or wall on a public path
   - Any situation posing immediate risk to life or limb

⚠️ HIGH (priority 4, sla_hours 8-24):
   - Large pothole on a highway / major road
   - Sewage overflow on a residential street
   - Broken drain cover on a busy footpath (fall hazard)
   - Dangling street-light pole about to fall
   - Stray cattle herd blocking a main road

🟡 MEDIUM (priority 3, sla_hours 24-36):
   - Street light not working in a residential area
   - Overflowing dustbin in a market area
   - Blocked storm-water drain (not yet flooding)
   - Damaged public toilet

🟢 LOW (priority 2, sla_hours 36-48):
   - Minor garbage accumulation on a side street
   - Faded road markings or signage
   - Slightly damaged park bench

⚪ MINIMAL (priority 1, sla_hours 48):
   - Cosmetic issues, very low public impact
   - Anything not fitting the higher categories

=== OUTPUT FORMAT ===
You MUST respond with ONLY a valid JSON object — no markdown fences, no explanation, no extra text.
When genuine is "NO", set sla_hours to 48, priority to 1, emergency to false.
Example:
{{"genuine": "YES", "sla_hours": 6, "priority": 5, "emergency": true}}
{{"genuine": "NO", "sla_hours": 48, "priority": 1, "emergency": false}}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[image, prompt],
    )
    raw = response.text.strip()

    # ── Parse structured JSON response ────────────────────────────────────
    return _parse_ai_response(raw)


def _parse_ai_response(raw: str) -> dict:
    """Parse Gemini's raw text into a validated classification dict."""
    # Strip potential markdown code fences
    cleaned = raw.strip()
    if cleaned.startswith('```'):
        cleaned = cleaned.split('\n', 1)[-1]  # remove first line
    if cleaned.endswith('```'):
        cleaned = cleaned.rsplit('```', 1)[0]
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: try to detect YES / NO from the raw text
        upper = raw.upper()
        if upper.startswith('NO'):
            return {'genuine': 'NO', 'sla_hours': 48, 'priority': 1, 'emergency': False}
        if upper.startswith('YES'):
            return {**_DEFAULTS, 'genuine': 'YES'}
        raise ValueError(f"Gemini returned unparseable response: {raw!r}")

    # Normalise fields with safe defaults
    genuine = str(data.get('genuine', 'YES')).upper().strip()
    if genuine not in ('YES', 'NO'):
        genuine = 'YES' if 'YES' in genuine else 'NO'

    sla_hours = int(data.get('sla_hours', 48))
    sla_hours = max(2, min(sla_hours, 48))  # clamp 2-48

    priority = int(data.get('priority', 1))
    priority = max(1, min(priority, 5))  # clamp 1-5

    emergency = bool(data.get('emergency', False))

    return {
        'genuine': genuine,
        'sla_hours': sla_hours,
        'priority': priority,
        'emergency': emergency,
    }


# ---------------------------------------------------------------------------
# Backward-compatible wrapper (used by existing callers before migration)
# ---------------------------------------------------------------------------
def is_complaint_genuine(image_path: str, description: str) -> bool:
    """Legacy wrapper — returns True/False only. Prefer classify_complaint()."""
    result = classify_complaint(image_path, description)
    return result['genuine'] == 'YES'
