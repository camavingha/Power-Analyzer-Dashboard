import serial
import time

class ModbusClient:
    def __init__(self, port='COM3', baud_rate=9600, peripheral_address=0x01):
        self.port = port
        self.baud_rate = baud_rate
        self.peripheral_address = peripheral_address
        self.serial_settings = {
            'baudrate': baud_rate,
            'bytesize': serial.EIGHTBITS,
            'parity': serial.PARITY_NONE,
            'stopbits': serial.STOPBITS_ONE,
            'timeout': 0.1
        }

    def calculate_crc(self, data):
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc.to_bytes(2, byteorder='little')

    def create_read_request(self, function_code, register=0x0000, num_registers=0x0002):
        request = bytearray([
            self.peripheral_address,
            function_code,
            register >> 8,
            register & 0xFF,
            num_registers >> 8,
            num_registers & 0xFF
        ])
        crc = self.calculate_crc(request)
        request.extend(crc)
        return request

    def read_register(self, function_code, register, num_registers):
        try:
            with serial.Serial(self.port, **self.serial_settings) as ser:
                request = self.create_read_request(function_code, register, num_registers)
                ser.write(request)
                time.sleep(0.1)
                response = ser.read(256)

                if response:
                    raw_bytes = response[3:-2]
                    decimal_value = int.from_bytes(raw_bytes, byteorder='big')
                    return decimal_value
                else:
                    return None
        except Exception as e:
            print(f"Error: {e}")
            return None
