"""
    const_baseline
    Definzioni delle costanti usate in training evaluate e pipeline
"""
from dataclasses import dataclass

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
    MAX_LENGTH: int = 64
    # New field for seed so we can reproduce the results
    SEED: int = 42

    # Training
    OUTPUT_DIR: str = "./outputs-baseline-debug"
    LEARNING_RATE: float = 2e-5
    BATCH_SIZE: int = 4
    NUM_EPOCHS: int = 1
    WEIGHT_DECAY: float = 0.01
    SAVE_TOTAL_LIMIT: int = 1
    LOGGING_STEPS: int = 5
    SAVE_STRATEGY_MODE: str = "no"
    REPORT_TO_MODE: str = "mlflow"
    MLFLOW_RUN_NAME: str = "twitter-sentiment-roberta-debug"
    MLFLOW_MODE_RUN: str = "DEBUG"
    MLFLOW_DATASET_TYPE: str = "SMALL"
    MLFLOW_ARTIFACT_PATH: str = "out-model-baseline-debug"
    FLAG_USE_CPU: bool = True
    MAX_STEPS: int = 20
    FLAG_DEBUG_MODE: bool = True
    FLAG_MONITOR_METRICS: bool = True

    # Export table
    FLAG_DROP_EXPORT_TABLE: bool = True
    FLAG_CREATE_EXPORT_TABLE: bool = True
    # In ConfigDebugConstants
    METRICS_DB_PATH: str = "metrics_debug.db"


# SETUP CONFIGURAZIONE
# pylint: disable=invalid-name,too-many-instance-attributes
@dataclass(frozen=True)
class ConfigProdConstants:
    """
    Global Config. Const of Environment
    """
    NUM_CLASSES: int = 3
    MAX_LENGTH: int = 128
    # New field for seed so we can reproduce the results
    SEED: int = 42

    # Training
    OUTPUT_DIR: str = "./outputs-baseline-prod"
    LEARNING_RATE:float = 2e-5
    BATCH_SIZE: int= 16
    NUM_EPOCHS: int = 3
    WEIGHT_DECAY: float = 0.01
    SAVE_TOTAL_LIMIT: int = 2
    LOGGING_STEPS: int = 50
    SAVE_STRATEGY_MODE: str = "epoch"
    REPORT_TO_MODE: str = "mlflow"
    MLFLOW_RUN_NAME: str = "twitter-sentiment-roberta-prod"
    MLFLOW_MODE_RUN: str = "PROD"
    MLFLOW_DATASET_TYPE: str = "ALL"
    MLFLOW_ARTIFACT_PATH: str = "out-model-baseline-prod"

    FLAG_USE_CPU: bool = False
    FLAG_DEBUG_MODE: bool= False
    FLAG_MONITOR_METRICS: bool =True

    # Export table
    FLAG_DROP_EXPORT_TABLE: bool = True
    FLAG_CREATE_EXPORT_TABLE: bool = True
    # In ConfigProdConstants (magari in produzione punta a una cartella di rete o un volume persistente)
    METRICS_DB_PATH: str = "metrics_prod.db"

