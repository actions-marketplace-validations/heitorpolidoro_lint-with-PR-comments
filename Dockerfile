FROM alpine

ENV PYTHONUNBUFFERED=1

RUN apk add --update --no-cache \
    bash \
    python3 py3-pip \
    && pip install \
    flake8 \
    PyGithub

COPY entrypoint.py /entrypoint.py

RUN chmod +x /entrypoint.py

CMD ["/entrypoint.py"]
ENTRYPOINT ["python3"]