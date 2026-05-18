import logging

def print_counter(my_dataset_label,label_map,title):
    # 3. Estrai le etichette del train set e contale con Counter
    counter_num = Counter(my_dataset_label)

    # 4. Converti i codici numerici nei rispettivi nomi di sentiment
    counter_sentiment = {label_map[chiave]: valore for chiave, valore in counter_num.items()}

    # Mostra il risultato
    print(f"--- Start Suddivisione Sentiment nel dataset di {title} ---")
    for sentiment, quantity in counter_sentiment.items():
        print(f"{sentiment}: {quantity}")
    print(f"--- End Suddivisione Sentiment nel dataset di {title} ---")


"""
    Configurazione di base
    Qui decidiamo il livello minimo (WARNING) e il formato del messaggio
    nel codice con setTrace attivo il debug
"""
def init_debug_logger():
    logging.basicConfig( level=logging.WARNING,
                            # level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s',
                            datefmt='%H:%M:%S',
                            force=True
                        )

    # Creazione di un oggetto logger
    logger = logging.getLogger("CyberEyeAppLogger")
    logger.setLevel(logging.INFO)
    return logger

def test_debug_division(logger,a, b):
    logger.debug(f"Inizio funzione con parametri: a={a}, b={b}")

    if b == 0:
        logger.error("Tentativo di divisione per zero!")
        return None

    if b < 0:
        logger.warning("Il divisore è negativo, il risultato cambierà segno.")

    risultato = a / b
    logger.info(f"Divisione completata con successo. Risultato: {risultato}")
    return risultato

