import datetime
import fileinput
import sys
import opern
import os
import pexpect
import time
import subprocess
import linecache
base_dir = ""
temp_dir = ""
source_dir = ""
destination_dir = ""
auth_fail = []
repo_fail = []
synced = []
tries = {}

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

def authenticate(child,username,password):
	child.expect(pexpect.EOF)
	child.sendline(username)
	child.sendline(password)
	return child
#Check for data.txt file
#initialize base dir
def setup():
	global base_dir
	base_dir = os.path.realpath(__file__)
	base_dir = base_dir[0:base_dir.rfind('/')]
	os.chdir(base_dir)
	child = pexpect.spawn ("ls",timeout=5)
	child.logfile_read = sys.stdout
	child.expect(pexpect.EOF)
	if "data.txt" in child.before:
		print("Found data.txt")
		print("Removing any previous copy of report.txt")
		os.system("rm "+base_dir+"/report.txt")
		os.system("touch "+base_dir+"/report.txt")
		return True
	else:
		print("data.txt file missing!")
		print("Place data.txt in the SYNC folder...")
		return False
#make temp folder and verify the repos and credentials
def verify(opn):
	clean()
	success = True
	global base_dir
	global temp_dir
	global source_dir
	global destination_dir
	temp_dir = base_dir + "/temp"
	os.chdir(base_dir)
	os.system("mkdir temp")
	os.chdir(temp_dir)
	print("Inside temp directory...")
	time.sleep(2)#raw_input("Press Enter to continue...")
	print("Checking/Cloning for source repo url:")
	try:
		child = pexpect.spawn ("git clone "+opn.get_source_url())
		child.logfile_read = sys.stdout
		#print("Authenticating source user...")
		time.sleep(2)#raw_input("Press Enter to continue...")
		#child = authenticate(child,opn.get_source_user(),opn.get_source_pass())
		#timeout may change according to repo size
		time.sleep(60)
		child.expect(pexpect.EOF)
		if "Checking connectivity... done." in child.before:
			print("source repo cloned successfully...")
			time.sleep(2)#raw_input("Press Enter to continue...")
			#verifying source directory name
			source_dir = temp_dir + "/" + opn.get_source()
			#child.expect(pexpect.EOF)
			if os.path.isdir(source_dir):
				print("source repo name and clone names match")
				child.expect(pexpect.EOF)		
			else:
				#global repo_fail
				repo_fail.append(opn.get_component())
				opn.set_do(False)
				print("source repo name and clone names don't match")
				print("Aborting")
				success = False
		elif "fatal: Authentication failed " in child.before:
			#global auth_fail
			auth_fail.append(opn.get_component())
			opn.set_do(False)
			print("Authentication failed in cloning source repo...")
			print("Problem with source repo name/url or user credentials")
			time.sleep(2)#raw_input("Press Enter to continue...")
			clean()
			success = False
		else:
			print("Unknown Error Occured")
			clean()
			sys.exit()
	except Exception as ex:
		print("Error occured while cloning source repo")
		#template = "An exception of type {0} occurred. Arguments:\n{1!r}"
		#message = template.format(type(ex).__name__, ex.args)
    		#print message
		PrintException()
		success = False
	if not success:
		os.chdir(base_dir)
		return success
	os.chdir(temp_dir)
	print("Inside temp directory...")
	time.sleep(2)#raw_input("Press Enter to continue...")
	print("Checking/Cloning for destination repo url:")
	try:
		child = pexpect.spawn ("git clone "+opn.get_destination_url())
		child.logfile_read = sys.stdout
		#print("Authenticating destination user...")
		time.sleep(2)#raw_input("Press Enter to continue...")
		child.expect("Password for 'https:")
		child.sendline(opn.get_destination_pass())
		#child = authenticate(child,opn.get_destination_user(),opn.get_destination_pass())
		#timeout may change according to repo size
		time.sleep(60)
		child.expect(pexpect.EOF)
		if "Checking connectivity... done." in child.before:
			print("destination repo cloned successfully...")
			time.sleep(2)#raw_input("Press Enter to continue...")
			#verifying source directory name
			destination_dir = temp_dir + "/" + opn.get_destination()
			if os.path.isdir(source_dir):
				print("source repo name and clone names match")
				child.expect(pexpect.EOF)		
			else:
				#global repo_fail
				repo_fail.append(opn.get_component())
				opn.set_do(False)
				print("source repo name and clone names don't match")
				print("Aborting")
				success = False
		elif "fatal: Authentication failed " in child.before:
			#global auth_fail
			auth_fail.append(opn.get_component())
			opn.set_do(False)
			print("Authentication failed in cloning destination repo...")
			print("Problem with destination repo name/url or user credentials")
			time.sleep(2)#raw_input("Press Enter to continue...")
			clean()
			success = False
		else:
			print("Unknown Error Occured")
			clean()
			sys.exit()
	except Exception as ex:
		print("Error occured while cloning source repo")
		template = "An exception of type {0} occurred. Arguments:\n{1!r}"
		message = template.format(type(ex).__name__, ex.args)
    		print message
		success = False
	os.chdir(temp_dir)
	return success
