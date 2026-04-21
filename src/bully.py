# bully.py

from config import NODES
from messages import ELECTION, ANSWER, COORDINATOR
from utils import log, send_message


"""
Questo file contiene la logica principale del Bully Algorithm.

Qui viene gestito il comportamento del nodo quando:
- avvia un'elezione
- riceve un messaggio ELECTION
- riceve un messaggio ANSWER
- riceve un messaggio COORDINATOR

Per ora realizziamo la struttura base del comportamento.
Successivamente aggiungeremo anche la gestione completa dei timeout.
"""


class BullyNode:
    """
    Questa classe rappresenta lo stato logico del nodo rispetto
    all'algoritmo di elezione.

    Non gestisce direttamente la socket server: quello è compito di node.py.

    Questa classe si occupa invece di:
    - tenere traccia del coordinatore corrente
    - sapere se è in corso un'elezione
    - reagire ai messaggi ricevuti
    """

    def __init__(self, node_id):
        """
        Costruttore della classe.

        Parametri:
        - node_id: ID del nodo corrente

        Variabili principali:
        - coordinator_id: coordinatore attualmente noto
        - election_in_progress: indica se il nodo è dentro una procedura di elezione
        - received_answer: indica se il nodo ha ricevuto almeno un ANSWER
        """

        self.node_id = node_id
        self.coordinator_id = None
        self.election_in_progress = False
        self.received_answer = False

    def start_election(self):
        """
        Questo metodo avvia una nuova elezione.

        Il nodo invia un messaggio ELECTION a tutti i nodi con ID più alto.

        Logica dell'algoritmo:
        - se esistono nodi con ID maggiore, il nodo li contatta
        - se non esistono nodi con ID maggiore, allora questo nodo
          è il più alto attivo e può proclamarsi coordinatore
        """

        log(self.node_id, "Avvio elezione")

        self.election_in_progress = True
        self.received_answer = False

        higher_nodes = [node_id for node_id in NODES if node_id > self.node_id]

        if not higher_nodes:
            """
            Se non ci sono nodi con ID superiore, questo nodo è il più alto.
            Quindi può diventare coordinatore direttamente.
            """
            log(self.node_id, "Nessun nodo con ID superiore")
            self.become_coordinator()
            return

        for target_id in higher_nodes:
            log(self.node_id, f"Invio ELECTION a P{target_id}")
            send_message(self.node_id, target_id, ELECTION)

        """
        Per ora qui ci fermiamo.

        In una fase successiva aggiungeremo il timeout:
        - se non arriva nessun ANSWER entro T, il nodo diventa coordinatore
        - se arriva almeno un ANSWER, aspetta il messaggio COORDINATOR
        """

    def handle_message(self, message):
        """
        Questo metodo riceve un messaggio già interpretato da node.py
        e decide quale comportamento eseguire.

        Parametri:
        - message: dizionario Python con le informazioni del messaggio
        """

        msg_type = message.get("type")
        sender_id = message.get("sender")

        if msg_type == ELECTION:
            self.handle_election(sender_id)

        elif msg_type == ANSWER:
            self.handle_answer(sender_id)

        elif msg_type == COORDINATOR:
            self.handle_coordinator(sender_id)

        else:
            log(self.node_id, f"Tipo di messaggio sconosciuto: {msg_type}")

    def handle_election(self, sender_id):
        """
        Questo metodo gestisce la ricezione di un messaggio ELECTION.

        Regola del Bully Algorithm:
        - se un nodo riceve ELECTION da un nodo con ID più basso,
          risponde con ANSWER
        - poi, se non ha già un'elezione in corso, può avviare una propria elezione
        """

        log(self.node_id, f"Ricevuto ELECTION da P{sender_id}")

        if sender_id < self.node_id:
            log(self.node_id, f"Invio ANSWER a P{sender_id}")
            send_message(self.node_id, sender_id, ANSWER)

            if not self.election_in_progress:
                """
                Se questo nodo non sta già partecipando ad un'elezione,
                avvia una nuova elezione per verificare se esiste un nodo
                ancora più alto attivo.
                """
                self.start_election()

    def handle_answer(self, sender_id):
        """
        Questo metodo gestisce la ricezione di un messaggio ANSWER.

        Significato:
        - esiste almeno un nodo con ID più alto che è attivo
        - quindi questo nodo non può proclamarsi subito coordinatore
        """

        log(self.node_id, f"Ricevuto ANSWER da P{sender_id}")

        self.received_answer = True

    def handle_coordinator(self, sender_id):
        """
        Questo metodo gestisce la ricezione del messaggio COORDINATOR.

        Azioni eseguite
        - il nodo mittente si sta proclamando coordinatore
        - tutti gli altri nodi devono aggiornare il coordinatore corrente
          e terminare l'elezione in corso
        """

        log(self.node_id, f"Ricevuto COORDINATOR da P{sender_id}")

        self.coordinator_id = sender_id
        self.election_in_progress = False
        self.received_answer = False

        log(self.node_id, f"Il nuovo coordinatore è P{sender_id}")

    def become_coordinator(self):
        """
        Questo metodo viene chiamato quando il nodo conclude di essere
        il nodo attivo con ID più alto.

        Azioni eseguite:
        - imposta se stesso come coordinatore
        - termina l'elezione
        - invia COORDINATOR a tutti gli altri nodi con ID più basso
        """

        self.coordinator_id = self.node_id
        self.election_in_progress = False
        self.received_answer = False

        log(self.node_id, "Mi dichiaro COORDINATORE")

        lower_nodes = [node_id for node_id in NODES if node_id < self.node_id]

        for target_id in lower_nodes:
            log(self.node_id, f"Invio COORDINATOR a P{target_id}")
            send_message(self.node_id, target_id, COORDINATOR)
