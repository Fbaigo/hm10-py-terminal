import logging
import serial, time

APP_MAIN = "HM-10-terminal"

class HMTerminal():
    def __init__(self, port:str, baudrate:int):
        self.port = port

        self.serial_if = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

    def open(self):
        if not self.serial_if.is_open:
            self.serial_if.open()
            print(f"Opened serial port {self.port}")
        else:
            print(f"Serial port {self.port} already opened")

    def test_hm10_state(self):
        cmd = b"AT\r\n" # All AT commands must be terminated at \r\n AT will be replied with OK
        self.serial_if.write(cmd)
        
        while True:
            data = self.serial_if.readline()
            if data:
                decoded_data = data.decode('utf-8', errors="ignore")
                print(f"Received: {decoded_data}")

                if decoded_data == "OK":
                    self.serial_if.close()
                    break
            else:
                print("No data received within timeout, trying again...")
            time.sleep(0.5)
    
    def __del__(self):
        if self.serial_if.is_open:
            print(f"Closing serial port {self.port}")
            self.serial_if.close()



if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(APP_MAIN)
    logger.setLevel(logging.INFO)

    hm_terminal = HMTerminal("/dev/ttyUSB0", 9600)
    hm_terminal.open()
    hm_terminal.test_hm10_state()

    while True:
        print("At main")
        time.sleep(1)
