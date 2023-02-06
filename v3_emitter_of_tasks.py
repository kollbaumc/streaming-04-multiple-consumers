"""
    Chris Kollbaum 2/2/2023

    This code takes the lines of task.csv and sends them to a queue
    one at a time to be retrieved by multiple consumers one at a time.
    One consumer may get one message and the other another and so on and 
    so on.  

"""

import pika
import sys
import webbrowser
import csv
import socket
import time


def offer_rabbitmq_admin_site():
    """Offer to open the RabbitMQ Admin website"""
    ans = input("Would you like to monitor RabbitMQ queues? y or n ")
    print()
    if ans.lower() == "y":
        webbrowser.open_new("http://localhost:15672/#/queues")
        print()

def send_message(host: str, queue_name: str, message: str):
    """
    Creates and sends a message to the queue each execution.
    This process runs and finishes.

    Parameters:
        host (str): the host name or IP address of the RabbitMQ server
        queue_name (str): the name of the queue
        message (str): the message to be sent to the queue
    """
    host = "localhost"
    port = 9999
    address_tuple = (host, port)

    # use the socket constructor to create a socket object we'll call sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

    # read from a file to get some fake data
    input_file = open("tasks.csv", "r")

    # create a csv reader for our comma delimited data
    reader = csv.reader(input_file, delimiter=",")


    for row in reader:
        # read a row from the file
        tasks = row

        # use an fstring to create a message from our data
        # notice the f before the opening quote for our string?
        fstring_message = f"[{tasks}]"
    
        # prepare a binary (1s and 0s) message to stream
        MESSAGE = fstring_message.encode()

        # use the socket sendto() method to send the message
        sock.sendto(MESSAGE, address_tuple)

        # sleep for a few seconds
        time.sleep(3)

        try:
            # create a blocking connection to the RabbitMQ server
            conn = pika.BlockingConnection(pika.ConnectionParameters(host))
            # use the connection to create a communication channel
            ch = conn.channel()
            # use the channel to declare a durable queue
            # a durable queue will survive a RabbitMQ server restart
            # and help ensure messages are processed in order
            # messages will not be deleted until the consumer acknowledges
            ch.queue_declare(queue=queue_name, durable=True)
            # use the channel to publish a message to the queue
            # every message passes through an exchange
            ch.basic_publish(exchange="", routing_key=queue_name, body=MESSAGE)
            # print a message to the console for the user
            print(f" [x] Sent {MESSAGE}")

        except pika.exceptions.AMQPConnectionError as e:
            print(f"Error: Connection to RabbitMQ server failed: {e}")
            sys.exit(1)

        finally:
            # close the connection to the server
            conn.close()

# Standard Python idiom to indicate main program entry point
# This allows us to import this module and use its functions
# without executing the code below.
# If this is the program being run, then execute the code below
if __name__ == "__main__":  
    # ask the user if they'd like to open the RabbitMQ Admin site
    offer_rabbitmq_admin_site()
    # get the message from the command line
    # if no arguments are provided, use the default message
    # use the join method to convert the list of arguments into a string
    # join by the space character inside the quotes
    message = " ".join(sys.argv[1:]) or '{MESSAGE}'
    # send the message to the queue
    send_message("localhost","task_queue_v3",message)