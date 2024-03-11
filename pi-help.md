# Pi help

## Hardware

breadboards aren't designed to handle large currents, so avoid using them for power going to Neopixels, boards, etc.

## OS

### Log in

```bash
ssh interlucid@interlucidpi
```

### Volume

set master volume to 100%

```bash
amixer cset numid=3 100%
```

actually I don't think this works ^ it doesn't seem to do anything when I have audio playing

```bash
amixer set Master 40000
```

set between 0 and 65536; quality tends to degrade after about 55000 though so just up the volume through whatever you're sending it to at that point

40000 is actually pretty good and more or less matches max volume on the MacBook (as of Nov 2023)

you may need to stop the python3 script using another terminal (if Ctrl + C doesn't work)

### Python

```bash
killall python3
```

helpful grep that keeps the headers in the filtered output so you can still know what's going on

```bash
ps -elf | grep -e  python3 -e UID
```

### Run on startup

```service
[Unit]
Description=Controller for Neopixels
After=multi-user.target

[Service]
Environment="XDG_RUNTIME_DIR=/run/user/1000"
Environment="PULSE_RUNTIME_PATH=/run/user/1000/pulse/"
WorkingDirectory=/home/interlucid/Music/neopixels
User=interlucid
Type=simple
Restart=always
ExecStart=/usr/bin/python3 /home/interlucid/Music/neopixels/main_controller.py

[Install]
WantedBy=multi-user.target
```

if you can get audio to work without systemd but it fails with systemd, that's probably because audio is a "user process" and you need to pass in user environment variables to systemd to get it to work (see https://askubuntu.com/questions/1379890/how-to-play-a-sound-from-a-systemd-service-on-ubuntu)

you can use variables like the following; make sure your user is 1000 or change the ID if not:

```
Environment="XDG_RUNTIME_DIR=/run/user/1000"
Environment="PULSE_RUNTIME_PATH=/run/user/1000/pulse/"
```

start with systemd

```bash
sudo systemctl enable --now neopixel.service
```

stop with systemd

```bash
sudo systemctl disable --now neopixel.service
```

using `--now` both makes it enabled or disabled on restart and also starts or stops the service at the same time

reload after changing the file

```bash
sudo systemctl daemon-reload
sudo systemd-analyze verify neopixel.service
```

status

```bash
systemctl status neopixel.service
```

logs

```bash
sudo journalctl -u neopixel.service
sudo journalctl -u neopixel.service -f # see shell
sudo journalctl -u neopixel.service -n 100 # see last 100 logs
```

## Drivers

important page that probably helped fix `ws2811_init failed with code -3 (Hardware revision is not supported)`: https://github.com/jgarff/rpi_ws281x/issues/483

you will probably get cryptic errors if your device isn't officially supported. see [this issue](https://github.com/jgarff/rpi_ws281x/issues/483) (and note the comment where it says `setup.py install` doesn't work so you need to run `sudo pip3 install /[path to packages]/rpi-ws281x-python/library` instead)

Raspberry Pi 3 A+ model info (add to rpihw.c; don't forget the comma in the previous block)

```c
    {
        .hwver = 0x9020e1,
        .type = RPI_HWVER_TYPE_PI4,
        .periph_base = PERIPH_BASE_RPI4,
        .videocore_base = VIDEOCORE_BASE_RPI2,
        .desc = "Pi 3 Model A Plus Rev 1.1"
    },
```

## Python

In order to control the pixels, the script must have `sudo` privileges. Note: VLC _cannot_ be run with `sudo` privileges! (even Python VLC)

as of 10/17/2023 I've decided to go with sending messages using stdin and PIPE and stuff to the subprocess to give it "commands" from the parent process. the parent plays VLC and the child controls the lights (sudo-ed)

### Flask

when creating the Flask subprocess I had to capture the output with a pipe. I then printed it from the main process with a prefix so I would know what lines were coming from Flask vs. the main process

sometimes print statements wouldn't work in Flask (or they would, but they would only show up when you sent an interrupt to Flask which isn't super helpful). apparently this is probably due to line buffering things that Flask does. usually you can get around this by adding `flush = True` to your print statement. this will flush the output buffer or something and actually immediately show the print statement

## VLC

VLC cannot be run as `sudo`! including in a Python VLC script (if the Python file is run as `sudo`)

```bash
cvlc -vvv --no-video
```

- `cvlc` runs VLC headless (no GUI)
- `-vvv` max level of debugging
- `--no-video` disables video playback/output
