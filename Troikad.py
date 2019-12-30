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

        if os.path.isfile('downloads/'+filename):   # check if the file has been downloaded well
            print("File received correctly!\nReturn to main\n")
            time.sleep(2)
        else:   # if the file is not found
            print("Unknown error encountered while writing to disk\nReturn to main\n")

        time.sleep(1)
        break

    main()  # calling the function main
        
        
def send():   	
    print(os.listdir('downloads/'))
    filepath = 'downloads/'
    filename = input("\nInserisci il nome del file da inviare: ")

    reverseConnection = input("Se il destinatario non ha la porta TCP 2442 aperta puoi provare l'invio inverso, che può aiutare in caso di problemi di rete\nVuoi usare questa funzione?[yes][no] ")
    if reverseConnection.lower() == "yes":
        reverseConnect(filepath, filename)
    elif reverseConnection.lower() == "no":
        print("ok, ho capito\n")
    else:
        print("Qualsiasi cosa hai scritto lo prendo come un no\n")
	
    ipSend = input("Inserisci l'indirizzo ip a cui connettersi: ")
    server_address = (ipSend, 2442)
    print('connessione a {} porta {}'.format(*server_address))

    #print(filepath+filename)
	
    flag = 0
    #Crea un socket TCP/IP per peer
    sendS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
    sendS.setblocking(True)
    sendS.settimeout(5)
    try:
    	sendS.connect(server_address)
    except:
    	print("Host non raggiungibile oppure momentaneamente occupato\n")
    	main()
    sendS.settimeout(None)

    print("Connessione a {}:{} riuscita".format(*server_address))
    if os.path.exists(filepath) and os.path.isfile(filepath+filename):
        sendS.sendall(filename.encode('utf-8'))
        time.sleep(2)
        
        f = open(filepath+filename, 'rb')
        data = f.read(1024)
        while data:
            sendS.send(data)
            data = f.read(1024)
        sendS.shutdown(socket.SHUT_WR)
        print("File inviato!\n")
        f.close()
    else:
        print("Hai inserito un file non esistente!\n")
        message = "errorFile"
        connection.sendall(message.encode('utf-8'))

    sendS.close()


def reverseConnect(filepath, filename):

    try:
        sendS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        #collego il socket alla porta
        send_address = ('0.0.0.0', 2442)
        sendS.bind(send_address)
        print('In avvio su:{}  Porta:{}'.format(*send_address))
    except:
        print("Socket non avviato/inizializzato!")
        time.sleep(2)
        print("Errore rilevato, programma in arresto...")
        time.sleep(1)
        sys.exit()
    
    sendS.listen(1)
    
    print('\nIn attesa di una connessione\n')

    sendS.setblocking(True)
    sendS.settimeout(60)
    try:
        connection, client_address = sendS.accept()
    except:
        print("Per sicurezza ho disattivato la modalita ricezione(Timeout scaduto)\nPer ricevere nuovamente inserisca 'ricevere'\n\n")
        sendS.close()
        main()
    sendS.settimeout(None)
    
            
    #ip = str(client_address[0])
    print('connessione da {} porta:{}'.format(*client_address))
        
    if os.path.exists(filepath) and os.path.isfile(filepath+filename):
        connection.sendall(filename.encode('utf-8'))
        time.sleep(2)
        
        f = open(filepath+filename, 'rb')
        data = f.read(1024)
        while data:
            connection.send(data)
            data = f.read(1024)
        connection.shutdown(socket.SHUT_WR)
        print("File inviato!\n")
        f.close()
    else:
        print("Hai inserito un file non esistente!\n")
        message = "errorFile"
        connection.sendall(message.encode('utf-8'))
        
    sendS.close()
    main()

def reverseReceive():

    ipSend = input("\nInserisci l'indirizzo ip a cui connettersi: ")
    server_address = (ipSend, 2442)
    print('connessione a {} porta {}'.format(*server_address))

    #print(filepath+filename)
	
    flag = 0
    #Crea un socket TCP/IP per peer
    ricv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
    ricv.setblocking(True)
    ricv.settimeout(5)
    try:
    	ricv.connect(server_address)
    except:
    	print("Host non raggiungibile oppure momentaneamente occupato\n")
    	main()
    ricv.settimeout(None)

    print("Connessione a {}:{} riuscita".format(*server_address))

    filename = ricv.recv(1024)
    filename = filename.decode('utf-8')
    if filename == "errorFile":
        print("C'è stato un errore lato mittente, riavvia la ricezione\n")
        main()
    
    print('Ricevendo:'+filename)
    time.sleep(2)

    flag = True
    f = open("./downloads/{}".format(filename), 'wb')
    data = ricv.recv(1024)
    while data:
        try:
            f.write(data)
            data = ricv.recv(1024)
        except:
            print("\n\nErrore durante la ricezione del file")
            f.close()
            os.remove('downloads/'+filename)
            flag = False
            time.sleep(2)

    if flag:        
        f.close()
            
    ricv.close()

    if os.path.isfile('downloads/'+filename):
        print("File ricevuto correttamente!\nRitorno al Main\n")
        time.sleep(2)
    else:
        print("Errore sconosciuto rilevato durante scrittura su disco\nRitorno al Main\n")

    time.sleep(1)

    main()
        

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
    *    For more informations check README.txt     *
    *************************************************
    """)
    
    
if __name__ == '__main__':
    main()
