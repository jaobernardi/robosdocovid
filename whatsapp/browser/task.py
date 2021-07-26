from structures import IO_Var, User, Config
from selenium import webdriver
import api
import events
from datetime import datetime
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import generate_uuid
from selenium.webdriver.common.action_chains import ActionChains
from .methods import send_message
import logging


def run_browser():
	# setup config and activites io var instances.
	config = Config()
	#messages = Messages()
	activities = IO_Var(config.whatsapp["activities_path"])
	# set the options for chrome.
	chrome_options = Options()
	chrome_options.add_argument("--no-sandbox")
	chrome_options.add_argument("user-data-dir=" + config.whatsapp["session_path"])
	chrome_options.add_argument("--headless")
	chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
	# setup the driver.
	driver = webdriver.Chrome(config.whatsapp['chromedriver_path'], options=chrome_options)
	driver.get("https://web.whatsapp.com")
	# wait for the page to fully load-up.
	WebDriverWait(driver, 200).until(
		EC.presence_of_element_located((By.CSS_SELECTOR, "."+config.whatsapp["class_ready_checks"])))

	last = ["", ""]
	while True:
		last_writeable = False
		sleep(1)
		try:
			# check for new activites.
			if action := activities.last:
				# get and run the last activity.
				logging.info(f"Executando ação {action.token}")
				action.data(driver)
				activities.remove(action)

			# check for new messages
			new = driver.find_elements_by_class_name(config.whatsapp["class_new_message"])

			# check if there is new messages and allow the pointer to update.
			if len(new) > 0:
				last_writeable = True
				x = new[0]
				x.click()
			# get user's name.
			try:
				name = driver.find_element_by_class_name(config.whatsapp["class_name"]) \
					.find_element_by_tag_name("span") \
					.text

			except:
				continue

			# check for user pointer change
			if not last_writeable and last[0] != name:
				last = [None, None]
				continue

			# get last message
			try:
				msg_object = driver.find_elements_by_class_name(
					"message-in")[-1:][0]

				text = msg_object \
					.find_element_by_class_name("selectable-text") \
					.text
			except:
				continue

			# if the pointer's user and text are still the same, skip.
			if last[0] == name and last[1].id == msg_object.id:
				continue

			# skip whenever there is a change of user and the pointer is not writable.
			if last[0] != name and not last_writeable:
				continue
			acknowledge = datetime.now()
			# update the pointer.
			last = [name, msg_object]
			# fire the message event.
			user = api.get_user(name)
			if not user:
				api.create_user(name, generate_uuid())
				user = api.get_user(name)
				user.new = True
			logging.info(f"[{name}]: {text}")
			event = events.call_event("new_message", cancellable=True, user=user, message=text, response="", acknowledge=acknowledge)

			# check if there is an response and if the event isn't cancelled.
			if event and not event.cancelled:
				# make the event response a list.
				if not isinstance(event.response, list):
					event.response = [event.response]
				# find the msg box.
				msg_box = driver.find_elements_by_class_name(config.whatsapp["class_message_box"])[1]
				# mark the reply message
				js = "var messages = document.getElementsByClassName(\"message-in\");messages[messages.length-1].dispatchEvent(new MouseEvent('dblclick', {'view': window,'bubbles': true,'cancelable': true}));"
				driver.execute_script(js)
				# supporting multiple response messages.
				for response in event.response:

					# setup the JS code to be injected.
					# send message
					js = f'event = document.createEvent("UIEvents");doc = document.getElementsByClassName("{config.whatsapp["class_message_box"]} copyable-text selectable-text")[1];doc.innerHTML = arguments[0];event.initUIEvent("input", true, true, window, 1);doc.dispatchEvent(event);'

					# execute the code and send an ENTER keystroke to the message box.
					driver.execute_script(js, response)
					msg_box.send_keys(Keys.ENTER)
			else:
				msg_box = driver.find_elements_by_class_name(config.whatsapp['class_message_box'])[1]
				# setup the JS code to be injected.
				# mark the reply message
				js = "var messages = document.getElementsByClassName(\"message-in\");messages[messages.length-1].dispatchEvent(new MouseEvent('dblclick', {'view': window,'bubbles': true,'cancelable': true}));"
				# send message
				js += f'event = document.createEvent("UIEvents");doc = document.getElementsByClassName("{config.whatsapp["class_message_box"]} copyable-text selectable-text")[1];doc.innerHTML = arguments[0];event.initUIEvent("input", true, true, window, 1);doc.dispatchEvent(event);'

				# execute the code and send an ENTER keystroke to the message box.
				#driver.execute_script(js, messages.errors["500"])
				driver.execute_script(js, "500")
				msg_box.send_keys(Keys.ENTER)

		except Exception as e:
		    # TO-DO: whenever there is an error, report it.
		    print(e)
		    # whenever there is an index error, reset the pointer.
		    if isinstance(e, IndexError):
		        last = ["", None]
