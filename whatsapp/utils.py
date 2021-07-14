from string import ascii_letters
from random import choice
import uuid
import difflib


def generate_token(length=10):
	return "".join([choice(ascii_letters) for i in range(length)])

def generate_uuid():
	return str(uuid.uuid1())

def check_match(in1, in2, margin=0.8):
	if difflib.SequenceMatcher(None, in1, in2).ratio() >= margin:
		return True
	return False
