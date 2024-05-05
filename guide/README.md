# Hardware Guide

### Service ID

`4fafc201-1fb5-459e-8fcc-c5c9c331914b`

### Characteristics

1. `aeab4b05-a5fd-4c89-89de-17f1509e2734` - PDM bytes (16khz, 2 bytes per sample, 1 channel), using mulaw codec.
2. `9f83442c-7da2-49ca-94e3-b06201a58508` - Voltage, 32 bytes
3. `2BED` - Battery State, "0" or "1", or "30" and "31" in hex value. 0 - not charging, 1 - charging

### Example

in `transcribe.py` you can find an example of a BLE client
that receives bytes from Compass and uses Deepgram to transcribe.

How to run?

1. Create virtual environment

```
python -m venv venv
```

2. Install requirements

```
pip install -r requirements.txt
```

3. Make sure your Compass is on
4. Run the script

```
python transcribe.py
```
