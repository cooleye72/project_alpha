FROM gdssingapore/airbase:python-3.13
# 1. Install Python 3.11 alongside existing Python
RUN apt-get install -y python3.11 python3.11-dev python3.11-venv && \
    apt-get clean

# 2. Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --set python3 /usr/bin/python3.11

# 3. Verify Python version
RUN python3 --version | grep "3.11" && \
    pip --version | grep "python 3.11

# 4. Set environment variables
ENV PYTHONUNBUFFERED=TRUE

# 5. Install requirements
COPY --chown=app:app requirements.txt ./
RUN pip install -r requirements.txt

# 6. Copy application code
COPY --chown=app:app . ./

# 7. Switch to non-root user
USER app

# 8. Run Streamlit
CMD ["bash", "-c", "streamlit run app.py --server.port=$PORT"]

# comment here for build