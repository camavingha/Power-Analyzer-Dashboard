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

        # Register scaling factors and units
        self.calibration_map = {
            0x0000: (10, "V"),
            0x0010: (10, "V"),
            0x0020: (10, "V"),
            0x003E: (10, "V"),
            0x0040: (10, "V"),  
            0x0042: (10, "V"),

            0x0002: (1, "mA"),
            0x0012: (1, "mA"),
            0x0022: (1, "mA"),
            0x0044: (1, "mA"),
           
            0x0046: (100, "%"),
            0x0048: (100, "%"),
            0x004A: (100, "%"),
            0x004C: (100, "%"),
            0x004E: (100, "%"),
            0x0050: (100, "%"),
            0x0030: (1, "W"),
            0x0036: (1, "VA"),
            0x0038: (100, "%"),
            0x0060: (1, "Wh"),

            0x003C: (100, "Hz")
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

                    # Apply calibration
                    scale, unit = self.calibration_map.get(register, (1, ""))  # Default scale 1, unit empty
                    calibrated_value = decimal_value / scale
                    return f"{calibrated_value:.2f} {unit}"  # Round to 2 decimal places
                else:
                    # Return "N/A" but keep unit
                    _, unit = self.calibration_map.get(register, (1, ""))
                    return f"N/A {unit}"
        except Exception as e:
            print(f"Error: {e}")
            _, unit = self.calibration_map.get(register, (1, ""))
            return f"N/A {unit}"
