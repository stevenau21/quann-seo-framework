FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn httpx
COPY server.py .
EXPOSE 5002
CMD ["python", "server.py"]
