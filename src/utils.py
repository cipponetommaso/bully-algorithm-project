# utils.py

import socket
from config import NODES
from messages import build_message

"""
Questo file contiene funzioni di supporto utilizzate nel progetto.

In particolare:
- una funzione per stampare i log in modo chiaro
- una funzione per inviare messaggi tra nodi

Serve per evitare di ripetere lo stesso codice in più file.
"""


def log(node_id, message):
    """
    Questa funzione stampa un messaggio in modo standard.

    Tutti i log avranno questo formato:
    [P1] messaggio
    [P2] messaggio

    Parametri:
    - node_id: ID del nodo che stampa il messaggio
    - message: testo da stampare
    """

    print(f"[P{node_id}] {message}")


def send_message(sender_id, target_id, msg_type):
    """
    Questa funzione invia un messaggio ad un altro nodo tramite socket TCP.

    Parametri:
    - sender_id: nodo che invia il messaggio
    - target_id: nodo che deve riceverlo
    - msg_type: tipo di messaggio (ELECTION, ANSWER, COORDINATOR)

    Il funzionamento è il seguente:
    - si apre una connessione verso il nodo destinatario
    - si costruisce il messaggio in formato JSON
    - si invia il messaggio
    - la connessione viene chiusa automaticamente
    """

    # Recupero indirizzo e porta del nodo destinatario
    host, port = NODES[target_id]

    try:
        # Creazione del socket TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Connessione al nodo destinatario
            s.connect((host, port))

            # Creazione del messaggio
            message = build_message(msg_type, sender_id)

            # Invio del messaggio convertito in bytes
            s.sendall(message.encode())

    except Exception as e:
        """
        Questo errore può verificarsi se:
        - il nodo destinatario è spento
        - la connessione fallisce

        È un comportamento importante per il progetto, perché
        simula il guasto di un nodo (ad esempio P5).
        """
        log(sender_id, f"Errore nell'invio a P{target_id}: {e}")

def is_node_alive(target_id):
    """
    Questa funzione verifica se un nodo è raggiungibile.

    Parametri:
    - target_id: ID del nodo da controllare

    Il controllo viene fatto provando ad aprire una connessione TCP
    verso il nodo target.

    Se la connessione riesce il nodo è considerato attivo.
    Se la connessione fallisce il nodo è considerato non
    raggiungibile, quindi potenzialmente fallito.
    Si verifica solo se la porta è raggiungibile.
    """

    host, port = NODES[target_id]

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Impostiamo un timeout breve per non bloccare il nodo
            s.settimeout(1)
            s.connect((host, port))

        return True

    except Exception:
        return False
