FROM gdssingapore/airbase:python-3.13
# 1. Install Python 3.11 alongside existing Python
RUN apt-get update && \
    apt-get install -y python3.11 python3.11-dev python3.11-venv && \
    apt-get clean

# 2. Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.11 2 && \
    update-alternatives --set python3 /usr/bin/python3.11 && \
    update-alternatives --set python /usr/bin/python3.11

# 3. Verify Python version
RUN python3 --version && \
    python3.11 --version && \
    python3 -m pip --version

# 2. Create and activate a Python 3.11 virtual environment
# RUN python3.11 -m venv /opt/venv311
# ENV PATH="/opt/venv311/bin:$PATH"

# 4. Set environment variables
ENV PYTHONUNBUFFERED=TRUE

# 5. Install requirements
COPY --chown=app:app requirements.txt ./
RUN pip3.11 install -r requirements.txt

# 6. Copy application code
COPY --chown=app:app . ./

# 7. Switch to non-root user
USER app

# 8. Run Streamlit
CMD ["bash", "-c", "python3.11 -m streamlit run app.py --server.port=$PORT"]

# comment here for build