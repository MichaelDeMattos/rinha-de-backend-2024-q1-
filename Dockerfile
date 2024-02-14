FROM python:3.11

# Install base dependences
RUN apt update \
    && apt install gcc python3-dev iputils-ping wait-for-it python3-venv firebird-dev -y \
    && pip install --upgrade pip \
    && apt-get install tzdata -y

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
CMD ["wait-for-it -h 127.0.0.1 -p 3050 --strict --timeout=300 -- python init.py"]
