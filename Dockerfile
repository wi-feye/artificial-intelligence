FROM python:3.8
#FROM conda/miniconda3:latest
LABEL maintainer="Wi-Feye"
LABEL version="1.0"
LABEL description="Wi-Feye Artificial Intelligence"

# copying the environment
COPY . /app

# setting the workdir
WORKDIR /app

RUN ["apt", "update"]
RUN ["apt-get", "install" ,"-y", "libgdal-dev"]

# installing all requirements
RUN ["pip3", "install", "-r", "requirements.txt"]

# exposing the port
EXPOSE 10003/tcp

# main command
# CMD ["python3", "-m", "flask", "--app", "src", "run", "-p", "10001", "--host=0.0.0.0"]
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
