import Client
import sys

def cb1(address, data):
    print (address, 'Client1: received "%s"' % data)
    pass

def cb2(address, data):
    print (address, 'Client2: received "%s"' % data)
    pass

def main():
    client1 = Client.ClientConnection('localhost', 5000, cb1)
    if (client1.Connect()):
        client1.SendData(bytes("Itay1", encoding='utf8'))
    if (client1.Connect()):
        client1.SendData(bytes("Itay1", encoding='utf8'))

    client2 = Client.ClientConnection('localhost', 5000, cb2)
    if (client2.Connect()):
        client2.SendData(bytes("Itay2", encoding='utf8'))

    print ("\nPress Enter key to exit...\n")
    sys.stdin.flush()
    sys.stdin.read(1)
    client1.Disconnect()
    client2.Disconnect()
    pass

if __name__ == "__main__":
    main()