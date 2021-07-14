import api
import events
import tasks
import utils
from browser import send_message


@tasks.thread_function
def retrieve_report(user, name):
	query = api.resolve_name(name)
	if not query:
		send_message(user, "404")
	else:
		send_message(user, "204")


@events.add_handle("new_message")
def message_handler(event):
	message = event.message
	user = event.user
	args = message.split(" ")

	if utils.check_match("ping", args[0]):
		return "Pong!"

	elif utils.check_match("parciais", args[0]):
		if len(args) > 1:
			retrieve_report(user, " ".join(args[1:]))
		else:
			return "Not enough arguments"
		return "Running!"
