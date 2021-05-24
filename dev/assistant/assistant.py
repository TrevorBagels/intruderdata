import datetime


class AssistantInteraction:
	def __init__(self, core, tts=True):
		self.core = core
	
	def take_input(self, prompt=""):
		return input(prompt)
	
	def inform(self, message):
		print(message)

	def process_command(self, message):
		pass



class AssistantCore:
	def __init__(self):
		self.interaction = AssistantInteraction(self)



a = AssistantCore()
a.interaction.take_input("Hello!")