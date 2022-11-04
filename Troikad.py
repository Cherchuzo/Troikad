import os
import socket
import sys
import time
import urllib.request
import subprocess
import platform
import json
from threading import Thread
#import netifaces as ni


__author__ = "Cherchuzo"
__version__ = "1.0"
__status__ = "Improving"


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # doesn't need to be reachable
    s.connect(('10.255.255.255', 1))
    IP = s.getsockname()[0]
    
    try:
        external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    except:
        external_ip = 'Unavailable' # if the website is not responding or there isn't an internet connection
    finally:
        s.close()
    return IP,external_ip # returning the local and public IP address


def receive():
    
    reverseConnection = input("If you don't have an available TCP port open you can try to receive backwards, which can help in some cases\nDo you want to use this mode?[yes][no] ")   # is helpful if your friend or colleague has a TCP port open, otherwise it cannot work
    if reverseConnection.lower() == "yes":
        reverseReceive()
    elif reverseConnection.lower() == "no":
        print("Okay let's continue\n")
    else:
        print("Whatever you wrote I take it as a No\n")

    try:
        ricv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # I create a TCP socket to receive connections

        # I connect the socket to the port
        port = int(input("Enter the port number where u want the app to bind: "))

        ricv_address = ('0.0.0.0', port)  #listening on the port that the user chose
        ricv.bind(ricv_address)
        print("Starting on:{}  Port:{}".format(*ricv_address))
    except:     # if the port is already in use or an unknown error occurs
        print("Socket not started / initialized!")
        time.sleep(2)
        print("Error found, application shutting down...")
        time.sleep(1)
        sys.exit()

    
    ricv.listen(1)  # waiting for a maximum of one connection at once
    while True:
        print("\nWaiting for a connection\n")
        
        ricv.setblocking(True)
        ricv.settimeout(60) # setting a timeout for security purpose
        try:
            connection, client_address = ricv.accept()  # accepting the connection
        except: # in case you forget the receive mode in operation
            print("For security reasons I have disabled receive Mode(Timeout expired)\nTo receive again write 'receive'\n\n")
            ricv.close()
            main()  #return to main
        ricv.settimeout(None)
            
        #ip = str(client_address[0])
        print("Connection from: {} port:{}".format(*client_address))
        
        fileStats = connection.recv(1024)    # receiving file name or a signal of error at Sender side
        fileStats = json.loads(fileStats.decode('utf-8'))    # decoding JSON received
        if fileStats["name"] == "errorFile":    # if an error occurred at Sender side
            print("There was an error on the sender side, restart receiving\n")
            main()

        print("Receiving:"+fileStats["name"])
        time.sleep(2)

        flag = True
        f = open("./downloads/{}".format(fileStats["name"]), 'wb')  # create and write in the new file
        realSize = fileStats["size"]    # the size of the file that we're going to receive
        data = connection.recv(1024)
        currentSize = len(data)
        while data:     # this loop continues until data arrives
            try:
                f.write(data)
                data = connection.recv(1024)
                currentSize += len(data)
            except:     # if the sender stop sending or an unknown error occurs
                print("\n\nError found while receiving the file")
                f.close()
                os.remove('downloads/'+fileStats["name"])   # removes the uncompleted file
                flag = False
                time.sleep(2)

            print("\rProgress: [{0:50s}] {1:.2f}%".format('#' * int((currentSize/realSize) * 50), (currentSize/realSize)*100), end="", flush=True)

        if flag:        
            f.close()
            
        connection.close()

        if os.path.isfile('downloads/'+fileStats["name"]):  # check if the file is healthy
            print("File received correctly!\nReturning to main\n")
            time.sleep(2)
        else:
            print("Unknown error encountered while writing to disk\nReturning to main\n")

        time.sleep(1)
        break

    main()
        
        
