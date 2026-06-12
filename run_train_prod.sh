# Cancellando tutti i check point il train riparta sempre 
# dall'ultima versione del modello di HuggingFace

flag_demo=1
if flag_demo=1
    rm -r -f ./src/outputs-baseline-debug/model_weights/checkpoint*
    cd src
    python -m train.train_baseline --mode DEBUG 2>&1 | tee train_debug.log
else
    rm -r -f ./src/outputs-baseline-prod/model_weights/checkpoint*
    cd src
    python -m train.train_baseline --mode PROD 2>&1

    
