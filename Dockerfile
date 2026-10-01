# Stage 1: builder
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files first for better Docker layer caching
COPY pyproject.toml uv.lock ./

# Create the virtual environment and install dependencies
RUN uv sync --frozen --no-dev --no-install-project


# Stage 2: runtime
FROM python:3.12-slim

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application source code
COPY src/ ./src/

# Make the virtual environment available
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "src.food11.serve:app", "--host", "0.0.0.0", "--port", "8000"]