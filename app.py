"""Entrypoint do dashboard.

Local:
    python app.py

Render:
    gunicorn app:server --workers 1 --threads 4 --timeout 120
"""

from __future__ import annotations

from dashboard import create_app

app = create_app()
server = app.server


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
