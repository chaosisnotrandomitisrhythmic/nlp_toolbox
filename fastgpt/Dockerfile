FROM python:3.10

WORKDIR /code/src

COPY --link --chown=1000 src/ .

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]