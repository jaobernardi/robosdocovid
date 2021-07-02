from .dataset_collections import PR_Collect, SC_Collect, RS_Collect

def run():
	PR_Collect()
	print("Done PR")
	RS_Collect()
	print("Done RS")
	SC_Collect()
	print("Done")
