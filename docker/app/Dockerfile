# use -alpine and install deps manually to reduce image size?
FROM python:3.8.10 as base
# The enviroment variable ensures that the python output is set straight
# to the terminal without buffering it first
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Create a user to avoid running containers as root
RUN addgroup --system sportdiag && adduser --system --ingroup sportdiag sportdiag

RUN apt-get update && apt-get install -y -q --no-install-recommends \
  # dependencies for building Python packages
  build-essential \
  # postgres client (psycopg2) dependencies
  libpq-dev \
  # cleaning up unused files to reduce the image size
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /home/sportdiag/src/
ENV PATH /home/sportdiag/.local/bin:$PATH
RUN chown sportdiag: /home/sportdiag/src/
RUN chmod -R u+rw /home/sportdiag/src/
USER sportdiag
# Copy file describing base image/common dependencies for dev and prod image
# XXX COPY --chown=sportdiag:sportdiag ./requirements/base.txt requirements/base.txt
COPY ./requirements/base.txt requirements/base.txt
RUN python -m pip install --upgrade pip
# Install common dependencies
RUN pip install --no-cache-dir -r requirements/base.txt
# Copy entrypoint script which waits for the DB to be ready
# XXX COPY --chown=sportdiag:sportdiag ./docker/app/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY ./docker/app/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN ls -la
USER root
RUN chmod +x /usr/local/bin/entrypoint.sh
USER sportdiag
# XXX
RUN ls -la
# This script will run before every command executed in the container
ENTRYPOINT ["entrypoint.sh"]

# Define an image for local development. Inherits common packages from the base stage.
FROM base as dev
RUN echo "\n***\n***\nDEV IMAGE BUILD STARTED\n***\n***\n"
# XXX next
RUN whoami
# Copy file describing development dependencies
# XXX COPY --chown=sportdiag:sportdiag ./requirements/dev.txt requirements/dev.txt
COPY ./requirements/dev.txt requirements/dev.txt
# Copy the script that starts the development application server (runserver)
# XXX COPY --chown=sportdiag:sportdiag ./docker/app/start-dev-server.sh /usr/local/bin/start-dev-server.sh
COPY ./docker/app/start-dev-server.sh /usr/local/bin/start-dev-server.sh
RUN ls -la
USER root
RUN chmod +x /usr/local/bin/start-dev-server.sh
RUN ls -la
USER sportdiag
# Install development dependencies
RUN pip install --no-cache-dir -r requirements/dev.txt

# XXX
RUN ls -la

USER sportdiag
# The development server starts by default when the container starts
CMD ["start-dev-server.sh"]

# Define an image for production. Inherits common packages from the base stage.
FROM base as prod
RUN echo "\n***\n***\nPROD IMAGE BUILD STARTED\n***\n***\n"
RUN whoami
# Copy file describing production dependencies
# XXX COPY --chown=sportdiag:sportdiag ./requirements/prod.txt requirements/prod.txt
COPY ./requirements/prod.txt requirements/prod.txt
# Copy the script that starts the production application server (gunicorn)
# XXX COPY --chown=sportdiag:sportdiag ./docker/app/start-prod-server.sh /usr/local/bin/start-prod-server.sh
COPY ./docker/app/start-prod-server.sh /usr/local/bin/start-prod-server.sh
RUN ls -la
USER root
RUN chmod +x /usr/local/bin/start-prod-server.sh
RUN ls -la
USER sportdiag
# Create directory for collecting static files
RUN mkdir /home/sportdiag/src/collected_static
# XXX RUN chown sportdiag /home/sportdiag/src/collected_static
# Create files for storing users access data.. this is just for testing and should be deleted later
RUN touch approved_fake_psychologists_raw_passwords.txt
RUN touch demo_clients_raw_passwords.txt
RUN touch fake_researchers_raw_passwords.txt
# XXX RUN chown sportdiag approved_fake_psychologists_raw_passwords.txt
# XXX RUN chown sportdiag demo_clients_raw_passwords.txt
# XXX RUN chown sportdiag fake_researchers_raw_passwords.txt

# Create media files directories for project apps
# RUN mkdir /media/accounts
RUN mkdir -p media/sportdiag/surveys
# XXX RUN chown -R sportdiag media

# Install production dependencies
RUN pip install --no-cache-dir -r requirements/prod.txt
# Copy the source code of django app to the working directory
# XXX COPY --chown=sportdiag:sportdiag . ./
COPY . ./

#RUN touch approved_fake_psychologists_raw_passwords.txt
#RUN touch demo_clients_raw_passwords.txt
#RUN touch fake_researchers_raw_passwords.txt

# XXX
RUN ls -la

USER sportdiag
# The production server starts by default when the container starts
CMD ["start-prod-server.sh"]
