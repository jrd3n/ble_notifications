from bluepy import btle

# Define a callback function to handle notifications
def handle_notification(handle, data):
    print("Received notification from handle {}: {}".format(handle, data))

# Specify the MAC address of the BLE device you want to connect to
iTag_MAC = 'FF:FF:10:BD:96:ED'

# Connect to the device
try:
    device = btle.Peripheral(iTag_MAC, iface=1)
except:
    print("Could not connect to device, please run hciconfig to see if the interface is up and running.")
    exit()

print(device.getState())

# Enable notifications for a specific characteristic
characteristic_uuid = '0000ffe100001000800000805f9b34fb'
characteristic = device.getCharacteristics(uuid=characteristic_uuid)[0]
handle = characteristic.getHandle()
device.writeCharacteristic(handle + 1, b"\x01\x00", withResponse=True)

# Set the notification callback function
device.withDelegate(btle.DefaultDelegate())
device.setDelegate(btle.DefaultDelegate())

# Main loop to listen for notifications
while True:
    if device.waitForNotifications(1.0):
        print("CLICK")
        continue

# Disconnect from the device
device.disconnect()
