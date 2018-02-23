FROM ubuntu:latest
RUN apt-get update
RUN apt-get install -y python-pip
RUN apt-get install -y apache2
RUN pip install -U pip
RUN pip install -U flask
RUN pip install -U flask-cors
RUN \
  apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10 && \
  echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' > /etc/apt/sources.list.d/mongodb.list && \
  apt-get update && \
  apt-get install -y mongodb-org && \
  rm -rf /var/lib/apt/lists/*
VOLUME ["/data/db"]
VOLUME ["/log/mongodb.log"]
RUN echo "ServerName localhost  " >> /etc/apache2/apache2.conf
RUN echo "$user     hard    nproc       20" >> /etc/security/limits.conf
ADD ./src/service /service
ADD ./src/html /var/www/html
EXPOSE 80
EXPOSE 8080
# Expose ports.
#   - 27017: process
#   - 28017: http
EXPOSE 27017
EXPOSE 28017
CMD ["/bin/bash", "/service/start_services.sh"]
