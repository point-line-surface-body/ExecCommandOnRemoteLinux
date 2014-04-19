"""Friendly Python SFTP interface.

pysftp is forked with permission of ssh.py, originally authored by
Zeth @ http://commandline.org.uk/python/sftp-python-really-simple-ssh/

requires:
paramiko - http://www.lag.net/paramiko/
  requires:
  pycrypto - http://www.dlitz.net/software/pycrypto/

License: BSD  (see http://code.google.com/p/pysftp/source/browse/trunk/LICENSE.txt)
"""

import os, sys
import tempfile
import paramiko

__version__ = "$Rev: 9 $"
class Connection(object):
    """Connects and logs into the specified hostname. 
    Arguments that are not given are guessed from the environment.
        host             - The Hostname of the remote machine.
        username         - Your username at the remote machine.(None)
        private_key 	 - Your private key file.(None)
        password         - Your password at the remote machine.(None)
        port 	         - The SSH port of the remote machine.(22)
        private_key_pass - password to use if your private_key is encrypted(None)
        log              - log connection/handshake details (False)
    returns a connection to the requested machine
    
    srv = pysftp.Connection('example.com')
    """ 

    def __init__(self,
                 host,
                 username = None,
                 private_key = None,
                 password = None,
                 port = 22,
                 private_key_pass = None,
                 log = True,
                 ):
        self._sftp_live = False
        self._sftp = None
        if not username:
            username = os.environ['LOGNAME']

        if log:
            # Log to a temporary file.
            templog = tempfile.mkstemp('.txt', 'ssh-')[1]
            paramiko.util.log_to_file(templog)
            print "templog:%s" % templog

        # Begin the SSH transport.
        self._transport = paramiko.Transport((host, port))
        self._tranport_live = True
        # Authenticate the transport. prefer password if given
        if password:
            # Using Password.
            self._transport.connect(username = username, password = password)
        else:
            # Use Private Key.
            if not private_key:
                # Try to use default key.
                if os.path.exists(os.path.expanduser('~/.ssh/id_rsa')):
                    private_key = '~/.ssh/id_rsa'
                elif os.path.exists(os.path.expanduser('~/.ssh/id_dsa')):
                    private_key = '~/.ssh/id_dsa'
                else:
                    raise TypeError, "You have not specified a password or key."

            private_key_file = os.path.expanduser(private_key)
            try:  #try rsa
                xSx_key = paramiko.RSAKey.from_private_key_file(private_key_file,private_key_pass)
            except paramiko.SSHException:   #if it fails, try dss
                xSx_key = paramiko.DSSKey.from_private_key_file(private_key_file,password=private_key_pass)
            self._transport.connect(username = username, pkey = xSx_key)
    
    def _sftp_connect(self):
        """Establish the SFTP connection."""
        if not self._sftp_live:
            self._sftp = paramiko.SFTPClient.from_transport(self._transport)
            self._sftp_live = True

    def _callback(self,a,b):
        # http://eleveni386.7axu.com/index.php/2012/09/10/python-%E8%BF%9B%E5%BA%A6%E6%9D%A1/
        #sys.stdout.write('Data Transmission %.2f M [%3.2f%%]\r' %(a/1024./1024.,a*100./int(b)))
        #if (int(a/1024./1024.) % 2 == 0 and int(a/1024./1024. *100) % 5 == 0 ):
        if (int(a*100./b) % 10 == 0 and int(a*1000/b) % 10 < 2):
            sys.stdout.write('|%-40s| %.2f M [%3.2f%%]\r' %('>'*int(a*40./b), a/1024./1024.,a*100./int(b)))
            sys.stdout.flush()

    def get(self, remotepath, localpath = None):
        """Copies a file between the remote host and the local host."""
        if not localpath:
            localpath = os.path.split(remotepath)[1]
        self._sftp_connect()
        self._sftp.get(remotepath, localpath, self._callback)

    def put(self, localpath, remotepath = None):
        """Copies a file between the local host and the remote host."""
        if not remotepath:
            remotepath = os.path.split(localpath)[1]
        self._sftp_connect()
        self._sftp.put(localpath, remotepath, self._callback)

    def execute(self, command):
        """Execute the given commands on a remote machine."""
        channel = self._transport.open_session()
        channel.exec_command(command)
        output = channel.makefile('rb', -1).readlines()
        if output:
            #return output
            for i in output:
                print i
        else:
            return channel.makefile_stderr('rb', -1).readlines()

    def chdir(self, path):
        """change the current working directory on the remote"""
        self._sftp_connect()
        self._sftp.chdir(path)
        
    def getcwd(self):
        """return the current working directory on the remote"""
        self._sftp_connect()
        return self._sftp.getcwd()
        
    def listdir(self, path='.'):
        """return a list of files for the given path"""
        self._sftp_connect()
        return self._sftp.listdir(path)
        
    def close(self):
        """Closes the connection and cleans up."""
        # Close SFTP Connection.
        if self._sftp_live:
            self._sftp.close()
            self._sftp_live = False
        # Close the SSH Transport.
        if self._tranport_live:
            self._transport.close()
            self._tranport_live = False

    def __del__(self):
        """Attempt to clean up if not explicitly closed."""
        self.close()

def main():
    """Little test when called directly."""
    # Set these to your own details.
    myssh = Connection('example.com')
    myssh.put('ssh.py')
    myssh.close()

# start the ball rolling.
if __name__ == "__main__":
    #s = pysftp.Connection(host='135.251.157.188', port=22, username='XXX', password='XXX')
    s = Connection(host='172.24.186.70', port=22, username='XXX', password='XXX', log = True)
    print "="*160 
    print "getcwd :",s.getcwd()
    print "="*160 
    print "listdir:",s.listdir()
    print "="*160 

    #local files in the current directory
    filelist = os.listdir('.')
    print "local  :",filelist[-2]
    for f in filelist:
        print f
    #targetdir = os.path.join(s.getcwd(), filelist[-2])
    #s.chdir(targetdir)
    #s.execute('dir')
    print "="*160 
    print "Uploading download_zipfile.py"
    s.put('download_zipfile.py')

    print s.listdir()
    print "="*160 
    print s.execute("pwd")
    print s.execute("uname -a")
    print s.execute("./utinfo")
    print s.execute("cat config.xml")
    print s.execute("md5sum dsp.zip")
    print "="*160
    s.chdir(r"/home/senya/LteCloud")
    print s.getcwd()
    print "="*160
    os.chdir(r"d:/")
    s.chdir(r"/home/senya")
    s.get("dsp.zip")
    print "Close!\n"
    s.close()
