FROM python:3.8-slim-buster

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -e ./compiler pytest torch torchvision tqdm

CMD ["python3", "compiler/tests/TestPrograms/testprogs.py"]
