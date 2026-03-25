import requests
from io import BytesIO
from PIL import Image as PILImage

from .ai_utils import ensure_pil_image, add_watermark, generate_social_caption

def handle_image_generation(model, prompt, data, aspect_ratio="16:9", quality="4K"):
    combined_context = f"Data context:\n{data.get('gdp','')}"
    full_prompt = f"{combined_context}\nUser prompt: {prompt}"

    if model == "OpenAI DALL·E" or model == "OpenAI":
        openai.api_key = st.secrets.get("OPENAI_API_KEY", "")
        resp = openai.Image.create(
            prompt=full_prompt,
            n=1,
            size="1024x1024"
        )
        url = resp["data"][0]["url"]
        img_bytes = requests.get(url).content
        img = ensure_pil_image(img_bytes)

    elif model == "Gemini":
        client = genai.Client(api_key=st.secrets.get("GOOGLE_API_KEY",""))
        resp = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                image_config=types.ImageConfig(aspect_ratio=aspect_ratio, image_size=quality)
            )
        )
        parts = [p for p in resp.parts if p.inline_data]
        img = ensure_pil_image(parts[0].inline_data.data) if parts else None

    else:
        img = None

    if img:
        img = add_watermark(img, "@rkjat65")
        caption = generate_social_caption(prompt, model)
    else:
        caption = ""

    return img, caption
