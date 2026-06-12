
# immagine che viene scaricata dal Docker Hub
FROM python:3.12-slim

# definizione della workdir del container
WORKDIR /app

# Copiamo il file requirements.txt (che si presume sia nella home del progetto)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# mostra TUTTI i file dentro ci_cd nei log di GitHub se qualcosa non va
# RUN ls -R ci_cd
RUN echo "Start app.py pipeline ci"

# Esecuzione dello script python
CMD ["python", "ci_cd/CD/app.py"]