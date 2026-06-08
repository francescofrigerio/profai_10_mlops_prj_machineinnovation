"""
   python -m pytest ci_cd/CI/test_integration.py -v
"""
import os
import pytest
from datasets import load_dataset

# tokenizer definitions
# model and pipeline definitions
from transformers import (  AutoModelForSequenceClassification,
                            AutoTokenizer,
                            pipeline )

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

class TestIntegrationPipe:
    """
        Class to test the integration of different components of the application
    """
    
    def test_1_pipeline_my(self,model_and_tokenizer):
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

    def test_2_pipeline_hf(self,model_and_tokenizer):
        """
             Test prediction pipeline based on HF
        """
        # MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        # tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        # model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        model, tokenizer = model_and_tokenizer

        # uso l'oggetto pipeline di Hugging Face
        # La pipeline di Hugging Face è un'astrazione di alto livello: 
        # prende il testo, 
        # tokenizza il testo, 
        # passa il testo tokenizzato al modello, 
        # applica la funzione di attivazione (Softmax) 
        # trasforma l'output in una lista di dizionari Python.
        # Quando si scrive outputs = nlp_pipeline(text), 
        # la variabile outputs non contiene i logit, ma una lista come:
        
        #  [{'label': 'positive', 'score': 0.9887862205505371}]
        nlp_pipeline = pipeline("text-classification",
                                 model=model,
                                 tokenizer=tokenizer
                                 )

        text = "It's fantastic!! Inter wins both Italian League and Italian Cup"
        outputs = nlp_pipeline(text)
        # x visualizzare le print passare in input -s
        # print(f"outputs {outputs}")
        # outputs [{'label': 'positive', 'score': 0.9887862205505371}]
        # pred = outputs.logits.argmax(dim=1)
        # assert pred.item() in [0,1,2]
        # Verifics che l'output sia una lista non vuota
        assert isinstance(outputs, list)
        assert len(outputs) > 0
        
        # Estrae il dizionario del primo (e unico) testo passato
        result = outputs[0]
        assert "label" in result
        assert "score" in result
        
        # Verifica che il punteggio di confidenza sia valido (tra 0 e 1)
        assert 0.0 <= result["score"] <= 1.0
        
        #  restituisce una label in formato str
        assert isinstance(result["label"], str)
        assert result["label"] in ('positive','negative','neutral')
 
    
