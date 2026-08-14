FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
COPY scripts/download_data.sh /app/scripts/download_data.sh
RUN chmod +x /app/scripts/download_data.sh
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]