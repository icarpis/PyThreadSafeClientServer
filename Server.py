import socket
import sys
import threading
import select

class ServerConnection():

    def __clientThread(self, callback, connection, client_address):
        try:
            inputs = [ connection ]
            outputs = [ ]
            timeout = 1
            while self.startClients and (client_address in self.connections):
                readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
                if not ((readable or writable or exceptional)):
                    if (not self.startClients):
                        break
                    continue

                if (not self.startClients or (client_address not in self.connections)):
                    break

                quit = False
                for sock in readable:
                    data = sock.recv(self.bufferSize)
                    if (len(data) == 0):
                        quit = True
                        break

                    if (data and (len(data) > 0)):
                        try:
                            callback(client_address, data)
                        except Exception as e:
                            print('Server: callback has thrown an exception ', e)
                            pass
                if (quit):
                    break
        except Exception as e:
            print ('Server: ', e)
        finally:
            try:
                connection.close()
                del self.connections[client_address]
            except:
                pass
            print("Exiting Client Thread")
            callback(client_address, None)


    def __listenerThread(self, callback, numOfAllowedConnections):
        try:
            self.sock.settimeout(0)
            self.sock.setblocking(0)
            self.sock.listen(numOfAllowedConnections)
            print ('Server: Waiting for a connection...')
            read_list = [self.sock]
            timeout = 1
            while self.startListener:
                readable, writable, exceptional = select.select(read_list, [], [], timeout)
                if not ((readable or writable or exceptional)):
                    if (not self.startListener):
                        break
                    continue

                connection = None
                connection, client_address = self.sock.accept()
                connection.setblocking(0)
                self.mutex.acquire()
                if (self.startListener and connection):
                    self.connections[client_address] = connection
                    print ('\nServer: client connected:', client_address)
                    t = threading.Thread( target=self.__clientThread, args=(callback, connection, client_address) )
                    self._connectionThreads.append(t)
                    t.start()
                self.mutex.release()
                if (self.startListener and connection and self.onCon):
                    try:
                        self.onCon(client_address)
                    except:
                        print('Server: onCon callback has thrown an exception!')
                        pass
        except Exception as e:
            print (e)
            self.Close()
        finally:
            print("Exiting Listener Thread")

    def __init__(self):
        self._listenerThread = None
        self.connections = {}
        self._connectionThreads = []
        self.mutex = threading.Lock()
        self.sock = None
        self.callback = None
        self.startClients = False
        self.numOfAllowedConnections = None

    def Open(self, ip, port, dataCallback, onNewConCallback, numOfAllowedConnections, bufferSize = 1000):
        status = True
        try:
            self.mutex.acquire()
            if (self.sock):
                return False

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.callback = dataCallback
            self.onCon = onNewConCallback
            self.numOfAllowedConnections = numOfAllowedConnections
            self.bufferSize = bufferSize
            server_address = (ip, port)
            self.sock.bind(server_address)
            print ('Creating socket on %s port %s' % self.sock.getsockname())
            self.startListener = True
            self.startClients = True
            self._listenerThread = threading.Thread( target=self.__listenerThread, args=(self.callback, self.numOfAllowedConnections, ) )
            self._listenerThread.start()
        except Exception as e:
            print(e)
            status = False
        finally:
            self.mutex.release()
            return status

    def Close(self):
        self.mutex.acquire()
        try:
            if (self.startListener == False):
                return False

            self.startListener = False
            if (self._listenerThread):
                try:
                    self._listenerThread.join(3)
                except Exception as e:
                    pass

            self.startClients = False
            try:
                for sock in self.connections:
                    self.connections[sock].close()
            except Exception as e:
                pass
            self.connections = {}

            for t in self._connectionThreads:
                try:
                    t.join(3)
                except Exception as e:
                    pass

            self._connectionThreads = []
        finally:
            self.mutex.release()
            return True

    def SendDataAll(self, data):
        try:
            self.mutex.acquire()
            print ('Server: sending "%s"' % data)
            for connection in self.connections.values():
                connection.sendall(data)
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            self.mutex.release()

    def SendData(self, sock, data):
        try:
            self.mutex.acquire()
            if sock in self.connections:
                print (sock, 'Server: sending "%s"' % data)
                self.connections[sock].sendall(data)
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            self.mutex.release()

    def GetNumOfSockets(self):
        try:
            self.mutex.acquire()
            numOfCon = len(self.connections)
            return numOfCon
        finally:
            self.mutex.release()

    def CloseSocket(self, sock):
        try:
            self.mutex.acquire()
            if sock in self.connections:
                try:
                    self.connections[sock].close()
                    del self.connections[sock]
                except:
                    pass
        finally:
            self.mutex.release()

    def GetSocket(self, index):
        try:
            sock = None
            self.mutex.acquire()
            sock = list(self.connections.items())[index][0]
            return sock
        except IndexError:
            return None
        finally:
            self.mutex.release()
