#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: YS
# Date:



import os, sys, time
sys.path.append( os.path.dirname( os.path.abspath(__file__) ) )
import paramiko

currentPath = os.getcwd()
#print currentPath
#print os.path.dirname( os.path.abspath(__file__) )


class sshConnect(object):
	def __init__(self, usrName, passWd, host, port=22, logfile = "paramiko.log"):
		self.channel = paramiko.SSHClient()
		self.channel.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.logfile = logfile #self.logfile = os.path.join(os.getcwd(),"paramiko.log")

		try:
			self.channel.connect( host, port, username = usrName, password= passWd, pkey=None, timeout=None, allow_agent=False, look_for_keys=False)
			#self.connect('135.251.224.225',22,username = 'XXX',password='XXX', pkey=None, timeout=None, allow_agent=False, look_for_keys=False)
		except Exception, e:
			#print("Exception: %s: %s\n" %(e.errno, e.strerror))
			print e
			#self.close()
		else:
			self.sftp = self.channel.open_sftp()
			#self.sftp = paramiko.SFTPClient.from_transport(self.channel)
		self.Flag = '=';
		self.numofFlag = 80;

	def exectueCommand(self, cmdList, verbose=False, timeoutsec=180):
		if len(cmdList) == 0:
			return
		startTimeStamp = time.time()
		
		fh = open(self.logfile, 'a+')
		for cmd in cmdList:
			if verbose:
				print self.Flag*self.numofFlag
				print "Exectuing Command: %s\n" % cmd
			fh.write(self.Flag*self.numofFlag + "\n")
			fh.write("\nExectuing Command: %s\n" % cmd)
			
			stdin,stdout,stderr = self.channel.exec_command(cmd, timeout=timeoutsec)
			out = stdout.readlines()
			if verbose:
				for i in out:
					print i.rstrip()
					fh.write(i)
				#print '-'*self.numofFlag
			
		fh.close()
		print "\n",'-'*self.numofFlag
		print "Used Time:", time.time() - startTimeStamp, "s"
		print self.Flag*self.numofFlag

	def upload(self, localFile, remoteFile, verbose=False ):
		startTimeStamp = time.time()
		print "Copying LocalFile=",localFile," To RemoteFile=",remoteFile
		if verbose:
			self.sftp.put(localFile, remoteFile, self._callback)
		else:
			self.sftp.put(localFile, remoteFile)
		print "Used Time:", time.time() - startTimeStamp, "s"

	#sftp.get(remotepath, localpath)
	def download(self, remoteFile, localFile, verbose=False):
		print "Downloading RemoteFile=",remoteFile," To LocalFile=",localFile
		startTimeStamp = time.time()
		if verbose:
			self.sftp.get(remoteFile, localFile, self._callback)
		else:
			self.sftp.get(remoteFile, localFile)
		print "Used Time:", time.time() - startTimeStamp, "s"

	def _callback(self,a,b):
		# http://eleveni386.7axu.com/index.php/2012/09/10/python-%E8%BF%9B%E5%BA%A6%E6%9D%A1/
		#sys.stdout.write('Data Transmission %.2f M [%3.2f%%]\r' %(a/1024./1024.,a*100./int(b)))
		#if (int(a/1024./1024.) % 2 == 0 and int(a/1024./1024. *100) % 5 == 0 ):
		if (int(a*100./b) % 10 == 0 and int(a*1000/b) % 10 < 2):
			sys.stdout.write('|%-40s| %.2f M [%3.2f%%]\r' %('>'*int(a*40./b), a/1024./1024.,a*100./int(b)))
			sys.stdout.flush()

	def close(self):
		#if self.channel.is_active():
		self.sftp.close()
		self.channel.close()

	def __enter__(self):
		return self

	def __exit__(self, type, value, tb):
		self.sftp.close()
		self.channel.close()

if __name__ == '__main__':
	CompileSHACmd = "perl /home/senya/LteCloud/LaunchLteCloudCompiling -csl=XXX  -stream=SHA  -newest  -type='B4860 Macro SDCAM Rev1'  -cw='10.6.3' "
	print CompileSHACmd
	Commands = ['pwd', CompileSHACmd ,'free|grep Mem']
	t = sshConnect('XXX','XXX','172.24.186.182',22)
	t.exectueCommand(Commands, verbose=True, timeoutsec=180)
	t.download("/localdisk/Temp/moc.jpg",os.path.join(currentPath,"moc.jpg"))
	t.close
	print "Over!"