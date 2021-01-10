import Server

def onNewConnection(sock):
    print(sock)

def dataCallback(sock, data):
    print (sock, 'server received "%s"' % data)
    pass
    
def main():
    import sys
    serverConnection = Server.ServerConnection()
    serverConnection.Open('localhost', 5000, dataCallback, onNewConnection, 3)

    print("\n1. Press Enter to continue...\n")
    sys.stdin.flush()
    sys.stdin.read(1)

    serverConnection.SendDataAll(bytes("Itay3", encoding='utf8'))

    numOfSock = serverConnection.GetNumOfSockets()
    print ("\nConnections: ", numOfSock)
    sock = None
    if (numOfSock > 0):
        sock = serverConnection.GetSocket(0)
    if (sock):
        serverConnection.SendData(sock, bytes("Itay4", encoding='utf8'))

    print("\n2. Press Enter to continue...\n")
    sys.stdin.flush()
    sys.stdin.read(1)
    serverConnection.CloseSocket(sock)

    print("\nPress Enter to Exit...\n")
    sys.stdin.flush()
    sys.stdin.read(1)

    serverConnection.Close()
    pass

if __name__ == "__main__":
    main()
    