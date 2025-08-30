FROM python:3.11-slim

WORKDIR /dashboard

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./dashboard .

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
