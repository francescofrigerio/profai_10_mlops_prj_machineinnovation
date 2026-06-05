

E' possibile visualizzare queste informazioni
anche con help in linea della script ./setup.sh

----------------------------------------------------
1. Verifica Python (max versione 3.12)
Python 3.12.1
----------------------------------------------------

----------------------------------------------------
2. SCRIPT D'INSTALLAZIONE CONTROLLO MODIFICA E RESET ENVIRONMEN
2.1 -> setup.sh --init  (inizializza progetto , install. librerie/venv) 
2.2 -> setup.sh --change  (modifica struttura progetto , installazione nuove librerie) 
2.3 -> setup.sh --install  (installazione librerie tramite requirements.txt) 
2.4 -> setup.sh --checks  (controllo GPU/CPU verifica installazione librerie) 
2.5 -> source .venv/bin/activate per attivare l'ambiente virtuale
2.6 -> deactivate per disattivare l'ambiente virtuale
2.7 -> ruff check file.py controllo superficiale di un file python
2.8 -> cd src + PYTHONPATH=. pylint train/train_baseline.py per controllo profondo di un file python
2.9 -> ./train_prod.sh Training in produzione
2.10-> ./train_debug.sh Training in debug(default)
2.11 -> ./pipe_prod.sh Pipeline Inference in produzione
2.12 -> ./pipe_debug.sh Pipeline Inference in debug

Esempio di output delle script pipe*.sh
Tweet: I love this ProfAi MLOps course! @HuggingFace http://example.com 
Risultato: [{'label': 'positive', 'score': 0.9962100982666016, 'sentiment': 'positive'}] 
----------------------------------------------------

----------------------------------------------------
3. Comandi docker:
docker compose up -d
docker compose down
docker system prune -a --volumes -f
----------------------------------------------------

----------------------------------------------------
4. Comandi per pulire ambiente e ricrearlo (da eseguire solo se necessario)
pip cache purge
deactivate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install torch --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
pip install -r requirements.txt --no-cache-dir
----------------------------------------------------






