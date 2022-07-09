# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
FROM python:3.8.10 as base
#maintainer
LABEL Author="JanSandor"
# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Create a user to avoid running containers as root in production
RUN addgroup --system sportdiag && adduser --system --ingroup sportdiag sportdiag
RUN apt-get update && apt-get install -y -q --no-install-recommends \
  # dependencies for building Python packages
  build-essential \
  # postgres client (psycopg2) dependencies
  libpq-dev \
  # cleaning up unused files to reduce the image size
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*
# Switch to the non-root user
USER sportdiag
# create root directory for our project in the container
# RUN mkdir /src
# Set the working directory to /src
# WORKDIR /src
WORKDIR /home/sportdiag/src/
# Copy the current directory contents into the container at /src
# COPY . /src/
# Copy the python depencencies list for pip
COPY --chown=sportdiag:sportdiag ./requirements/base.txt requirements/base.txt
# Switch to the root user temporary, to grant execution permissions.
USER root
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements/base.txt
# Copy entrypoint script which waits for the db to be ready
COPY --chown=sportdiag:sportdiag ./docker/app/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
USER sportdiag
# This script will run before every command executed in the container
ENTRYPOINT ["entrypoint.sh"]


# Define an image for local development. Inherits common packages from the base stage.
FROM base as dev
# Copy the scripts that starts the development application server (runserver)
COPY --chown=sportdiag:sportdiag ./docker/app/start-dev-server.sh /usr/local/bin/start-dev-server.sh
COPY --chown=sportdiag:sportdiag ./requirements/dev.txt requirements/dev.txt
COPY --chown=sportdiag:sportdiag ./approved_fake_psychologists_raw_passwords.txt ./approved_fake_psychologists_raw_passwords.txt
COPY --chown=sportdiag:sportdiag ./fake_researchers_raw_passwords.txt ./fake_researchers_raw_passwords.txt
USER root
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements/dev.txt
RUN chmod +x /usr/local/bin/start-dev-server.sh
USER sportdiag
# The development server starts by default when the container starts
CMD ["start-dev-server.sh"]


# Define an image for production. Inherits common packages from the base stage.
FROM base as prod
# Install extra packages required in production
USER root
COPY --chown=sportdiag:sportdiag ./requirements/prod.txt requirements/prod.txt
RUN pip install --no-cache-dir -r requirements/prod.txt
# Copy the script that starts the production application server (gunicorn)
COPY --chown=sportdiag:sportdiag ./docker/app/start-prod-server.sh /usr/local/bin/start-prod-server.sh
RUN chmod +x /usr/local/bin/start-prod-server.sh
USER sportdiag
# Copy the source code of our django app to the working directoy
# COPY --chown=sportdiag:sportdiag . ./
# The production server starts by default when the container starts
CMD ["start-prod-server.sh"]