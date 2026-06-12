""" 
   app.py 
   Service Model Serving Application
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

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
    # Usiamo la pipeline di Hugging Face per gestire tokenizzazione e inferenza
    # CLASSIFIER = SentimentPipeline(CONFIG.MODEL_DIR)
    CLASSIFIER = None

    print({"status": "Modello caricato con successo!"})
# pylint: disable=broad-exception-caught
except Exception as e:
    print(f"Errore nel caricamento del modello: {e}")
    CLASSIFIER = None

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

@app.on_event("startup")
def load_model():
    """
        this function is called when the FastAPI application starts.
        So we load the model at startup to ensure it's ready for inference
        when the first request arrives.This is a best praticse to avoid
        loading the model on demand for each request.
    """

    global CLASSIFIER
    
    # CLASSIFIER = SentimentPipeline(CONFIG.MODEL_DIR)
    # Recupera il token impostato 
    # nelle impostazioni dello Space di Hugging Face
    hf_token = os.getenv("HF_TOKEN")
    model_repo_id = "MachineInnovation/twitter-sentiment-model"
    CLASSIFIER = SentimentPipeline(model_repo_id, token=hf_token)


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

@app.get("/predict")
def predict_sentiment_from_web(text: str):
    """
        Endpoint per l'analisi del sentiment
        direttamentre da web browser o da strumenti come curl o Postman
    """
    if not CLASSIFIER:
        raise HTTPException(status_code=500, detail="KO:modello non caricato sul server")

    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Il testo fornito non può essere vuoto.")

    try:
        # Esegue l'inferenza
        _,result = CLASSIFIER.predict(text)

        # Convertiamo l'etichetta del modello in qualcosa
        # di leggibile (se presente nella mappa)
        raw_label = result["label"]
        friendly_label = LABEL_MAPPING.get(raw_label, raw_label)

        return {
            "text": text,
            "sentiment": friendly_label,
            "confidence_score": round(result["score"], 4),
            "raw_label": raw_label
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore predict_from_web: {str(e)}") from e

@app.post("/predict")
def predict_sentiment_from_app(request: TextRequest):
    """
       Endpoint per l'analisi del sentiment
       Riceve un testo in ingresso da un applicazione o via curl / Postman
       e restituisce il sentiment associato
    """
    if not CLASSIFIER:
        raise HTTPException(status_code=500, detail="KO:modello non caricato sul server")

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Il testo fornito non può essere vuoto.")

    try:
        # Esegue l'inferenza
        _,result = CLASSIFIER.predict(request.text)

        # Convertiamo l'etichetta del modello in qualcosa
        # di leggibile (se presente nella mappa)
        raw_label = result["label"]
        friendly_label = LABEL_MAPPING.get(raw_label, raw_label)

        return {
            "text": request.text,
            "sentiment": friendly_label,
            "confidence_score": round(result["score"], 4),
            "raw_label": raw_label
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore predict_from_app: {str(e)}") from e

# 5. Avvio del server (obbligatorio su porta 7860 per Hugging Face)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
