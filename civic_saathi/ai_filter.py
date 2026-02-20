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
You are an AI assistant helping validate civic infrastructure complaints for a Smart City platform.
Your role is to SUPPORT human reviewers, not replace them.

Task: Check whether the uploaded IMAGE visually matches the TEXT complaint below.

Complaint description:
"{description}"

Rules:
- If the image clearly shows or relates to the issue described → answer YES
- If the image is irrelevant, unrelated, blank, misleading, or cannot be verified → answer NO
- You must respond with ONLY one word: YES or NO
- Do not provide any explanation.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[image, prompt],
    )
    answer = response.text.strip().upper()

    # Normalise: treat any "YES" response as genuine
    return answer.startswith("YES")
