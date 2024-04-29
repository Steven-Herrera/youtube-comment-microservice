FROM python:3.10
LABEL maintainer="Steven Herrera stevenherrera46375@utexas.edu"

WORKDIR /app
COPY ./docker_requirements.txt /app/docker_requirements.txt
RUN pip install --no-cache-dir pip==23.3.1 && pip install --no-cache-dir -r /app/docker_requirements.txt

COPY app.py /app/app.py

CMD [ "python", "./app.py" ]