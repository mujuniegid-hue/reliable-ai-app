import os
import time
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
MAX_ATTEMPTS = 3
BASE_DELAY_SECONDS = 1
RETRYABLE_CODES = {429, 500, 503, 504}

client = genai.Client(api_key=api_key)


def call_with_retry(make_request, max_attempts=MAX_ATTEMPTS, base_delay=BASE_DELAY_SECONDS):
    for attempt in range(1, max_attempts + 1):
        try:
            return make_request()
        except Exception as error:
            code = getattr(error, "code", None)
            retryable = code in RETRYABLE_CODES or code is None

            if not retryable or attempt == max_attempts:
                logger.error("Request failed (attempt %d of %d): %s", attempt, max_attempts, error)
                raise

            wait_time = base_delay * (2 ** (attempt - 1))
            logger.warning(
                "Attempt %d of %d failed (code: %s). Retrying in %d seconds...",
                attempt, max_attempts, code, wait_time,
            )
            time.sleep(wait_time)


def ask_gemini(customer_message):
    prompt = (
        "You are a polite assistant for a small shop. "
        "Reply briefly and helpfully to this customer message:\n\n"
        f"{customer_message}"
    )
    logger.info("Sending request to Gemini (message length: %d)", len(customer_message))

    response = call_with_retry(
        lambda: client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
    )

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