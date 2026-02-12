import os
import google.generativeai as genai
import time


class DocGenerationAgent:
    def __init__(self, model_name="gemini-2.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY missing")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate(self, metadata: dict, ext: str) -> str:
        name = metadata.get("name")
        args = metadata.get("args", [])
        returns = metadata.get("returns", "None")

        style = "Google Style" if ext == ".py" else "JSDoc"

        prompt = f"""
You are a senior software documentation engineer.

Generate a concise and accurate {style} documentation block.

FUNCTION METADATA:
- Name: {name}
- Arguments: {args}
- Returns: {returns}

Rules:
- Do NOT invent parameters.
- If arguments exist, include an Args section.
- If return is not None, include a Returns section.
- Be concise (<100 words).
- Professional tone.
- Return ONLY raw docstring text.
"""

        try:
            time.sleep(1)
            response = self.model.generate_content(prompt)
            return response.text.strip().replace('"""', '').replace('/**', '').replace('*/', '')
        except:
            return "Auto-generated documentation."
