The components used in this project:
    1. Esp32-wroom-32D
    2. MEMS INMP441 with I2s Microphone
    3. Speaker + I2s Amplifier
    4. Sd card 


Apis' used in this project:
    1. Gemini
    2. Voice RSS 


How it works? 
                                  Gemini, Voice RSS      
                                           ^
                                           =
                                           =
                                           v
                    microphone = = = = > Esp32  = = = = > Speaker + Amp
                                           ^
                                           =
                                           =
                                           v
                                        sd card

recording with mic ----> saving it to sd card ----> uploading the file to gemini 
----> getting uri from gemini ----> requesting again for answer ----> getting response as text 
----> sending text to voice RSS ----> getting response as audio ----> streaming the audio
