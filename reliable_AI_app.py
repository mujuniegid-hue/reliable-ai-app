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

MODEL_NAME = "gemini-3.5-flash-lite"
MAX_ATTEMPTS = 3
BASE_DELAY_SECONDS = 1
RETRYABLE_CODES = {429, 500, 503, 504}
MAX_MESSAGE_LENGTH = 1000
FALLBACK_REPLY = (
    "Sorry, I couldn't prepare a reply right now. "
    "Please contact the shop directly."
)

# Edit these facts so they match your (real or pretend) shop.
SHOP_INFO = """
Shop name: HamTech Store
Opening hours: Monday to Saturday, 8am to 6pm. Closed on Sundays.
Delivery: Monday to Saturday only. No Sunday delivery.
Payment: Cash and mobile money.
"""


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY is missing")
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file.")
    return genai.Client(api_key=api_key)


def validate_message(message):
    if message is None or not message.strip():
        logger.warning("Rejected empty message")
        raise ValueError("The message is empty. Please type something.")

    message = message.strip()

    if len(message) > MAX_MESSAGE_LENGTH:
        logger.warning("Rejected message that was too long (%d characters)", len(message))
        raise ValueError(
            f"The message is too long. Please keep it under {MAX_MESSAGE_LENGTH} characters."
        )

    return message


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
    customer_message = validate_message(customer_message)

    prompt = (
        "You are a polite assistant for a small shop. "
        "Use ONLY the shop information below to answer. "
        "If the answer is not in the shop information, say you are not sure "
        "and suggest the customer contact the shop directly. Never guess.\n\n"
        f"SHOP INFORMATION:\n{SHOP_INFO}\n"
        f"CUSTOMER MESSAGE:\n{customer_message}"
    )

    client = get_client()
    logger.info("Sending request to Gemini (message length: %d)", len(customer_message))

    response = call_with_retry(
        lambda: client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
    )

    reply = response.text
    if not reply or not reply.strip():
        logger.warning("Gemini returned an empty reply; using fallback")
        return FALLBACK_REPLY

    logger.info("Reply received (length: %d)", len(reply))
    return reply


def main():
    logger.info("App started")
    customer_message = input("Customer message: ")

    try:
        reply = ask_gemini(customer_message)
    except ValueError as error:
        print(f"\nInput problem: {error}")
        return
    except RuntimeError as error:
        print(f"\nSetup problem: {error}")
        return
    except Exception:
        print("\nSorry, something went wrong. Please try again later.")
        return

    print("\nAI reply:")
    print(reply)


if __name__ == "__main__":
    main()