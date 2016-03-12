import sys
import numpy as np
import matplotlib.pyplot as plt


def plot_xticks():	
	names = []
	values = []

	for l in open(sys.argv[1],'r'):
		l = l.strip()
		name,val = l.split('=')
		names.append(name)
		values.append(val)

	x = np.arange(len(values))
	y = np.array(values)


	my_xticks = names
	plt.xticks(x,my_xticks)
	plt.ylabel('count')

	plt.plot(x,y)
	plt.show()

def plot_freq():
	values = []
	for l in open(sys.argv[1],'r'):
		l = l.strip()
		name,val = l.split('=')		
		values.append(int(val))
	plt.hist(values)
	plt.show()

plot_freq()