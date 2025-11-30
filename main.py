import time, sys
from hm_terminal import HMTerminal

#['AT', 'AT+RESET', 'AT+VERSION', 'AT+HELP', 'AT+NAME', 'AT+PIN', 'AT+BAUD', 'AT+LADDR', 
# 'AT+ADDR', 'AT+DEFAULT', 'AT+RENEW', 'AT+STATE', 'AT+PWRM', 'AT+POWE', 'AT+SLEEP', 'AT+ROLE', 
# 'AT+PARI', 'AT+STOP', 'AT+INQ', 'AT+SHOW', 'AT+CONN', 'AT+IMME', 'AT+START', 'AT+UUID', 'AT+CHAR']

if __name__ == "__main__":
    baudrate = 9600
    hm_terminal = HMTerminal("/dev/ttyUSB0", baudrate)
    
    if not hm_terminal.open():
        sys.exit()
        
    if hm_terminal.test_device():
        commands = hm_terminal.get_supported_cmds()
        #print(commands)
    else:
        sys.exit()

    while True:
        print("Idle for 1s")
        time.sleep(1)
