# A Dockerfile with common issues: floating base tag, runs as root, no healthcheck.
FROM python:latest
RUN pip install flask requests
COPY . /app
WORKDIR /app
EXPOSE 8080
CMD ["python", "app.py"]
