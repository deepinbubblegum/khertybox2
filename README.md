# KhertyBox
## create virtual serial port

```text
sudo socat -d -d pty,link=/dev/COM98,raw,echo=0,b9600 pty,link=/dev/COM99,raw,echo=0,b9600
```
## connection file config.yaml
```
serialport:
  port: "/dev/ttyACM0"
  baudrate: 5760
  bytesize: "EIGHTBITS" # FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS
  parity: "PARITY_EVEN" # PARITY_NONE, PARITY_EVEN, PARITY_ODD PARITY_MARK, PARITY_SPACE
  stopbits: "STOPBITS_ONE" # STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO
```