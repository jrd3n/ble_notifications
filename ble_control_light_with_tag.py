from bluepy.btle import Peripheral, DefaultDelegate
import time

class SmartBulb:
    def __init__(self, device_address):
        self.device_address = device_address
        self.peripheral = None

    def connect(self):
        self.peripheral = Peripheral(self.device_address)

    def disconnect(self):
        if self.peripheral:
            self.peripheral.disconnect()
            self.peripheral = None

    def send_value(self, handle, value):
        if self.peripheral:
            value = bytes.fromhex(value)
            self.peripheral.writeCharacteristic(handle, value, withResponse=True)

    def on(self):
        self.send_value(0x9, '7e04016401ffff00ef')

    def off(self):
        self.send_value(0x9, '7e04010001ffff00ef')

    def set_color(self, color):
        color_code = {
            'red': '7e070503ff000010ef',
            'green': '7e07050300ff0010ef',
            'blue': '7e0705030000ff10ef',
            'white': '7e0505014fffff08ef'
        }
        if color in color_code:
            self.send_value(0x9, color_code[color])

    def party_lights(self):
        for _ in range(10):
            self.send_value(0x9, '7e07050300ff0010ef')
            time.sleep(0.2)
            self.send_value(0x9, '7e0705030000ff10ef')
            time.sleep(0.2)
            self.send_value(0x9, '7e070503ff000010ef')
            time.sleep(0.2)


class BLETag:
    def __init__(self, device_address, characteristic_uuid):
        self.device_address = device_address
        self.characteristic_uuid = characteristic_uuid
        self.peripheral = None
        self.notification_callback = None

    def connect(self):
        self.peripheral = Peripheral(self.device_address)

    def disconnect(self):
        if self.peripheral:
            self.peripheral.disconnect()
            self.peripheral = None

    def enable_notifications(self, callback):
        if self.peripheral:
            # Set up notification delegate
            self.notification_callback = callback
            notification_delegate = NotificationDelegate(callback)
            self.peripheral.setDelegate(notification_delegate)

            # Find the characteristic by UUID
            characteristic = self.peripheral.getCharacteristics(uuid=self.characteristic_uuid)[0]

            # Enable notifications for the characteristic
            self.peripheral.writeCharacteristic(characteristic.valHandle + 1, b'\x01\x00', withResponse=True)

    def listen_notifications(self):
        if self.peripheral:
            while True:
                if self.peripheral.waitForNotifications(1.0):
                    continue

                # Additional code can be added here to perform other tasks while waiting for notifications

class NotificationDelegate(DefaultDelegate):
    def __init__(self, callback):
        DefaultDelegate.__init__(self)
        self.callback = callback

    def handleNotification(self, cHandle, data):
        if self.callback:
            self.callback(cHandle, data)

if __name__ == "__main__":
    # Replace 'BE:58:97:00:1C:62' with the MAC address of your smart bulb
    bulb_MAC = 'BE:58:97:00:1C:62'
    # Create an instance of the SmartBulb class
    bulb = SmartBulb(bulb_MAC)
    # Connect to the smart bulb
    bulb.connect()

    # Replace 'FF:FF:10:BD:96:ED' with the MAC address of your BLE tag
    itag_MAC = 'FF:FF:10:BD:96:ED'
    # Replace '0000ffe100001000800000805f9b34fb' with the UUID of the characteristic you want to listen to
    itag_characteristic_uuid = '0000ffe100001000800000805f9b34fb'
    # Create an instance of the BLETag class
    itag = BLETag(itag_MAC, itag_characteristic_uuid)
    # Connect to the BLE tag
    itag.connect()
    # Enable notifications for the characteristic and pass the callback function
    
    # Callback function to handle received notifications
    def handle_notification(cHandle, data):
        print(f"Received notification on handle {cHandle}: {data.hex()}")
        bulb.on()
        bulb.party_lights()
        bulb.set_color('white')

    itag.enable_notifications(handle_notification)
    # Listen for notifications
    itag.listen_notifications()