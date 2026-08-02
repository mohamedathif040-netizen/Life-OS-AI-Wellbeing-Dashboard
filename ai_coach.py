import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def get_ai_coaching(summary):
    prompt = f"""
You are Life-OS, an honest but supportive productivity coach.

Today's screen-time summary:

{summary}

Analyze:

1. Overall digital habits.
2. Biggest distraction.
3. Positive habits.
4. Three practical real-world activities to replace excessive screen time.
5. End with one motivational sentence.

Keep the response under 250 words.
Use Markdown formatting.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return response.text

def get_avatar_prompt(summary):
    prompt = f"""
You are an AI that creates short image prompts.

Based on this screen-time summary:

{summary}

Rules:
- If screen time is excessive, create a prompt showing someone wasting time on a phone.
- If screen time is balanced, create a prompt showing a productive, healthy person.
- Keep the prompt under 30 words.
- Return ONLY the image prompt.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return response.text.strip()