import sys

class operation:
	def __init__(self,data):
		self.__index = data[0]
		self.__component = data[1]
		self.__source = data[2]
		self.__source_url = data[3]
		self.__source_user = data[4]
		self.__source_pass = data[5]
		self.__destination = data[6]
		self.__destination_user = data[8]
		self.__destination_pass = data[9]
		self.__destination_url = data[7]
		self.__do = True if data[10]=="True" else False
		self.__last_commit_id = data[11]

	def set_index(self,index):
		self.__index = int(index)
	def get_index(self):
		return self.__index

	def set_component(self,component):
		self.__component = component
	def get_component(self):
		return self.__component

	def set_source(self,source):
		self.__source = source
	def get_source(self):
		return self.__source

	def set_source_user(self,source_user):
		self.__source_user = source_user
	def get_source_user(self):
		return self.__source_user

	def set_source_pass(self,source_pass):
		self.__source_pass = source_pass
	def get_source_pass(self):
		return self.__source_pass

	def set_source_url(self,source_url):
		self.__source_url = source_url
	def get_source_url(self):
		return self.__source_url

	def set_destination(self,destination):
		self.__destination = destination
	def get_destination(self):
		return self.__destination

	def set_destination_user(self,destination_user):
		self.__destination_user = destination_user
	def get_destination_user(self):
		return self.__destination_user

	def set_destination_pass(self,destination_pass):
		self.__destination_pass = destination_pass
	def get_destination_pass(self):
		return self.__destination_pass

	def set_destination_url(self,destination_url):
		self.__destination_url = destination_url
	def get_destination_url(self):
		return self.__destination_url

	def set_do(self,do):
		self.__do = True if do=='True'	else False

	def get_do(self):
		return self.__do

        def set_last_commit_id(self,last_commit_id):
                self.__last_commit_id = last_commit_id

        def get_last_commit_id(self):
                return self.__last_commit_id

	def display(opn):
		print("Index:"+str(opn.get_index()))
		print("Component:"+opn.get_component())
		print("Source:"+opn.get_source())
		print("Source User:"+opn.get_source_user())
		print("Source Pass:"+opn.get_source_pass())
		print("Source Url:"+opn.get_source_url())
		print("Destination:"+opn.get_destination())
		print("Destination User:"+opn.get_destination_user())
		print("Destination Pass:"+opn.get_destination_pass())
		print("Destination Url:"+opn.get_destination_url())
		print("Do:"+str(opn.get_do()))
		print("Last Commit ID:",opn.get_last_commit_id());
