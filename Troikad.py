import os
import socket
import sys
import time
import urllib.request
import subprocess
import platform
from threading import Thread


__author__ = "Cherchuzo"
__version__ = "1.0"
__status__ = "Improving"


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # doesn't need to be reachable
    s.connect(('10.255.255.255', 1))
    IP = s.getsockname()[0]
    
    try:
        external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')  # requesting public IP address
    except:
        external_ip = 'Unavailable' # if the website is not responding or there isn't an internet connection
    finally:
        s.close()   # shutting down the socket
    return IP,external_ip   # returning the local and public IP address


def receive():
    
    reverseConnection = input("If you don't have TCP port 2442 open you can try to receive backwards, which can help in some cases\nDo you want to use this mode?[yes][no] ")   # is helpful if your friend or colleague has TCP port 2442 open, otherwise it cannot work
    if reverseConnection.lower() == "yes":
        reverseReceive()
    elif reverseConnection.lower() == "no":
        print("okay let's continue\n")
    else:
        print("whatever you wrote I take it as a No\n")

    try:
        ricv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # I create a TCP socket to receive connections
    
        # I connect the socket to the port
        ricv_address = ('0.0.0.0', 2442)    # default port is 2442, you can change it if u want, but you need to change the port even in send function
        ricv.bind(ricv_address)
        print('Starting on:{}  Port:{}'.format(*ricv_address))
    except:     # if the port is already in use or an unknown error occurs
        print("Socket not started / initialized!")
        time.sleep(2)
        print("Error found, application shutting down...")
        time.sleep(1)
        sys.exit()

    
    ricv.listen(1)  # waiting for a maximum of one connection at once
    while True:
        print('\nWaiting for a connection\n')
        
        ricv.setblocking(True)
        ricv.settimeout(60) # setting a timeout
        try:
            connection, client_address = ricv.accept()  # accepting the connection
        except:     # in case you forget the receive mode in operation
            print("For security reasons I have disabled receive Mode(Timeout expired)\nTo receive again write 'receive'\n\n")
            ricv.close()
            main()  #return to main
        ricv.settimeout(None)
            
        print('Connection from: {} port:{}'.format(*client_address))
        
        filename = connection.recv(1024)    # receiving file name or a signal of error at Sender side
        filename = filename.decode('utf-8')
        if filename == "errorFile":     # if an error occurred at Sender side
            print("There was an error on the sender side, restart receiving\n")
            main()

        print('Receiving:'+filename)
        time.sleep(2)

        flag = True
        f = open("./downloads/{}".format(filename), 'wb')   # creating and writing in the new file
        data = connection.recv(1024)    # starting receiving
        while data:     # this loop continues until data arrives
            try:
                f.write(data)
                data = connection.recv(1024)
            except:     # if the sender stop sending or an unknown error occurs
                print("\n\nError found while receiving the file")
                f.close()
                os.remove('downloads/'+filename)
                flag = False
                time.sleep(2)

        if flag:        
            f.close()
            
        connection.close()
        ricv.close()

        if os.path.isfile('downloads/'+filename):   # check if the file has been downloaded well
            print("File received correctly!\nReturn to main\n")
            time.sleep(2)
        else:   # if the file is not found
            print("Unknown error encountered while writing to disk\nReturn to main\n")

        time.sleep(1)
        break

    main()  # calling the function main
        
        
def send():   	
    print(os.listdir('downloads/'))     # print all the files inside download folder
    filepath = 'downloads/'
    filename = input("\nEnter the name of the file to be sent: ")

    reverseConnection = input("If the receiver does not have the TCP 2442 port open you can try reverse sending, which can help in case of network problems\nDo you want to use this feature?[yes][no] ")   # to use if the receiver is also using it
    if reverseConnection.lower() == "yes":
        reverseSend(filepath, filename)
    elif reverseConnection.lower() == "no":
        print("okay let's continue\n")
    else:
        print("whatever you wrote I take it as a No\n")
	
    ipSend = input("Enter the ip address to connect to: ")
    server_address = (ipSend, 2442)     # default port is 2442, you can change it easily here
    print('Connecting to: {} port:{}'.format(*server_address))

    #print(filepath+filename)   # debug
	
    flag = 0
    
    sendS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # I create a TCP socket
	
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
        sendS.sendall(filename.encode('utf-8'))     # send the file name
        time.sleep(2)
        
        f = open(filepath+filename, 'rb')   # open file with read mode
        data = f.read(1024)     #start sending
        while data:
            sendS.send(data)
            data = f.read(1024)
        sendS.shutdown(socket.SHUT_WR)  # closing the connection
        print("File sent!\n")
        f.close()   #close the file
    else:
        print("You ad inserted an inexistent file!\n")
        message = "errorFile"
        connection.sendall(message.encode('utf-8'))     # sending the error

    sendS.close()


