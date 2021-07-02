from .dataset_collection import PR_Collect, SC_Collect, RS_Collect

def main():
	PR_Collect()
	print("Done PR")
	RS_Collect()
	print("Done RS")
	SC_Collect()
	print("Done")

if __name__ == '__main__':
	main()
