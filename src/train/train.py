"""
   Codice per eseguire il train del modello
"""
# Configuration and Parametrization
import random
import logging
import shutil

# Preprocess text (username and link placeholders)
import re

# Export dati su db sqlite
import sqlite3
from datetime import datetime

# metrics definitions
import numpy as np
# import pandas as pd

from metrics import compute_metrics
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
from scipy.special import softmax

# fine tuning
# from transformers import AutoModelForMaskedLM
# from transformers import DataCollatorForLanguageModeling

# mflow for tracking
import mlflow
import mlflow.transformers

# predictions
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import label_binarize
from sklearn.metrics import roc_curve, auc


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

class_names = [label_mapping[i] for i in range(CONFIG.NUM_CLASSES)]

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

def test_baseline(trainer_,
                  tokenized_dataset_):
    """
        run test on tokenized_dataset
    """
    # valutazione sui dati di test
    test_metrics = trainer_.evaluate( eval_dataset=tokenized_dataset_["test"])

    logger.info("\nTEST METRICS")
    for key, value in test_metrics.items():
        logger.info(f"{key}: {value}")

    # Logging MLflow
    mlflow.log_metrics({ "test_accuracy": test_metrics.get("eval_accuracy"),
                         "test_loss": test_metrics.get("eval_loss"),
                         "test_precision": test_metrics.get("eval_precision"),
                         "test_recall": test_metrics.get("eval_recall"),
                         "test_f1": test_metrics.get("eval_f1")
                        })
    return test_metrics

def plot_confusion_matrix(trainer_):
    """
        plot confusion matrix on test data
    """
    predictions = trainer_.predict(tokenized_dataset["test"])

    y_true = predictions.label_ids
    y_pred = np.argmax(predictions.predictions, axis=1)

    cm = confusion_matrix(y_true, y_pred)

    plt.figure(figsize=(6,6))
    sns.heatmap(cm, annot=True, fmt="d")
    plt.title("Confusion Matrix")

    plt.savefig("confusion_matrix.png")
    mlflow.log_artifact("confusion_matrix.png")


def plot_roc_curve(trainer_):
    """
        Ripassare la logica e le definizioni
        ROC richiede score/probabilità continue
        NON classi discrete
    """
    predictions = trainer_.predict(tokenized_dataset["test"])
    # labels reali
    y_true = predictions.label_ids
    # KO sono valori discreti
    # y_pred = np.argmax(predictions.predictions, axis=1)
    # logits del modello
    logits = predictions.predictions

    # probabilità softmax
    y_scores = softmax(logits, axis=1)

    # Binarizza labels/target (es: la classe 2 diventa [0, 0, 1, 0...])
    n_classes = CONFIG.NUM_CLASSES
    y_true_bin = label_binarize(y_true, classes=range(n_classes))

    # Inizializza dizionari per memorizzare FPR, TPR e AUC per ogni classe
    # fpr = dict()
    # tpr = dict()
    # roc_auc = dict()
    fpr = {}
    tpr = {}
    roc_auc = {}

    # 2. Calcola la curva ROC per ogni singola classe (One-vs-Rest)
    for i in range(n_classes):
        # y_scores sono le probabilità (output softmax)
        # devo essere convertite in array numpy dal chiamante o nel train
        fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], y_scores[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])

        # 3. Calcola la Micro-Average ROC curve (opzionale, aggrega tutto)
        fpr["micro"], tpr["micro"], _ = roc_curve(y_true_bin.ravel(), y_scores.ravel())
        roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

        # 4. Plotting
        plt.figure(figsize=(10, 8))

        # Plot della curva Micro-Average
        plt.plot(fpr["micro"], tpr["micro"],
                  label=f'micro-average ROC curve (area = {roc_auc["micro"]:0.2f})',
                  color='deeppink', linestyle=':', linewidth=4)

        # Plot delle curve per alcune classi specifiche (o tutte, ma 37 sono tante!)
        # Esempio: mostriamo solo le prime 3 classi per non intasare il grafico
        colors = ['aqua', 'darkorange', 'cornflowerblue']
        for i, color in zip(range(3), colors):
            plt.plot(fpr[i], tpr[i], color=color, lw=2,
                      # label=f'ROC curve class {class_map[str(i+1)]} (area = {roc_auc[i]:0.2f})')
                      label=f'ROC curve class {class_names[str(i)]} (area = {roc_auc[i]:0.2f})')

        plt.plot([0, 1], [0, 1], 'k--', lw=2)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic (ROC) Multiclass')
        plt.legend(loc="lower right")
        plt.grid(True)
        plt.show()

