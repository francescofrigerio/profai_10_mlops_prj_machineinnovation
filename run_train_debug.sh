# Cancellando tutti i check point il train riparta sempre 
# dall'ultima versione del modello di HuggingFace
rm -r -f ./src/outputs-baseline-debug/model_weights/checkpoint*
cd src
python -m train.train_baseline --mode DEBUG 2>&1 | tee train_debug.log
# PYTHONPATH=. python train/train_baseline.py --mode DEBUG 2>&1 | tee train_debug.log
