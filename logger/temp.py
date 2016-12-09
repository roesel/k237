import serial
import json

ser = serial.Serial('COM8', 9600)


def read_measurement():
    ser.write(b'L')

    bytes_response = ser.readline()
    string_response = str(bytes_response, 'utf-8')
    response = string_response.replace('\r\n', '')
    # print(response)

    return response


def convert_response(response):
    d_in = json.loads(response)
    d_out = {}
    for key, value in d_in.items():
        d_out[key] = float(value)
    return d_out


response = read_measurement()
data = convert_response(response)
print(data)
