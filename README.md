# Reliable Shop Reply Assistant

A small Python app that reads a customer message and drafts a polite reply
using the Gemini API. It uses only the shop information provided in the code,
and it is built to keep working when things go wrong.

## What it does
- Takes a customer message and returns an AI-written reply
- **Logging:** records events and errors to `app.log`
- **Retry logic:** retries temporary API failures (429, 500, 503, 504)
  up to 3 times, waiting 1 and then 2 seconds between tries
- **Edge cases:** rejects empty or too-long messages, handles a missing
  API key, and shows a fallback message if Gemini returns no text
- **Tests:** automated pytest tests that use fake clients (no real API calls)

## Bugs found and fixed
1. **AI invented shop facts.** It said "yes" to Sunday delivery with no
   information. Fixed by adding shop details to the prompt and telling the
   model not to guess.
2. **Empty input was sent to the API.** Fixed with input validation before
   the API call.
3. **Empty AI replies printed as `None`.** Fixed with a fallback message.

Details are in `BUGS.md`.

## How to run

1. Install Python 3 and clone this repo.
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install the libraries:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and put in your Gemini API key
   (free from Google AI Studio).
5. Start the app:
   ```
   python reliable_AI_app.py
   ```

## How to run the tests
```
python -m pytest -v
```
Result when I ran it: [write your real summary line, e.g. "18 passed"]

## Notes
- Edit `SHOP_INFO` in `reliable_AI_app.py` to match your own shop.
- Never commit your `.env` file.