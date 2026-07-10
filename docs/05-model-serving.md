                    # MACHINE INNOVATION MODEL SERVING

## 1. Architettura del servizio `05-model-serving.md`
Questa sezione descrive l'architettura di Model Serving del progetto, la configurazione dello Space di Hugging Face, il Dockerfile utilizzato e le modalità di deploy e test del servizio FastApi.

Il modello viene distribuito come servizio REST utilizzando:

- FastAPI
- Uvicorn
- Docker
- Hugging Face Spaces (Docker SDK)

All'avvio dello Space:

1. FastAPI inizializza il servizio.
2. Viene recuperato il token HF_TOKEN dalle variabili d'ambiente.
3. Il modello viene scaricato dal Model Hub:
   francescofrigerio/machine-innovation-sentiment-model
4. Il modello viene mantenuto in memoria per servire le richieste di inferenza.

## 2. Contenuto del file requirements:
 ```bash
fastapi
uvicorn
pydantic
torch --index-url https://download.pytorch.org/whl/cpu
transformers
sentencepiece
protobuf
huggingface-hub
 ```

Nota sul pacchetto torch:
Il progetto viene eseguito esclusivamente su CPU (GitHub Codespaces e Hugging Face Spaces). Per questo motivo viene installata esplicitamente la versione CPU di PyTorch.

Forzare l'installazione della versione CPU di PyTorch rende il build dello Space molto più veloce (ci mette pochi secondi invece di svariati minuti), perché evita al container di HF di scaricare e compilare i gigabyte inutili di driver CUDA per GPU.

## 3. Dockerfile: utente non privilegiato (UID 1000)

Vedere la seguente documentazione che specifica
come per motivi di sicurezza, Hugging Face richiede che il container venga eseguito con un utente non privilegiato avente UID 1000.
https://huggingface.co/docs/hub/spaces-sdks-docker

La sintassi viene anche raccomandata nelle best praticse:
https://docs.docker.com/build/building/best-practices/

I container su Hugging Face non possono girare come root. La piattaforma è configurata per avviare il container impostando forzatamente l'utente con ID 1000. Se il Dockerfile non crea un utente con quell'UID specifico e non gli assegna i permessi di scrittura sulla cartella dell'app ($HOME/app), il container fallirà l'avvio con errori di tipo Permission Denied quando FastAPI cercherà di scrivere file temporanei o cache.

## 4. Dockerfile versione di python 3.12.slim
La versione slim di python rimuovono quasi tutti i tool di compilazione per ridurre il peso dell'immagine (passando da ~1GB a ~100MB).
L'opzione build-essential deve essere usata nel machine learning
perchè molte librerie Python non distribuiscono sempre i binari pre-compilati (chiamati Wheels) per qualsiasi combinazione di sistema operativo e versione di Python. 
Alcune librerie utilizzate dal progetto (o dalle loro dipendenze) potrebbero dover compilare componenti C/C++ durante l'installazione.
Se pip trova un pacchetto che deve essere compilato al momento dell'installazione e non trova un compilatore C++ (fornito appunto da build-essential e gcc), il comando pip install fallisce durante il build di Docker.

## 5. Dockerfile pulizia della cache
Vedere anche le best praticse
https://docs.docker.com/build/building/best-practices/

Comando eseguito : 
 ```bash
rm -rf /var/lib/apt/lists/*
 ```

Quando si esegue apt-get update, Debian/Ubuntu scarica i registri di tutti i pacchetti disponibili su internet, creando centinaia di megabyte di file di cache dentro il container. 
Se non vengono cancellati nella stessa identica riga (RUN) 
in cui sono installati i pacchetti, quei file rimarranno memorizzati per sempre nel "layer" di Docker, rendendo l'immagine finale inutilmente pesante. Rimuoverli mantiene l'immagine snella e veloce da caricare su Hugging Face.
Vedere anche la pagina dedicata alla build della cache
https://docs.docker.com/build/cache/

## 6. Per fare il deploy su Hugging face
eseguire e alla fine controllare il log container sull'interfaccia web di Hugging Face.

 ```bash
 cd model_serving
./deploy_space.sh

In fase di sviluppo è possibile utilizzare deploy_space.sh per preparare la cartella dist_space, contenente esclusivamente i file necessari allo Space.
Nella versione finale del progetto il deploy sullo Space di Hugging Face è completamente automatizzato tramite la pipeline GitHub Actions.
 ```
## 7. Test in locale(pc, codespace) con i seguenti script curl
 ```bash
model_serving/test_predict_from_app.sh esegue una post  
model_serving/test_predict_from_web.sh esegue una post
 ```
 
## 8. E' possibile anche testare la get direttamente sul browser
con il seguente url:

https://francescofrigerio-spacemachineinnovatorsmlops.hf.space/predict?text=Oggi è una orribile giornata

https://francescofrigerio-spacemachineinnovatorsmlops.hf.space/predict?text=Oggi è una meravigliosa giornata

https://francescofrigerio-spacemachineinnovatorsmlops.hf.space/predict?text=Oggi è una giornata strana







