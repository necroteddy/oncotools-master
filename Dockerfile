# Start with anaconda as the base image
FROM continuumio/anaconda:latest

# Create app directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Copy directories
COPY config /usr/src/app/config
COPY src /usr/src/app/src
COPY tests /usr/src/app/tests

# Copy files
COPY setup.py /usr/src/app
COPY requirements.txt /usr/src/app
COPY test.py /usr/src/app

# Uninstall matplotlib from conda and replace with pip
# This is specific to Unix systems
RUN conda remove --force --yes matplotlib
RUN pip install matplotlib

# Install oncotools
RUN cd /usr/src/app && python setup.py install

# Install SQL Drivers for Unix
RUN apt-get install -y freetds-bin
RUN apt-get install -y freetds-common
RUN apt-get install -y freetds-dev
RUN apt-get install -y tdsodbc

# Copy config files for database connection
COPY config/odbcinst.ini /etc
COPY config/odbc.ini /etc

# Expose port and start
RUN cd /usr/src/app && python test.py -v
CMD /bin/bash
