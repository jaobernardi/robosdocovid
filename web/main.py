from structures import Server, Config
import servers
import events
from worker.worker import run
from tasks import add_process

add_process("Worker", run)
events.call_event("startup")
config = Config()
server = Server(config.host, config.port, config.certificate, config.private_key)
server.https_start()

def shutdown(*args, **kwargs):
    server.stop()
    exit()


signal.signal(signal.SIGINT, shutdown)
