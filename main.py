import time, sys
from hm_terminal import HMTerminal

if __name__ == "__main__":
    baudrate = 9600
    hm_terminal = HMTerminal("/dev/ttyUSB0", baudrate)
    
    if not hm_terminal.open():
        sys.exit()
        
    if hm_terminal.test_device():
        commands = hm_terminal.get_supported_cmds()
    else:
        sys.exit()

    while True:
        print("Idle for 1s")
        time.sleep(1)
