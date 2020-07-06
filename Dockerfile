FROM python:latest
COPY pz/ /usr/ms/pr
WORKDIR /usr/ms/pr
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y python3-pip && pip3 install matplotlib influxdb\
    && apt-get install -y python3-tk
COPY start.sh /usr/ms/pr
RUN chmod +x start.sh
CMD ["./start.sh"]