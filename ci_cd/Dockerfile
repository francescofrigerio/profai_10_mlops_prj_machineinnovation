#docker file
# utilizziamo un immagine di partenza già definita
# scegliamo un immagine di base su cui andare a costruire
# un immagine che viene scaricata dal Docker Hub
FROM python:3.12-slim

# definizione della workdir del container
WORKDIR /app

# copiamo contenuto e logica della nostra app (app.py) nel container sotto /app
# copiamo tutto quello che sta nella dir CD sotto la cartella app del container

# Se lanci il comando di build stando 
# già dentro la cartella CD, Docker non troverà mai un percorso chiamato ./6_CI_CD/CD perché per lui la cartella corrente è "il mondo intero"
# KO -> COPY ./6_CI_CD/CD /app
# Copia il contenuto della cartella specifica nella cartella corrente del container (.)
# COPY ./6_CI_CD/CD .
COPY . .

# spostata sopra definizione della workdir del container
# WORKDIR /app

# Verifica la presenza dei file nella workdir
# RUN ls -la
# RUN ls -R 
RUN ls 6_CI_CD

RUN ls 6_CI_CD/CD

RUN ls 6_CI_CD/CD/app.py

# Esecuzione dello script python
# CMD ["python","app.py"]
CMD ["python", "6_CI_CD/CD/app.py"]