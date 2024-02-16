FROM python:3.11-alpine

# Install base dependences
RUN apk update \
    && apk add bash gcc python3-dev py3-pip shadow pkgconf libpq-dev

# Download wait-for-it
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /opt/bin/
RUN chmod +x /opt/bin/wait-for-it.sh && chown -R 1000:1000 /opt/bin/wait-for-it.sh

# Create new user
RUN useradd --create-home foo
WORKDIR /home/foo/rinha-de-backend-2024-q1

# Copy source files
COPY ./requirements.txt /home/foo/rinha-de-backend-2024-q1
RUN rm -rf venv && \
    python -m venv venv && \
    . ./venv/bin/activate && \
    pip install --upgrade pip && pip install -r requirements.txt
ENV PATH="/home/foo/rinha-de-backend-2024-q1/venv/bin:$PATH"
COPY . /home/foo/rinha-de-backend-2024-q1/

# Run main application
USER 1000
WORKDIR /home/foo/rinha-de-backend-2024-q1/src
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["/opt/bin/wait-for-it.sh -h 127.0.0.1 -p 5432 --strict --timeout=300 -- python init.py"]
