from google import genai
from google.genai import types
import streamlit as st
from PIL import Image

def generate_with_gemini(
    prompt,
    context_data=None,
    aspect_ratio="16:9",
    image_size="4K"
):
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        st.error("GOOGLE_API_KEY missing")
        return None

    client = genai.Client(api_key=api_key)

    full_prompt = f"""
Create a professional economic visualization for India Economic Pulse.

User request:
{prompt}

Use ONLY this data context:
{context_data}

Design:
- Indian tricolor theme
- Clean infographic
- Professional
"""

    try:
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                tools=[{"google_search": {}}],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=image_size
                )
            )
        )

        image_parts = [p for p in response.parts if p.inline_data]
        if not image_parts:
            return None

        return image_parts[0].as_image()

    except Exception as e:
        st.error(f"Gemini error: {e}")
        return None
