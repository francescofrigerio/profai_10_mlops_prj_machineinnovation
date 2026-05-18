
import evaluate
import numpy as np

def compute_metrics(eval_pred):
    accuracy = evaluate.load("accuracy")
    f1_metric = evaluate.load("f1")
    precision_metric = evaluate.load("precision")
    recall_metric = evaluate.load("recall")

    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)

    acc = accuracy.compute(predictions=predictions,references=labels)
    f1 = f1_metric.compute( predictions=predictions,references=labels,average="weighted")
    precision = precision_metric.compute(predictions=predictions, references=labels, average="weighted")["precision"]
    recall = recall_metric.compute(predictions=predictions, references=labels, average="weighted")["recall"]

    return { "accuracy": acc,
              "f1": f1,
              "precision": precision,
              "recall": recall
          }