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
            'timeout': 0.1  # Reduced timeout for faster responses
        }
        self.data = {}  # Store processed responses
        self.ser = None  # Keep serial port open

    def open_connection(self):
        if self.ser is None or not self.ser.is_open:
            self.ser = serial.Serial(self.port, **self.serial_settings)

    def close_connection(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

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

    def create_read_request(self, function_code, register, num_registers):
        request = bytearray([
            self.peripheral_address,
            function_code,
            register >> 8,
            register & 0xFF,
            num_registers >> 8,
            num_registers & 0xFF
        ])
        request.extend(self.calculate_crc(request))
        return request

    def read_register(self, function_code, register, num_registers, label):
        try:
            request = self.create_read_request(function_code, register, num_registers)
            self.ser.write(request)
            time.sleep(0.1)  # Reduced sleep time
            response = self.ser.read(256)  # Read response

            if response:
                raw_hex = response.hex(' ').upper()
                raw_bytes = response[3:-2]  # Exclude address, function code, and CRC
                decimal_value = int.from_bytes(raw_bytes, byteorder='big')
                self.data[label] = decimal_value
                print(f"{label}: {decimal_value}")
            else:
                print(f"Failed to read {label}. Response incomplete.")
        except Exception as e:
            print(f"Error reading {label}: {e}")

    def collect_data(self, config):
        self.open_connection()  # Keep serial port open
        try:
            while True:
                print("\nReading data...")
                print("=================================")
                for param in config:
                    self.read_register(param['function_code'], param['register'], param['num_registers'], param['label'])
                time.sleep(0.1)  # Reduced overall sleep time
        finally:
            self.close_connection()  # Close port when stopping

if __name__ == "__main__":
    config = [
        {"function_code": 0x04, "register": 0x0000, "num_registers": 0x0002, "label": "L1 Phase Voltage"},
        {"function_code": 0x04, "register": 0x0010, "num_registers": 0x0002, "label": "L2 Phase Voltage"},
        {"function_code": 0x04, "register": 0x0020, "num_registers": 0x0002, "label": "L3 Phase Voltage"},
        {"function_code": 0x04, "register": 0x003E, "num_registers": 0x0002, "label": "L1/L2 Voltage"},
        {"function_code": 0x04, "register": 0x0040, "num_registers": 0x0002, "label": "L2/L3 Voltage"},
        {"function_code": 0x04, "register": 0x0042, "num_registers": 0x0002, "label": "L3/L1 Voltage"},

        {"function_code": 0x04, "register": 0x0002, "num_registers": 0x0002, "label": "L1 Current "},
        {"function_code": 0x04, "register": 0x0012, "num_registers": 0x0002, "label": "L2 Current "},
        {"function_code": 0x04, "register": 0x0022, "num_registers": 0x0002, "label": "L3 Current "},
        {"function_code": 0x04, "register": 0x0044, "num_registers": 0x0002, "label": "Neutral Current "},

        {"function_code": 0x04, "register": 0x0030, "num_registers": 0x0002, "label": "Active 3-Phase Power"},
        {"function_code": 0x04, "register": 0x0036, "num_registers": 0x0002, "label": "Apparent 3-Phase Power"},
        {"function_code": 0x04, "register": 0x0038, "num_registers": 0x0002, "label": "3-Phase Power Factor"},
        {"function_code": 0x04, "register": 0x0060, "num_registers": 0x0002, "label": "Consume Active Energy"},

        {"function_code": 0x04, "register": 0x003C, "num_registers": 0x0002, "label": "L1 Frequency"},
        {"function_code": 0x04, "register": 0x0046, "num_registers": 0x0002, "label": "L1 (%)THD Voltage"},
        {"function_code": 0x04, "register": 0x0048, "num_registers": 0x0002, "label": "L2 (%)THD Voltage"},
        {"function_code": 0x04, "register": 0x004A, "num_registers": 0x0002, "label": "L3 (%)THD Voltage"},
        {"function_code": 0x04, "register": 0x004C, "num_registers": 0x0002, "label": "L1 (%)THD Current"},
        {"function_code": 0x04, "register": 0x004E, "num_registers": 0x0002, "label": "L2 (%)THD Current"},
        {"function_code": 0x04, "register": 0x0050, "num_registers": 0x0002, "label": "L3 (%)THD Current"},
    ]
    client = ModbusClient(port='COM3', baud_rate=9600, peripheral_address=0x01)
    client.collect_data(config)