#If failure/termination occurs then cleaning up the temp directory so that no new conflicts occur
def clean():
	global base_dir
	os.chdir(base_dir)
	os.system("rm -rf temp")
	return True

#returns the last commit id of the source repo
def get_last_commit_id(opn):
	global source_dir
	global temp_dir
	cur_dir = os.getcwd()
	os.chdir(source_dir)
	proc = subprocess.Popen(['git log --format="%H" -n 1'], stdout=subprocess.PIPE, shell=True)
	(out, err) = proc.communicate()
	os.chdir(cur_dir)
	return (out)

#performs the sync operation
def perform(opn):
	if not verify(opn):
		print("Can't sync "+opn.get_component())
		return False
	try:
		global base_dir
		print("Sync operation verified and is ready to execute")
		with open(base_dir+'/report.txt', 'a') as f:
			f.write(opn.get_component()+'\n')
		global temp_dir
		global source_dir
		global destination_dir
		success = True
		print("Starting sync")
		time.sleep(2)#raw_input("Press Enter to continue...")
		os.chdir(destination_dir)
		print("Changing working directory")
		os.chdir(destination_dir)
		time.sleep(2)
		print("Print performing cherry pick")
		#get all the commits to be cherry picked
		os.chdir(source_dir)
		temp_str = 'git log --pretty=format:"%H" --no-merges '+str(opn.get_last_commit_id())+".."
		print(temp_str)
		proc = subprocess.Popen(temp_str, stdout=subprocess.PIPE, shell=True)
        	(out, err) = proc.communicate()
        	commits = out.split('\n')
		count = 0
		i = 0
		while(i<len(commits)):
			if (len(commits[i])<5):
				commits.remove(commits[i])
			else:
				i+=1
		if len(commits)==0:
			with open(base_dir+'/report.txt', 'a') as f:
				print("Nothing new to cherry pick for "+opn.get_component())
				f.write("Nothing new to cherry-pick"+'\n')
			return success
		print("Totally " + str(len(commits)) + " are meant to be merged for "+opn.get_component())
		print("List of commits")
		display(commits)
		for commit in reversed(commits):
			os.chdir(destination_dir)
			print("CherryPickiing "+commit)
			temp_str = "git fetch "+opn.get_source_url()+" master && git cherry-pick "+commit
			proc = subprocess.Popen([temp_str], stdout=subprocess.PIPE, shell=True)
			(out, err) = proc.communicate()
			if "Your branch is up-to-date with 'origin/master'" in out:
				print("Commit already cherry picked to destination updating last commit with new one")
				os.chdir(base_dir)
				with open('data.txt', 'r') as file :
  					filedata = file.read()
				filedata = filedata.replace(opn.get_last_commit_id(), commit)
				opn.set_last_commit_id(commit)
				with open('data.txt', 'w') as file:
					file.write(filedata)
				continue
			#elif "error: could not apply" in out or "error: 'cherry-pick' is not possible because you have " in out or "error: could not apply" in err or "error: 'cherry-pick' is not possible because you have " in err:
			elif len(out)==0:
				success = False
				print("Facing merge conflict! Aboting Sync for "+opn.get_component())
				os.chdir(base_dir)
				with open(base_dir+'/report.txt', 'a') as f:
					f.write(opn.get_component()+" encountered merge conflict for Commit:"+commit+'\n')
				break
			else:
				print("-----------------------Something new to commit----------------")
				print("Doing git amend")
				os.chdir(destination_dir)
				os.system("git commit --amend --no-edit")
				print("performing git push")
				d = str(datetime.datetime.today()).split()[0]
				child = pexpect.spawn("git push origin HEAD:refs/for/master%topic=topic_name-"+d)
				child.logfile_read = sys.stdout
				child.expect("Password for '")
				child.sendline(opn.get_destination_pass())
				time.sleep(60)
				output = child.read()
				output = output.split('\n')
				i = 0
				while i<len(output):
					if "remote:   https:" not in output[i]:
						output.remove(output[i])
						continue
					i+=1
				for i in range(len(output)):
					with open(base_dir+'/report.txt', 'a') as f:
					    f.write(output[i][10:-4]+'\n')
				child.expect(pexpect.EOF)
				if len(output)>0:
					print(commit+" cherry-picked for component "+opn.get_component())
					count=count+1
					#Update last commit for the component
				else:
					print("Failed to push commit:"+commit+" can't guarentee safe push for the rest of the commits...")
					success = False
		if success:
			print("Sync successfull!")
			print("Replacing last commit with new one")
			os.chdir(base_dir)
			with open('data.txt', 'r') as file :
  				filedata = file.read()
			filedata = filedata.replace(opn.get_last_commit_id(), commit)
			with open('data.txt', 'w') as file:
				file.write(filedata)
		else:
			print("Sync failed partially/fully can't assert full cherry pick")
	except Exception as ex:
		print("Sync failed some exception occured!")
		PrintException()
		success = False
	return success

