FROM python:3

RUN mkdir /opt/es_exporter

COPY es_exporter.py /opt/es_exporter/
COPY requirements.txt /opt/es_exporter/
COPY entrypoint.sh /opt/es_exporter/
COPY config.json /opt/es_exporter/config.json

RUN cd /opt/es_exporter
RUN pip install -r /opt/es_exporter/requirements.txt

CMD ["python", "/opt/es_exporter/es_exporter.py"]