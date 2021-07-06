from .dataset_collections import PR_Collect, SC_Collect, RS_Collect, National_Collect
import time

def run():
	while True:
		PR_Collect()
		print("Done PR")
		RS_Collect()
		print("Done RS")
		SC_Collect()
		print("Done SC")
		National_Collect()
		print("Done")
		time.sleep(30*60)
