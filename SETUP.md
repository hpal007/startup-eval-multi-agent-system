**Quick Setup — Backend & UI**

- **Repo root:** `se-system` (this file)

**Prerequisites**
- Python 3.12+ and `pip` (venv recommended)
- Node.js 18+ and `npm` or `yarn`

**Backend (Python)**
- Create and activate venv:
  - macOS / zsh:
    ```bash
    python3.12 -m venv .venv
    source .venv/bin/activate
    ```
- Install dependencies (uses `pyproject.toml`):
  ```bash
  pip install --upgrade pip
  pip install -e .
  ```
- Environment: copy `.env` if you use one (not included). Example:
  ```bash
  cp .env.example .env  # if provided
  ```
- Run the backend (development):
  - Run with Uvicorn (FastAPI app expected):
    ```bash
    uvicorn main:app --reload --port 8000
    ```
  - Or run the CLIs / agents directly:
    ```bash
    python main.py
    # or
    python main_cli.py
    ```

**Frontend (UI)**
- Enter UI folder and install:
  ```bash
  cd ui
  npm install
  # or
  yarn
  ```
- Run development server:
  ```bash
  npm run dev
  # or
  yarn dev
  ```
- Default Next.js dev port: `3000`.

**Database / Persistence**
- Project includes `sessions.db` at repo root for local sessions — keep it writable.

**Ports & Access**
- Backend default (development): `http://localhost:8000`
- Frontend default: `http://localhost:3000`

**Troubleshooting**
- If Python imports fail, ensure project installed in editable mode `pip install -e .` or add repo root to `PYTHONPATH`.
- If Node build issues occur, remove `node_modules` and reinstall: `rm -rf node_modules && npm install`.
- If ports are busy, change `--port` for uvicorn or `PORT` env var for Next.js.

**Next steps (optional)**
- Run backend tests: `pytest` from repo root (dev extras required).
- Build production UI: `cd ui && npm run build && npm run start`.

If you want, I can add a `.env.example`, a small `Procfile`, or npm script glue for proxying API requests from the UI — tell me which you prefer.
