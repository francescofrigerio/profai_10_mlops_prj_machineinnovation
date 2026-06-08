"""
    test_unit_preprocess.py
    
    to test path set
    import sys
    print(sys.path)
"""
import numpy as np

from src.utils.utils import preprocess_tweet 
from src.train.metrics import compute_metrics

class TestUnitPreprocess:
    """
        Class to test single functions of the application
    """
    def test_1_preprocess_tweet(self):
        """
            test preprocess function
        """
        result = preprocess_tweet("@lautaro check https://google.com")

        assert isinstance(result, str)

    def test_2_label_mapping(self):
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

  
