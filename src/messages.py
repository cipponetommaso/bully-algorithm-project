# messages.py

import json

"""
Questo file definisce i tipi di messaggi utilizzati nel sistema
e le funzioni per crearli e interpretarli.

I messaggi devono rispettare la traccia del progetto, quindi
possono essere solo di tre tipi:
- ELECTION
- ANSWER
- COORDINATOR

Per rappresentare i messaggi utilizziamo il formato JSON,
perché è semplice da leggere e da convertire.
"""

# Tipi di messaggi previsti dall'algoritmo
ELECTION = "ELECTION"
ANSWER = "ANSWER"
COORDINATOR = "COORDINATOR"


def build_message(msg_type, sender_id):
    """
    Questa funzione crea un messaggio da inviare ad un altro nodo.

    Parametri:
    - msg_type: tipo del messaggio (ELECTION, ANSWER, COORDINATOR)
    - sender_id: ID del nodo che invia il messaggio

    Il messaggio viene costruito come un dizionario Python e poi
    convertito in stringa JSON.
    """

    message = {
        "type": msg_type,
        "sender": sender_id
    }

    # Conversione del dizionario in stringa JSON
    return json.dumps(message)


def parse_message(raw_data):
    """
    Questa funzione serve per interpretare un messaggio ricevuto.

    Parametri:
    - raw_data: dati ricevuti dalla rete (in formato bytes)

    La funzione:
    - converte i bytes in stringa
    - converte la stringa JSON in dizionario Python

    Restituisce:
    - un dizionario con i dati del messaggio
    - oppure None se c'è un errore
    """

    try:
        # Conversione da bytes a stringa
        data_str = raw_data.decode()

        # Conversione da JSON a dizionario Python
        return json.loads(data_str)

    except Exception as e:
        # Se il messaggio non è valido o è corrotto
        print("Errore durante il parsing del messaggio:", e)
        return None
