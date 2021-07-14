'''
This package is basically the brain for the bot. It detects, processes and awnser the messages.
Also, messages are serialized using dill, so it can run handle multi-threaded/proceses projects.
'''
from .task import run_browser
from .methods import send_message
