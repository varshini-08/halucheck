# HaluCheck UI frontend validation

## Implementation

The production entrypoint is `app.py`. It now renders the dark dashboard
header and question workspace directly, while `visualization/dashboard.py`
owns the post-analysis dashboard (response, metrics, donut summary, evidence,
and session-backed history). The earlier renderer is named
`_render_analysis_legacy`; there is one active `render_analysis` definition.
`app_new.py` is explicitly marked as a legacy prototype and is not the
production entrypoint.

No hallucination, retrieval, LLM, NLI, extraction, evaluation, dataset, or
service algorithms were changed by this UI correction.

## Static verification commands

```powershell
cd D:\halu
python scripts\verify_ui_frontend.py
python -m py_compile app.py visualization\dashboard.py
python -m compileall -q app.py services extraction verification evaluation retrieval analysis visualization scripts
```

## Runtime/UI verification

Use a fresh port so an old Streamlit process cannot mask the new code:

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -match 'streamlit|app\.py|app_new\.py' } |
  Select-Object ProcessId,CommandLine

# If process command lines are restricted on your machine, use this fallback:
Get-Process python,streamlit -ErrorAction SilentlyContinue |
  Select-Object Id,ProcessName,Path,StartTime

$out='results\final_validation\ui_frontend.stdout.log'
$err='results\final_validation\ui_frontend.stderr.log'
$p=Start-Process -FilePath 'python' -ArgumentList @('-m','streamlit','run','app.py','--server.headless','true','--server.port','8510') -WorkingDirectory 'D:\halu' -WindowStyle Hidden -PassThru -RedirectStandardOutput $out -RedirectStandardError $err
Start-Sleep -Seconds 8
try {
  $r=Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8510' -TimeoutSec 10
  "HTTP_STATUS=$($r.StatusCode) CONTENT=$($r.Content.Length)"
} finally { Stop-Process -Id $p.Id -ErrorAction SilentlyContinue }
Get-Content $out,$err -ErrorAction SilentlyContinue
```

Open `http://127.0.0.1:8510` and hard-refresh (`Ctrl+F5`). The page should
show “New Analysis”, a dark navy sidebar, a blue Analyze button, and no
“Welcome to HaluCheck” or “AI VERIFICATION WORKSPACE” legacy hero. Complete an
analysis to verify that real response, claims, evidence, metrics, donut values,
and recent-history rows appear.

## If the old UI still appears

1. The browser is on the wrong port/process. Use the process command above and
   open the exact port printed by the fresh launch.
2. `app_new.py` was launched. Stop it and launch `app.py` explicitly.
3. A stale server is serving old source. Stop the old PID, use a new port, and
   hard-refresh the browser.
4. Run `python scripts\verify_ui_frontend.py`; its renderer line and marker
   confirm which source Streamlit will execute.

## Status

Static checks and compilation are required before sign-off. Runtime HTTP
startup confirms the app can be served; visual confirmation must be made in a
browser at the fresh URL because a headless HTTP request cannot inspect CSS
layout or clicks.

Latest run: `verify_ui_frontend.py` passed; `py_compile` passed; recursive
`compileall` passed; `pytest` passed (62 tests, 3 existing deprecation
warnings); fresh Streamlit port 8510 returned HTTP 200 with content.
