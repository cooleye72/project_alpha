FROM python:3.11.13-slim-bookworm AS builder-0

RUN apt-get update
# COPY --chown=app:app requirements_build.txt ./
# RUN pip install --no-cache-dir -r requirements_build.txt

# Stage 2: Final image
FROM gdssingapore/airbase:python-3.13-builder

RUN apt-get update && \
    apt-get install -y vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
    
COPY --from=builder-0 /usr/local/bin/python3.11 /usr/local/bin/python3.11
COPY --from=builder-0 /usr/local/bin/pip3.11 /usr/local/bin/pip3.11
COPY --from=builder-0 /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder-0 /usr/local/lib/libpython3.11.so* /usr/local/lib/

# Copy Streamlit executables and entrypoints
# COPY --from=builder-0 /usr/local/bin/streamlit /usr/local/bin/
# COPY --from=builder-0 /usr/local/lib/python3.11/site-packages/streamlit /usr/local/lib/python3.11/site-packages/streamlit

RUN update-alternatives --install /usr/local/bin/python python /usr/local/bin/python3.11 1 && \
    update-alternatives --install /usr/local/bin/python3 python3 /usr/local/bin/python3.11 1 && \
    /usr/local/bin/python3.11 -m pip install --no-cache-dir --upgrade pip

ENV PYTHONUNBUFFERED=TRUE
COPY --chown=app:app requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=app:app . ./
COPY --chown=app:app .env ./
COPY --chown=app:app .streamlit/secrets.toml ./.streamlit/secrets.toml
USER app
CMD ["bash", "-c", "streamlit run app.py --server.port=$PORT"]