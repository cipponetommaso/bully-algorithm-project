# bully.py

import threading
import time

from config import NODES, ANSWER_TIMEOUT, COORDINATOR_TIMEOUT
from messages import ELECTION, ANSWER, COORDINATOR
from utils import log, send_message, is_node_alive


"""
Questo file contiene la logica principale del Bully Algorithm.

Qui viene gestito il comportamento del nodo quando:
- avvia un'elezione
- riceve un messaggio ELECTION
- riceve un messaggio ANSWER
- riceve un messaggio COORDINATOR

Vengono anche gestiti:
- i timeout reali richiesti dalla traccia
- il controllo automatico del coordinatore corrente
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
    - gestire i timeout dell'algoritmo
    - controllare periodicamente se il coordinatore è ancora attivo
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
        - coordinator_received: indica se il nodo ha ricevuto il messaggio COORDINATOR
        - answer_timer: timer usato per aspettare ANSWER
        - coordinator_timer: timer usato per aspettare COORDINATOR
        """

        self.node_id = node_id
        self.coordinator_id = None
        self.election_in_progress = False
        self.received_answer = False
        self.coordinator_received = False

        self.answer_timer = None
        self.coordinator_timer = None

        # Lock utile per evitare problemi tra thread diversi
        self.lock = threading.Lock()

    def start_election(self):
        """
        Questo metodo avvia una nuova elezione.

        Il nodo invia un messaggio ELECTION a tutti i nodi con ID più alto.

        Logica dell'algoritmo:
        - se esistono nodi con ID maggiore, il nodo li contatta
        - poi aspetta per un certo tempo un eventuale ANSWER
        - se non esistono nodi con ID maggiore, allora questo nodo
          è il più alto attivo e può proclamarsi coordinatore
        """

        with self.lock:
            log(self.node_id, "Avvio elezione")

            self.election_in_progress = True
            self.received_answer = False
            self.coordinator_received = False
            self.coordinator_id = None

            self.cancel_timers()

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
            Dopo aver inviato ELECTION, il nodo aspetta per un tempo limitato
            eventuali messaggi ANSWER.

            Se nessun ANSWER arriva entro il timeout, il nodo conclude
            di essere il più alto attivo e si proclama coordinatore.
            """
            self.answer_timer = threading.Timer(ANSWER_TIMEOUT, self.on_answer_timeout)
            self.answer_timer.start()

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

        Dopo aver ricevuto ANSWER:
        - il nodo smette di aspettare altri ANSWER
        - inizia ad aspettare il messaggio COORDINATOR
        """

        with self.lock:
            log(self.node_id, f"Ricevuto ANSWER da P{sender_id}")

            self.received_answer = True

            if self.answer_timer is not None:
                self.answer_timer.cancel()
                self.answer_timer = None

            """
            Ora il nodo sa che esiste almeno un nodo superiore attivo.
            Deve quindi aspettare che uno di questi si proclami coordinatore.
            """
            if self.coordinator_timer is None:
                self.coordinator_timer = threading.Timer(
                    COORDINATOR_TIMEOUT,
                    self.on_coordinator_timeout
                )
                self.coordinator_timer.start()

    def handle_coordinator(self, sender_id):
        """
        Questo metodo gestisce la ricezione del messaggio COORDINATOR.

        Significato:
        - il nodo mittente si sta proclamando coordinatore
        - tutti gli altri nodi devono aggiornare il coordinatore corrente
          e terminare l'elezione in corso
        """

        with self.lock:
            log(self.node_id, f"Ricevuto COORDINATOR da P{sender_id}")

            self.coordinator_id = sender_id
            self.election_in_progress = False
            self.received_answer = False
            self.coordinator_received = True

            self.cancel_timers()

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
        self.coordinator_received = True

        self.cancel_timers()

        log(self.node_id, "Mi dichiaro COORDINATORE")

        lower_nodes = [node_id for node_id in NODES if node_id < self.node_id]

        for target_id in lower_nodes:
            log(self.node_id, f"Invio COORDINATOR a P{target_id}")
            send_message(self.node_id, target_id, COORDINATOR)

    def on_answer_timeout(self):
        """
        Questo metodo viene chiamato automaticamente quando scade
        il tempo massimo di attesa per un messaggio ANSWER.

        Se nessun ANSWER è stato ricevuto, il nodo conclude di essere
        il nodo attivo con ID più alto e diventa coordinatore.
        """

        with self.lock:
            if not self.received_answer and self.election_in_progress:
                log(self.node_id, "Timeout scaduto: nessun ANSWER ricevuto")
                self.become_coordinator()

    def on_coordinator_timeout(self):
        """
        Questo metodo viene chiamato automaticamente quando scade
        il tempo massimo di attesa per il messaggio COORDINATOR.

        Significato:
        - il nodo aveva ricevuto almeno un ANSWER
        - quindi sapeva che esisteva un nodo superiore attivo
        - ma nessuno si è proclamato coordinatore entro il tempo previsto

        In questo caso il nodo riavvia una nuova elezione.
        """

        with self.lock:
            if not self.coordinator_received and self.election_in_progress:
                log(self.node_id, "Timeout scaduto: nessun COORDINATOR ricevuto")
                log(self.node_id, "Riavvio elezione")

        """
        La nuova elezione viene avviata fuori dal blocco lock
        per evitare problemi di concorrenza.
        """
        if self.election_in_progress and not self.coordinator_received:
            self.start_election()

    def monitor_coordinator(self):
        """
        Questo metodo controlla periodicamente se il coordinatore corrente
        è ancora raggiungibile.

        Il controllo viene fatto solo se:
        - esiste un coordinatore noto
        - il coordinatore non è il nodo corrente
        - non è già in corso un'elezione

        Se il coordinatore non risponde:
        - il nodo lo considera fallito
        - cancella il coordinatore corrente
        - avvia automaticamente una nuova elezione

        Questo controllo non introduce nuovi messaggi applicativi.
        Viene verificata solo la raggiungibilità della socket TCP.
        """

        while True:
            time.sleep(COORDINATOR_TIMEOUT)

            with self.lock:
                """
                Se non conosciamo alcun coordinatore, non c'è nulla da controllare.
                """
                if self.coordinator_id is None:
                    continue

                """
                Se il coordinatore corrente è il nodo stesso, non serve controllarlo.
                """
                if self.coordinator_id == self.node_id:
                    continue

                """
                Se è già in corso un'elezione, non facciamo altri controlli
                per evitare sovrapposizioni inutili.
                """
                if self.election_in_progress:
                    continue

                coordinator_id = self.coordinator_id

            """
            Il controllo della raggiungibilità viene fatto fuori dal lock
            per non bloccare il resto del sistema.
            """
            alive = is_node_alive(coordinator_id)

            if not alive:
                with self.lock:
                    """
                    Ricontrolliamo che il coordinatore non sia già cambiato
                    mentre stavamo facendo il test di raggiungibilità.
                    """
                    if self.coordinator_id == coordinator_id and not self.election_in_progress:
                        log(self.node_id, "Timeout: coordinatore non risponde")
                        log(self.node_id, f"P{coordinator_id} viene considerato fallito")
                        self.coordinator_id = None

                """
                L'elezione viene avviata fuori dal lock
                per evitare problemi di concorrenza.
                """
                self.start_election()

    def start_monitoring(self):
        """
        Questo metodo avvia il thread che controlla periodicamente
        lo stato del coordinatore.

        Il thread gira in background per tutta la vita del nodo.
        """

        monitor_thread = threading.Thread(target=self.monitor_coordinator)
        monitor_thread.daemon = True
        monitor_thread.start()

    def cancel_timers(self):
        """
        Questo metodo annulla eventuali timer attivi.

        Serve quando:
        - arriva un messaggio che chiude l'elezione
        - il nodo diventa coordinatore
        - bisogna ripartire da uno stato pulito
        """

        if self.answer_timer is not None:
            self.answer_timer.cancel()
            self.answer_timer = None

        if self.coordinator_timer is not None:
            self.coordinator_timer.cancel()
            self.coordinator_timer = None