def send():   	
    print(os.listdir("downloads/"))     # print all the files inside download folder
    filepath = "downloads/"
    filename = input("\nEnter the name of the file to be sent: ")

    reverseConnection = input("If the receiver does not have any TCP port open you can try reverse sending, which can help in case of network problems\nDo you want to use this feature?[yes][no] ")   # to use if the receiver is also using it
    if reverseConnection.lower() == "yes":
        reverseConnect(filepath, filename)
    elif reverseConnection.lower() == "no":
        print("Okay let's continue\n")
    else:
        print("Whatever you wrote I take it as a No\n")
	
    ipSend = input("Enter the ip address to connect to: ")
    portSend = int(input("Enter the port: "))
    server_address = (ipSend, portSend)
    print('Connecting to {} port {}'.format(*server_address))
	

    flag = 0
    sendS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # creating a TCP socket
	
    sendS.setblocking(True)
    sendS.settimeout(5)     # timeout for connection
    try:
    	sendS.connect(server_address)
    except:
    	print("Host unreachable or busy\n")
    	main()
    sendS.settimeout(None)

    print("Connection to {}:{} successful".format(*server_address))
    if os.path.exists(filepath) and os.path.isfile(filepath+filename):  # control if the file is existing
        sendS.sendall((json.dumps({"name":filename, "size":os.stat(filepath+filename).st_size}, ensure_ascii=False)).encode("utf-8"))   # send the file name as a JSON
        time.sleep(2)
        
        f = open(filepath+filename, 'rb')   # open file in read mode
        realSize = os.stat(filepath+filename).st_size   # retrieves the size of the file
        data = f.read(1024)
        currentSize = len(data)
        while data:
            sendS.send(data)    # starts sending
            print("\rProgress: [{0:50s}] {1:.2f}%".format('#' * int((currentSize/realSize) * 50), (currentSize/realSize)*100), end="", flush=True)
            data = f.read(1024)
            currentSize += len(data)
        sendS.shutdown(socket.SHUT_WR)  # closing the connection
        print("\nFile sent!\n")
        f.close()
    else:
        print("\nYou had inserted an inexistent file!\n")
        message = "errorFile"
        connection.sendall((json.dumps({"name":message, "size":[os.stat(filepath+filename).st_size]}, ensure_ascii=False)).encode("utf-8"))     # sending the error

    sendS.close()

# function used when the receiver has no open ports
def reverseConnect(filepath, filename):

    try:
        sendS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        port = int(input("Inserisci un numero di porta su cui l'applicazione si metterà in ascolto: "))
    
        # binding the port
        send_address = ('0.0.0.0', port)
        sendS.bind(send_address)
        print('Starting on:{}  Port:{}'.format(*send_address))
    except:     # if the port is already in use or an unknown error occurs
        print("Socket not started / initialized!")
        time.sleep(2)
        print("Error found, application shutting down...")
        time.sleep(1)
        sys.exit()
    
    sendS.listen(1)     # listening for one connection
    
    print("\nWaiting for a connection\n")

    sendS.setblocking(True)     # blocking the socket
    sendS.settimeout(60)        # setting timeout
    try:
        connection, client_address = sendS.accept()
    except:     # if the timeout occurs or there is an error
        print("For security reasons I have disabled sender Mode(Timeout expired)\nTo send again write 'send'\n\n")
        sendS.close()
        main()  # sending the user to main function
    sendS.settimeout(None)
    
    print("Connection from {} port:{}".format(*client_address))
        
    if os.path.exists(filepath) and os.path.isfile(filepath+filename):  # checking if the selected really exist
        connection.sendall((json.dumps({"name":filename, "size":os.stat(filepath+filename).st_size}, ensure_ascii=False)).encode("utf-8"))  # JSON with all the info needed to the receiver
        time.sleep(2)   # sleep used to sync and send correctly the filename
        
        f = open(filepath+filename, 'rb')   # starts reading the file
        realSize = os.stat(filepath+filename).st_size   # reading the size of the file
        data = f.read(1024)
        currentSize = len(data)
        while data:
            connection.send(data)   # sending file in bytes
            print("\rProgress: [{0:50s}] {1:.2f}%".format('#' * int((currentSize/realSize) * 50), (currentSize/realSize)*100), end="", flush=True)
            data = f.read(1024)
            currentSize += len(data)
        connection.shutdown(socket.SHUT_WR)     # shutting down correctly the connection
        print("\nFile sent!\n")
        f.close()   # closing the file
    else:
        print("\nYou have inserted a wrong filename!\n")
        message = "errorFile"
        connection.sendall((json.dumps({"name":message, "size":os.stat(filepath+filename).st_size}, ensure_ascii=False)).encode("utf-8"))   # sending error message
        
    sendS.close()
    main()

