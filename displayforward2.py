import logging.handlers
import socket
import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import logging
from logging.handlers import TimedRotatingFileHandler


# Configuration
listen_ip = '0.0.0.0'  # Listen on all available interfaces
listen_port = 514
destinations = ['192.168.1.78', '192.168.1.66']
dest_port = 514

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the listening IP and port
sock.bind((listen_ip, listen_port))


# Define a list of alternating background colors (yellow and blue)
background_colors = ["yellow", "light blue"]
color_index = 0  # Index to keep track of the current background color

# Create a logger with a rotating flile handler
logger = logging.getLogger()
handler = TimedRotatingFileHandler(filename='D:/syslog.log', when="midnight", interval=1, backupCount=7 )
formatter = logging.Formatter("[%(asctime)s]%(message)s", datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Function to forward syslog message and update GUI
def forward_and_log(message):
    global background_colors
    
    for dest_ip in destinations:
        sock.sendto(message, (dest_ip, dest_port))
    # Get current timestamp
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    # Insert a newline character before adding the timestamp and message to the text area
    text_area.insert(tk.END, f"\n[{timestamp}] {message.decode('utf-8').strip()}")  # Timestamp and message

    # Get the index of the last inserted character
    line_end = text_area.index(tk.END)
    # Get the index of the start of the last inserted line
    line_start = text_area.index(f"{line_end}-1l linestart")

    # Determine the background color for the current line
    line_number = int(line_start.split('.')[0])
    color_index = line_number % len(background_colors)
    background_color = background_colors[color_index]

    # Apply the background color to the current line
    text_area.tag_add(f"line{line_number}", line_start, line_end)
    text_area.tag_config(f"line{line_number}", background=background_color)


    text_area.see(tk.END,)  # Ensure new text is visible without scrolling


    # Log the message to file
    with open('D:/syslog.log', 'a') as logfile:
        logfile.write(f"[{timestamp}] {message.decode('utf-8').strip()}\n")

   

# Function to receive syslog messages
def receive_syslog():
    while True:
        # Receive a syslog message
        message, address = sock.recvfrom(8192)
        # Call function to forward and log the message
        forward_and_log(message)


# Create Tkinter window
window = tk.Tk()
window.title("Dollysolutions Gate Monitor")

# Create a scrolled text area for displaying messages
text_area = scrolledtext.ScrolledText(window, font=("Arial Black", 20))
text_area.pack(expand=True, fill='both')




# Start receiving syslog messages in a separate thread
receive_thread = threading.Thread(target=receive_syslog)
receive_thread.daemon = True
receive_thread.start()



# Start Tkinter event loop
window.mainloop()
