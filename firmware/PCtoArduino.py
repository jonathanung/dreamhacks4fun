#!/usr/bin/env python3
import serial
import time

# Adjust the port name as necessary (e.g., '/dev/ttyACM0' or '/dev/ttyUSB0')
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600

def main():
    try:
        # Open the serial port
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        # Wait a moment for the connection to initialize and Arduino to reset
        time.sleep(2)
        print("Serial connection established on", SERIAL_PORT)

        while True:
            # Send command to turn the LED ON
            key = input("Enter key: ")
            if key == " ":
                ser.write(b'ON\n')
            else: 
                ser.write(b'OFF\n')
            # print("Sent: ON")
            time.sleep(1)  # Wait 1 second

            # # Send command to turn the LED OFF
            # ser.write(b'OFF\n')
            # print("Sent: OFF")
            # time.sleep(1)  # Wait 1 second

    except serial.SerialException as e:
        print("Error opening serial port: ", e)
    except KeyboardInterrupt:
        print("Exiting program.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.write(b'OFF\n')  # Turn off the LED before closing the serial port
            ser.close()
            print("Serial port closed.")

if __name__ == '__main__':
    main()
