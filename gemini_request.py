from keys import gemini_API_KEY
import socket, ssl, json, os
from time import sleep


def send_audio(proxy_host, proxy_port):

    # === API Details ===
    api_host = 'generativelanguage.googleapis.com'
    api_port = 443
    upload_path = f'/upload/v1beta/files?key={gemini_API_KEY}'
    gen_path = f'/v1beta/models/gemini-2.0-flash-exp:generateContent?key={gemini_API_KEY}'

    # === File Details ===
    filename = 'recording.wav'
    filepath = '/sd/' + filename
    filetype = 'audio/wav'
    chunk_size = 1024

    file_size = os.stat(filepath)[6]
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    pre_body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f'Content-Type: {filetype}\r\n\r\n'
    )
    post_body = f'\r\n--{boundary}--\r\n'
    content_length = len(pre_body) + file_size + len(post_body)

    # === Upload File ===
    print("Connecting to proxy for upload...")
    s = socket.socket()
    s.connect((proxy_host, proxy_port))
    s.send(bytes(f"CONNECT {api_host}:{api_port} HTTP/1.1\r\nHost: {api_host}\r\n\r\n", 'utf-8'))

    resp = s.recv(4096)
    print("Proxy response:", resp.decode())
    if b'200 Connection Established' not in resp:
        raise Exception("Failed to establish CONNECT tunnel")

    ssl_sock = ssl.wrap_socket(s, server_hostname=api_host)

    request_headers = (
        f"POST {upload_path} HTTP/1.1\r\n"
        f"Host: {api_host}\r\n"
        f"X-Goog-Upload-Command: start, upload, finalize\r\n"
        f"X-Goog-Upload-Header-Content-Length: {file_size}\r\n"
        f"X-Goog-Upload-Header-Content-Type: {filetype}\r\n"
        f"Content-Type: multipart/form-data; boundary={boundary}\r\n"
        f"Content-Length: {content_length}\r\n"
        f"Connection: close\r\n\r\n"
    )

    ssl_sock.write(request_headers)
    ssl_sock.write(pre_body)

    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            ssl_sock.write(chunk)

    ssl_sock.write(post_body)

    print("Reading upload response...")
    upload_response = b""
    try:
        while True:
            data = ssl_sock.read(1024)
            if not data:
                break
            upload_response += data
    except:
        pass
    ssl_sock.close()

    # === Extract File URI and MIME Type from JSON ===
    upload_text = upload_response.decode()
    print("Upload response:", upload_text)

    file_uri = None
    mime_type = None
    try:
        body = upload_text.split("\r\n\r\n", 1)[-1]
        upload_json = json.loads(body)
        file_uri = upload_json.get("file", {}).get("uri")
        mime_type = upload_json.get("file", {}).get("mimeType")
    except Exception as e:
        print("Failed to parse fileUri or mimeType:", e)

    if not file_uri or not mime_type:
        raise Exception("Missing fileUri or mimeType in response!")

    print("Waiting before second request...")
    sleep(1)

    # === Send GenerateContent Request ===
    print("Connecting to proxy for generateContent...")
    s2 = socket.socket()
    s2.connect((proxy_host, proxy_port))
    s2.send(bytes(f"CONNECT {api_host}:{api_port} HTTP/1.1\r\nHost: {api_host}\r\n\r\n", 'utf-8'))

    resp2 = s2.recv(4096)
    print("Proxy response:", resp2.decode())
    if b'200 Connection Established' not in resp2:
        raise Exception("Failed to establish CONNECT tunnel (2nd request)")

    ssl_sock2 = ssl.wrap_socket(s2, server_hostname=api_host)

    payload_dict = {
      "contents": [
        {
          "role": "user",
          "parts": [
            {
              "fileData": {
                "fileUri": file_uri,
                "mimeType": mime_type
              }
            }
          ]
        },
        {
          "role": "user",
          "parts": [
            {
              "text": "answer this. Keep your response short and dont use /n or symbols or special characters except comma and period in your response, just use plain text."
            }
          ]
        }
      ],
      "generationConfig": {
        "temperature": 1,
        "topK": 40,
        "topP": 0.95,
        "maxOutputTokens": 256,
        "responseMimeType": "text/plain"
      }
    }

    payload = json.dumps(payload_dict)
    content_length = len(payload)

    request = (
        f"POST {gen_path} HTTP/1.1\r\n"
        f"Host: {api_host}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {content_length}\r\n"
        f"Connection: close\r\n\r\n"
    )

    ssl_sock2.write(request)
    ssl_sock2.write(payload)

    print("Reading Gemini response...")
    response = b""
    try:
        while True:
            data = ssl_sock2.read(1024)
            if not data:
                break
            response += data
    except:
        pass


    response = response.decode()
    response_parts = response.split("\r\n\r\n")
    body = response_parts[1]
    body_parts = body.split("\r\n")
    content = body_parts[1]

    parse_json = json.loads(content)
    raw_text = parse_json["candidates"][0]["content"]["parts"][0]["text"]

    text = raw_text[:-1]
    print(text)

    # === Cleanup ===
    ssl_sock2.close()
    os.umount('/sd')
    return text