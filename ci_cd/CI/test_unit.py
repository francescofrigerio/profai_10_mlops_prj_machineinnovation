"""
    unit_test.py
    
    to test path set
    import sys
    print(sys.path)
"""
import numpy as np

from src.utils.utils import preprocess_tweet 
from src.train.metrics import compute_metrics

class TestUnit:
    """
        Class to test single functions of the application
    """
    def test_1_preprocess_tweet(self):
        """
            test preprocess function
        """
        result = preprocess_tweet("@lautaro check https://google.com")

        assert isinstance(result, str)

    
    def test_2_compute_metrics_prediction_ok(self):
        """
            test compute metrics function
        """

        logits = np.array([[10, 0, 0],
                            [0, 10, 0],
                            [0, 0, 10]
                           ])

        labels = np.array([0, 1,2])

        result = compute_metrics((logits, labels))

        assert result["accuracy"] == 1.0
        assert result["f1"] == 1.0
        assert result["precision"] == 1.0
        assert result["recall"] == 1.0
    
    def test_3_compute_metrics_prediction_ko(self):
        """
            test compute metrics function
        """

        logits = np.array([[0, 10, 0],
                            [0, 0, 10],
                            [10, 0, 0]
                           ])

        labels = np.array([0, 1,2])

        result = compute_metrics((logits, labels))

        assert result["accuracy"] == 0.0
        assert result["f1"] == 0.0
        assert result["precision"] == 0.0
        assert result["recall"] == 0.0

    def test_compute_metrics_output_keys(self):
        """
            test compute metrics function
        """
        logits = np.array([[1,0,0]])

        labels = np.array([0])

        result = compute_metrics((logits, labels))

        expected = {"accuracy",
                    "f1",
                    "precision",
                    "recall"
                }

        assert set(result.keys()) == expected

    def test_label_mapping(self):
        """
            test label mapping data
        """
        label_mapping = { 0: "Negative",
                          1: "Neutral",
                          2: "Positive"
                        }
        assert label_mapping[0] == "Negative"
        assert label_mapping[1] == "Neutral"
        assert label_mapping[2] == "Positive"

  
