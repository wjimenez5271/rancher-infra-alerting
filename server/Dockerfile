FROM alpine:3.3
RUN apk add --no-cache python
RUN apk add --update --virtual build-dependencies \
    python-dev \
    py-pip \
    && pip install Flask==0.12 \
    && apk del build-dependencies
ADD . /opt/
CMD ["python", "/opt/main.py"]