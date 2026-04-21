# bully-algorithm-project
# Progetto 2 - Elezione del Coordinatore con Bully Algorithm

Questo progetto implementa un sistema distribuito su localhost che realizza
l'elezione di un coordinatore tramite Bully Algorithm.

Il sistema è composto da 5 nodi indipendenti, eseguiti in terminali separati,
che comunicano tramite socket TCP.

## Obiettivo

Il progetto si articola in due fasi principali:

1. Elezione iniziale del coordinatore, in cui P5 diventa coordinatore
2. Nuova elezione dopo il guasto di P5, in cui P4 diventa coordinatore

## Tecnologie utilizzate

- Python 3
- Socket TCP
- Threading
- JSON per il formato dei messaggi

## Struttura del progetto

- `src/node.py` : avvio del nodo e gestione della rete
- `src/bully.py` : logica del Bully Algorithm
- `src/config.py` : configurazione di nodi, porte e timeout
- `src/messages.py` : definizione e parsing dei messaggi
- `src/utils.py` : funzioni di supporto
- `docs/` : documentazione finale, video dimostrativo e materiali aggiuntivi

## Requisiti

Il progetto richiede Python 3.

Non sono necessarie librerie esterne, perché vengono utilizzati solo moduli
standard di Python.

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

## Comandi disponibili

Durante l'esecuzione di un nodo sono disponibili i seguenti comandi:

- `e` : avvia una nuova elezione
- `c` : mostra il coordinatore corrente
- `q` : termina il nodo

## Scenario dimostrativo

1. Avviare i 5 nodi
2. Da un nodo qualsiasi, digitare `e` per avviare l'elezione iniziale
3. Verificare che P5 venga eletto coordinatore
4. Terminare manualmente P5 con `Ctrl + C` o digitando `q`
5. Attendere la rilevazione automatica del guasto
6. Verificare che venga avviata una nuova elezione
7. Verificare che P4 diventi il nuovo coordinatore

## Note

Il sistema utilizza esclusivamente i messaggi richiesti dalla traccia del progetto:
- ELECTION
- ANSWER
- COORDINATOR

I timeout sono implementati realmente e il coordinatore viene monitorato
automaticamente.
