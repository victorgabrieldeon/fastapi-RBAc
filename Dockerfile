# Multi-stage build for smaller and more secure image
FROM python:3.12.2-slim AS builder

# Set working directory
WORKDIR /app

# Install PDM
RUN pip install --no-cache-dir pdm

# Copy dependency files
COPY pyproject.toml pdm.lock* ./

# Install dependencies in a virtual environment
RUN pdm install --prod --no-lock --no-editable

# Final stage
FROM python:3.12.2-slim

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . /app

# Create directory for database (if using SQLite)
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/public').read()"

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.main.app:app", "--host", "0.0.0.0", "--port", "8000"]
