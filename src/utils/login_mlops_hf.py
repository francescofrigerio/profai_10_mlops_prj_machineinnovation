"""
Modulo per la gestione dell'autenticazione con Hugging Face.
1.  Creare un Token** su Hugging Face (Photo profile -> Settings -> Auth -> Tokens)
    e premere (create new token)
2.  Eliminare i vecchi token .
3.  Inserire il nuovo token  nel repository github del progetto
    poi settings/Security Advance
    Segreto/Variabile d'ambiente `HF_TOKEN` nell'ambiente di ambiente di lavoro 
    Codespace + new repostory secret + add secret
4.  Leggere nel codice con una chiamata a getenv
"""
import os
from huggingface_hub import HfApi
from huggingface_hub import login

class Login():
    """
    Login:Classe che esegue la login a Hugging Face
    """
    def __init__(self,input_argv):
        """
        Class Login:inizializza valori in input
        """
        self._input_argv = input_argv
        # self.token = "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"
        # Recupera il token dall'ambiente, se non c'è usa una stringa vuota
        self.token = os.getenv("HF_TOKEN", "")

    def get_token(self):
        """ Return token value """
        return self.token

    def login_hf(self):
        """Effettua il login a Hugging Face utilizzando un token di accesso."""

        print(f" input_argv {self._input_argv}")

        if self._input_argv == 'MachineInnovation':
            # Verifica 'IL_TUO_TOKEN'
            print("Ok puoi accedere")
            token = self.token
        else:
            print("Ko Attenzione non potrai accedere")
            token = "token non valido"

        # Protezione: Se il token è vuoto o non valido, non tento il login
        if not token or token == "token non valido":
            print("Ko Errore: Il token HF_TOKEN è vuoto. Verificare le variabili d'ambiente.")
            return
        
        try:
            api = HfApi()

            # Questo comando usa il token per verificare che l'API risponda correttamente
            user_info = api.whoami(token=token)

            # from huggingface_hub import login
            # login()
            # Nota: login(token) evita che ti venga chiesto l'input interattivo
            login(token=token)

            print("Ok Accesso ad HuggingFace avvenuto con successo!")
            print(f"Utente connesso: {user_info['name']}")

        except Exception as e: # pylint: disable=broad-exception-caught
            print("Ko Errore di Accesso. Riprova con un nuovo token.")
            print(f"Dettagli: {e}")
