from structures import IO_Var, Config
from time import sleep
import os
import logging
import re
import difflib

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Send message method
def send_message(user, messages, is_file=False, create=False, callback=(lambda driver: None), fallback=(lambda driver: None)):
	# Create an instance of the Config IO and retrieve the path for the activites path
	config = Config()
	# The structures.IO_Var basically is a method retrieve and add persistent python-objects into files using the lib dill.
	activities = IO_Var(config.whatsapp["activities_path"])
	name = user.phone

	# make messages an instance of list
	if not isinstance(messages, list):
		messages = [messages]

	# Wrapped function to be executed by the Whatsapp Loop
	def wrapper(driver):
		try:
			from structures import Config
			config = Config()
			if create:
				driver.get(f"https://web.whatsapp.com/send?phone={name}")
				WebDriverWait(driver, 200).until(
					EC.presence_of_element_located((By.CSS_SELECTOR, "."+config.whatsapp["class_ready_checks"])))
			else:
				# Since this will be run on a different instance of python
				# there is a need to import all the libs we need, except those who already were imported on the whatsapp loop
				import difflib

				# Look for the search bar and then click it
				search = driver.find_element_by_css_selector("."+config.whatsapp["class_message_box"])
				search.click()
				# Send the Target user's name (or in this case, their phone name or contact name.)
				search.send_keys(name)

				# Check for alphabetical characters on the user's name
				if not re.search('[a-zA-Z]', name):
					# If there isn't any characters matched by this regex, just proceed by sending and enter keystroke
					search.send_keys(Keys.ENTER)
				else:
					# If there is letters on the user's name, check every single result for the perfect match, since
					# whatsapp will also return conversations with non-saved contacts which may have the target user's name
					# on their settings.
					# BY THE WAY: This code may be very inefficient, since it is old and I haven't got the time to re-do it.
					_try = 0
					_try_again = True
					WebDriverWait(driver, 1000).until(
						EC.presence_of_element_located((By.CSS_SELECTOR, ".matched-text")))

					while _try_again and _try < 5:
						try:
							a = difflib.get_close_matches(name, [element.text for element in
																 driver.find_elements_by_xpath(
																	 f"//*[@class='matched-text {config.whatsapp['class_match_search']}']")])[0]
							for element in driver.find_elements_by_xpath("//*[@class='matched-text {config.whatsapp['class_match_search']}']"):
								if element.text == a:
									a = element
							a.click()
							_try_again = False
						except Exception as e:
							_try += 1
							sleep(5)

			new_name = driver.find_element_by_class_name(config.whatsapp["class_name"]) \
				.find_element_by_tag_name("span") \
				.text
			if name == new_name:
				logging.info(f"Sending message to {name}")
				for message in messages:
					if is_file:
						driver.find_element_by_css_selector(
							'span[data-icon="clip"]').click()
						attach = driver.find_element_by_css_selector(
							'input[type="file"]')
						attach.send_keys(message)
						WebDriverWait(driver, 200).until(EC.presence_of_element_located(
							(By.XPATH, f"//div[contains(@class, '{config.whatsapp['class_file_send']}')]")))
						driver.find_element_by_xpath(
							f"//div[contains(@class, '{config.whatsapp['class_file_send']}')]").click()
					else:
						# Find the message box
						msg_box = driver.find_elements_by_class_name(config.whatsapp["class_message_box"])[1]

						# Javascript to be injected
						js = f'event = document.createEvent("UIEvents");doc = document.getElementsByClassName("{config.whatsapp["class_message_box"]} copyable-text selectable-text")[1];doc.innerHTML = arguments[0];event.initUIEvent("input", true, true, window, 1);doc.dispatchEvent(event);'

						# Execute the JS code
						driver.execute_script(js, message)

						# Send the message
						msg_box.send_keys(Keys.ENTER)
			else:
				logging.info(f"Moved pointer to {name} and found {new_name}")
				# Sleep to prevent any possible errors
			sleep(0.3)

			# Reset the search bar
			search.send_keys(Keys.ESCAPE)
		except:
			fallback(driver)
		else:
			callback(driver)

	# Append the function to the activities path
	activities.add(wrapper)
