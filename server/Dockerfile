FROM alpine:3.3
RUN apk add --no-cache python
RUN apk add --update --virtual build-dependencies \
    python-dev \
    py-pip \
    && pip install Flask==0.12 \
    && pip install tornado==4.4.2 \
    && pip install slackclient==1.0.5 \
    && apk del build-dependencies
ADD . /opt/
CMD ["python", "/opt/main.py"]