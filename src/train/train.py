"""
   Codice per eseguire il train del modello


"""
# Configuration and Parametrization
import random
import logging
import shutil

# Preprocess text (username and link placeholders)
import re

# metrics definitions
import numpy as np
# import pandas as pd

from evaluate import compute_metrics

# from dataclasses import dataclass, field



# Load dataset
from datasets import load_dataset




# tokenizer definitions
# model and pipeline definitions
# from transformers import pipeline
# from transformers import AutoTokenizer, AutoModelForSequenceClassification
# from transformers import set_seed
# training
# from transformers import DataCollatorWithPadding
# from transformers import Trainer, TrainingArguments

from transformers import (  AutoModelForSequenceClassification,
                            AutoTokenizer,
                            DataCollatorWithPadding,
                            Trainer,
                            TrainingArguments,
                            pipeline,
                            set_seed )

# Inferenza
import torch
# from scipy.special import softmax

# fine tuning
# from transformers import AutoModelForMaskedLM
# from transformers import DataCollatorForLanguageModeling

# mflow for tracking
import mlflow
import mlflow.transformers

# predictions
# import matplotlib.pyplot as plt
# from sklearn.metrics import confusion_matrix
# import seaborn as sns

from utils.login_mlops_hf import Login
from utils.constants import ConfigDebugConstants,ConfigProdConstants
from utils.utils import print_counter,init_debug_logger,test_debug_division

# Init global config
CONFIG_ = ConfigProdConstants()
CONFIG = ConfigDebugConstants()

# Init global logger
logger = init_debug_logger()

# Init global Maps dataset labels
label_mapping = { 0: "Negative",
                  1: "Neutral",
                  2: "Positive"
                }
# model and tokenizer
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

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

def train_baseline( model_ ,
                    tokenizer_,
                    train_dataset_,
                    val_dataset_ ):
    """
        esegue il train del modello
    """

    # CONFIGURAZIONE DI MlFlow
    # 1. IMPOSTA PRIMA IL TRACKING URI
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
    data_collator = DataCollatorWithPadding( tokenizer=tokenizer)
    # str_run_name="twitter-sentiment-roberta-debug"
    str_run_name=CONFIG.MLFLOW_RUN_NAME
    str_mode_run=CONFIG.MLFLOW_MODE_RUN
    str_dataset_type=CONFIG.MLFLOW_DATASET_TYPE

    data_collator = DataCollatorWithPadding( tokenizer=tokenizer_)

    if CONFIG.FLAG_DEBUG_MODE:
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
                                             report_to=CONFIG.REPORT_TO_MODE,
                                             logging_steps=CONFIG.LOGGING_STEPS,
                                             # no_cuda=CONFIG.FLAG_NO_CUDA,
                                             use_cpu=CONFIG.FLAG_USE_CPU,
                                             max_steps=CONFIG.MAX_STEPS
                                          )

        trainer = Trainer( model=model_,
                                    args=training_args,
                                    train_dataset=train_dataset_,
                                    eval_dataset=val_dataset_,
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
                                    save_strategy=CONFIG.SAVE_STRATEGY_MODE,
                                    metric_for_best_model="f1",
                                    load_best_model_at_end=True,
                                    save_total_limit=CONFIG.SAVE_TOTAL_LIMIT,
                                    seed=CONFIG.SEED,
                                    data_seed=CONFIG.SEED,
                                    # MLflow
                                    report_to=CONFIG.REPORT_TO_MODE,
                                    logging_steps=CONFIG.LOGGING_STEPS,
                                    # no_cuda=CONFIG.FLAG_NO_CUDA
                                    use_cpu=CONFIG.FLAG_USE_CPU
                                    )
        trainer = Trainer( model=model_,
                   args=training_args,
                   train_dataset=train_dataset_,
                   eval_dataset=val_dataset_,
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
        mlflow.transformers.log_model(
                                        transformers_model={ "model": trainer.model,
                                                             "tokenizer": tokenizer
                                                        },
                                        artifact_path="sentiment_model-base-2"
                                    )
        # Dopo trainer.train() e il logging su mlflow
        # liberioimmediatamente i GB occupati dai checkpoint temporanei.
        shutil.rmtree(CONFIG.OUTPUT_DIR)

# Program entrypoint
# python train.train_baseline.py DEBUG
# PYTHONPATH=. pylint train/train.py
if __name__ == '__main__':
    obj_login = Login("MachineInnovation")
    obj_login.login_hf()
    print(obj_login.get_token())

    set_all_seeds(CONFIG.SEED)

    # Test trace levels
    print("--- Inizio Test Logging ---")
    test_debug_division(logger,10, 2)   # Genera DEBUG e INFO
    test_debug_division(logger,10, -2)  # Genera DEBUG, WARNING e INFO
    test_debug_division(logger,10, 0)   # Genera DEBUG e ERROR
    logger.setLevel(logging.INFO)

    # 1. load dataset
    dataset = load_dataset("tweet_eval", "sentiment")



    print_counter(dataset["train"]["label"],label_mapping,"TRAIN")
    print_counter(dataset["validation"]["label"],label_mapping,"VAL")
    print_counter(dataset["test"]["label"],label_mapping,"TEST")

    print(dataset['train'])
    print(dataset['test'])
    print(dataset['validation'])

    print(dataset['train']['text'][6])
    print(dataset['train']['label'][6])

    # model and tokenizer
    # Use a pipeline as a high-level helper
    pipe = pipeline("text-classification", model=MODEL_NAME)

    # Load model directly
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    dataset = load_dataset("tweet_eval", "sentiment")

    tokenized_dataset = dataset.map(preprocess_function,
                                    batched=True
                                    )

    if CONFIG.FLAG_DEBUG_MODE:
        # debug mode con max_steps
        logger.info("RUN TRAIN WITH DEBUG MODE")
        small_train_dataset = tokenized_dataset["train"].shuffle(
                                                            seed=CONFIG.SEED
                                                            ).select (
                                                            range(CONFIG.SMALL_TRAIN_DATASET_SIZE))

        small_val_dataset = tokenized_dataset["validation"].shuffle (
                                                        seed=CONFIG.SEED
                                                        ).select (

                                                             range(CONFIG.SMALL_VAL_DATASET_SIZE))

        train_baseline(model,
                   tokenizer,
                   small_train_dataset,
                   small_val_dataset )
    else:
        logger.info("RUN TRAIN WITH PROD MODE")
        train_baseline(model,
                   tokenizer,
                   tokenized_dataset["train"],
                   tokenized_dataset["validation"] )
