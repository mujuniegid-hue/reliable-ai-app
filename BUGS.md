# Bug Notebook
## Suspicious spots
- App printed nothing at first (no real code yet)
- No check for empty input
- No check for missing API key
- No handling if the API call fails or times out
- response.text might be empty or None
## Confirmed bug candidate
- AI invents shop facts (said "yes" to Sunday delivery without knowing). Fix idea: give the prompt real shop info and tell it not to guess.