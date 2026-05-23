from groq import Groq
from openai import OpenAI

from config_runtime import GROQ_API_KEY, OPENAI_API_KEY, logger

GROQ_GPT_MODEL = "openai/gpt-oss-120b"
OPENAI_GPT_MODEL = "gpt-4o"

groq_client = Groq(api_key=GROQ_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def chat_completion_request(messages):
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_GPT_MODEL,
            messages=messages,
            max_tokens=500,
        )
        return response
    except Exception as exc:
        logger.warning("Groq chat failed, falling back to OpenAI: %s", exc)
        response = openai_client.chat.completions.create(
            model=OPENAI_GPT_MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.3,
        )
        return response


def safe_chat_content(messages, *, fallback_text='Something broke on my end. Try again in a minute.'):
    try:
        chat_response = chat_completion_request(messages)
        return chat_response.choices[0].message.content
    except Exception as exc:
        logger.exception("Chat completion failed: %s", exc)
        return fallback_text
