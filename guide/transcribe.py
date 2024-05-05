import asyncio
import bleak
from bleak import BleakClient, BleakScanner
import wave
from datetime import datetime
import numpy as np
import time
import os
import struct

from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)

DEEPGRAM_API_KEY = "ff0071baa966e55e33039f9377ab2915d4569047"
deepgram = DeepgramClient(DEEPGRAM_API_KEY)

DEVICE_NAME = "Compass"
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "aeab4b05-a5fd-4c89-89de-17f1509e2734"

SAMPLE_RATE = 16000 # samples per second
SAMPLE_WIDTH = 2 # bytes per second
CHANNELS = 1
BUFFER_SIZE = 320000 # 20 seconds of audio as incoming samples are compressed to 1 byte per sample

filename = "output.wav"

def ulaw2linear(ulaw_byte):
    """Decompresses mulaw byte to 16 bit sample"""
    EXPONENT_LUT = [0, 132, 396, 924, 1980, 4092, 8316, 16764]
    ulaw_byte = ~ulaw_byte
    sign = (ulaw_byte & 0x80)
    exponent = (ulaw_byte >> 4) & 0x07
    mantissa = ulaw_byte & 0x0F
    sample = EXPONENT_LUT[exponent] + (mantissa << (exponent + 3))
    if sign != 0:
        sample = -sample
    
    return sample

# Use 2 buffers, so the start of one buffer is not
# overwritten while processing it.
bytes_buffer1 = []
bytes_buffer2 = []
active_buffer_idx = 0

async def handle_audio_data(sender, data):
    global bytes_buffer1, bytes_buffer2, active_buffer_idx
    if active_buffer_idx == 0:
        bytes_buffer1.extend(data)
        if len(bytes_buffer1) >= BUFFER_SIZE:
            await process_audio(bytes_buffer1)
            bytes_buffer1 = []
            active_buffer_idx = 1
    else:
        bytes_buffer2.extend(data)
        if len(bytes_buffer2) >= BUFFER_SIZE:
            await process_audio(bytes_buffer2)
            bytes_buffer2 = []
            active_buffer_idx = 0
            
    

async def process_audio(audio_data):
    # convert each byte from mulaw 2 linear
    # using the ulaw2linear function
    linear_data = [ulaw2linear(byte) for byte in audio_data]
    linear_data = np.array(linear_data, dtype=np.int16)

    wav_file = wave.open(filename, "w")
    wav_file.setnchannels(CHANNELS)
    wav_file.setsampwidth(SAMPLE_WIDTH)
    wav_file.setframerate(SAMPLE_RATE)
    wav_file.writeframes(linear_data)
    wav_file.close()

    transcribe()
    print("Audio data written to output.wav")

def transcribe():
    #STEP 1: Read the audio file
    with open(filename, "rb") as file:
            buffer_data = file.read()

    payload: FileSource = {
            "buffer": buffer_data,
    }

    #STEP 2: Configure Deepgram options for audio analysis
    options = PrerecordedOptions(
        model="nova-2",
        smart_format=True,
        diarize=True,
        language="en"
        # detect_language=True
    )

    # STEP 3: Call the transcribe_file method with the text payload and options
    response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)

    #STEP 4: Extract the transcription from the response
    confidence = response['results']['channels'][0]['alternatives'][0]['confidence']
    print(f"Confidence: {confidence}")
    
    transcription_with_new_lines= ""
    if confidence >= 0.5:
        paragraphs = response['results']['channels'][0]['alternatives'][0]['paragraphs']['paragraphs']
        for paragraph in paragraphs:
            sentences = paragraph['sentences']
            for sentence in sentences:
                transcription_with_new_lines += sentence['text'] + "\n"
    else:
        transcription_with_new_lines = None
        
    print("transcription:")
    print(transcription_with_new_lines)

    # Delete the audio file before returning the transcription
    os.remove(filename)

async def main():
    devices = await BleakScanner.discover()
    compass = None

    for device in devices:
        if device.name and DEVICE_NAME in device.name:
            compass = device

    if compass is None:
        print("Could not find the compass device. Try restarting the wearable.")
        return
    

    try:
        async with BleakClient(compass.address) as client:
            # Read the value of the characteristic
            await client.start_notify(CHARACTERISTIC_UUID, handle_audio_data)

            while True:
                await asyncio.sleep(1)
            
    except Exception as e:
        print(e)
        print(f"Error: {e}")

    

asyncio.run(main())