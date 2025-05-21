from machine import SPI, Pin, I2S
import sdcard, os, network
from time import sleep


def wifi_connect(SSID, PASSWORD):
    # === WIFI Setup ===
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(SSID, PASSWORD)
    print("Connecting to Wi-Fi...")
    while not wifi.isconnected():
        sleep(1)
    print("Connected! Network config:", wifi.ifconfig())


def sdcard_setup(sd_sck, sd_mosi, sd_miso, sd_cs):
    # === SPI + SD Card Setup ===
    spi = SPI(
        2, 
        baudrate=1_000_000, 
        sck=Pin(sd_sck), 
        mosi=Pin(sd_mosi), 
        miso=Pin(sd_miso)
    )
    cs = Pin(sd_cs, Pin.OUT)
    sd = sdcard.SDCard(spi, cs)
    os.mount(sd, '/sd')
    print("SD card mounted.")
    return sd


def mic_setup(mic_sck, mic_ws, mic_sd):
    # === I2S Microphone Setup ===
    i2s_mic = I2S(
        0, 
        sck=Pin(mic_sck), 
        ws=Pin(mic_ws), 
        sd=Pin(mic_sd), 
        mode=I2S.RX, 
        bits=16, 
        format=I2S.MONO, 
        rate=16000, 
        ibuf=40000
    )
    return i2s_mic


def button_setup(button_pin):
    # === Button Setup ===
    button = Pin(button_pin, Pin.IN, Pin.PULL_UP)
    return button


def speaker_setup(apm_sck, apm_ws, apm_sd):
    # ======== Speaker I2s Setup ========
    i2s_speaker = I2S(
        1,
        sck=Pin(apm_sck),
        ws=Pin(apm_ws),
        sd=Pin(apm_sd),
        mode=I2S.TX,
        bits=16,
        format=I2S.MONO,
        rate=44100,  
        ibuf=20000 
    )
    return i2s_speaker