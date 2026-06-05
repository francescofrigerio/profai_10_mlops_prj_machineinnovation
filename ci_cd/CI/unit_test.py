class UnitTest:
    """
        Class to test single functions of the application
    """
    def test_preprocess_tweet():
        """
            test preprocess function
        """
        result = preprocess_tweet("@lautaro check https://google.com")

        assert isinstance(result, str)

    
    # test_metrics.py
    # test_pipeline.py