def reverseSend(filepath, filename):

    try:
        sendS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        #collego il socket alla porta
        send_address = ('0.0.0.0', 2442)
        sendS.bind(send_address)
        print("Starting on:{}  Port:{}".format(*send_address))
    except:     # if the port is already in use or an unknown error occurs
        print("Socket not started / initialized!")
        time.sleep(2)
        print("Error found, application shutting down...")
        time.sleep(1)
        sys.exit()
    
    sendS.listen(1)     # listening for one connection
    
    print("\nWaiting for a connection\n")

    sendS.setblocking(True)     # blocking the socket
    sendS.settimeout(60)    # setting timeout
    try:
        connection, client_address = sendS.accept()
    except:     # if the timeout occurs or there is an error
        print("For security reasons I have disabled sender Mode(Timeout expired)\nTo send again write 'send'\n\n")
        sendS.close()   # shutting down the socket
        main()  # sending the user to main function
    sendS.settimeout(None)
    
            
    #ip = str(client_address[0])
    print("Connection from: {} port:{}".format(*client_address))
        
    if os.path.exists(filepath) and os.path.isfile(filepath+filename):  # checking if the selected really exist
        connection.sendall(filename.encode('utf-8'))    # sending the filename
        time.sleep(2)   # sleep for send correctly the filename
        
        f = open(filepath+filename, 'rb')   # starts reading the file
        data = f.read(1024)     # sending file in bytes
        while data:
            connection.send(data)
            data = f.read(1024)
        connection.shutdown(socket.SHUT_WR)     # shutting down correctly the connection
        print("File sent!\n")
        f.close()   # closing the file
    else:
        print("You have inserted a wrong filename!\n")
        message = "errorFile"
        connection.sendall(message.encode('utf-8'))     # sending error message
        
    sendS.close()   # closing the socket
    main()

def reverseReceive():

    ipSend = input("\nEnter the ip address to connect to: ")
    server_address = (ipSend, 2442)     # creating a tuple with the ip and port
    print("Connection to: {} port:{}".format(*server_address))

    #print(filepath+filename)   # debug purpose
	
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

    filename = ricv.recv(1024)  # receiving the filename
    filename = filename.decode('utf-8')
    if filename == "errorFile":     # if the filename contain "errorfile" the sender was wrong to write the correct filename
        print("There was an error on the sender side, restart receiving\n")
        main()
    
    print('Receiving:'+filename)
    time.sleep(2)   # just a sleep

    flag = True
    f = open("./downloads/{}".format(filename), 'wb')   # opening to write on HDD
    data = ricv.recv(1024)  # start receiving file
    while data:
        try:
            f.write(data)
            data = ricv.recv(1024)
        except:     # if an unknown error occurs
            print("\n\nError found while receiving the file")
            f.close()   # closing the file
            os.remove('downloads/'+filename)    # removing the uncompleted file
            flag = False
            time.sleep(2)

    if flag:        
        f.close()
            
    ricv.close()    # closing the connection

    if os.path.isfile('downloads/'+filename):
        print("File received correctly!\nReturn to main\n")
        time.sleep(2)
    else:   # if the file is not found
        print("Unknown error encountered while writing to disk\nReturn to main\n")

    time.sleep(1)

    main()  #recalling the main()
        

def main():
    localIP,publicIP = get_ip()
    print("Public IP address:",publicIP)
    print("Local IP address:",localIP)

    choice = "?"
    
    if not os.path.exists("downloads"):
        os.mkdir("downloads")
    
    while choice != exit:
        try:
            choice = input("\n\nInsert connection mode(exit for exiting):\n-receive\n-send\n")
        except KeyboardInterrupt:
            print("Shutting down, typed CTRL-C\n")
            time.sleep(2)
            sys.exit()

        if choice.lower() == 'receive':
            receive()
        elif choice.lower() == 'send':
            send()
        elif choice.lower() == 'exit':
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
