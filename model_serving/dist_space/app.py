""" 
   app.py 
   Service Model Serving Application
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import uvicorn
import os

from utils.const_baseline import ConfigProdConstants
from train.pipe_baseline import SentimentPipeline

# 1. Inizializzazione dell'app FastAPI
app = FastAPI(title="Machine Innovation Sentiment Analysis API",
              description="API per sentiment analysys con Machine Innovation Model Serving",
              version="1.0"
            )

# 2. Caricamento del modello RoBERTa Standard
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

CONFIG = ConfigProdConstants()
print({"status": f"Caricamento del modello {MODEL_NAME} in corso..."})
try:
    # Usiamo la pipeline di Hugging Face per gestire tokenizzazione e inferenza in un colpo solo
    # sentiment_pipeline = pipeline("sentiment-analysis", model=MODEL_NAME)
    # classifier = SentimentPipeline(MODEL_NAME)
    classifier = SentimentPipeline(CONFIG.MODEL_DIR)

    print({"status": "Modello caricato con successo!"})
except Exception as e:
    print(f"Errore nel caricamento del modello: {e}")
    classifier = None

# 3. Definizione della struttura dei dati in ingresso (Pydantic)
class TextRequest(BaseModel):
    """
       Schema oer la richiesta di analisi del sentiment.
       Contiene un solo campo 'text' che rappresenta il testo da analizzare.
    """
    text: str

# Mappatura delle etichette del modello specifico di CardiffNLP per renderle più leggibili
# LABEL_0 -> Negative, LABEL_1 -> Neutral, LABEL_2 -> Positive)
LABEL_MAPPING = {
    "LABEL_0": "Negative",
    "LABEL_1": "Neutral",
    "LABEL_2": "Positive"
}

# 4. Definizione degli Endpoint

@app.get("/")
def home():
    """
       Endpoint di controllo per Hugging Face Spaces
    """
    return {
        "message": "Il server Machine Innovation Analysis è attivo!",
        "status": "healthy",
        "model_used": MODEL_NAME,
        "docs_url": "/docs"
    }

@app.post("/predict")
def predict_sentiment(request: TextRequest):
    """
       Endpoint per l'analisi del sentiment
    """
    if not classifier:
        raise HTTPException(status_code=500, detail="KO:modello non caricato sul server")

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Il testo fornito non può essere vuoto.")

    try:
        # Eseguiamo l'inferenza
        # result = sentiment_pipeline(request.text)[0]
        prediction,result = classifier.predict(request.text)

        # Formatta il risultato finale
        # for result in prediction:
        #     raw_label = result['label']
        #    result['sentiment'] = LABEL_MAPPING.get(raw_label, raw_label)

        # Convertiamo l'etichetta del modello in qualcosa di leggibile (se presente nella mappa)
        raw_label = result["label"]
        friendly_label = LABEL_MAPPING.get(raw_label, raw_label)

        return {
            "text": request.text,
            "sentiment": friendly_label,
            "confidence_score": round(result["score"], 4),
            "raw_label": raw_label
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante l'elaborazione: {str(e)}")

# 5. Avvio del server (obbligatorio su porta 7860 per Hugging Face)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
