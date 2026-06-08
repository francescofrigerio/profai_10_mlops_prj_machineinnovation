"""
   Integration tests for the Sentiment Analysis API.
   python -m pytest ci_cd/CI/test_integration_api.py -v
"""
import os
import sys
# Trova la root del progetto e aggiunge 'model_serving' al path di sistema
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../model_serving")))
import pytest
from fastapi.testclient import TestClient
from transformers import (  AutoModelForSequenceClassification,
                             AutoTokenizer)                            
# Disabila pylint solo per questo import perché Pylint non vede il path dinamico
# try:
#     from app import app  # pylint: disable=import-error
# except ImportError:
#     # Fallback per permettere l'analisi statica se necessario
#     app = None

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# client = TestClient(app)
# @pytest.fixture(scope="class")
def client(monkeypatch):
    """
        Crea un TestClient gestendo correttamente gli eventi di startup e shutdown.
    """

    from app import CONFIG, MODEL_NAME
    
    # Sovrascrive il path locale con l'ID online per evitare l'OSError
    monkeypatch.setattr(CONFIG, "MODEL_DIR", MODEL_NAME)

    # Il blocco 'with' triggera l'evento @app.on_event("startup")
    with TestClient(app) as test_client:
        yield test_client

# MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# @pytest.fixture(scope="session")
# def model_and_tokenizer():
#     """
#          Carica Model e tokenizer una volta sola
#     """
#     tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
#     model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
# 
#     return model, tokenizer

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
        assert "label" in data

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
