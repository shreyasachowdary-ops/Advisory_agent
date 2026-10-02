# ERP Integration — Copy Instructions

Copy these files into `lnpl_erp_dev_v1` on **school-server**.

## 1. Advisor page (sir's requested file)

```bash
# Root Pages folder (as shown in VS Code explorer)
cp erp-integration/Pages/AdvisorPage.js  lnpl_erp_dev_v1/Pages/AdvisorPage.js

# Also required if App.js imports from src/Pages (it does in current App.js)
cp erp-integration/src/Pages/AdvisorPage.js  lnpl_erp_dev_v1/src/Pages/AdvisorPage.js
```

## 2. Router — edit `src/components/App.js`

See [patches/App.js.patch.txt](patches/App.js.patch.txt)

## 3. Sidebar link — edit `src/components/Applicant/dashboard_applicant.js`

See [patches/dashboard_applicant.js.patch.txt](patches/dashboard_applicant.js.patch.txt)

## 4. API URL — edit `src/components/contexts/config_web.json`

Add `advisor_base_url` — see [patches/config_web.json.snippet](patches/config_web.json.snippet)

Use `http://127.0.0.1:8787` if ERP and advisor backend run on the same server.
Use the server's LAN IP if the browser runs on a different machine.

## 5. Backend CORS

In `advisor/backend/.env`, ensure `CORS_ORIGINS` includes your ERP URL (e.g. `http://106.51.158.20:3000`).

## 6. Start services

```bash
# Advisor backend
cd advisor/backend && .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8787 --reload

# ERP frontend (existing command)
cd lnpl_erp_dev_v1 && npm start
```

Open ERP → Admin Dashboard → Student → **Parent/Teacher Advisor**, or go to `/advisor`.