# function used by the receiver to retrieve the file with a reverse connection
def reverseReceive():

    ipSend = input("\nEnter the ip address to connect to: ")
    portSend = int(input("Enter the port: "))
    server_address = (ipSend, portSend)     # creating a tuple with the ip and port
    print('Connecting to {} port {}'.format(*server_address))

	
    flag = 0
    ricv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # creating TCP socket
	
    ricv.setblocking(True)
    ricv.settimeout(5)  # setting timeout
    try:
    	ricv.connect(server_address)
    except:
    	print("Host unreachable or busy\n")
    	main()
    ricv.settimeout(None)   # resetting the timeout

    print("Connection to {}:{} successful".format(*server_address))

    fileStats = ricv.recv(1024)
    fileStats = json.loads(fileStats.decode('utf-8'))   # receiving the filename as a JSON
    if fileStats["name"] == "errorFile":
        print("There was an error on the sender side, restart receiving\n")
        main()
    
    print('Receiving:'+fileStats["name"])
    time.sleep(2)   # just a sleep

    flag = True
    f = open("./downloads/{}".format(fileStats["name"]), 'wb')  # opening to write on storage
    realSize = fileStats["size"]    # size of the file
    data = ricv.recv(1024)  # starts receiving file
    currentSize = len(data)
    while data:
        try:
            f.write(data)
            data = ricv.recv(1024)
            currentSize += len(data)
        except:     # if an unknown error occurs
            print("\n\nError found while receiving the file")
            f.close()
            os.remove('downloads/'+fileStats["name"])   # removing the uncompleted file
            flag = False
            time.sleep(2)

        print("\rProgress: [{0:50s}] {1:.2f}%".format('#' * int((currentSize/realSize) * 50), (currentSize/realSize)*100), end="", flush=True)

    if flag:        
        f.close()
            
    ricv.close()

    if os.path.isfile('downloads/'+fileStats["name"]):
        print("\nFile ricevuto correttamente!\nRitorno al Main\n")
        time.sleep(2)
    else:   # if the file is not found
        print("\nErrore sconosciuto rilevato durante scrittura su disco\nRitorno al Main\n")

    time.sleep(1)

    main()


def main():
    localIP,publicIP = get_ip()
    print("Public IP address:",publicIP)
    print("Local IP address:",localIP)

    scelta = "?"
    
    if not os.path.exists("downloads"):
        os.mkdir("downloads")
    
    while scelta != exit:
        try:
            scelta = input(("\n\nInsert connection mode(exit for exiting):\n-receive\n-send\n"))
        except KeyboardInterrupt:
            print("Shutting down, typed CTRL-C\n")
            time.sleep(2)
            sys.exit()

        if scelta.lower() == 'receive':
            receive()
        elif scelta.lower() == 'send':
            send()
        elif scelta.lower() == 'exit':
            print("Shutting down...")
            time.sleep(2)
            sys.exit()
        else:
            print("You inserted a wrong value!\nPlease retry again\n")       

print("""\
    *************************************************
    *                   Welcome!                    *
    *     For exiting this program type 'exit'      *
    *    This app allows you to send/recv files     *
    *     For more informations check README.md     *
    *************************************************
    """)
    
    
if __name__ == '__main__':
    main()
