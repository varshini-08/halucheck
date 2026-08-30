# Testing

Use the existing environment:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
cd frontend
npm run build
```

Python compilation is checked with `python -m py_compile app.py api\main.py`. External provider behavior is mocked in unit tests; live Groq checks are manual and must never print credentials.
