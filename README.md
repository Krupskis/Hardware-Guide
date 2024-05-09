# 🧭 Hardware Guide

a tiny always on wearable for your conversations

1. [Example client to transcribe Compass streamed audio](https://github.com/Krupskis/Hardware-Guide/tree/main/guide)

Below you can find instructions on how to update your wearable. One caveat, it currently overrides the device name to `Compass`.

## Update using just a few lines!

You will need a Macbook (Intel or M-series) and python3

1. Clone the repository

```
git clone https://github.com/Krupskis/Hardware-Guide.git
```

2. Connect device to your Mac using a USB-C cable

3. Open terminal and get port of the connected device

```
ls /dev/tty.*
```

![Serial devices list](/images/macport.png)

The device port will show up as `/dev/tty.usbmodem...`

4. Install `pyserial`

```
pip install pyserial
```

5. Flash the device

```
cd mac_updates
python flash.py <port>
```

as per the above example:

```
python flash.py /dev/tty.usbmodem101
```

## UF2 instructions (Needs access to reset pin, not recommended)

1. double click reset pin
2. the device should mount as a volume, i.e. you can access it as a directory under `/Volumes` on a mac.
3. drag and drop the `flash.uf2` file to the XIAO Volume.
