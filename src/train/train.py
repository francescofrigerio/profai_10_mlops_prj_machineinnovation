"""
   Codice per eseguire il train del modello


"""
# Configuration and Parametrization
import random
import logging
import shutil

from utils.login_mlops_hf import Login

from utils import ConfigDebugConstants,ConfigProdConstants 
from utils import print_counter,init_debug_logger,test_debug_division

from evaluate import compute_metrics

# from dataclasses import dataclass, field
from transformers import set_seed

# Preprocess text (username and link placeholders)
import re
# Load dataset
from datasets import load_dataset


# metrics definitions

import numpy as np
import pandas as pd

# tonekizer definitions
from transformers import AutoTokenizer

# model and pipeline definitions
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# training
from transformers import DataCollatorWithPadding
from transformers import DataCollatorWithPadding
from transformers import Trainer, TrainingArguments

# Inferenza
import torch
from scipy.special import softmax

# fine tuning
from transformers import AutoModelForMaskedLM
from transformers import DataCollatorForLanguageModeling

# mflow for tracking
import mlflow
import mlflow.transformers

# predictions
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sns

def set_all_seeds(seed=42):
    """
        Riproducibilità dei risultati
    """
    random.seed(seed)
    np.random.seed(seed)

    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

    # determinismo CUDA
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    # HuggingFace
    set_seed(seed)

def preprocess_tweet(text):
    """
        implementa il preprocessing completo del testo 
    """

    # utenti
    text = re.sub(r'@\w+', '@user', text)
    # link
    text = re.sub(r'http\S+|www\S+', 'http', text)
    # lowercase
    text = text.lower()
    # spazi multipli
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def preprocess_function(examples):
    """
        funzione di preprocessing usando il tokenizer 
    """
    texts = [preprocess_tweet(t) for t in examples["text"]]

    return tokenizer( texts,
                      truncation=True,
                      # padding in fase di ttrainig per velocizzare
                      # padding="max_length",
                      max_length=128
                    )

