# AI Product Review Analyzer — Gemini Batch Edition

This clean version fixes the old Gemini SDK configuration and adds batch CSV/paste analysis.

- Modern `google-genai` SDK.
- `GEMINI_API_KEY` loaded explicitly from `backend/.env`.
- Default 25 reviews per Gemini request (`GEMINI_BATCH_SIZE`).
- Retry/backoff for transient Gemini errors.
- Local fallback when Gemini quota/API is unavailable.
- CSV support for common encodings, delimiters, and review column names.
- Reviews remain separate even when sent to Gemini in a batch.

## Windows
Use a normal Windows Python (not MSYS2 Python):
```cmd
"C:\Users\YOURNAME\AppData\Local\Programs\Python\Python313\python.exe" -m venv venv
venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```
Create `backend/.env` with `GEMINI_API_KEY=YOUR_KEY`. Optional: `GEMINI_MODEL` and `GEMINI_BATCH_SIZE`.
Start backend with `python -m uvicorn main:app --reload`. In another terminal run `npm install` and `npm run dev` in `frontend`.

Gemini quotas cannot be made unlimited by code or by changing keys within the same project. Batching reduces request usage; paid tiers provide higher project quotas.
