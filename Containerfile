FROM python:3.11

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

RUN apt-get update
RUN apt-get install -y locales
RUN sed -i -e 's/# fi_FI.UTF-8 UTF-8/fi_FI.UTF-8 UTF-8/' /etc/locale.gen \
 && locale-gen

RUN mkdir -p static
COPY *.py .
COPY templates templates

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]