# ftp retr stor dirs 
import sys
import ftplib
import os


uname = 'ftp'
passw = ''
ip = '172.93.35.245'
port = 21

remote_dir_info = {}
local_root = r'E:\backupswitch\localroot'

#ftp connect and login
def ftp_init():
	ftp = ftplib.FTP()
	print (ftp.connect(ip, port))
	print (ftp.login(uname, passw))
	return ftp

#def ftp_callback(buf):
#	print (buf)


def ftp_download(ftp, remote_dir, remote_file, local_file):
	print (ftp.cwd(remote_dir))
	f = open(local_file, 'wb')
	ftp.retrbinary('RETR %s'%remote_file, f.write)
	#ftp.retrbinary('RETR %s'%remote_file, ftp_callback)
	f.close()

# download server ---> local
def ftp_download_(ftp, remote_file, local_file):
	fname = local_file + '\\' + remote_file
	lsize = 0
	if os.path.exists(fname):
		lsize = os.lstat (fname).st_size
	f = open(fname, 'wb')
	#print f
	print ('lsize: %s'%lsize)

	ftp.retrbinary('RETR %s'%remote_file, f.write, rest=lsize)
	#ftp.retrbinary('RETR %s'%remote_file, f.write)
	#ftp.retrbinary('RETR %s'%remote_file, ftp_callback)
	f.close()



def ftp_upload(ftp, remote_dir, remote_file, local_file):
	print (ftp.cwd(remote_dir))
	f = open(local_file, 'rb')
	ftp.storbinary('STOR %s'%remote_file, f)
	f.close()

def ftp_upload_(ftp, local_file):
	f = open(local_file, 'rb')
	ftp.storbinary('STOR %s'%local_file, f)
	f.close()


def ftp_quit(ftp):
	ftp.close()


def ftp_get_dir(line):
	#print ('--> %s'%line[-1])
	#print (line.split())
	result = line.split()
	f_type = result[0][0]
	if f_type == '-':
		key = 'files'
	elif f_type == 'd':
		key = 'dirs'
	else:
		return
	remote_dir_info[key].append(result[-1])


def ftp_download_dir (ftp, remote_dir = '.', local_dir = '.'):
	global remote_dir_info
	ftp.cwd(remote_dir)
	remote_dir_info = {'parent': remote_dir, 'dirs': [], 'files': []}
	ftp.dir(ftp_get_dir)
	tmp = remote_dir_info
	print tmp
	path = local_dir + '\\' + remote_dir
	if os.path.exists(path) == False:
    #if not os.path.exists(path):
		os.mkdir(path)
		print ('create %s '%path)
	else:
		print ('%s existed'%path)

	for _dir in tmp['dirs']:
		ftp_download_dir(ftp, _dir, path)
		#ftp_download_dir(ftp, _dir, local_dir)
	ftp.cwd('..')


def ftp_download_file (ftp, remote_dir = '.', local_dir = '.'):
	global remote_dir_info
	ftp.cwd(remote_dir)
	remote_dir_info = {'parent': remote_dir, 'dirs': [], 'files': []}
	ftp.dir(ftp_get_dir)
	tmp = remote_dir_info
	print tmp
	#path = local_dir + '\\' + remote_dir
	#if os.path.exists(path) == False:
	#	os.mkdir(path)
	#	print ('path %s create'%path)
	#else:
	#	print ('path %s existed'%path)

	path = local_dir + '\\' + remote_dir
	for fname in tmp['files']:
		ftp_download_(ftp, fname, path)
		
	ftp.cwd('..')


def ftp_upload_file (ftp, remote_dir = '.', local_dir = '.'):
	global remote_dir_info
	ftp.cwd(remote_dir)
	remote_dir_info = {'parent': remote_dir, 'dirs': [], 'files': []}
	ftp.dir(ftp_get_dir)
	tmp = remote_dir_info
	print tmp
	#path = local_dir + '\\' + remote_dir
	#if os.path.exists(path) == False:
	#	os.mkdir(path)
	#	print ('path %s create'%path)
	#else:
	#	print ('path %s existed'%path)

	path = local_dir + '\\' + remote_dir

	for fname in tmp['files']:
		if os.path.exists(remote_dir + '\\' + fname) == False:
			print ('file %s to upload'%(remote_dir + '\\' + fname))
			#ftp_upload_(ftp, fname, path)
		else:
			print ('file %s existed'%(remote_dir + '\\' + fname))
		
	ftp.cwd('..')


def get_local_dir(local_dir):
	print ('>>> dir:', local_dir)
	os.chdir(local_dir)

	#ftp.mkd(local_dir)
	#ftp.cwd(local_dir)

	fds = os.listdir(os.getcwd())
	
	for l in fds:
		if os.path.isdir(l):
			get_local_dir(l)
		elif os.path.isfile(l):
			print ('file:', l)
		else:
			print ('ignore:', l)
	os.chdir('..')

	#ftp.cwd('..')
	print ('<<< dir:', local_dir)


# make dir on server according to local dir
def get_local_dir_(ftp, local_dir):
	print ('[[[ dir:', local_dir)
	os.chdir(local_dir)
	ftp.mkd(local_dir)
	ftp.cwd(local_dir)
	fds = os.listdir(os.getcwd())
	for l in fds:
		if os.path.isdir(l):
			get_local_dir_(ftp, l)
		elif os.path.isfile(l):
			print ('file:', l)
			ftp_upload_(ftp, l)
		else:
			print ('ignore:', l)
	os.chdir('..')
	ftp.cwd('..')
	print (']]] dir:', local_dir)

def get_local_file_(ftp, local_dir):
	print ('[[[ dir:', local_dir)
	os.chdir(local_dir)
	#ftp.mkd(local_dir)
	ftp.cwd(local_dir)
	fds = os.listdir(os.getcwd())
	for l in fds:
		if os.path.isdir(l):
			get_local_file_(ftp, l)
		elif os.path.isfile(l):
			print ('rm old file:', l)
			ftp.delete(l)
			print ('uploading file:', l)
			ftp_upload_(ftp, l)
		else:
			print ('ignore:', l)
	os.chdir('..')
	ftp.cwd('..')
	print (']]] dir:', local_dir)


if __name__ == '__main__':
	#ftp server dir
	
	
	tar_dir = 'pub'
	f = ftp_init()
	#ftp.cwd(tar_dir)
	##ftp.dir(ftp_get_dir)
	##ftp_download_dir (ftp, tar_dir, local_root)
	##ftp_download_
	##ftp_upload_file (ftp, tar_dir, local_root)
	##print remote_dir_info

	#upload_root_dir = r'E:\backupswitch\localroot\pub'
	##upload_dir = r'easybridge-B'
	##os.chdir(upload_root_dir)
	##f.cwd(tar_dir)
	##get_local_dir_(f, upload_dir)
	##print "done get_local_dir_file"

	# download srv -> local
	##ftp_download_dir (f, tar_dir, local_root)
	##ftp_download_file (f, tar_dir, local_root)

	# dirs demoninated by server
	# files uploaded according to localhost
	#upload_root_dir = r'E:\backupswitch\localroot\pub'
	##ftp_download_dir (f, tar_dir, local_root)
	upload_root_dir = r'E:\backupswitch\localroot\pub'
	upload_dir = r'easy'
	os.chdir(upload_root_dir)
	f.cwd(tar_dir)
	get_local_file_(f, upload_dir)

