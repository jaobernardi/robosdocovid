import dill
import os
from utils import generate_token


class IO_Wrapper:
	def __init__(self, data):
		print(data)
		self.token = generate_token()
		self.data = data


class Persistance_IO:
	def __init__(self, path):
		self.path = path

	@staticmethod
	def list(path):
		output = []
		for file in os.listdir(path):
			if file.endswith(".iov"):
				output.append("".join(file.split(".iov")[0]))
		return tuple(output)

	@staticmethod
	def load(path):
		try:
			with open(path, "rb") as file:
				output = dill.load(file)
				file.close()
		except:
			output = None
		return output

	@staticmethod
	def write(path, intake):
		with open(path, "wb") as file:
			print(intake)
			output = dill.dump(intake, file)


class IO_Var(Persistance_IO):
	def __init__(self, path):
		self.path = path

	def __len__(self):
		return len(os.listdir(self.path))

	@property
	def last(self):
		last = os.listdir(self.path)
		if len(last) == 0:
			return
		return self.load(self.path+last[0])

	def remove(self, wrapper):
		token = wrapper.token if isinstance(wrapper, IO_Wrapper) else wrapper
		if token+".iov" in os.listdir(self.path):
			os.remove(self.path+token+".iov")

	def add(self, data):
		wrapped = IO_Wrapper(data)
		print(wrapped)
		self.write(self.path+wrapped.token+".iov", wrapped)
