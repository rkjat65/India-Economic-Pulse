import openai
import anthropic
from google import genai

def build_data_context(data):
    text = []

    if "gdp" in data:
        df = data["gdp"]
        text.append(f"GDP latest: {df.iloc[-1]['GDP_growth']}%")

    # add more context
    
    return "\n".join(text)

SYSTEM_PROMPT = """
You are an economic data assistant.
Only answer using the provided data context.
If not available in the data, reply: Data not available.
"""

def handle_chat_query(model, query, data):
    context = build_data_context(data)
    prompt = f"{SYSTEM_PROMPT}\nContext:\n{context}\n\nQ: {query}\nA:"
    
    if model == "OpenAI DALL·E" or model == "OpenAI":
        openai.api_key = st.secrets.get("OPENAI_API_KEY", "")
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content

    if model == "Gemini":
        client = genai.Client(api_key=st.secrets.get("GOOGLE_API_KEY", ""))
        resp = client.models.generate_text(model="gemini-pro", contents=prompt)
        return resp.text or "No answer from Gemini."

    if model == "Claude":
        client = anthropic.Anthropic(api_key=st.secrets.get("ANTHROPIC_API_KEY", ""))
        resp = client.completions.create(
            model="claude-3.5-sonnet",
            prompt=prompt,
            max_tokens=150,
        )
        return resp["completion"]

    return "Model not supported."
