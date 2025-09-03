FROM ubuntu:latest
LABEL authors="kenhy"

ENTRYPOINT ["top", "-b"]