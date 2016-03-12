import sys
import re
import random

def get_line_count(filename):	
	line_count = 0		
	for l in open(filename,'r'):		
		line_count += 1	
	return line_count


if __name__ == "__main__":
	filename = sys.argv[1]	
	with open(filename,'rb') as f:
		data = f.read().split('\n')

	randome.shuffle(data)
	train_data = data[:80]
	test_data = data[20:]
	# count = get_line_count('Data/Brown_train.txt')

	# print 'lines in corpus are ' + str(count)
	# print 'splitting data in 80-train,20-test data...'
	# no_train_data = int(count * 0.8)
	# no_test_data = count - no_train_data

	# in_train_data = random.sample(range(1,count),no_train_data)
	