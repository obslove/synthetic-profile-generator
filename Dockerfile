FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md main.py ./
COPY synthetic_profiles ./synthetic_profiles
COPY examples ./examples

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "synthetic_profiles.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
