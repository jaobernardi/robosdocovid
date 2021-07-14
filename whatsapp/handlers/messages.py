import api
import events
import tasks
import utils

from structures import Messages, Config
from browser import send_message


# Special functions:
# retrieve_report - Responsable for retrieving the place's data in the background.
@tasks.thread_function
def retrieve_report(user, name):
	query = api.resolve_name(name)
	if not query:
		send_message(user, "404")
	else:
		send_message(user, "204")

# choice_menu - Custom handler for chosing something.
def choice_menu(choices, not_found, callback):
	def wrapper(event):
		message = event.message
		user = event.user

		if message in choices:
			user.temporary_context.custom_handler = None
			return callback(user, choices[message])
		else:
			return not_found.format(message=message)
	return wrapper

# Define place is supposed to be the callback whevener some new user picks a location
# that the api returns more than one result.
def define_place(user, place):
	user.places.append(place)
	user.flush_info()
	return ":)"


@events.add_handle("new_message")
def message_handler(event):
	messages = Messages()
	message = event.message
	user = event.user
	args = message.split(" ")
	# Relay the message to the custom handler
	if user.temporary_context.custom_handler:
		return user.temporary_context.custom_handler(event)

	# Check if the user is new.
	query = api.resolve_name(message)
	if query:
		# Check for multiple awnsers, if there is, set the flow for the choice menu.
		if len(query) > 1:
			choices = {}
			menu = ""
			index = 1
			for code in query:
				menu += f"{index} - {query[code]['name']}\n"
				choices[str(index)] = code
				index += 1
			# Define the custom message handler.
			user.temporary_context.custom_handler = choice_menu(choices, messages.errors['bad_choice'], define_place)
			return messages.flow["multiple_choices_places"].format(menu=menu)
	if utils.check_match("ping", args[0]):
		# Check if the first message is a place.
		return ":)"
	elif utils.check_match("parciais", args[0]):
		if len(args) > 1:
			retrieve_report(user, " ".join(args[1:]))
		else:
			return "Not enough arguments"
		return "Running!"
