
# immagine che viene scaricata dal Docker Hub
FROM python:3.12-slim

# definizione della workdir del container
WORKDIR /app

# Copiamo il file requirements.txt (che si presume sia nella home del progetto)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Verifica la presenza dei file nella workdir
# RUN ls -la
# RUN ls -R 
RUN ls ci_cd

RUN ls ci_cd/CD

RUN ls ci_cd/CD/app.py

# Esecuzione dello script python
CMD ["python", "ci_cd/CD/app.py"]