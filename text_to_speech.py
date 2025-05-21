from keys import TTS_API_KEY
import socket


def text_to_audio_play(text, proxy_host, proxy_port, i2s):

    # ======== BUILD HTTP REQUEST (via proxy) ========
    voice = 'John'
    lang = 'en-us'
    host = "api.voicerss.org"
    path = f"/?key={TTS_API_KEY}&hl={lang}&v={voice}&f=44khz_16bit_mono&src={text.replace(' ', '%20')}"
    request = (
        f"GET http://{host}{path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Connection: close\r\n\r\n"
    )

    # ======== CONNECT TO PROXY & STREAM ========
    addr = socket.getaddrinfo(proxy_host, proxy_port)[0][-1]
    s = socket.socket()
    s.connect(addr)
    print("Connected to proxy")

    try:
        s.send(request.encode())
        print("Request sent")

        while True:
            line = s.readline()
            if not line or line == b"\r\n":
                break

        s.read(44)

        print("Streaming audio...")
        while True:
            data = s.read(1024)
            if not data:
                break
            i2s.write(data)
            
    finally:
        s.close()
        i2s.deinit()
        print("Done playing audio.")