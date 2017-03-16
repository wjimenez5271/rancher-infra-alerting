FROM alpine:3.3
RUN apk add --no-cache python
RUN apk add --update --virtual build-dependencies \
    python-dev \
    py-pip \
    && pip install requests==2.13.0 \
    && pip install dnspython==1.15.0 \
    && apk del build-dependencies
ADD . /opt/
CMD ["python", "/opt/main.py"]