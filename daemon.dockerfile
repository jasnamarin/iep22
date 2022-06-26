FROM python:3

RUN mkdir -p /opt/src/applications
WORKDIR /opt/src/applications

COPY applications/daemon/application.py ./application.py
COPY applications/configuration.py ./configuration.py
COPY applications/utils.py ./utils.py
COPY applications/models.py ./models.py
COPY applications/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt
RUN rm -f /etc/localtime && ln -s /usr/share/zoneinfo/Europe/Belgrade /etc/localtime

ENV PYTHONPATH="/opt/src"

ENTRYPOINT ["python", "./application.py"]