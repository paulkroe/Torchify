FROM python:3.8-slim-buster

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -e ./compiler

CMD ["python3", "compiler/tests/TestPrograms/testprogs.py"]
