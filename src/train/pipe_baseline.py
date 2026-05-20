"""
    pipe_baseline.py
    Modulo per l'inferenza (Pipeline) usando il modello addestrato.

    Pipeline di Inferenza (pipeline.py): Un file separato 
    che prende il modello già addestrato (salvato sul disco o su MLflow) 
    e lo usa per classificare nuovi tweet reali a richiesta.

    Program entrypoint
    python train.pipeline.py DEBUG
    python train.pipeline.py PROD
"""
import argparse
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from utils.const_baseline import ConfigProdConstants,ConfigDebugConstants

# CONFIG = ConfigProdConstants()
# Usa il path dove il modello finale viene salvato (es. dopo il download da MLflow o da cartella locale stabile)
# NOTA: nel tuo train.py fai shutil.rmtree(CONFIG.OUTPUT_DIR), quindi assicurati di salvarlo 
# # in una cartella persistente se vuoi usarlo localmente!
MODEL_PATH = "./sentiment-model-final" 

def preprocess_tweet(text):
    """ Stesso preprocessing del training per consistenza dei dati """
    text = re.sub(r'@\w+', '@user', text)
    text = re.sub(r'http\S+|www\S+', 'http', text)
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

class SentimentPipeline:
    def __init__(self, model_path_or_name=MODEL_PATH):
        print(br"Caricamento del modello per l'inferenza...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path_or_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path_or_name)
        
        # Qui l'oggetto pipeline di Hugging Face esprime la sua vera utilità!
        self.nlp_pipeline = pipeline(
            "text-classification", 
            model=self.model, 
            tokenizer=self.tokenizer
        )
        
        self.label_mapping = {
            "LABEL_0": "Negative",
            "LABEL_1": "Neutral",
            "LABEL_2": "Positive"
        }

    def predict(self, tweet: str):
        """ Pulisce il testo e predice il sentiment """
        cleaned_tweet = preprocess_tweet(tweet)
        outputs = self.nlp_pipeline(cleaned_tweet)
        
        # Formatta il risultato finale
        for result in outputs:
            raw_label = result['label']
            result['sentiment'] = self.label_mapping.get(raw_label, raw_label)
        
        return outputs

if __name__ == "__main__":

    # Inizializza il parser
    parser = argparse.ArgumentParser(description="Pipeline di Training per Sentiment Analysis")

    # Definisci l'argomento (es. --mode, accettando solo DEBUG o PROD)
    parser.add_argument( '--mode',
                        type=str,
                        choices=['DEBUG', 'PROD'],
                        default='DEBUG',
                        help="Modalità di esecuzione dell'addestramento (default: DEBUG)"
                    )

    # Effettua il parse degli argomenti lanciati da terminale
    args = parser.parse_args()

    # Assegna la configurazione globale corretta in base all'input
    if args.mode == 'PROD':
        CONFIG = ConfigProdConstants()
        print("Training avviato in modalità: PRODUCTION")
    else:
        CONFIG = ConfigDebugConstants()
        print("Training avviato in modalità: DEBUG")

    # Esempio di utilizzo autonomo
    # Per testarlo prima del fine-tuning puoi usare MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    classifier = SentimentPipeline("cardiffnlp/twitter-roberta-base-sentiment-latest")
    
    test_tweet = "I love this new MLOps course! @HuggingFace http://example.com"
    prediction = classifier.predict(test_tweet)
    print(f"Tweet: {test_tweet}")
    print(f"Risultato: {prediction}")