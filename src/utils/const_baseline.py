"""
    const_baseline
    Definzioni delle costanti usate in training evaluate e pipeline
"""
from pathlib import Path

from dataclasses import dataclass

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# pylint: disable=invalid-name,too-many-instance-attributes
@dataclass(frozen=True)
class ConfigDebugConstants:
    """
    Global Config. Const of Environment
    Substiutes magic numbers with description names
    """

    NUM_CLASSES: int = 3
    SMALL_TRAIN_DATASET_SIZE: int = 500
    SMALL_VAL_DATASET_SIZE: int = 100
    MAX_LENGTH: int = 48
    # New field for seed so we can reproduce the results
    SEED: int = 42

    # Training
    OUTPUT_DIR = PROJECT_ROOT / "outputs-baseline-debug"
    LEARNING_RATE: float = 2e-5
    BATCH_SIZE: int = 4
    NUM_EPOCHS: int = 1
    WEIGHT_DECAY: float = 0.01
    SAVE_TOTAL_LIMIT: int = 1
    LOGGING_STEPS: int = 5
    # le due strategie devono essere uguali
    # in caso di FLAG_LOAD_BEST_MODEL = True
    EVAL_STRATEGY_MODE: str = "steps"
    SAVE_STRATEGY_MODE: str = "steps"
    REPORT_TO_MODE: str = "mlflow"
    MLFLOW_DIR = PROJECT_ROOT / "mlruns-debug"
    MLFLOW_RUN_NAME: str = "twitter-sentiment-roberta-debug"
    MLFLOW_MODE_RUN: str = "DEBUG"
    MLFLOW_DATASET_TYPE: str = "SMALL"
    MLFLOW_ARTIFACT_PATH: str = "out-model-baseline-debug"

    FLAG_LOAD_BEST_MODEL: bool = True
    FLAG_USE_CPU: bool = True
    MAX_STEPS: int = 20
    FLAG_DEBUG_MODE: bool = True
    FLAG_MONITOR_METRICS: bool = False

    # Export table
    FLAG_DROP_EXPORT_TABLE: bool = True
    FLAG_CREATE_EXPORT_TABLE: bool = True
    # In ConfigDebugConstants
    METRICS_DB_PATH: str = "metrics_debug.db"

    # Model Serving
    MODEL_DIR: str = PROJECT_ROOT / "model-debug"


# SETUP CONFIGURAZIONE
# pylint: disable=invalid-name,too-many-instance-attributes
@dataclass(frozen=True)
class ConfigProdConstants:
    """
    Global Config. Const of Environment
    """
    NUM_CLASSES: int = 3
    # MAX_LENGTH: int = 128
    MAX_LENGTH: int = 48
    # New field for seed so we can reproduce the results
    SEED: int = 42

    # Training
    OUTPUT_DIR = PROJECT_ROOT / "outputs-baseline-prod"
    
    LEARNING_RATE:float = 2e-5
    # Non ho abbastanza memoria x aumentare
    BATCH_SIZE: int= 16
    # NUM_EPOCHS: int = 3
    NUM_EPOCHS: int = 2
    WEIGHT_DECAY: float = 0.01
    SAVE_TOTAL_LIMIT: int = 2
    LOGGING_STEPS: int = 50
    # le due strategie devono essere uguali
    # in caso di FLAG_LOAD_BEST_MODEL = True
    EVAL_STRATEGY_MODE: str = "epoch"
    SAVE_STRATEGY_MODE: str = "epoch"
    REPORT_TO_MODE: str = "mlflow"
    MLFLOW_DIR = PROJECT_ROOT / "mlruns-prod"
    MLFLOW_RUN_NAME: str = "twitter-sentiment-roberta-prod"
    MLFLOW_MODE_RUN: str = "PROD"
    MLFLOW_DATASET_TYPE: str = "ALL"
    MLFLOW_ARTIFACT_PATH: str = "out-model-baseline-prod"

    FLAG_LOAD_BEST_MODEL: bool = True
    FLAG_USE_CPU: bool = False
    FLAG_DEBUG_MODE: bool= False
    FLAG_MONITOR_METRICS: bool =True

    # Export table
    FLAG_DROP_EXPORT_TABLE: bool = True
    FLAG_CREATE_EXPORT_TABLE: bool = True
    # In ConfigProdConstants (magari in produzione punta a una cartella di rete o un volume persistente)
    METRICS_DB_PATH: str = "metrics_prod.db"

    # Model Serving
    MODEL_DIR: str = PROJECT_ROOT / "model-prod"

