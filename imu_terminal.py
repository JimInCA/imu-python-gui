#!/usr/bin/python3

from tkinter import *
import serial
import time
import threading
import sys
import os
import glob

class Application(Frame):
	"""Build the basic window frame template"""

	def __init__(self, master, port):
		super(Application, self).__init__(master)
		self.pack(expand=Y, fill=BOTH)
		self.master.title('IMU Terminal')
		self._create_widgets()
		self.port = port

	def _create_widgets(self):
		self.button = Button(self, text = 'Start', command = self._Run_Stop)
		self.button.pack(side = TOP)
		self.button_state = 0

		self.text = Text(self, width = 150, height=30, setgrid=True, wrap=WORD,
			    undo=True, pady=2, padx=3)
		self.text.pack(side=LEFT, fill=Y, expand=Y)
		self.scrollbar = Scrollbar(self, command=self.text.yview, orient=VERTICAL)
		self.scrollbar.pack(side = RIGHT, fill = Y)
		self.scrollbar.config(command = self.text.yview)
		self.text.config(yscrollcommand = self.scrollbar.set)
		self.text.focus_set()

	def _Run_Stop(self):
		"""Event handler for the button"""
		if (self.button_state == 0):
			self.port.write(b'R\r')
			self.button.config(text = 'Running', bg = 'green',
					relief = SUNKEN, highlightbackground = 'green')
			self.button_state = 1
			self.display('The IMU is Running!\n')
		else:
			self.port.write(b'S\r')
			self.button.config(text = 'Stopped', bg = 'red',
					relief = RAISED, highlightbackground = 'red')
			self.button_state = 0
			self.display('The IMU is Stopped!\n')

	def display(self, output_msg):
		self.text.insert(END, output_msg)
		self.text.yview(END)


class DisplayMessages(threading.Thread):
	"""Display the messages coming in on the com port in """
	"""  the GUI text window.                            """

	def __init__(self, port, text_display):
		super().__init__()
		self.port = port
		self.text_display = text_display

	def run(self):
		try:
			while True:
				rcv = self.readlineCR() + b'\n'
				self.text_display(rcv)
		except (RuntimeError):
			print("Cought Thread Exception!\n")

	def readlineCR(self):
		rv = b''
		while True:
			ch = self.port.read()
			if ch == b'\n':
				return rv
			rv += ch

def serial_ports():
	"""Lists serial ports"""
	if sys.platform.startswith('win'):
		ports = ['COM' + str(i + 1) for i in range(256)]

	elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
		# this is to exclude your current terminal "/dev/tty"
		ports = glob.glob('/dev/tty[A-Za-z]*')

	elif sys.platform.startswith('darwin'):
		ports = glob.glob('/dev/tty.*')

	else:
		raise EnvironmentError('Unsupported platform')

	result = []
	for port in ports:
		try:
			s = serial.Serial(port)
			s.close()
			result.append(port)
		except (OSError, serial.SerialException):
			pass
	return result


# Start of program

try:
	port_name = sys.argv[1]
except:
	if (os.name == str('nt')):
		port_name = str('COM13')
	else:
		port_name = str('/dev/ttyUSB0')
try:
	baudrate = int(sys.argv[2])
except:
	baudrate = 9600

try:
	port = serial.Serial(port_name, baudrate, timeout=3.0)
	print("Initializing Port {0} with a baud rate of {1}".format(port_name, baudrate))
except (OSError):
	print("Port {0} is invalid.".format(port_name))
	print("Found Ports:")
	for s in serial_ports():
		print("%s" % s)
	print("Program Terminating.")
	sys.exit()

try:
	root = Tk()
	app = Application(root, port)
	monitor = DisplayMessages(port, app.display)
	monitor.start()
	app.mainloop()
except:
	print("Cought Main Exception\n")



