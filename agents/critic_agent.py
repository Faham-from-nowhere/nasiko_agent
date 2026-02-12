import os
import time
import json
import re
import google.generativeai as genai


class CriticAgent:
    """
    Hybrid Docstring Validation Agent.

    Layer 1: Deterministic rule-based validation.
    Layer 2: AI-based semantic and stylistic critique.
    Layer 3: Auto-refinement loop (optional external trigger).
    """

    def __init__(self, model_name="gemini-2.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY environment variable is missing!")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    # ===============================
    # 1️⃣ RULE-BASED VALIDATION
    # ===============================
    def rule_based_check(self, docstring: str, metadata: dict) -> tuple[bool, str]:
        if not docstring.strip():
            return False, "Docstring is empty."

        args = metadata.get("args", [])
        returns = metadata.get("returns")

        # Check Args section exists if arguments exist
        if args:
            if "Args:" not in docstring:
                return False, "Missing 'Args:' section."

            for arg in args:
                if re.search(rf"\b{re.escape(arg)}\b", docstring) is None:
                    return False, f"Argument '{arg}' not documented."

        # Check Returns section if return annotation exists
        if returns and returns != "None":
            if "Returns:" not in docstring:
                return False, "Missing 'Returns:' section."

        return True, "Rule-based validation passed."

    # ===============================
    # 2️⃣ AI VALIDATION
    # ===============================
    def ai_critique(self, docstring: str, metadata: dict) -> tuple[bool, str]:
        prompt = f"""
You are a strict senior software reviewer.

Evaluate the following docstring.

METADATA:
- Function Name: {metadata.get('name')}
- Args: {metadata.get('args')}
- Returns: {metadata.get('returns')}

DOCSTRING:
{docstring}

Evaluate:
1. Is the summary clear and specific?
2. Does it logically match the function name?
3. Is it professional and concise?
4. Does it follow Google Style?

Respond ONLY in valid JSON:
{{
  "status": "PASS" or "FAIL",
  "reason": "brief explanation"
}}
"""

        try:
            time.sleep(1)
            response = self.model.generate_content(prompt)
            text = response.text.strip()

            # Extract JSON safely
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if not json_match:
                return False, "AI response malformed."

            parsed = json.loads(json_match.group())

            if parsed.get("status") == "PASS":
                return True, "AI validation passed."
            else:
                return False, parsed.get("reason", "AI critique failed.")

        except Exception as e:
            return False, f"AI validation error: {str(e)}"

    # ===============================
    # 3️⃣ FULL VALIDATION PIPELINE
    # ===============================
    def critique(self, docstring: str, metadata: dict) -> tuple[bool, str]:
        # Step 1: Rule-based validation
        rule_pass, rule_msg = self.rule_based_check(docstring, metadata)
        if not rule_pass:
            return False, f"Rule Failure: {rule_msg}"

        # Step 2: AI validation
        ai_pass, ai_msg = self.ai_critique(docstring, metadata)
        if not ai_pass:
            return False, f"AI Failure: {ai_msg}"

        return True, "Docstring fully validated."

    # ===============================
    # 4️⃣ AUTO-REFINEMENT LOOP
    # ===============================
    def refine(self, docstring: str, metadata: dict, feedback: str) -> str:
        """
        Ask AI to fix docstring based on critique feedback.
        """
        prompt = f"""
You previously generated this docstring:

{docstring}

It failed validation for this reason:
{feedback}

Fix the docstring while following Google Style strictly.
Return ONLY the corrected docstring text.
"""

        try:
            time.sleep(1)
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return docstring  # Fallback: return original if refinement fails
