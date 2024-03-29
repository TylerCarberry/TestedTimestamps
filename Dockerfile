FROM borda/docker_python-opencv-ffmpeg:cpu-py3.9-cv4.5.1

ENV APP_HOME /app
ENV PYTHONIOENCODING UTF-8

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

WORKDIR $APP_HOME
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

RUN apt-get -y update && apt-get -y install ffmpeg

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.

# https://stackoverflow.com/a/64084917
CMD ["/usr/bin/python3", "run_gunicorn.py", "--workers", "1", "--threads", "4", "app:app"]
