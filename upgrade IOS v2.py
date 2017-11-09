from tkinter import *
from tkinter import ttk
import random
import os
import re
import socket
import sys
import netmiko
import time
import multiprocessing
from getpass import getpass
from netmiko import ConnectHandler, SCPConn



#Debug
import logging
logging.basicConfig(filename='test.log', level=logging.DEBUG)
logger = logging.getLogger("netmiko")
#Debug


def ssh_command(ip,username,password):
	try:
		net_connect = netmiko.ConnectHandler(device_type='cisco_ios', ip=ip, username=username, password=password) 
		return net_connect.send_command_expect('show ver')
	except:
		failtext = ip + " Couldn't be SSHed to "
		to_doc("fails.csv", failtext)
	

def read_in_info(file_name):
	print (file_name)
	tmp = []
	for line in open(file_name, 'r').readlines():
		line = remove_return(line)
		line = line.split(',')
		tmp.append(line)
	return tmp


def remove_return(entry):
	tmp = entry.rstrip('\n')
	return tmp

def get_ip (input):
	return(re.findall(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)', input))

def read_devices (file_name):
	for line in open(file_name, 'r').readlines():
		if get_ip(line):
			for each in get_ip(line): 
				my_devices.append(each)

def to_doc(file_name, varable):
	f=open(file_name, 'a')
	f.write(varable)
	f.write('\n')
	f.close()

def find_ver(sh_ver,upgrade_info):
	for each in upgrade_info:
		if each[1] in sh_ver:
			return each

			
def transfer_file(net_connect,file):
	net_connect.config_mode()
	net_connect.send_command('ip scp server enable')
	scp_conn = SCPConn(net_connect)
	s_file = file
	d_file = file
	scp_conn.scp_transfer_file(s_file, d_file)
	try:
		net_connect.send_command('no ip scp server enable')
		net_connect.exit_config_mode()
	except:
		pass
		
def verify(device_type,command):
	net_connect = netmiko.ConnectHandler(device_type='cisco_ios', ip=ip, username=username, password=password) 
	net_connect.config_mode()
	net_connect.send_command('no ip scp server enable')
	net_connect.exit_config_mode()
	verify = net_connect.send_command_expect (command,delay_factor=30)
	if device_type[4] in verify:
		print (ip+" "+'Successfully copied and verified')
		try:
			net_connect.config_mode()
		except:
			error = ip+" "+"didn't go into config mode"
			to_doc("fails.csv", error)
			pass
		try:
			net_connect.send_command('no boot system',delay_factor=.3)
		except:
			error = ip + " didn't take no boot system command"
			to_doc("fails.csv", error)
			pass
		try:
			command = "boot system "+device_type[2]+device_type[3]
			net_connect.send_command(command,delay_factor=.5)
		except:
			error = ip + " didn't take boot system command"
			to_doc("fails.csv", error)
			pass
		
		try:
			net_connect.exit_config_mode()
		except:
			error = ip + " config mode didn't exit"
			to_doc("fails.csv", error)
		
		try:
			net_connect.send_command ('write memory')
			start_config = net_connect.send_command ('show run | i boot')
		except:
			error = "'write mem' or 'show run | i boot' didn't work on "+ ip
			to_doc("fails.csv", error)
			pass
		
		print (command)
		#print (start_config)
		if command in start_config:
			print (ip +" boot statment is now correct and config is saved")
			done = ip + ", boot statment is now correct and config is saved"
			to_doc("success.csv",done)

		elif command not in start_config:
			print (4)
			bootstatment = net_connect.send_command ('show boot')
	#		print (bootstatment)
	#		print (command)
			temp_command = device_type[2]+device_type[3]
	#		print (temp_command)
			if temp_command in bootstatment:
				print (ip +" boot statment is now correct and config is saved")
				done = ip + ",  boot statment is now correct and config is saved"
				print("done")
				to_doc("success.csv",done)
			else:
				error= "Boot statment not correct on " + ip
				to_doc("fails.csv", error)
		else:			
			error= "something went wrong with " + ip
			to_doc("fails.csv", error)
	else:
		return(verify)

	
	
def update_ios(ip,username,password,device_type):
	
#This part uploads the code from the device the program runs on
	net_connect = netmiko.ConnectHandler(device_type='cisco_ios', ip=ip, username=username, password=password) 
	transfer_file(net_connect,device_type[3])
	
#This part uploads the code from the specified server
	#command = 'cd '+device_type[2]
	#net_connect.send_command_expect(command)
	#command = 'copy scp://'+username+"@"+device_type[5]+'/'+device_type[3]+" "+device_type[2]+'/'+device_type[3]
	#net_connect.send_command_timing(command)
	#print (device_type[3])
	#net_connect.send_command_timing(remove_return(device_type[3]))
    #
	#net_connect.send_command_timing(password, delay_factor=30)
	##time.sleep(200)
	#	#print (1)


			
	
#Uncomment these lines for a slow link where the OS isn't getting copied correctly
	#sleep_time = 600
	#time.sleep(sleep_time)
	#print (str(sleep_time/60)+' min is up, off to verify')
	command = "verify "+ device_type[2]+device_type[3]
	output = verify(device_type,command)
	if output:
		print (output)
		if "No such file or directory" in output:
			#print (output)
			command = "verify /md5 " + device_type[2]+device_type[3]
			output = verify(device_type,command)
		else:
			error= "something went wrong with " + ip
			to_doc("fails.csv", error)	
	
	

def upgradeios(ip,username,password):
	upgrade_info = read_in_info('upgrade info.csv')
	print (ip)
	sh_ver = ssh_command(ip,username,password)
	ip = remove_return(ip)
	print (ip)
	device_type = find_ver(sh_ver,upgrade_info)
	print (device_type)
	update_ios(ip,username,password,device_type)

def start_this_stuff(ip):
	 
	p1 = multiprocessing.Process(target = upgradeios, args = (ip,username,password))
	p1.start()

username = input("Username: ")
password = getpass() 	


my_devices = []			
read_devices('IPs.txt')
print (my_devices)
for ip in my_devices:
	upgradeios(ip,username,password)
		#print (ip)



