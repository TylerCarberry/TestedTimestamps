FROM valian/docker-python-opencv-ffmpeg:py3

ENV APP_HOME /app
ENV PYTHONIOENCODING UTF-8
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
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app
