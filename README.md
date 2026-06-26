# AI Data Assistant

A small Streamlit app that lets you ask natural-language questions about your data and returns answers, SQL queries, and raw data tables.

## Features

- Natural-language querying over data via `agent.py`
- Streamlit UI in `app.py` for chat-like interaction
- Shows generated SQL and dataframes when available

## Requirements

- Python 3.8+
- See [requirements.txt](requirements.txt) for Python dependencies

## Quick start

1. Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1    # PowerShell
# or: venv\Scripts\activate  # cmd
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Provide credentials

The repo contains `key.json` which the app may use for API credentials. Do NOT commit secrets to GitHub. Prefer adding your credentials file to `.gitignore` or set environment variables as required by your `agent.py` implementation.

4. Run the app (Streamlit):

```powershell
streamlit run app.py
```

Or use the project runner if present:

```powershell
python run.py
```

## Project structure

- [app.py](app.py) — Streamlit front-end
- [agent.py](agent.py) — Query/LLM logic
- [run.py](run.py) — optional runner
- [requirements.txt](requirements.txt) — Python deps

## Development notes

- Add `key.json` to `.gitignore` to avoid pushing secrets.
- If you plan to push to GitHub, ensure remote is set and branch is `main` (or your chosen default).

## Contributing

Feel free to open issues or PRs. Keep secrets out of commits.

## License

MIT
# ai-data-assistant