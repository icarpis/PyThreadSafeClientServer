import socket
import threading
import select

class ClientConnection():

    def __init__(self, ip, port, callback, silence=True, bufferSize = 1000):
        self.mutex = threading.Lock()
        self.sock = None
        self.ip = ip
        self.port = port
        self.callback = callback
        self.clientThread = None
        self.connected = False
        self.silence = silence
        self.bufferSize = bufferSize
        self.localPort = None

    def __clientThread(self):
        try:
            inputs = [ self.sock ]
            outputs = [ ]
            timeout = 1
            while self.connected:
                readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
                if not ((readable or writable or exceptional)):
                    if (not self.connected):
                        break
                    continue

                if (not self.connected):
                    break

                for sock in readable:
                    data = sock.recv(self.bufferSize)
                    if (data and self.callback):
                        self.callback(self.sock.getsockname(), data)
        except Exception as e:
            print (self.localPort, " - Client callback has thrown an exception!  ", e)
            pass
        finally:
            if (self.callback):
                self.callback(self.sock.getsockname(), None)
            print(self.localPort, "Exiting Client Thread")

    def Connect(self):
        try:
            self.mutex.acquire()
            if (self.connected):
                return False
            self.connected = True
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (self.ip, self.port)
            print ('Client: connecting to %s port %s' % server_address)
            self.sock.connect(server_address)
            self.sock.setblocking(0)
            self.localPort = self.sock.getsockname()[1]
            t = threading.Thread( target=self.__clientThread)
            self.clientThread = t
            self.clientThread.start()
            return True
        except Exception as e:
            self.mutex.release()
            self.Disconnect()
            print (e)
            return False
        finally:
            if (self.mutex.locked()):
                self.mutex.release()

    def Disconnect(self):
        try:
            self.mutex.acquire()
            if (not self.connected):
                return False

            self.connected = False
            if (self.clientThread):
                try:
                    self.clientThread.join()
                except Exception as e:
                    pass
            if (self.sock):
                self.sock.close()
            return True
        finally:
            self.mutex.release()

    def IsConnected(self):
        try:
            self.mutex.acquire()
            return self.connected
        finally:
            self.mutex.release()

    def SendData(self, data):
        try:
            self.mutex.acquire()
            if (not self.connected):
                return False
            if (self.sock):
                if (not self.silence):
                    print (self.sock.getsockname(), 'Client: sending "%s"' % data)
                self.sock.sendall(data)
                return True
        except Exception as e:
            print(e)
            return False
        finally:
            self.mutex.release()
