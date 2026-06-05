class IntegrationTest:
    """
        Class to test the integration of different components of the application
    """
    
    def test_1_dataset_loading():
        """
            Test loadinf of the dataset
        """
        dataset = load_dataset("tweet_eval","sentiment")

        assert len(dataset["train"]) > 0

    def test_2_model_and_tokenizer(self):
        """
           Test compatibnility between model and tokenizer
        """
        MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

        text = "I love this project"

        inputs = tokenizer(text,return_tensors="pt")
        outputs = model(**inputs)
        print(outputs.logits.shape)
        assert outputs.logits.shape[-1] == 3

    def test_3_pipeline_my(self):
        """
            Test prediction pipeline not based on HF
        """
        MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(model_path_or_name)

        text = "It's fantastic!! Inter wins both Italian League and Italian Cup"

        inputs = tokenizer(text,
                            return_tensors="pt"
                          )

    outputs = model(**inputs)

    pred = outputs.logits.argmax(dim=1)

    assert pred.item() in [0,1,2]

        
        
        pred = outputs.logits.argmax(dim=1)
        assert pred.item() in [0,1,2]


    def test_4_pipeline_hf(self):
        """
            Test prediction pipeline based on HF
        """
        MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(model_path_or_name)

        # uso l'oggetto pipeline di Hugging Face
        nlp_pipeline = pipeline("text-classification",
                                model=self.model,
                                tokenizer=self.tokenizer
                                )

        text = "It's fantastic!! Inter wins both Italian League and Italian Cup"
        outputs = nlp_pipeline(text)
        
        pred = outputs.logits.argmax(dim=1)
        assert pred.item() in [0,1,2]

    def test_5_saved_model_files():
        """
            Test that the model files are saved correctly
        """
        # verify this path runtime
        OUTPUT_DIR = "./outputs-baseline-prod"
        required_files = [ "config.json",
                            "model.safetensors",
                            "tokenizer.json",
                            "tokenizer_config.json"
                        ]

        for f in required_files:
            assert os.path.exists(os.path.join(OUTPUT_DIR,f))

    
    from app import app
    client = TestClient(app)
    
    def test_6_home():
       """ 
            test home to be sure deploy was succesful
       """
       response = client.get("/")
       assert response.status_code == 200
       data = response.json()
       assert data["status"] == "healthy"


    def test_7_post():
        """
             test predict post endpoint
        """
        response = client.post(
             "/predict",
             json={
                 "text": "I love this movie"
             }
        )
        assert response.status_code == 200
        data = response.json()
        assert "label" in data

    def test_8_get():
        """
             test predict get endpoint
        """
        response = client.get("/predict/text="I love this movie")

        assert response.status_code == 200
        data = response.json()
        assert "label" in data
    
    def test_predict_empty():
        """
            test predict endpoint with empty text
        """
        response = client.post("/predict",
                                json={
                                "text": ""
                                })
    assert response.status_code == 400

