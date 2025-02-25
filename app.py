from flask import Flask, render_template, jsonify
from modbus_client import ModbusClient
from flask import request, send_file
import csv
import json
from fpdf import FPDF
import io
import pdfkit
from flask import Flask, render_template, jsonify, request, Response




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

@app.route('/export', methods=['POST'])
def export_data():
    data = request.get_json()
    export_format = request.args.get('format', 'csv')

    if not data:
        return jsonify({"error": "No data to export"}), 400

    # CSV Export
    if export_format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Timestamp"] + list(data[0].keys())[1:])  # Header
        for row in data:
            writer.writerow(row.values())
        return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=export.csv"})

    elif export_format == 'txt':
        output = io.StringIO()
        output.write("KMITL-CP Sensor Data Log\n")
        output.write("=" * 40 + "\n")
        for row in data:
            output.write(f"Timestamp: {row['timestamp']}\n")
            for key, value in row.items():
                if key != "timestamp":
                    output.write(f"{key}: {value}\n")
                output.write("-" * 40 + "\n")

        return Response(output.getvalue(), mimetype="text/plain",headers={"Content-Disposition": "attachment;filename=export.txt"})

    elif export_format == 'pdf':
        html_content = "<h1>Exported Data</h1><table border='1'><tr><th>Timestamp</th>"
        html_content += "".join([f"<th>{key}</th>" for key in data[0].keys() if key != "timestamp"])
        html_content += "</tr>"
        for row in data:
            html_content += "<tr><td>" + "</td><td>".join(map(str, row.values())) + "</td></tr>"
        html_content += "</table>"

        pdf = pdfkit.from_string(html_content, False)
        return Response(pdf, mimetype="application/pdf", headers={"Content-Disposition": "attachment;filename=export.pdf"})

    return jsonify({"error": "Invalid format"}), 400


if __name__ == '__main__':
    app.run(debug=True)
