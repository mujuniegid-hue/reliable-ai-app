import os
from dotenv import load_dotenv
from google import genai

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
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    return response.text


def main():
    customer_message = input("Customer message: ")
    reply = ask_gemini(customer_message)
    print("\nAI reply:")
    print(reply)


if __name__ == "__main__":
    main()