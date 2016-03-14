import re
import os
import sys
import operator
from collections import defaultdict

class HMM():

	def __init__(self,trainFileName,testFileName):
		self.ftrain =  trainFileName 
		self.ftest =   testFileName		
		self.MINFREQ = 6
		self.STOP_SYMBOL = 'STOP'
		self.START_SYMBOL = ''	

		if not os.path.exists('../logfiles'):
			os.makedirs('../logfiles')
		self.logdir = '../logfiles'

		if not os.path.exists('../resultfiles'):
			os.makedirs('../resultfiles')
		self.resultdir = '../resultfiles'

	#get counts of different parameters		
	def get_counts(self):		
		self.word_tag = defaultdict(int)
		self.unigram = defaultdict(int)
		self.bigram = defaultdict(int)
		self.trigram = defaultdict(int)
		self.word_count = defaultdict(int)	
		self.token_count =	0
		
		line_count = 0	
		print 'Processing Train Data..........'
		for l in open(self.ftrain,'r'):				
			l = l.strip()

			tag_penult = ''
			tag_last = ''
			tag_current = ''						

			line_count += 1												
			#print 'processing line #' + str(line_count) + '.......................'
			for ll in l.split(' '):										
					
				#word,tag = ll.split('/')      #will be problem eg: origin/destination/NOUN
				word = ll.rsplit('/',1)[0]				
				tag = ll.rsplit('/',1)[1]
				tag_penult = tag_last
				tag_last = tag_current
				tag_current = tag

				self.word_count[word] += 1
				self.word_tag[(word,tag)] += 1
				self.unigram[tag] += 1
				self.bigram[(tag_last,tag_current)] += 1
				self.trigram[(tag_penult,tag_last,tag_current)] += 1			
				
			self.unigram[self.STOP_SYMBOL] += 1
			self.bigram[(tag_current,self.STOP_SYMBOL)] += 1
			self.trigram[(tag_last,tag_current,self.STOP_SYMBOL)] += 1

		for tag in self.unigram:
			self.token_count += self.unigram[tag]

		#print self.word_tag.keys()
		print "#unigram are: " + str(len(self.unigram))		
		#print self.unigram		
		print "#bigram are: " + str(len(self.bigram))		
		#print self.bigram
		print "#trigram are: " + str(len(self.trigram))		
		#print self.trigram		


		#log the data in file		
		fwc = open(os.path.join(self.logdir + '/initial_word_count.txt'),'w')		
		for word,count in sorted(self.word_count.items(),key=operator.itemgetter(1)):
			fwc.write(word + ' = ' + str(count) + '\n')		
		fwc.close()

		fwc = open(os.path.join(self.logdir + '/initial_word_tag.txt'),'w')
		for wordtag,count in sorted(self.word_tag.items(),key=operator.itemgetter(1)):
			fwc.write(str(wordtag) + ' = ' + str(count) + '\n')
		fwc.close()

		fwc = open(os.path.join(self.logdir + '/unigram.txt'),'w')
		for tag,count in sorted(self.unigram.items(),key=operator.itemgetter(1)):
			fwc.write(tag + ' = ' + str(count) + '\n')		
		fwc.close()

		fwc = open(os.path.join(self.logdir + '/bigram.txt'),'w')
		for tag,count in sorted(self.bigram.items(),key=operator.itemgetter(1)):
			fwc.write(str(tag) + ' = ' + str(count) + '\n')		
		fwc.close()

		fwc = open(os.path.join(self.logdir + '/trigram.txt'),'w')
		for tag,count in sorted(self.trigram.items(),key=operator.itemgetter(1)):
			fwc.write(str(tag) + ' = ' + str(count) + '\n')						
		fwc.close()

	def get_e(self,word,tag):
		return float(self.word_tag[(word,tag)])/float(self.unigram[tag])

	def get_q_laplace_smoothing(self,tag_penult,tag_last,tag_current):
		return float(self.trigram[(tag_penult,tag_last,tag_current)] + 1)/float(self.bigram[(tag_penult,tag_last)] + len(self.word_count))

	def get_q_interpolation_smoothing(self,tag_penult,tag_last,tag_current):
		total = float(0)
		temp = float(self.bigram[(tag_penult,tag_last)])
		if temp > 0:
			total += float(self.l3 * self.trigram[(tag_penult,tag_last,tag_current)]) / temp
		temp = float(self.unigram[tag_last])
		if temp > 0:
			total += float(self.l2 * self.bigram[(tag_last,tag_current)]) / temp
		temp = float(self.token_count)
		if temp > 0:
			total += float(self.l1 * self.unigram[tag_current]) / temp
		return  total


	def deleted_interpolation(self):
		self.l1 = float(0)
		self.l2 = float(0)
		self.l3 = float(0)
		for (tag_penult,tag_last,tag_current) in self.trigram:
			

			temp = float(self.bigram[(tag_penult,tag_last)] - 1)
			if temp <= 0:
				val1 = 0
			else:
				val1 = float(self.trigram[(tag_penult,tag_last,tag_current)] - 1)/temp
			
			temp = float(self.unigram[tag_last] - 1)
			if temp <=0 :
				val2 = 0
			else:
				val2 = float(self.bigram[(tag_last,tag_current)] - 1)/temp
			
			temp = float(self.token_count-1)
			if temp <=0 :
				val3 = 0
			else:
				val3 = float(self.unigram[tag_current] - 1)/temp			



			if val1 >= val2 and val1 >= val3:
				self.l3 += self.trigram[(tag_penult,tag_last,tag_current)]
			elif val2 >= val1 and val2 >= val3:
				self.l2 += self.trigram[(tag_penult,tag_last,tag_current)]
			elif val3 >= val1 and val3 >= val2:
				self.l1 += self.trigram[(tag_penult,tag_last,tag_current)]

		total_count = float(self.l1) + float(self.l2) + float(self.l3)
		self.l1 = self.l1 / float(total_count)
		self.l2 = self.l2 / float(total_count)
		self.l3 = 1 - (self.l1 + self.l2)

	def get_parameters(self,method='RARE',smoothing='Interpolation'):
		#get all the words
		self.words = set([key[0] for key in self.word_tag.keys()])
		self.map_rare_word(method)

		#get updated words affter applying mapping with self.MINFREQ
		self.words = set([key[0] for key in self.word_tag.keys()])
		print '# words are ' + str(len(self.words)) + '\n'
		self.tags = set(self.unigram.keys())		

		self.Q = defaultdict(int)
		self.E = defaultdict(int)

		#get e value for each word_tag pair
		sys.stderr.write('getting E values...\n')
		fwc = open(os.path.join(self.logdir + '/e_values.txt'),'w')		
		for (word,tag) in self.word_tag:
			self.E[(word,tag)] = self.get_e(word,tag)
			fwc.write(word+'|'+tag+'='+str(self.E[(word,tag)])+'\n')
				
		#get q value for each trigram
		sys.stderr.write('getting Q values...\n')		
		fwc = open(os.path.join(self.logdir + '/q_values_' + method + '_' + smoothing + '.txt'),'w')		
		
		# get values of lambdas
		if smoothing == 'Interpolation':
			self.deleted_interpolation()
			print 'lambda1: ' + str(self.l1) + '\t' + 'lambda2: ' + str(self.l2) + '\t' + 'lambda3: ' + str(self.l3) + '\t'

			for (tag_penult,tag_last,tag_current) in self.trigram:
					self.Q[(tag_penult,tag_last,tag_current)] = self.get_q_interpolation_smoothing(tag_penult,tag_last,tag_current)
					fwc.write(tag_current+'|'+tag_penult+','+tag_last+'='+str(self.Q[(tag_penult,tag_last,tag_current)])+'\n')		

		elif smoothing == 'Laplace':
			for (tag_penult,tag_last,tag_current) in self.trigram:
				self.Q[(tag_penult,tag_last,tag_current)] = self.get_q_laplace_smoothing(tag_penult,tag_last,tag_current)
				fwc.write(tag_current+'|'+tag_penult+','+tag_last+'='+str(self.Q[(tag_penult,tag_last,tag_current)])+'\n')
									
	def map_rare_word(self,method='RARE'):
		new_word_tag = defaultdict(int)
		new_word_count = defaultdict(int)

		#change less frequent words with frequency < self.MINFREQ
		for word in self.word_count:			
			if self.word_count[word] < self.MINFREQ :
				if method == 'RARE':
					new_word_count['RARE'] += self.word_count[word]
				elif method == 'GROUP':
					new_word_count[self.subcategorize(word)] += self.word_count[word]
			else:
				new_word_count[word] += self.word_count[word]

		#update word,tag
		for (word,tag) in self.word_tag:
			if self.word_count[word] < self.MINFREQ :
				if method == 'RARE':
					new_word_tag[('RARE',tag)] += self.word_tag[(word,tag)]
				elif method == 'GROUP':
					new_word_tag[(self.subcategorize(word),tag)] += self.word_tag[(word,tag)]
			else:
				new_word_tag[(word,tag)] += self.word_tag[(word,tag)]
				
		self.word_tag = new_word_tag
		self.word_count = new_word_count
		self.words = set([key[0] for key in self.word_tag.keys()])

		fwc = open(os.path.join(self.logdir + '/updated_word_count.txt'),'w')		
		for word,count in sorted(self.word_count.items(),key=operator.itemgetter(1)):
			fwc.write(word + ' = ' + str(count) + '\n')		
		fwc.close()

		fwc = open(os.path.join(self.logdir + '/updated_word_tag.txt'),'w')
		for wordtag,count in sorted(self.word_tag.items(),key=operator.itemgetter(1)):
			fwc.write(str(wordtag) + ' = ' + str(count) + '\n')
		fwc.close()		

	def subcategorize(self,word):
		if not re.search(r'\w',word):
			return '<PUNCS>'
		elif re.search(r'[A-Z]',word):
			return '<CAPS>'
		elif re.search(r'\d',word):
			return '<NUM>'
		elif re.search(r'(ion\b|ty\b|ics\b|ment\b|ence\b|ance\b|ness\b|ist\b|ism\b)',word):
			return '<NOUNLIKE>'
		elif re.search(r'(ate\b|fy\b|ize\b|\ben|\bem)',word):
			return '<VERBLIKE>'
		elif re.search(r'(\bun|\bin|ble\b|ry\b|ish\b|ious\b|ical\b|\bnon)',word):
			return '<JJLIKE>'
		else:
			return '<OTHER>'	

	def tagger(self,method='RARE',smoothing='Laplace'):
		#train the model
		#fp = open(self.flog,'a')
		
		sys.stderr.write('get_counts..............\n')		
		self.get_counts()
		sys.stderr.write('get_parameters............\n')
		self.get_parameters(method,smoothing)

		#start the tagging part
		print 'start tagging part...........'
		self.sent = []
		fout = open(os.path.join(self.resultdir + '/tagger_out_' + method  + '_' + smoothing + '.txt'),'w')		
		sys.stderr.write('generating tag path by viterbi algorithm.....\n')
		lineno = 1
		for l in open(self.ftest,'r'):
			l = l.strip()
			self.sent = l.split(' ')
			if lineno % 100 == 0:
				sys.stderr.write(str(lineno) + '\n')
			lineno += 1
			#sys.stderr.write(' '.join(self.sent) + '\n')
			path = self.viterbi(self.sent,method)
			#print 'printing path....'
			#print path

			for i in range(0,len(self.sent)):
				fout.write(self.sent[i] + '/' + path[i] + ' ')

			self.sent = []
			fout.write('\n')				
		fout.close()

	def get_word(self,sent,k):
		if k < 0:
			return ''
		else: 
			return sent[k]

	def get_possible_tags(self,k):
		if k == -1:
			return set([''])
		if k == 0 :
			return set([''])
		else:
			return self.tags

	def viterbi(self,sent,method='RARE'):
		#assuming sent don't contain STOP symbol		
		P = {}		
		BP = {}
		P[0,'',''] = 1		
		n = len(sent)
		y = ["" for x in range(n+1)]		

		for k in range(1,n+1):
			word = sent[k-1]
			
			#handle unknown words
			if word not in self.words:
				if method == 'RARE':
					word = 'RARE'
				elif method == 'GROUP':
					word = self.subcategorize(word)


			for u in self.get_possible_tags(k-1):
				for v in self.get_possible_tags(k):
					P[k,u,v],prev_w = max([(float(P[k-1,w,u]*self.Q[w,u,v]*self.E[word,v]),w) for w in self.get_possible_tags(k-2)])
					BP[k,u,v] = prev_w			
			
		val,y[n-1],y[n] = max([(float(P[n,u,v]*self.Q[u,v,self.STOP_SYMBOL]),u,v) for u in self.get_possible_tags(n-1) for v in self.get_possible_tags(n)])

		for k in range(n-2,0,-1):
			y[k] = BP[k+2,y[k+1],y[k+2]]

		y.pop(0)
		return y


#python hmm.py ../Data/Brown_tagged_train.txt ../Data/sample_test.txt RARE Laplace
#python hmm.py ../Data/Brown_tagged_train.txt ../Data/sample_test.txt GROUP Interpolation
if __name__ == "__main__":
	
	if len(sys.argv) != 5:
		print 'Please provide all file names: \n'
		print 'argv[1]:train file name with taggs'
		print 'argv[2]:test file name'
		print 'argv[3]:Method \t ie: deliverable1 - RARE OR deliverable2 - GROUP'		
		print 'argv[4]:Smoothing technique: Laplace or Interpolation\n'		
		print 'Program exiting now.'
		exit()


	if (sys.argv[3]!='RARE' and sys.argv[3]!='GROUP'):
		print 'argv[3] enrty is not correct, Please Enter either RARE or GROUP.'
		print 'Program exiting now.'
		exit()

	if (sys.argv[4]!='Laplace' and sys.argv[4]!='Interpolation'):
		print 'argv[4] enrty is not correct, Please Enter either Laplace or Interpolation'
		print 'Program exiting now.'
		exit()

	hmm = HMM(sys.argv[1],sys.argv[2])

	hmm.tagger(sys.argv[3],sys.argv[4])