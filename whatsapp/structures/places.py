from .files import Config, Messages
import random


class Place:
	def __init__(self, name, type, parents, ibge_code, geojson, timestamps, sources, data, alias=[], reference_whatsapp=None, reference_twitter=None):
		self.name = name
		self.type = type
		self.parents = parents
		self.ibge_code = ibge_code
		self.geojson = geojson
		self.timestamp = timestamps
		self.sources = sources
		self.data = data
		self.alias = []

	@property
	def report(self):
		messages = Messages()
		config = Config()

		header = f"```Boletim``` - ```{self.name}```\n_Este é um boletim sobre a situação da Covid-19 em {self.name}_\n\n"
		footer = f"_______________\n{random.choice(messages.foot_notice)}\n_______________\n🔍 - {', '.join(self.sources)}\n🔕 - Para deixar de receber boletins de {self.name}, envie ```remover {self.name}```\n🛑 - Para cancelar *todos os seus boletins,* envie ```cancelar```\n📚 - Para mais informações, envie ```metodologia```"
		body = ""
		for key, value in self.data.items():
			if key in config.fields:
				body += f"```{config.fields[key]['name']}:``` _{value}{config.fields[key]['final_character']}_\n"
		return header+body+footer