def display(objs):
	sno = 1
	for obj in objs:
		print(str(sno)+". "+obj)
		sno+=1

#to prepare a list of operations to be executed
def init_opns():
	global base_dir
	txt = open(base_dir+"/data.txt").read().split("\n")
	opns = []
	for line in txt:
		data = line.split(" ")
		if len(data)==12:
			o = opern.operation(data)
			if o.get_do():
				opns.append(o)
		elif data[0]!="":
			print("Error:Incorrect operation format for operation "+data[0])
	return opns
	
def get_tries(component):
	global tries
	if component not in tries.keys():
		tries[component] = 1	
	return tries[component]
def refine_opns(opns):
	import copy
	temp = copy.deepcopy(opns)
	res = []
	for i in range(0,len(temp)):
		t = temp[i]
		if t.get_component() not in auth_fail and t.get_component() not in repo_fail and get_tries(t.get_component())<=2 and t.get_component() not in synced:
			res.append(t)
	opns = res
	return res
#Execution starts from here
if __name__ == "__main__":
	from datetime import datetime
	sync_time = []
	#Check for data.txt file
	if setup():
		while True:
			opns = init_opns()
			#check no of tries
			opns = refine_opns(opns)
			if opns!=[]:
				print("Following component(s) will be synced")
			temp = []
			for i in opns:
				temp.append(i.get_component())
			display(temp)
			count = len(opns)
			if count==0:
				break
			for opn in opns:
				try:
					print("Performing sync for "+opn.get_component()+" component : TRY No: "+str(get_tries(opn.get_component())))
					if perform(opn):
						print(opn.get_component()+" successfully synced")
						opn.set_do(False)
						synced.append(opn.get_component())
						sync_time.append(str(datetime.now().time()))
					else:
						print("Failed to sync "+opn.get_component())
				except Exception as ex:
					print("Unexpected error occured")
					print("Cleaning up")
					template = "An exception of type {0} occurred. Arguments:\n{1!r}"
				    	message = template.format(type(ex).__name__, ex.args)
    					print message
					time.sleep(2)#raw_input("Press Enter to continue...")
				clean()
				t = get_tries(opn.get_component())
				tries[opn.get_component()]=t+1
		for i in range(0,len(synced)):
			synced[i]+=(" at "+sync_time[i])
		if len(synced)>0:
			print("Susuccessfully merged components")
			display(synced)
		if len(auth_fail)>0:
			print("Authentication failed for following components")
			display(auth_fail)
		if len(repo_fail)>0:
			print("Repo initialization failed for following components")
			display(auth_fail)
		
	else:
		print("Data file missing...Exiting")
