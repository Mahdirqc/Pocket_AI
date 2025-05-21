import struct, os


# === WAV File Handling ===
def write_wav_header(f, sample_rate, bits_per_sample, num_channels):
    datasize = 0
    f.write(b'RIFF')
    f.write(struct.pack('<I', datasize + 36))
    f.write(b'WAVEfmt ')
    f.write(struct.pack('<IHHIIHH', 16, 1, num_channels, sample_rate,
                         sample_rate * num_channels * bits_per_sample // 8,
                         num_channels * bits_per_sample // 8, bits_per_sample))
    f.write(b'data')
    f.write(struct.pack('<I', datasize))


def update_wav_header(filename):
    size = os.stat(filename)[6]
    with open(filename, "r+b") as f:
        f.seek(4)
        f.write(struct.pack('<I', size - 8))
        f.seek(40)
        f.write(struct.pack('<I', size - 44))


def mic_record(button, i2s_mic):

    # === Start Recording ===
    buffer = bytearray(1024)
    wav_path = "/sd/recording.wav"

    print("Press and hold the button to record...")

    try:
        with open(wav_path, "wb") as wav:
            write_wav_header(wav, 16000, 16, 1)
            
            while True:
                if button.value() == 0:
                    print("Recording...")
                    while button.value() == 0:
                        num_read = i2s_mic.readinto(buffer)
                        if num_read > 0:
                            wav.write(buffer[:num_read])
                            
                    print("Recording stopped.")
                    break

        i2s_mic.deinit()
        update_wav_header(wav_path)
        print("Saved to", wav_path)

    except Exception as e:
        print("Error during recording:", e)