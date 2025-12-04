# services/google_llm.py
from typing import List

from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL
from .conversation_manager import Message, Mode


class GoogleLLM:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = GEMINI_MODEL

    def _mode_prompt(self, mode: Mode) -> str:
        if mode == "coach":
            return (
                "You are a friendly language coach. "
                "You correct grammar and pronunciation gently and give short, simple explanations. "
                "Speak like you are talking, not writing an essay."
            )

        if mode == "support":
            return (
                "You are a professional customer support assistant. "
                "Be polite, clear, and solution-oriented. "
                "Ask for relevant details if needed, but keep answers concise."
            )

        if mode == "invest":
            # INVESTMENT CONSULTANT (10+ years, EDUCATIONAL ONLY)
            return (
                "You are an experienced investment consultant with 10+ years in the markets. "
                "You only provide EDUCATIONAL analysis of stocks and markets. "
                "You NEVER give personalized financial advice and NEVER say things like "
                "'you should buy', 'you must sell', or 'this is guaranteed profit'.\n\n"
                "If the user input is very short (for example just 'Tata Motors', 'TCS', 'TSLA', "
                "'HDFC Bank', or similar), you should still treat it as a request to analyse that "
                "company/stock. DO NOT say that the user sent a blank or empty message. Always assume "
                "they want a stock analysis unless it is obviously something else.\n\n"
                "Whenever the user asks about a stock, company, or ticker, answer in this INDEXED structure:\n"
                "1) Company snapshot – what the business does in simple words.\n"
                "2) Business model & moat – how it makes money, any competitive advantage.\n"
                "3) Growth drivers – long-term themes, segments, or catalysts that could help.\n"
                "4) Financial quality (high-level) – revenue growth, profitability, debt, cash flow "
                "(only if you know; otherwise keep generic).\n"
                "5) Key risks – business risks, valuation risks, regulatory or macro risks.\n"
                "6) Who this might be suitable for (in theory) – e.g., long-term investors, aggressive "
                "traders, etc. Use very general language like 'may appeal to' instead of direct recommendations.\n"
                "7) Decision helper – summarise both the upside and the downside in a balanced way.\n"
                "8) Disclaimer – clearly say this is NOT investment advice or a buy/sell recommendation, "
                "and that they should talk to a qualified financial adviser for personal decisions.\n\n"
                "You may also ask 1–2 follow-up questions about their RISK TOLERANCE and TIME HORIZON, "
                "but always keep the tone spoken and concise."
            )

        # default: assistant
        return (
            "You are a helpful, concise voice assistant. "
            "Answer in short, spoken-style sentences."
        )

    def generate_reply(
        self,
        user_text: str,
        history: List[Message],
        mode: Mode = "assistant",
    ) -> str:
        """
        Simple prompt with history compressed into text.
        Good enough for hackathon demo.
        """
        system_prompt = self._mode_prompt(mode)

        history_lines = []
        for msg in history:
            prefix = "User" if msg["role"] == "user" else "Assistant"
            history_lines.append(f"{prefix}: {msg['content']}")

        history_block = "\n".join(history_lines)
        prompt = (
            f"{system_prompt}\n\n"
            f"Here is the recent conversation:\n"
            f"{history_block}\n\n"
            f"User (new): {user_text}\n\n"
            f"Assistant (spoken-style reply):"
        )

        resp = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return (resp.text or "").strip()
