import setup_pins
import mic
import gemini_request
import text_to_speech


# === Wi-fi setup ===
SSID = "Your_SSID"
PASSWORD = "Your_password"
proxy_host = 'Your_proxy_host'
proxy_port = 8080

# === Sdcard pin setup ===
sd_sck = 18
sd_mosi = 23
sd_miso = 19
sd_cs = 5

# === Microphone pin setup ===
mic_sck = 14
mic_ws = 15
mic_sd = 32  

# === Button pin Setup ===
button_pin = 4

# === Amp(Speaker) pin setup ===
apm_sck = 26
apm_ws = 25
apm_sd = 22


#  === Initializing the components ===
setup_pins.wifi_connect(SSID, PASSWORD)
sd = setup_pins.sdcard_setup(sd_sck, sd_mosi, sd_miso, sd_cs)
button = setup_pins.button_setup(button_pin)
i2s_mic = setup_pins.mic_setup(mic_sck, mic_ws, mic_sd)
i2s_speaker = setup_pins.speaker_setup(apm_sck, apm_ws, apm_sd)

# === Recording, Requesting, Streaming ===
mic.mic_record(button, i2s_mic)
text = gemini_request.send_audio(proxy_host, proxy_port)
text_to_speech.text_to_audio_play(text, proxy_host, proxy_port, i2s_speaker)