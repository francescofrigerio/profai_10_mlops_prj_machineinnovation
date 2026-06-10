"""
   Integration tests for the Sentiment Analysis API.
   python -m pytest ci_cd/CI/test_integration_api.py -v
"""
import os
import sys
import random
# Trova la root del progetto e aggiunge 'model_serving' al path di sistema
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../model_serving")))
import pytest
from fastapi.testclient import TestClient
from transformers import (  AutoModelForSequenceClassification,
                             AutoTokenizer)                            
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

@pytest.fixture
def client(monkeypatch):

    class MockPipeline:
        """ 
            Con questa classe 
            quando lo startup di app.py esegue
                CLASSIFIER = SentimentPipeline(CONFIG.MODEL_DIR)
            in realtà costruisce:
                CLASSIFIER = MockPipeline(CONFIG.MODEL_DIR)
        """
        
        def __init__(self, *args, **kwargs):
            print("MOCK PIPELINE CREATA")

        # def predict(self, text):
        #
        #    sentiment = random.choice(["positive", "negative", "neutral"])
        #
        #    return {
        #        "label": sentiment,
        #        "sentiment": sentiment
        #    }
        def predict(self, text):
            # Scegliamo un'etichetta coerente con la LABEL_MAPPING di app.py (LABEL_0, LABEL_1, LABEL_2)
            raw_label = random.choice(["LABEL_0", "LABEL_1", "LABEL_2"])
            
            # app.py si aspetta che result contenga "label" e "score"
            result = {
                "label": raw_label,
                "score": 0.9876
            }
            # app.py fa: _, result = CLASSIFIER.predict(text). Ritorniamo una tupla.
            return None, result

    # importa tutto il modulo non solo l'oggetto
    # from app import app
    import app
    # app.CLASSIFIER = MockPipeline()
    # monkeypatch.setattr("app.CLASSIFIER",MockPipeline())
    # monkeypatch.setattr(app,"CLASSIFIER",MockPipeline())
    monkeypatch.setattr(app, "SentimentPipeline", MockPipeline)
    
    with TestClient(app.app) as client:
        yield client

class TestIntegrationApi:
    """
        Class to test the integration of different components of the application
    """
    def test_1_home(self,client):
        """ 
             test home to be sure deploy was succesful
        """
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
 

    def test_2_post(self,client):
        """
              test predict post endpoint
        """
        response = client.post( "/predict",
                                json={
                                "text": "I love this movie"
                                })
        assert response.status_code == 200
        data = response.json()
        
        assert "sentiment" in data
        assert "raw_label" in data

    def test_3_get(self,client):
        """
              test predict get endpoint
        """
        response = client.get("/predict",params={"text": "I love this movie"})
        response = client.get("/predict?text=I love this movie")
        assert response.status_code == 200
        data = response.json()
        assert "sentiment" in data

    def test_9_predict_empty(self,client):
        """
            test predict endpoint with empty text
        """
        response = client.post("/predict", json={
                                            "text": ""
                                            })
        assert response.status_code == 400
