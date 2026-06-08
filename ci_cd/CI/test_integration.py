"""
   python -m pytest ci_cd/CI/test_integration.py -v
"""
import os
import pytest
from datasets import load_dataset

# tokenizer definitions
# model and pipeline definitions
# from transformers import (  AutoModelForSequenceClassification,
#                             AutoTokenizer,
#                            pipeline )
from transformers import (  AutoModelForSequenceClassification,
                            AutoTokenizer )

import torch

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import uvicorn


from src.utils.const_baseline import ConfigProdConstants

@pytest.fixture(scope="session")
def model_and_tokenizer():

    MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

    return model, tokenizer

class TestIntegration:
    """
        Class to test the integration of different components of the application
    """
    
    def test_1_dataset_loading(self,model_and_tokenizer):
        """
            Test loadinf of the dataset
        """
        dataset = load_dataset("tweet_eval","sentiment")

        assert len(dataset["train"]) > 0

    def test_2_model_and_tokenizer(self,model_and_tokenizer):
        """
           Test compatibnility between model and tokenizer
        """
        # MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        # tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        # model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        model, tokenizer = model_and_tokenizer

        text = "I love this project"

        inputs = tokenizer(text,return_tensors="pt")
        outputs = model(**inputs)
        # print(outputs.logits.shape)
        assert outputs.logits.shape[-1] == 3

    def test_3_pipeline_my(self,model_and_tokenizer):
        """
            Test prediction pipeline not based on HF
        """
        # MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        # tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        # model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        model, tokenizer = model_and_tokenizer

        text = "It's fantastic!! Inter wins both Italian League and Italian Cup"

        inputs = tokenizer(text,
                            return_tensors="pt"
                          )

        outputs = model(**inputs)

        pred = outputs.logits.argmax(dim=1)

        assert pred.item() in [0,1,2]

#     def test_4_pipeline_hf(self):
#         """
#             Test prediction pipeline based on HF
#         """
        # MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        # tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        # model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
#        model, tokenizer = model_and_tokenizer

        # uso l'oggetto pipeline di Hugging Face
#        nlp_pipeline = pipeline("text-classification",
#                                 model=self.model,
#                                 tokenizer=self.tokenizer
#                                 )

#         text = "It's fantastic!! Inter wins both Italian League and Italian Cup"
#         outputs = nlp_pipeline(text)
#         
#         pred = outputs.logits.argmax(dim=1)
#         assert pred.item() in [0,1,2]
# 
    def test_5_saved_model_files(self):
        """
            Test that the model files are saved correctly
        """
        CONFIG = ConfigProdConstants()
        # verify this path runtime
    
        required_files = [ "config.json",
                            "model.safetensors",
                            "tokenizer.json",
                            "tokenizer_config.json"
                        ]

        for f in required_files:
            assert os.path.exists(os.path.join(CONFIG.OUTPUT_DIR,f))

    
#    from app import app
#    client = TestClient(app)
#    
#    def test_6_home(self):
#       """ 
#            test home to be sure deploy was succesful
#       """
#       response = client.get("/")
#       assert response.status_code == 200
#       data = response.json()
#       assert data["status"] == "healthy"
#
#
#    def test_7_post(self):
#        """
#             test predict post endpoint
#        """
#        response = client.post(
#             "/predict",
#             json={
#                 "text": "I love this movie"
#             }
#        )
#        assert response.status_code == 200
#        data = response.json()
#        assert "label" in data
#
#    def test_8_get(self):
#        """
#             test predict get endpoint
#        """
#        # response = client.get("/predict",params={"text": "I love this movie"}
#        response = client.get("/predict?text=I love this movie")
#
#        assert response.status_code == 200
#        data = response.json()
#        assert "label" in data
#    
#    def test_predict_empty(self):
#        """
#            test predict endpoint with empty text
#        """
#        response = client.post("/predict",
#                                json={
#                                "text": ""
#                                })
#    assert response.status_code == 400

