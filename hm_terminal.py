import logging
import serial
from enum import Enum

_HM_LOGGER_NAME = "[HM-10-terminal]"
_HM_LOGGING_LEVEL = logging.INFO

# All AT commands must be terminated at \r\n 
class ATCommands(str, Enum):
    op_at = "AT\r\n"
    op_help = "AT+HELP\r\n"

    def opcode(self) -> bytes:
        return bytes(str.__str__(self), encoding='utf-8')

class HMTerminal(object):
    logging.basicConfig(
        format='%(asctime)s %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(_HM_LOGGER_NAME)
    logger.setLevel(_HM_LOGGING_LEVEL)

    def __init__(self, port:str, baudrate:int):
        self.supported_cmds = None

        self.port = port
        self.serial_if = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

    def open(self) -> bool:
        """
            Open a serial communication por for the HM device
        """
        if not self.serial_if.is_open:
            self.serial_if.open()
            self.logger.info(f"Opened serial port {self.port}")
        else:
            self.logger.warning(f"Serial port {self.port} already opened")

        return self.serial_if.is_open

    def test_device(self) -> bool:
        """
            Checks if the HM device replies to AT commands properly
        """
        self.serial_if.write(ATCommands.op_at.opcode())
        data = self.serial_if.readline()
        status_ok = False

        if data:
            decoded_data = data.decode('utf-8', errors="ignore")
            self.logger.info(f"AT sent. Received: {decoded_data}")
        else:
            self.logger.error("AT sent. No data received")

        status_ok = True if "OK" in decoded_data else False
        
        return status_ok

    def get_supported_cmds(self) -> list:
        """
            Send AT+HELP command to get a list of all supported commands
        """
        replies = []
        self.serial_if.write(ATCommands.op_help.opcode())

        # the read_until(terminator=b'') method doesn't get the complete device reply so we get one by one
        while True:
            data = self.serial_if.readline()
            replies.append(data)

            if data:
                continue
            else:
                break

        for reply in replies:
            reply = reply.decode('utf-8', errors="ignore")
        
        msg = ''.join(map(lambda d: d.decode('utf-8', errors='ignore'), replies))
        self.logger.debug(f"Received: {msg}")

        msg_cmds_match = msg.split('\n')
        msg_cmds_match = [row[row.find('AT'):-1].split(' ')[0] for row in msg_cmds_match if 'AT' in row]
        self.supported_cmds = msg_cmds_match

        return msg_cmds_match
    
    def is_opcode_supported(self, opcode:str) -> bool:
        """
            opcode format is the same as any AT command. AT+<something>
        """
        is_supported = True if opcode in self.supported_cmds else False
        return is_supported
    
    def __del__(self):
        if self.serial_if.is_open:
            self.logger.info(f"Closing serial port {self.port}")
            self.serial_if.close()