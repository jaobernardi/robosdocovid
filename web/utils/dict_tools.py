import re


def union_dicts_with_regex(regex, dicts):
	output = {}
	regex = re.compile(regex)
	for dict in dicts:
		for key, item in dict.items():
			if regex.match(key):
				if key not in output:
					output[key] = type(item)()
				output[key] += item
	return output
