FROM python:3.9

RUN apt-get update\
    && apt-get install -y sudo\
    && apt install -y vim

RUN sudo pip install Flask &&\
    sudo pip install psycopg2 &&\
    pip install -U flask-cors &&\
    pip install kafka-python
    #sudo pip install SQLAlchemy==1.3.5

RUN mkdir -p /home/projects/flask-crud-app/templates/


#COPY ./app.py /home/projects/flask-crud-app/

#COPY ./templates/* /home/projects/flask-crud-app/templates






EXPOSE 5000

ENTRYPOINT ["/bin/bash"]

