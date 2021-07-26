import handlers
from browser import run_browser
import logging
import threading
FORMAT = '[%(levelname)s] [%(threadName)s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

if __name__ == '__main__':
	threading.current_thread().name = "Browser"
	run_browser()
