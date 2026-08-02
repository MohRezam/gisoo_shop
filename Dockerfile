FROM ubuntu:latest
LABEL authors="mohrez"

ENTRYPOINT ["top", "-b"]