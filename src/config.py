# config.py

"""
Questo file contiene tutte le configurazioni globali del progetto.

Sono qui definiti:
- quali nodi esistono
- su quali porte ascoltano
- i timeout richiesti dall'algoritmo

In questo modo, se vogliamo cambiare qualcosa, come ad esempio
una porta, non dobbiamo modificare tutto il codice, ma solo questo file.
"""

# Indirizzo localhost, visto che tutti i nodi girano in locale
HOST = "127.0.0.1"

# Mappa dei nodi: ID -> (HOST, PORTA)
# Ogni nodo ascolta su una porta diversa
NODES = {
    1: (HOST, 5001),
    2: (HOST, 5002),
    3: (HOST, 5003),
    4: (HOST, 5004),
    5: (HOST, 5005),
}

# Timeout in secondi per ricevere un messaggio ANSWER
# Serve quando un nodo avvia un'elezione
ANSWER_TIMEOUT = 3

# Timeout per ricevere il messaggio COORDINATOR
# Serve quando un nodo aspetta che qualcun altro diventi coordinatore
COORDINATOR_TIMEOUT = 5

# Dimensione in byte massima del messaggio ricevuto
BUFFER_SIZE = 4096
