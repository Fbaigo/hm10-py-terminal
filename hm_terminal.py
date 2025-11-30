import logging
import serial
from enum import Enum

_HM_LOGGER_NAME = "[HM-10-terminal]"
_HM_LOGGING_LEVEL = logging.INFO

# All AT commands must be terminated at \r\n
# op codes terminated with q are queries

class ATCommands(str, Enum):
    op_at = "AT\r\n"
    op_help = "AT+HELP\r\n"
    op_imme = "AT+IMME\r\n"
    op_imme_q = "AT+IMME?\r\n"

    def opcode(self) -> bytes:
        return bytes(str.__str__(self), encoding='utf-8')
    
    def __str__(self) -> str:
        return str.__str__(self)

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
    
    def send_at_command(self, opcode:str) -> str:
        if "\r\n" not in opcode:
            opcode = opcode.replace('\r', '')
            opcode = opcode.replace('\n', '')
            opcode = ''.join([opcode, "\r\n"])
            
        opcode = bytes(opcode, encoding="utf-8", errors="ignore")
        self.serial_if.write(opcode)

        replies = []
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

        return msg
    
    def _parse_reply(self, msg:str) -> tuple:
        status = None
        param = None
        
        try:
            status = msg.split('+')[0]
        except:
            pass

        try:
            param = msg.split(':')[1].replace('\r\n', '')
        except:
            pass
    
        return (status, param)

    def test_device(self) -> bool:
        """
            Checks if the HM device replies to AT commands properly
        """
        status_ok = False
        msg = self.send_at_command(ATCommands.op_at)

        if msg:
            self.logger.info(f"AT sent. Received: {msg}")
        else:
            self.logger.error("AT sent. No data received")

        status_ok = True if "OK" in msg else False
        return status_ok

    def get_supported_cmds(self) -> list:
        """
            Send AT+HELP command to get a list of all supported commands
        """

        msg = self.send_at_command(ATCommands.op_help)

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
    
    def get_work_mode(self):
        msg = self.send_at_command(ATCommands.op_imme_q)
        workmode = self._parse_reply(msg)
        return workmode
    
    def __del__(self):
        if self.serial_if.is_open:
            self.logger.info(f"Closing serial port {self.port}")
            self.serial_if.close()