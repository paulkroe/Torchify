FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN apt-get install -y graphviz

WORKDIR /app
 
COPY . /app

RUN pip3 install --no-cache-dir -e ./compiler && pip3 install --no-cache-dir graphviz

CMD python3 compiler/tests/TestPrograms/testprogs.py && python3 compiler/tests/TestPrograms/demo.py