FROM ubuntu:20.04
FROM python:3
FROM aiogram/telegram-bot-api
RUN apt update && apt upgrade -y
RUN pip install aiodocker
COPY handler.py /handler.py
COPY main.py /main.py
COPY variables.py /variables.py
RUN chmod +x /main.py
CMD python3 /main.py