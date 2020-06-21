# docker images
# docker run --name april -it 8d68ea8cc930 bash
# docker rm april
# docker attach april

FROM ubuntu:latest

ENV UNAME pi

RUN apt-get -y update && apt-get -y upgrade
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install apt-utils
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install mplayer pulseaudio
RUN DEBIAN_FRONTEND=noninteractive apt-get install --yes pulseaudio-utils
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install bluetooth bluez bluez-tools rfkill git
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python3 python-gobject python3-pip
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install git
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install festival
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install php apache2 libapache2-mod-php
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install vim nano
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install sudo
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install usbutils
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install expect
# this is required for numpy
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install libatlas-base-dev
ENV TZ=Europe/London
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY pulse-client.conf /etc/pulse/client.conf

RUN echo "%sudo ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN useradd -G sudo,lp,bluetooth,www-data -ms /bin/bash pi
RUN gpasswd -a pi audio
RUN echo "Set disable_coredump false" >> /etc/sudo.conf

USER $UNAME
WORKDIR /home/pi
COPY . /home/pi/smartbot/

USER root
RUN chown pi:pi /home/pi/smartbot

USER $UNAME
WORKDIR /home/pi
RUN mkdir Music
