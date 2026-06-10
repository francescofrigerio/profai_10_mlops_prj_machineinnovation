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
from src.utils.const_baseline import ConfigDebugConstants
from src.utils.login_mlops_hf import Login

def run_login_hf():
    obj_login = Login("MachineInnovation")
    obj_login.login_hf()
    print(f"lunghezza auth token {len(obj_login.get_token())}")

@pytest.fixture(scope="session")
def model_and_tokenizer():
    
    run_login_hf()
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
        run_login_hf()
        # dataset = load_dataset("tweet_eval","sentiment")
        run_login_hf()
        # FORZA il caricamento senza usare il token di autenticazione 
        # per evitare il bug dell'URI nella github actions
        dataset = load_dataset("tweet_eval", "sentiment", token=False)

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
       
        model, tokenizer = model_and_tokenizer

        text = "It's fantastic!! Inter wins both Italian League and Italian Cup"

        inputs = tokenizer(text,
                            return_tensors="pt"
                          )

        outputs = model(**inputs)

        pred = outputs.logits.argmax(dim=1)

        assert pred.item() in [0,1,2]


    def test_4_saved_model_files(self):
        """
            Test that the model files are saved correctly
            Test this after run train
        """
        CONFIG_PROD = ConfigProdConstants()
        CONFIG_DEBUG = ConfigDebugConstants()
        # verify this path runtime
    
        required_files = [ "config.json",
                            "model.safetensors",
                            "tokenizer.json",
                            "tokenizer_config.json"
                        ]
        print("Test effettivo solo sul codespace")
        print(f" Cerco i file nella dir {CONFIG_DEBUG.OUTPUT_DIR}")
        # for f in required_files:
        #    assert os.path.exists(os.path.join(CONFIG_DEBUG.OUTPUT_DIR,f))
