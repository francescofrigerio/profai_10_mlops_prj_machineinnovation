FROM python:3.12-slim

# Installiamo le dipendenze di sistema minime 
# (opzionale ma consigliato per build stabili)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /lib/apt/lists/*

# Crea una directory di lavoro
WORKDIR /code

# Copia i requisiti e installali
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Configura un utente non-root
# (Standard di sicurezza richiesto da Hugging Face)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

# Imposta la directory di lavoro dell'utente
WORKDIR $HOME/app

# Copia il resto del codice nell'applicazione
COPY --chown=user . $HOME/app

# Avvia l'applicazione FastAPI sulla porta 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]