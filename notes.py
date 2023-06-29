from bluepy import btle

# Define a callback function to handle notifications
def handle_notification(handle, data):
    print("Received notification from handle {}: {}".format(handle, data))

# Specify the MAC address of the BLE device you want to connect to
iTag_MAC = 'FF:FF:10:BD:96:ED'
characteristic_uuid = '0000ffe100001000800000805f9b34fb'

def connect_to_device():
        # Connect to the device
    while True:
        try:
            device = btle.Peripheral(iTag_MAC, iface=0)
            # print(device.getState())
        except:

            print("Could not connect to device, please run hciconfig to see if the interface is up and running.")
            # exit()

        if  device.getState() == "conn":
            return device

if __name__ == "__main__":

    while True:

        try:

            device = connect_to_device()

            if device.getState() == "conn":

                print("Connected to device")
                # Enable notifications for a specific characteristic

                characteristic = device.getCharacteristics(uuid=characteristic_uuid)[0]
                handle = characteristic.getHandle()
                device.writeCharacteristic(handle + 1, b"\x01\x00", withResponse=True)

                # Set the notification callback function
                #device.withDelegate(btle.DefaultDelegate())
                device.withDelegate(handle_notification)
                #device.setDelegate(btle.DefaultDelegate())
                device.setDelegate(handle_notification)

                # Main loop to listen for notifications
                while True:
                    if device.waitForNotifications(1):
                        print("CLICK")
                        continue

        except:
            print("Some error, more than likely Disconnected from device.")

              # Disconnect from the device
            #device.disconnect()