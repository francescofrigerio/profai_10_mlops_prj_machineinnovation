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

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

def preprocess_tweet(text):
    """ Stesso preprocessing del training per consistenza dei dati """
    text = re.sub(r'@\w+', '@user', text)
    text = re.sub(r'http\S+|www\S+', 'http', text)
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

class SentimentPipeline:
    """
        SentimentPipeline Class (for inference)
    """
    def __init__(self, model_path_or_name=""):
        """
            Inizalizza la classe che implementa la pipeline
        """
        print(br"Caricamento del modello per l'inferenza...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path_or_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path_or_name)

        # uso l'oggetto pipeline di Hugging Face
        self.nlp_pipeline = pipeline("text-classification",
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

    def predict_batch(self, tweets: list[str]):
        """ 
            Predice il sentiment per una lista di tweet 
        """
        cleaned_tweets = [preprocess_tweet(t) for t in tweets]
        outputs = self.nlp_pipeline(cleaned_tweets)

        # Gestisce l'output flat o nested
        # a seconda di come Hugging Face restituisce il batch
        for result in outputs:
            if isinstance(result, list):
                for res in result:
                    res['sentiment'] = self.label_mapping.get(res['label'], res['label'])
            else:
                result['sentiment'] = self.label_mapping.get(result['label'], result['label'])

        return outputs

if __name__ == "__main__":

    # Inizializza il parser
    parser = argparse.ArgumentParser(description="Pipeline di Inferenza per Sentiment Analysis")

    # Definisci l'argomento (es. --mode, accettando solo DEBUG o PROD)
    parser.add_argument( '--mode',
                        type=str,
                        choices=['DEBUG', 'PROD'],
                        default='DEBUG',
                        help="Modalità di esecuzione dell'inferenza (default: DEBUG)"
                    )

    # Effettua il parse degli argomenti lanciati da terminale
    args = parser.parse_args()

    # Assegna la configurazione globale corretta in base all'input
    if args.mode == 'PROD':
        CONFIG = ConfigProdConstants()
        print("Inferenza avviato in modalità: PRODUCTION")
    else:
        CONFIG = ConfigDebugConstants()
        print("Inferenza avviato in modalità: DEBUG")

    MODEL_PATH = CONFIG.OUTPUT_DIR
    # Esempio di utilizzo
    # classifier = SentimentPipeline(MODEL_NAME)
    if args.mode == 'PROD':
        classifier = SentimentPipeline(MODEL_PATH)
    else:
        # classifier = SentimentPipeline(MODEL_NAME)
        classifier = SentimentPipeline(MODEL_PATH)

    TEST_TWEET = "I love this new MLOps course! @HuggingFace http://example.com"
    prediction = classifier.predict(TEST_TWEET)
    print(f"Tweet: {TEST_TWEET}")
    print(f"Risultato: {prediction}")
