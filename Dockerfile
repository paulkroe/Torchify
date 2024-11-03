FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y graphviz && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -e ./compiler && pip install --no-cache-dir graphviz

CMD python3 compiler/tests/TestPrograms/testprogs.py && python3 compiler/tests/TestPrograms/demo.py
