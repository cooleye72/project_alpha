FROM gdssingapore/airbase:python-3.13
# Remove Python 3.13 and install 3.11
RUN apt-get update && \
    apt-get remove -y python3.13 && \
    apt-get install -y python3.11 python3.11-dev python3.11-venv && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    apt-get clean

# 2. Verify Python version
RUN python3 --version | grep "3.11" && \
    pip --version | grep "python 3.11"

# 3. Set environment variables
ENV PYTHONUNBUFFERED=TRUE

# 4. Install requirements
COPY --chown=app:app requirements.txt ./
RUN pip install -r requirements.txt

# 5. Copy application code
COPY --chown=app:app . ./

# 6. Switch to non-root user
USER app

# 7. Run Streamlit
CMD ["bash", "-c", "streamlit run app.py --server.port=$PORT"]

# comment here for build