# Bug Notebook
## Suspicious spots
## Bug #1: AI invented shop facts
- Before: said "Yes, we offer Sunday delivery" with no information
- Cause: prompt had no shop facts and no "don't guess" rule
- Fix: added SHOP_INFO and a "use only this information" instruction
- Result: (write what you saw in Test 3 and Test 4)

## Bug #2: Empty input sent to the API
- Before: ...
- Fix: validate_message() ...

## Bug #3: Empty AI reply printed as "None"
- Fix: FALLBACK_REPLY ...
## Confirmed bug candidate
- AI invents shop facts (said "yes" to Sunday delivery without knowing). Fix idea: give the prompt real shop info and tell it not to guess.