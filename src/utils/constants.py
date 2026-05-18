from dataclasses import dataclass, field

@dataclass(frozen=True)
class ConfigDebugConstants:
    """
    Global Config. Const of Environment
    Substiutes magic numbers with description names
    """

    NUM_CLASSES=3
    SMALL_TRAIN_DATASET_SIZE=500
    SMALL_VAL_DATASET_SIZE=100
    MAX_LENGTH=64
    # New field for seed so we can reproduce the results
    SEED: int = 42

    # Training
    OUTPUT_DIR = "./sentiment-model-base-2-debug"
    LEARNING_RATE=2e-5
    BATCH_SIZE=4
    NUM_EPOCHS = 1
    WEIGHT_DECAY=0.01
    SAVE_TOTAL_LIMIT=1
    LOGGING_STEPS=5
    SAVE_STRATEGY_MODE="no"
    REPORT_TO_MODE="mlflow"
    MLFLOW_RUN_NAME="twitter-sentiment-roberta-debug"
    MLFLOW_MODE_RUN="DEBUG"
    MLFLOW_DATASET_TYPE="SMALL"
    FLAG_NO_CUDA=True
    MAX_STEPS=20
    FLAG_DEBUG_MODE=True
    FLAG_MONITOR_METRICS=True

    # Export table
    FLAG_DROP_EXPORT_TABLE=True
    FLAG_CREATE_EXPORT_TABLE=True

# SETUP CONFIGURAZIONE
@dataclass(frozen=True)
class ConfigProdConstants:
    """
    Global Config. Const of Environment
    Substiutes magic numbers with description names
    """

    NUM_CLASSES=3
    MAX_LENGTH=128
    # New field for seed so we can reproduce the results
    SEED: int = 42

    # Training
    OUTPUT_DIR = "./sentiment-model-base-2"
    LEARNING_RATE=2e-5
    BATCH_SIZE=16
    NUM_EPOCHS = 3
    WEIGHT_DECAY=0.01
    SAVE_TOTAL_LIMIT=2
    LOGGING_STEPS=50
    SAVE_STRATEGY_MODE="epoch"
    REPORT_TO_MODE="mlflow"
    MLFLOW_RUN_NAME="twitter-sentiment-roberta-prod"
    MLFLOW_MODE_RUN="PROD"
    MLFLOW_DATASET_TYPE="ALL"

    FLAG_NO_CUDA=False
    FLAG_DEBUG_MODE=False
    FLAG_MONITOR_METRICS=True

    # Export table
    FLAG_DROP_EXPORT_TABLE=True
    FLAG_CREATE_EXPORT_TABLE=True








