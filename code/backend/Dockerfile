# The backend image: Python, the dependencies, and our code.
FROM python:3.12-slim

# WeasyPrint draws the routine PDFs and needs these text libraries.
# curl is used by the health check in docker-compose.yml.
RUN apt-get update \
 && apt-get install --no-install-recommends -y \
      libpango-1.0-0 \
      libpangoft2-1.0-0 \
      libharfbuzz0b \
      fonts-dejavu-core \
      curl \
 && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install the dependencies on their own layer. Docker reuses this layer until
# pyproject.toml changes, so rebuilding after a code change is fast.
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir ".[dev]"

COPY . .

# Run as a normal user, not as root.
RUN useradd --create-home app && chown -R app:app /app
USER app

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
