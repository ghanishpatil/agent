FROM astral/uv:python3.13-trixie-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_TOOL_BIN_DIR=/usr/local/bin

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=src/uv.lock,target=uv.lock \
    --mount=type=bind,source=src/pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY src/ /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

COPY flag /flag

RUN mkdir -p /app/data

ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT []
CMD ["uv", "run", "gunicorn", "-w", "1", "--threads", "1", "-b", "0.0.0.0:5000", "app:app"]
