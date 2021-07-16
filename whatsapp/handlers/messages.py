import api
import events
import tasks
import utils

from structures import Messages, Config
from browser import send_message


# Special functions:
# retrieve_report - Responsable for retrieving the place's data in the background.
@tasks.thread_function
def retrieve_report(user, name, code=False):
	messages = Messages()
	if not code:
		query = api.resolve_name(name)
		if len(query) > 1:
			choices = {}
			menu = ""
			index = 1
			for code in query:
				add_up = ''
				if "parents" in query[code]:
					for parent in query[code]['parents']:
						if parent['type'] == 'state':
							add_up = ", "+parent['alias'][0]
							break
				menu += f"{index} - {query[code]['name']}{add_up}\n"
				choices[str(index)] = code
				index += 1
			# Define the custom message handler.
			user.temporary_context.custom_handler = choice_menu(choices, messages.errors['bad_choice'], (lambda user, place: retrieve_report(user, place, True)))
			send_message(user, messages.flow["multiple_choices_places"].format(menu=menu))
			return
		elif query:
			name = list(query)[0]
		else:
			send_message(user, messages.error["place_not_found"].format(place=name))
			return
	place = api.get_place_data(name)
	send_message(user, place.report)

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
	messages = Messages()
	place_data = api.ibge_lookup(place)
	if place not in user.places:
		user.places.append(place)
		user.flush_info()
	if not len(user.places):
		return messages.success['first_register'].format(place=place_data['name'])

	return messages.success['add_place'].format(place=place_data['name'])

def remove_place(user, place):
	messages = Messages()
	place_data = api.ibge_lookup(place)
	if place in user.places:
		user.places.remove(place)
		user.flush_info()

	return messages.success['remove_place'].format(place=place_data['name'])


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
	if user.new or not len(user.places):
		query = api.resolve_name(message)
		if query:
			# Check for multiple awnsers, if there is, set the flow for the choice menu.
			if len(query) > 1:
				choices = {}
				menu = ""
				index = 1
				for code in query:
					add_up = ""
					if "parents" in query[code]:
						for parent in query[code]['parents']:
							if parent['type'] == 'state':
								add_up = ", "+parent['alias'][0]
								break
					menu += f"{index} - {query[code]['name']}{add_up}\n"
					choices[str(index)] = code
					index += 1
				# Define the custom message handler.
				user.temporary_context.custom_handler = choice_menu(choices, messages.errors['bad_choice'], define_place)
				return messages.flow["multiple_choices_places"].format(menu=menu)
			else:
				place = list(query)[0]
				place_data = api.ibge_lookup(place)
				user.places.append(place)
				user.flush_info()

				return messages.success['welcome_with_place'].format(place=place_data['name'])
		else:
			return messages.flow["welcome"]

	if utils.check_match("ping", args[0]):
		# Check if the first message is a place.
		return "Pong!"

	elif utils.check_match("adicionar", args[0]):
		if len(args) > 1:
			place = " ".join(args[1:])
			query = api.resolve_name(place)
			if query:
				# Check for multiple awnsers, if there is, set the flow for the choice menu.
				if len(query) > 1:
					choices = {}
					menu = ""
					index = 1
					for code in query:
						add_up = ""
						if "parents" in query[code]:
							for parent in query[code]['parents']:
								if parent['type'] == 'state':
									add_up = ", "+parent['alias'][0]
									break
						menu += f"{index} - {query[code]['name']}{add_up}\n"
						choices[str(index)] = code
						index += 1
					# Define the custom message handler.
					user.temporary_context.custom_handler = choice_menu(choices, messages.errors['bad_choice'], define_place)
					return messages.flow["multiple_choices_places"].format(menu=menu)
				elif query:
					return define_place(user, list(query)[0])
				else:
					return messages.errors["place_not_found"].format(place=place)
		else:
			return messages.errors["wrong_usage"].format(command=args[0], usage="_local_", example_arguments="São Paulo")

	elif utils.check_match("remover", args[0]):
		if len(args) > 1:
			place = " ".join(args[1:])
			query = api.resolve_name(place)
			if query:
				# Check for multiple awnsers, if there is, set the flow for the choice menu.
				if len(query) > 1:
					choices = {}
					menu = ""
					index = 1
					for code in query:
						add_up = ""
						if "parents" in query[code]:
							for parent in query[code]['parents']:
								if parent['type'] == 'state':
									add_up = ", "+parent['alias'][0]
									break
						menu += f"{index} - {query[code]['name']}{add_up}\n"
						choices[str(index)] = code
						index += 1
					# Define the custom message handler.
					user.temporary_context.custom_handler = choice_menu(choices, messages.errors['bad_choice'], remove_place)
					return messages.flow["multiple_choices_places"].format(menu=menu)
				elif query:
					return remove_place(user, list(query)[0])
				else:
					return messages.errors["place_not_found"].format(place=place)
		else:
			return messages.errors["wrong_usage"].format(command=args[0], usage="_local_", example_arguments="São Paulo")

	elif utils.check_match("lista", args[0]):
		output = ""
		for place in user.places:
			place = api.ibge_lookup(place)
			if "parents" in place:
				for parent in place['parents']:
					if parent['type'] == 'state':
						add_up = ", "+parent['alias'][0]
						break
			output += f"📌 {place['name']}{add_up}\n"
		return messages.success["place_list"].format(menu=output)

	elif utils.check_match("metodologia", args[0]):
		api.delete_user(user)
		return messages.success["metodologia"]

	elif utils.check_match("cancelar", args[0]):
		api.delete_user(user)
		return messages.success["delete"]

	elif utils.check_match("parciais", args[0]) or utils.check_match("boletim", args[0]):
		if len(args) > 1:
			retrieve_report(user, " ".join(args[1:]))
		else:
			return messages.errors["wrong_usage"].format(command=args[0], usage="_local_", example_arguments="São Paulo")
		return messages.flow["report_build"]
	else:
		return [messages.errors["not_found"].format(command=args[0])]+["💁‍ ```Comandos disponíveis:```",
		("👉 ```ping``` - Responde 'pong' _(use-o para verificar se estou respondendo corretamente!)_\n"
		"👉 ```boletim``` - Envia o boletim da região que desejar.\n"
		"👉 ```remover``` - Remove um local da sua lista.\n"
		"👉 ```adicionar``` - Adiciona um local a sua lista.\n"
		"👉 ```lista``` - Mostra a sua lista.\n"
		"👉 ```cancelar``` - Cancela a sua inscrição.\n"
		"👉 ```metodologia``` - Mostra a metodologia.")
		]
