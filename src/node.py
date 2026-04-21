# node.py

import socket
import sys
import threading

from config import NODES, BUFFER_SIZE
from messages import parse_message
from utils import log
from bully import BullyNode


"""
Questo file rappresenta il punto di avvio di ogni nodo del sistema.

Ogni nodo:
- legge il proprio ID dagli argomenti passati da terminale
- apre una socket server sulla porta associata
- resta in ascolto di connessioni in ingresso
- riceve i messaggi dagli altri nodi
- passa i messaggi ricevuti alla logica del Bully Algorithm

In questo file gestiamo:
- la parte di rete
- l'avvio del nodo
- la ricezione dei messaggi
"""


class Node:
    """
    Questa classe rappresenta un singolo nodo del sistema distribuito.

    Ogni nodo conosce:
    - il proprio ID
    - il proprio host
    - la propria porta

    Inoltre possiede un oggetto BullyNode, che contiene
    la logica dell'algoritmo di elezione.
    """

    def __init__(self, node_id):
        """
        Costruttore del nodo.

        Parametri:
        - node_id: identificativo del nodo, ad esempio 1, 2, 3, 4 o 5

        Dal file config.py recuperiamo automaticamente host e porta
        associati a questo nodo.

        Inoltre inizializziamo anche la parte logica
        del Bully Algorithm.
        """

        self.node_id = node_id
        self.host, self.port = NODES[node_id]

        # Oggetto che gestisce la logica dell'algoritmo Bully
        self.bully_node = BullyNode(node_id)

    def start_server(self):
        """
        Questo metodo avvia il server TCP del nodo.

        Il server:
        - si lega all'host e alla porta del nodo
        - resta in ascolto continuo
        - accetta le connessioni in ingresso
        - crea un thread separato per gestire ogni client

        In questo modo il nodo può ricevere più messaggi senza bloccarsi.
        """

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()

        log(self.node_id, f"Nodo avviato su {self.host}:{self.port}")
        log(self.node_id, "In attesa di messaggi...")

        while True:
            client_socket, client_address = server_socket.accept()

            # Ogni connessione in ingresso viene gestita in un thread separato
            client_thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket, client_address)
            )
            client_thread.start()

    def handle_client(self, client_socket, client_address):
        """
        Questo metodo gestisce una singola connessione in ingresso.

        Parametri:
        - client_socket: socket del client connesso
        - client_address: indirizzo del client

        Il metodo:
        - riceve i dati
        - interpreta il messaggio
        - passa il messaggio alla logica Bully
        - chiude la connessione
        """

        try:
            raw_data = client_socket.recv(BUFFER_SIZE)

            if not raw_data:
                return

            message = parse_message(raw_data)

            if message is None:
                log(self.node_id, "Messaggio ricevuto non valido")
                return

            # Il messaggio viene gestito dalla logica del Bully Algorithm
            self.bully_node.handle_message(message)

        except Exception as e:
            log(self.node_id, f"Errore nella gestione della connessione: {e}")

        finally:
            client_socket.close()


def main():
    """
    Questa è la funzione principale del programma.

    Controlla che l'utente abbia passato correttamente l'ID del nodo
    da riga di comando.

    Esempio corretto:
    python node.py 1
    """

    if len(sys.argv) != 2:
        print("Uso corretto: python node.py <node_id>")
        sys.exit(1)

    try:
        node_id = int(sys.argv[1])
    except ValueError:
        print("L'ID del nodo deve essere un numero intero")
        sys.exit(1)

    if node_id not in NODES:
        print("ID del nodo non valido. Deve essere uno tra: 1, 2, 3, 4, 5")
        sys.exit(1)

    node = Node(node_id)
    node.start_server()


if __name__ == "__main__":
    main()
