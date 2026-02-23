"""
Filter B: AI-Assisted Complaint Authenticity Verification
Uses Gemini Vision API to check whether the submitted image
visually supports the complaint description.

NOTE: AI is used as a validation assistant, not a sole decision-maker.
All AI decisions are logged for transparency and audit.
"""

import logging
from google import genai
from google.genai import types
from django.conf import settings
from PIL import Image

logger = logging.getLogger(__name__)


def is_complaint_genuine(image_path: str, description: str) -> bool:
    """
    AI-assisted verification of complaint image against description.

    Sends the complaint image and description to Gemini Vision and asks
    whether the image visually matches the reported issue.

    Returns:
        True  → AI considers complaint genuine (image supports description)
        False → AI considers complaint unrelated / misleading

    Raises:
        Exception → caller must handle and apply fail-safe logic
    """
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    image = Image.open(image_path)

    prompt = f"""
You are a STRICT authenticity checker for CivicSaathi, a Smart City civic complaints platform.
Your ONLY job is to decide whether the image is a legitimate photo of a real, visible civic infrastructure problem that falls within municipal jurisdiction.

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

=== HARD REJECT — ANSWER NO FOR ANY OF THESE ===
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

=== DECISION RULES ===
1. The image MUST clearly and visibly show the civic infrastructure problem described.
2. The problem MUST fall under one of the 14 departments listed above.
3. If the image shows a person as the main subject (even near a civic issue) → NO
4. If you cannot clearly see the reported civic problem → NO
5. If there is any reasonable doubt → NO
6. If both rules 1 and 2 are satisfied → YES

You must respond with ONLY one word: YES or NO. No explanation.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[image, prompt],
    )
    answer = response.text.strip().upper()

    # Normalise: treat any "YES" response as genuine
    return answer.startswith("YES")
