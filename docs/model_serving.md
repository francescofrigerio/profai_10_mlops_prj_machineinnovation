# MODEL SERVING MACHINE INNOVATION
https://huggingface.co/francescofrigerio/spaces

https://huggingface.co/spaces/francescofrigerio/SpaceMachineInnovatorsMlOps
https://huggingface.co/spaces/francescofrigerio/ModelMachineInnovatorsMlOps

https://huggingface.co/francescofrigerio/machine-innovation-sentiment-model


1. requirements.txt

Segue il Contenuto del file requirements:

fastapi
uvicorn
pydantic
torch --index-url https://download.pytorch.org/whl/cpu
transformers
sentencepiece
protobuf
huggingface-hub

Nota sulla riga torch:
Il progetto gira(codespace di github e Space di Hugging Face) su CPU. 
Forzare l'installazione della versione CPU di PyTorch rende il build dello Space molto più veloce (ci mette pochi secondi invece di svariati minuti), perché evita al container di HF di scaricare e compilare i gigabyte inutili di driver CUDA per GPU.

2. Dockerfile userid

Vedere la seguente documentazione che specifica
come per motivi di sicurezza l'utente che esegue il servizio
non debba essere root ma l'utente con userid = 1000
https://huggingface.co/docs/hub/spaces-sdks-docker

La sintassi viene anche raccomandata nelle best praticse:
https://docs.docker.com/build/building/best-practices/

I container su Hugging Face non possono girare come root. La piattaforma è configurata per avviare il container impostando forzatamente l'utente con ID 1000. Se il Dockerfile non crea un utente con quell'UID specifico e non gli assegna i permessi di scrittura sulla cartella dell'app ($HOME/app), il container fallirà l'avvio con errori di tipo Permission Denied quando FastAPI cercherà di scrivere file temporanei o cache.

3. Dockerfile versione di python 3.12.slim
La versione slim di python rimuovono quasi tutti i tool di compilazione per ridurre il peso dell'immagine (passando da ~1GB a ~100MB).
L'opzione build-essential deve essere usata nel machine learning
perchè molte librerie Python non distribuiscono sempre i binari pre-compilati (chiamati Wheels) per qualsiasi combinazione di sistema operativo e versione di Python. Se pip trova un pacchetto che deve essere compilato al momento dell'installazione e non trova un compilatore C++ (fornito appunto da build-essential e gcc), il comando pip install fallisce durante il build di Docker.

4. Dockerfile pulizia della cache
Vedere anche le best praticse
https://docs.docker.com/build/building/best-practices/

Comando eseguito : rm -rf /var/lib/apt/lists/*.

Quando si esegue apt-get update, Debian/Ubuntu scarica i registri di tutti i pacchetti disponibili su internet, creando centinaia di megabyte di file di cache dentro il container. 
Se non vengono cancellati nella stessa identica riga (RUN) 
in cui sono installati i pacchetti, quei file rimarranno memorizzati per sempre nel "layer" di Docker, rendendo l'immagine finale inutilmente pesante. Rimuoverli mantiene l'immagine snella e veloce da caricare su Hugging Face.
Vedere anche la pagina dedicata alla build della cache
https://docs.docker.com/build/cache/

5. Per fare il deploy su Hugging face
eseguire deploy_space.sh

6. Aggiornare github e allineare il local space

7. Copiare localmente sul pc la cartella ./model_serving/dist_pace
dalla dir locale collegata a github alla dir locale collegata allo space.

8. Test in locale(pc, codespace) con i seguenti script curl
model_serving/test_predict_from_app.sh esegue una post  
model_serving/test_predict_from_web.sh esegue una post

9. E' possibile anche testare la get direttamente sul browser
con il seguente url:
https://francescofrigerio-spacemachineinnovatorsmlops.hf.space/predict?text=Oggi è una orribile giornata

https://francescofrigerio-spacemachineinnovatorsmlops.hf.space/predict?text=Oggi è una meravigliosa giornata

https://francescofrigerio-spacemachineinnovatorsmlops.hf.space/predict?text=Oggi è una giornata strana







