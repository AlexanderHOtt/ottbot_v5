FROM openjdk:17-jdk-slim

WORKDIR /lavalink

COPY application.yml .

RUN apt update -y && apt upgrade -y
RUN apt install wget -y
RUN wget https://github.com/freyacodes/Lavalink/releases/latest/download/Lavalink.jar
EXPOSE 2333

ENTRYPOINT ["java", "-jar", "Lavalink.jar", "-c", "application.yml"]
