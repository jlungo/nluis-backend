FROM python:3.11-alpine3.20

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk update && apk add --no-cache \
    # Core build tools
    build-base \
    bash \
    musl-dev \
    linux-headers \
    libffi-dev \
    zlib-dev \
    # Python packaging helpers
    py3-pip \
    py3-setuptools \
    py3-wheel \
    py3-numpy \
    # Postgres
    postgresql-dev \
    # Geospatial deps
    gdal-dev \
    gdal-tools \
    geos-dev \
    proj-dev \
 && rm -rf /var/cache/apk/*

WORKDIR /app

COPY requirements.txt /app/

ENV CFLAGS="-I/usr/include/gdal"
ENV LDFLAGS="-L/usr/lib"

RUN pip install --upgrade pip --root-user-action=ignore && \
    pip install --prefer-binary -r requirements.txt --root-user-action=ignore

COPY . /app/

ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
