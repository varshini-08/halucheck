# Final Submission Checklist

- [x] Source code and GitHub repository
- [x] README and run instructions
- [x] Architecture, workflow, algorithm, and data-flow documentation
- [x] Testing and performance reports
- [x] Results, limitations, and future scope
- [x] Demo test cases and demo script
- [x] Viva questions and answers
- [x] Final release and audit reports
- [x] API-key and `.env` protection
- [ ] Browser screenshots captured
- [ ] Responsive screenshots captured
- [ ] Manual evidence accordion/history/export validation recorded
- [ ] Gemini live test recorded if quota is available
- [ ] Optional-source live evidence recorded where configured

Run before submission:

```powershell
cd D:\halu
.\.venv\Scripts\python.exe -m py_compile app.py api\main.py
.\.venv\Scripts\python.exe -m pytest tests -q
cd frontend
npm run build
```
