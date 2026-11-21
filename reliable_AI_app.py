import os
import logging
from dotenv import load_dotenv
from google import genai

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

MODEL_NAME = "gemini-3.5-flash-lite"

client = genai.Client(api_key=api_key)


def ask_gemini(customer_message):
    prompt = (
        "You are a polite assistant for a small shop. "
        "Reply briefly and helpfully to this customer message:\n\n"
        f"{customer_message}"
    )
    logger.info("Sending request to Gemini (message length: %d)", len(customer_message))
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
    except Exception as error:
        logger.error("Gemini request failed: %s", error)
        raise

    reply = response.text
    logger.info("Reply received (length: %d)", len(reply) if reply else 0)
    return reply


def main():
    logger.info("App started")
    customer_message = input("Customer message: ")
    reply = ask_gemini(customer_message)
    print("\nAI reply:")
    print(reply)


if __name__ == "__main__":
    main()