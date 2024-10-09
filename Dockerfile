FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -e ./compiler

RUN pip install --no-cache-dir pytest

CMD ["python3", "compiler/tests/TestPrograms/testprogs.py"]
