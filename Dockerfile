FROM python:3.10-slim
LABEL maintainer="Steven Herrera stevenherrera46375@utexas.edu"

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl=7.88.1-10+deb12u5 && rm -rf /var/lib/apt/lists/*
RUN mkdir /app/.streamlit && mkdir /app/resources

COPY ./docker_requirements.txt /app/docker_requirements.txt
COPY ./.streamlit/config.toml /app/.streamlit/config.toml
COPY ./resources/video_library_favicon.png /app/resources/video_library_favicon.png

RUN pip install --no-cache-dir pip==23.3.1 && pip install --no-cache-dir -r /app/docker_requirements.txt

EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

COPY app.py /app/app.py
# streamlit will say you can view the app at http://0.0.0.0:8501 
# but you actually need to use 127.0.0.1:8501 or localhost:8501 in your browser
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]