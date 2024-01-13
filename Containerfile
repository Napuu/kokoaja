FROM python:3.11

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY *.py .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]