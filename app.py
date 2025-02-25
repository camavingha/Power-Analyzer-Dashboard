from flask import Flask, render_template, jsonify
from modbus_client import ModbusClient

app = Flask(__name__)

modbus = ModbusClient(port='COM3', baud_rate=9600, peripheral_address=0x01)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data', methods=['GET'])
def get_data():
    data = {
        "L1 Phase Voltage": modbus.read_register(0x04, 0x0000, 0x0002),
        "L2 Phase Voltage": modbus.read_register(0x04, 0x0010, 0x0002),
        "L3 Phase Voltage": modbus.read_register(0x04, 0x0020, 0x0002),
        "L1/L2 Voltage": modbus.read_register(0x04, 0x003E, 0x0002),
        "L2/L3 Voltage": modbus.read_register(0x04, 0x0040, 0x0002),
        "L3/L1 Voltage": modbus.read_register(0x04, 0x0042, 0x0002),
        "L1 Current": modbus.read_register(0x04, 0x0002, 0x0002),
        "L2 Current": modbus.read_register(0x04, 0x0012, 0x0002),
        "L3 Current": modbus.read_register(0x04, 0x0022, 0x0002),
        "Neutral Current": modbus.read_register(0x04, 0x0044, 0x0002),
        "Active 3-Phase Power": modbus.read_register(0x04, 0x0030, 0x0002),
        "Apparent 3-Phase Power": modbus.read_register(0x04, 0x0036, 0x0002),
        "3-Phase Power Factor": modbus.read_register(0x04, 0x0038, 0x0002),
        "Consume Active Energy": modbus.read_register(0x04, 0x0060, 0x0002),
        "L1 Frequency": modbus.read_register(0x04, 0x003C, 0x0002),
        "L1 (%)THD Voltage": modbus.read_register(0x04, 0x0046, 0x0002),
        "L2 (%)THD Voltage": modbus.read_register(0x04, 0x0048, 0x0002),
        "L3 (%)THD Voltage": modbus.read_register(0x04, 0x004A, 0x0002),
        "L1 (%)THD Current": modbus.read_register(0x04, 0x004C, 0x0002),
        "L2 (%)THD Current": modbus.read_register(0x04, 0x004E, 0x0002),
        "L3 (%)THD Current": modbus.read_register(0x04, 0x0050, 0x0002),
    }

    print("all data =>\n", data)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
