# Streamlit Deployment Guide

## Entry point

Use this entrypoint file when deploying:

```text
streamlit_app.py
```

## Local run

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Streamlit Community Cloud

1. Push this repository to GitHub.
2. Go to https://share.streamlit.io.
3. Click **Create app**.
4. Select the GitHub repository and branch.
5. Set the main file path to:

```text
streamlit_app.py
```

6. In **Advanced settings → Secrets**, add:

```toml
GOOGLE_API_KEY = "your_api_key_here"
```

7. Deploy.

## Notes

- Do not commit `.env` or real API keys.
- If no API key is configured, the app still runs in deterministic demo mode.
- The app includes four interactive sections: Strategy Builder, Copilot, Industry Graph, and Market Research Analyzer.
