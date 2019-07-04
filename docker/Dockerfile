FROM python:3.6-alpine

ARG HTTP_PROXY=${HTTP_PROXY}
ARG HTTPS_PROXY=${HTTPS_PROXY}
ARG PKG_VERSION
ENV http_proxy $HTTP_PROXY
ENV https_proxy $HTTPS_PROXY
ENV pkg_version=${PKG_VERSION}

ADD . /service
WORKDIR /service

RUN sh /service/docker-env-conf.sh

EXPOSE 8403
USER onap
WORKDIR /service
ENTRYPOINT vfc/nfvo/lcm/docker/docker-entrypoint.sh