def create_table_baseline(path_connect="metrics.db"):
    """
        Creazione tabella SQLite
        path_connect="metrics.db"
        path_connect="/content/drive/MyDrive/my_project/metrics.db"
    """

    conn = sqlite3.connect(path_connect)
    # End Creazione del db se non esiste crea il file

    # Start Creazione una tabella model_metrics_baseline
    cursor = conn.cursor()

    if CONFIG.FLAG_DROP_EXPORT_TABLE:
        cursor.execute("DROP TABLE IF EXISTS model_metrics_baseline")

    if CONFIG.FLAG_CREATE_EXPORT_TABLE:
        cursor.execute("""CREATE TABLE IF NOT EXISTS model_metrics_baseline (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  dom_name TEXT,
                  exp_id TEXT,
                  accuracy REAL,
                  precision REAL,
                  recall REAL,
                  f1_score REAL
                  )
                  """)

    conn.commit()
    conn.close()
    # End Creazione una tabella model_metrics_baseline

def insert_table_baseline(metrics,
                          exp_obj,
                          path_connect="metrics.db"):
    """
        Inserisci i dati in tabella a partire
        dalle metriche ritornate dal training/test
        e dall'experimenti id determinato
        a partire dal nome dell'esperimento di MLflow
    """
    # Estrai i dati dal dizionario metrics del trainer
    # Assicurati che le chiavi corrispondano a quelle calcolate in compute_metrics
    acc = metrics.get("eval_accuracy", 0)
    prec = metrics.get("eval_precision", 0)
    rec = metrics.get("eval_recall", 0)
    f1 = metrics.get("eval_f1", 0)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dom_name = CONFIG.MLFLOW_RUN_NAME
    # Recupera l'ID di MLflow
    # exp_obj = mlflow.get_experiment_by_name(experiment_name)
    if exp_obj is not None:
        exp_id = exp_obj.experiment_id
    else:
        exp_id = "N/A"

    conn = sqlite3.connect(path_connect)
    cursor = conn.cursor()

    # Inserimento manuale
    cursor.execute("""INSERT INTO model_metrics_baseline
                      (timestamp, dom_name,accuracy, precision, recall, f1_score)
                      VALUES (?,?,? , ?, ?, ?, ?)
                   """,
                   (timestamp,dom_name,exp_id, acc, prec, rec, f1))

    conn.commit()
    conn.close()

def train_baseline( model_ ,
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

    data_collator = DataCollatorWithPadding( tokenizer=tokenizer)

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
        train_metrics = trainer.evaluate()

        # Seleziona solo le metriche che ti interessano per il monitoraggio:
        monitoring_metrics = { "eval_accuracy": train_metrics.get("eval_accuracy"),
                               "eval_precision": train_metrics.get("eval_precision"),
                               "eval_recall": train_metrics.get("eval_recall"),
                               "eval_f1": train_metrics.get("eval_f1"),
                               "eval_loss": train_metrics.get("eval_loss")
                              }
        # log metriche finali
        if CONFIG.FLAG_MONITOR_METRICS:
            mlflow.log_metrics(monitoring_metrics)
        else:
            mlflow.log_metrics(train_metrics)

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

    # grafici sui dati di test
    plot_confusion_matrix(trainer)
    plot_roc_curve(trainer)

    test_metrics = test_baseline(trainer,tokenized_dataset)

    # start export to sqllite
    create_table_baseline()
    insert_table_baseline(train_metrics,
                          mlflow.get_experiment_by_name(experiment_name))
    insert_table_baseline(test_metrics,
                          mlflow.get_experiment_by_name(experiment_name))
    # end export to sqllite

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

    logger.info(f"{dataset['train']}")
    logger.info(f"{dataset['test']}")
    logger.info(f"{dataset['validation']}")
    # print(dataset['test'])
    # print(dataset['validation'])

    logger.info(f"{dataset['train']['text'][6]}")
    logger.info(f"{dataset['train']['label'][6]}")

    # model and tokenizer
    # Use a pipeline as a high-level helper
    pipe = pipeline("text-classification", model=MODEL_NAME)

    # Load model directly
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    dataset = load_dataset("tweet_eval", "sentiment")

    tokenized_dataset = dataset.map(preprocess_function,
                                    batched=True)

    if CONFIG.FLAG_DEBUG_MODE:
        # debug mode con max_steps
        logger.info("START RUN TRAIN WITH DEBUG MODE")
        small_train_dataset = tokenized_dataset["train"].shuffle(
                                                            seed=CONFIG.SEED
                                                            ).select (
                                                            range(CONFIG.SMALL_TRAIN_DATASET_SIZE)
                                                            )

        small_val_dataset = tokenized_dataset["validation"].shuffle (
                                                        seed=CONFIG.SEED
                                                        ).select (
                                                             range(CONFIG.SMALL_VAL_DATASET_SIZE)
                                                            )

        train_baseline(model,
                       small_train_dataset,
                       small_val_dataset )
        logger.info("END RUN TRAIN WITH DEBUG MODE")
    else:
        logger.info("RUN TRAIN WITH PROD MODE")
        train_baseline(model,
                   tokenized_dataset["train"],
                   tokenized_dataset["validation"] )
        logger.info("END TRAIN WITH PROD MODE")
