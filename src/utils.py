class Stat:
  
	def __init__(self):
		self.propagate= 0
		self.wmp= 0 # whether a weakly monotonic propagator might has been executed
		self.fail= 0
		self.node= 0
		self.depth= 0
		self.memory= 0
		

	def report(self):
		print('==  propagations:\t', self.propagate)
		print('==  wmp:\t',self.wmp)
		print('==  nodes:\t',self.node)
		print('==  peak depth:\t',self.depth)
		print('==  fail:\t',self.fail) 
		print('==  peak memory:\t',self.memory/1024,'KB')



class Solution:
	def __init__(self, **kwds):
		self.__dict__.update(kwds)



class Problem:
	def __init__(self, **kwds):
		self.__dict__.update(kwds)