def train(model):
   """
       esegue il train del modello
   """
   mlflow.set_tracking_uri("file:./mlruns")
   # 2. DEFINISCI IL NOME DELL'ESPERIMENTO
   experiment_name = "twitter_sentiment_roberta_base_2"

   # 3. RECUPERA O CREA L'ESPERIMENTO IN MODO SICURO
   experiment = mlflow.get_experiment_by_name(experiment_name)
   if experiment is None:
      experiment_id = mlflow.create_experiment(experiment_name)
   else:
      experiment_id = experiment.experiment_id

   # 4. IMPOSTA L'ESPERIMENTO ATTIVO TRAMITE IL SUO ID REALE
   mlflow.set_experiment(experiment_id=experiment_id)

   # MFlow Logging 
   # 
   # 
   #                            
   data_collator = DataCollatorWithPadding( tokenizer=tokenizer)
   # str_run_name="twitter-sentiment-roberta-debug"
   str_run_name=CONFIG.MLFLOW_RUN_NAME
   str_mode_run=CONFIG.MLFLOW_MODE_RUN
   str_dataset_type=CONFIG.MLFLOW_DATASET_TYPE

   if CONFIG.FLAG_DEBUG_MODE == True:
         # debug mode con max_steps
         logger.info("RUN TRAINING WITH DEBUG MODE")
         training_args = TrainingArguments(  output_dir=CONFIG.OUTPUT_DIR ,
                                             learning_rate=CONFIG.LEARNING_RATE,
                                             per_device_train_batch_size=CONFIG.BATCH_SIZE,
                                             per_device_eval_batch_size=CONFIG.BATCH_SIZE,
                                             num_train_epochs=CONFIG.NUM_EPOCHS ,
                                             weight_decay=CONFIG.WEIGHT_DECAY,
                                             eval_strategy="epoch",
                                             # save_strategy="epoch",
                                             save_strategy=CONFIG.SAVE_STRATEGY_MODE,
                                             metric_for_best_model="f1",
                                             load_best_model_at_end=True,
                                             save_total_limit=CONFIG.SAVE_TOTAL_LIMIT,
                                             seed=CONFIG.SEED,
                                             data_seed=CONFIG.SEED,
                                             # MLflow
                                             # report_to="mlflow",
                                             report_to=CONFIG.REPORT_TO_MODE,
                                             logging_steps=CONFIG.LOGGING_STEPS,
                                             no_cuda=CONFIG.FLAG_NO_CUDA,
                                             max_steps=CONFIG.MAX_STEPS
                                          )

         trainer = Trainer( model=model,
                                    args=training_args,
                                    # train_dataset=tokenized_dataset["train"],
                                    # eval_dataset=tokenized_dataset["validation"],
                                    train_dataset=small_train_dataset,
                                    eval_dataset=small_val_dataset,
                                    # processing_class=tokenizer,
                                    # tokenizer=tokenizer,
                                    data_collator=data_collator,
                                    compute_metrics=compute_metrics )



   else:
         logger.info("RUN TRAININ WITH PROD MODE")
         training_args = TrainingArguments(  output_dir=CONFIG.OUTPUT_DIR ,
                                    learning_rate=CONFIG.LEARNING_RATE,
                                    per_device_train_batch_size=CONFIG.BATCH_SIZE,
                                    per_device_eval_batch_size=CONFIG.BATCH_SIZE,
                                    num_train_epochs=CONFIG.NUM_EPOCHS ,
                                    weight_decay=CONFIG.WEIGHT_DECAY,
                                    eval_strategy="epoch",
                                    # save_strategy="epoch",
                                    save_strategy=CONFIG.SAVE_STRATEGY_MODE,
                                    metric_for_best_model="f1",
                                    load_best_model_at_end=True,
                                    save_total_limit=CONFIG.SAVE_TOTAL_LIMIT,
                                    seed=CONFIG.SEED,
                                    data_seed=CONFIG.SEED,
                                    # MLflow
                                    # report_to="mlflow",
                                    report_to=CONFIG.REPORT_TO_MODE,
                                    logging_steps=CONFIG.LOGGING_STEPS,
                                    no_cuda=CONFIG.FLAG_NO_CUDA
                                    )
         trainer = Trainer( model=model,
                   args=training_args,
                   train_dataset=tokenized_dataset["train"],
                   eval_dataset=tokenized_dataset["validation"],
                   # processing_class=tokenizer,
                   # tokenizer=tokenizer,
                   data_collator=data_collator,
                   compute_metrics=compute_metrics )

   with mlflow.start_run(run_name=str_run_name):
         mlflow.set_tag("mode", str_mode_run)
         mlflow.set_tag("dataset_type", str_dataset_type)

         mlflow.set_tag("project", "twitter_sentiment")
         mlflow.set_tag("framework", "huggingface")
         mlflow.set_tag("model_family", "roberta")

         # log parametri custom
         mlflow.log_param("model_name", MODEL_NAME)
         mlflow.log_param("dataset", "tweet_eval")
         mlflow.log_param("max_length", CONFIG.MAX_LENGTH)

         trainer.train()

         # valutazione sul validation
         metrics = trainer.evaluate()

         # Seleziona solo le metriche che ti interessano per il monitoraggio:
         monitoring_metrics = { "eval_accuracy": metrics.get("eval_accuracy"),
                               "eval_precision": metrics.get("eval_precision"),
                               "eval_recall": metrics.get("eval_recall"),
                               "eval_f1": metrics.get("eval_f1"),
                               "eval_loss": metrics.get("eval_loss")
                              }
         # log metriche finali
         if CONFIG.FLAG_MONITOR_METRICS:
                mlflow.log_metrics(monitoring_metrics)
         else:
                mlflow.log_metrics(metrics)

         # salva modello HuggingFace
         mlflow.transformers.log_model(transformers_model={ "model": trainer.model,
                                                               "tokenizer": tokenizer
                                                            },
                                                            artifact_path="sentiment_model-base-2"
                                          )
         # Dopo trainer.train() e il logging su mlflow
         # liberioimmediatamente i GB occupati dai checkpoint temporanei.                                                      #
         shutil.rmtree(CONFIG.OUTPUT_DIR)    





# Program entrypoint
if __name__ == '__main__':
    obj_login = Login("MachineInnovation")
    obj_login.login_hf()
    print(obj_login.get_token())

    # Init global config
    # CONFIG = ConfigProdConstants()
    CONFIG = ConfigDebugConstants()

    # Test trace levels
    print("--- Inizio Test Logging ---")
    logger = init_debug_logger()
    test_debug_division(logger,10, 2)   # Genererà DEBUG e INFO
    test_debug_division(logger,10, -2)  # Genererà DEBUG, WARNING e INFO
    test_debug_division(logger,10, 0)   # Genererà DEBUG e ERROR
    logger.setLevel(logging.INFO)

    # 1. load dataset
    dataset = load_dataset("tweet_eval", "sentiment")

    # 2. Maps dataset labels
    label_mapping = { 0: "Negative",
                      1: "Neutral",
                      2: "Positive"
                     }
    
    print_counter(dataset["train"]["label"],label_mapping,"TRAIN")
    print_counter(dataset["validation"]["label"],label_mapping,"VAL")
    print_counter(dataset["test"]["label"],label_mapping,"TEST")

    print(dataset['train'])
    print(dataset['test'])
    print(dataset['validation'])

    print(dataset['train']['text'][6])
    print(dataset['train']['label'][6])
    
    # model and tokenizer
    MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

    # Use a pipeline as a high-level helper
    # pipe = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
    pipe = pipeline("text-classification", model=MODEL_NAME)
    # tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment-latest")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    # Load model directly
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)



    dataset = load_dataset("tweet_eval", "sentiment")

    tokenized_dataset = dataset.map(preprocess_function,
                                batched=True)

    # CONFIGURAZIONE DI MlFlow
    # 1. IMPOSTA PRIMA IL TRACKING URI
    train(model,tokenizer,tokenized_dataset)



