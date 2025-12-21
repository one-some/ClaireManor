# Basically a global echo server. #nosecuritygrindset
# Normally I would use websockets because I'm secretly a webdev posing as a
# jack of all trades programmer but that's between you and me


import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def client_thread(

with socket.socket() as listen:
    listen.bind(("", 42069))
    listen.listen()

    while True:
        con, address = listen.accept()
        threading.Thread(target=handler, args=(client_soc,), daemon=True).start() 

