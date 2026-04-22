# Progetto 2 - Elezione del Coordinatore con Bully Algorithm

Questo progetto implementa un sistema distribuito su localhost che realizza
l'elezione di un coordinatore tramite Bully Algorithm.

Il sistema è composto da 5 nodi indipendenti, eseguiti in terminali separati,
che comunicano esclusivamente tramite socket TCP.

---

## Obiettivo

Il progetto dimostra due fasi fondamentali:

1. Elezione iniziale del coordinatore, in cui il nodo con ID massimo (P5) viene eletto coordinatore
2. Nuova elezione dopo il guasto di P5, in cui il nodo con ID più alto ancora attivo (P4) diventa il nuovo coordinatore

---

## Tecnologie utilizzate

- Python 3
- Socket TCP
- Threading
- JSON per la serializzazione dei messaggi

---

## Struttura del progetto

- `src/node.py` : avvio del nodo e gestione della comunicazione di rete
- `src/bully.py` : implementazione del Bully Algorithm
- `src/config.py` : configurazione di nodi, porte e timeout
- `src/messages.py` : definizione e parsing dei messaggi
- `src/utils.py` : funzioni di supporto (log, invio messaggi, controllo nodi)
- `docs/` : documentazione finale, video dimostrativo e materiali aggiuntivi

---

## Requisiti

Il progetto richiede Python 3.

Non sono necessarie librerie esterne, in quanto vengono utilizzati
esclusivamente moduli standard di Python.

---

## Esecuzione

Aprire 5 terminali separati e lanciare i seguenti comandi:

### Terminale 1
python3 src/node.py 1

### Terminale 2
python3 src/node.py 2

### Terminale 3
python3 src/node.py 3

### Terminale 4
python3 src/node.py 4

### Terminale 5
python3 src/node.py 5

---

## Comandi disponibili

Durante l'esecuzione di un nodo sono disponibili i seguenti comandi:

- `e` : avvia una nuova elezione
- `c` : mostra il coordinatore corrente
- `q` : termina il nodo

---

## Scenario dimostrativo

1. Avviare i 5 nodi
2. Da un nodo qualsiasi, digitare `e` per avviare l'elezione iniziale
3. Verificare che P5 venga eletto coordinatore
4. Terminare manualmente P5 con `Ctrl + C` oppure digitando `q` nel nodo P5
5. Attendere la rilevazione automatica del guasto
6. Verificare che venga avviata una nuova elezione
7. Verificare che P4 diventi il nuovo coordinatore

---

## Note

Il sistema utilizza esclusivamente i messaggi richiesti dalla traccia:

- ELECTION  
- ANSWER  
- COORDINATOR  

Sono implementati due timeout reali:

- `T` (ANSWER_TIMEOUT) per l'attesa delle risposte
- `T′` (COORDINATOR_TIMEOUT) per l'attesa del coordinatore

Il coordinatore viene monitorato automaticamente e, in caso di guasto,
il sistema avvia una nuova elezione senza intervento manuale.
