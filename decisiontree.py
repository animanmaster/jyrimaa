class Node:
	def __init__(self, question, yes = None, no = None, terminal = False, value=None):
		self.question = question
		self.yes = yes
		self.no = no
		self.value = value
		self.terminal = terminal
	
	def isYes(self, **kwargs):
		return self.eval(**kwargs)
	
	def isNo(self, **kwargs):
		return not self.eval(**kwargs)
	
	def eval(self, **kwargs):
		return self.question(**kwargs)

class DecisionTree:
	def __init__(self, root=Node(lambda: True, terminal=True)):
		self.root = root
	
	def decide(self, **kwargs):
		current = self.root
		while current and not current.terminal:
			current = current.yes if current.isYes(**kwargs) else current.no
		return current.value


