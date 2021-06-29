from string import ascii_letters
from random import choice

def generate_string(length=10):
	return "".join([choice(ascii_letters) for i in range(length)])
