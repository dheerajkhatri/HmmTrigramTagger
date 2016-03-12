import re
import os
import sys
import operator
from collections import defaultdict

class HMM():

	def __init__(self,trainFileName,testFileName,logFileName):
		self.ftrain =  trainFileName 
		self.ftest =   testFileName
		self.flog  =  logFileName
		self.fp = open(self.flog,'w')
		if not os.path.exists('log files'):
			os.makedirs('log files')
		self.logdir = 'log files'

	#get counts of different parameters		
	def get_counts(self):		
		self.word_tag = defaultdict(int)
		self.uni_tag = defaultdict(int)
		self.bi_tag = defaultdict(int)
		self.tri_tag = defaultdict(int)
		self.word_count = defaultdict(int)		
		
		line_count = 0	
		for l in open(self.ftrain,'r'):				
			l = l.strip()

			tag_penult = ''
			tag_last = ''
			tag_current = ''						

			line_count += 1												
			print 'processing line #' + str(line_count) + '.......................'
			for ll in l.split(' '):						
				#print ll
				if ll == './.':
					tag_penult = tag_last
					tag_last = tag_current
					tag_current = 'STOP'

					#sentece boundary case
					if tag_last != '' and tag_penult != '':
						self.bi_tag[(tag_last,tag_current)] += 1
						self.tri_tag[(tag_penult,tag_last,tag_current)] += 1
				else:
					
					#word,tag = ll.split('/')      #will be problem eg: origin/destination/NOUN
					word = ll.rsplit('/',1)[0]
					self.word_count[word] += 1
					tag = ll.rsplit('/',1)[1]
					tag_penult = tag_last
					tag_last = tag_current
					tag_current = tag

					self.word_tag[(word,tag)] += 1
					self.uni_tag[tag] += 1
					self.bi_tag[(tag_last,tag_current)] += 1
					self.tri_tag[(tag_penult,tag_last,tag_current)] += 1

					#starting bigram
					if tag_penult == '' and tag_last == '':
						self.bi_tag[('','')] += 1													


		
		#print self.word_tag.keys()
		print "#uni_tag are: " + str(len(self.uni_tag))		
		#print self.uni_tag		
		print "#bi_tag are: " + str(len(self.bi_tag))		
		#print self.bi_tag
		print "#tri_tag are: " + str(len(self.tri_tag))		
		#print self.tri_tag		


		#log the data in file		
		fwc = open(os.path.join(self.logdir + '/initial_word_count.txt'),'w')		
		for word,count in sorted(self.word_count.items(),key=operator.itemgetter(1)):
			fwc.write(word + ' = ' + str(count) + '\n')		
		fwc.close()

		fwc = open(os.path.join(self.logdir + '/initial_word_tag.txt'),'w')
		for wordtag,count in sorted(self.word_tag.items(),key=operator.itemgetter(1)):
			fwc.write(str(wordtag) + ' = ' + str(count) + '\n')
		fwc.close()

		fwc = open(os.path.join(self.logdir + '/uni_tag.txt'),'w')
		for tag,count in sorted(self.uni_tag.items(),key=operator.itemgetter(1)):
			fwc.write(tag + ' = ' + str(count) + '\n')		
		fwc.close()

		fwc = open(os.path.join(self.logdir + '/bi_tag.txt'),'w')
		for tag,count in sorted(self.bi_tag.items(),key=operator.itemgetter(1)):
			fwc.write(str(tag) + ' = ' + str(count) + '\n')		
		fwc.close()

		fwc = open(os.path.join(self.logdir + '/tri_tag.txt'),'w')
		for tag,count in sorted(self.tri_tag.items(),key=operator.itemgetter(1)):
			fwc.write(str(tag) + ' = ' + str(count) + '\n')						
		fwc.close()

	def get_e(self,word,tag):
		return float(self.word_tag[(word,tag)])/float(self.uni_tag[tag])

	def get_q(self,tag_penult,tag_last,tag_current):
		return float(self.tri_tag[(tag_penult,tag_last,tag_current)])/float(self.bi_tag[(tag_penult,tag_last)])

	def get_parameters(self,method='UNK'):
		#get all the words
		self.words = set([key[0] for key in self.word_tag.keys()])
		if method == 'UNK':
			self.UNK()
		elif method == 'MORPHO':
			self.MORPHO()

		self.words = set([key[0] for key in self.word_tag.keys()])
		print '# words are ' + str(len(self.words)) + '\n'
		self.tags = set(self.uni_tag.keys())		

		self.Q = defaultdict(int)
		self.E = defaultdict(int)

		self.fp.write('getting E values...\n')
		#get e value for each word_tag pair
		for (word,tag) in self.word_tag:
			self.E[(word,tag)] = self.get_e(word,tag)
			self.fp.write(word+'|'+tag+'='+str(self.E[(word,tag)])+'\n')
		
		self.fp.write('\n')
		self.fp.write('getting Q values...\n')
		#get q value for each trigram
		for (tag_penult,tag_last,tag_current) in self.tri_tag:
			self.Q[(tag_penult,tag_last,tag_current)] = (self.get_q(tag_penult,tag_last,tag_current)+1) / float(len(self.word_count))
			self.fp.write(tag_current+'|'+tag_penult+','+tag_last+'='+str(self.Q[(tag_penult,tag_last,tag_current)])+'\n')

	def UNK(self):
		new_word_tag = defaultdict(int)

		#change less frequent words with frequency < 6
		for (word,tag) in self.word_tag:
			new_word_tag[(word,tag)] = self.word_tag[(word,tag)]
			if(self.word_tag[(word,tag)] < 6):
				new_word_tag[('<UNKNOWN>',tag)] += self.word_tag[(word,tag)]

		self.word_tag = new_word_tag	

	def subcategorize(self,word):
		if not re.search(r'\w',word):
			return '<PUNCS>'
		elif re.search(r'[A-Z]',word):
			return '<CAPITAL>'
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

	def MORPHO(self):
		new_word_tag = defaultdict(int)
		new_word_count = defaultdict(int)		

		#change less frequent words with frequency < 6
		#update word_count
		for word in self.word_count:			
			if self.word_count[word] < 6 :
				new_word_count[self.subcategorize(word)] += self.word_count[word]
			else:
				new_word_count[word] = self.word_count[word]

		#update word,tag
		for (word,tag) in self.word_tag:
			if self.word_count[word] < 6:
				new_word_tag[(self.subcategorize(word),tag)] += self.word_tag[(word,tag)]
			else:
				new_word_tag[(word,tag)] = self.word_tag[(word,tag)]
				
		self.word_tag = new_word_tag
		self.word_count = new_word_count

		
		fwc = open(os.path.join(self.logdir + '/updated_word_count.txt'),'w')		
		for word,count in sorted(self.word_count.items(),key=operator.itemgetter(1)):
			fwc.write(word + ' = ' + str(count) + '\n')		
		fwc.close()

		fwc = open(os.path.join(self.logdir + '/updated_word_tag.txt'),'w')
		for wordtag,count in sorted(self.word_tag.items(),key=operator.itemgetter(1)):
			fwc.write(str(wordtag) + ' = ' + str(count) + '\n')
		fwc.close()		

	def tagger(self,outFileName,method='UNK'):
		#train the model
		#fp = open(self.flog,'a')
		self.fp.write('inside tagger function\n\n')
		sys.stderr.write('get_counts..............\n')		
		self.get_counts()
		sys.stderr.write('get_parameters............\n')
		self.get_parameters(method)

		#start the tagging part
		print 'start tagging part...........'
		self.sent = []
		fout = open(outFileName,'w')
		sys.stderr.write('generating tag path by viterbi algorithm.....\n')
		for l in open(self.ftest,'r'):			
			l = l.strip()
			self.sent = l.split(' ')
			# remove last STOP symbol from list
			temp = self.sent.pop(-1)
			sys.stderr.write(' '.join(self.sent) + '\n')
			path = self.viterbi(' '.join(self.sent),method)
			#print 'printing path....'
			#print path

			for i in range(0,len(self.sent)):
				fout.write(self.sent[i] + '/' + path[i] + ' ')
			fout.write('./.')
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

	def viterbi(self,sent,method='UNK'):
		#assuming sent don't contain STOP symbol
		P = {}
		y = []		
		P[0,'',''] = 1		
		n = len(sent)
		BP = {}

		for k in range(1,n+1):
			word = sent[k-1]
			
			#handle unknown words
			if word not in self.words:
				if method == 'UNK':
					word = '<UNK>'
				elif method == 'MORPHO':
					word = self.subcategorize(word)


			for u in self.get_possible_tags(k-1):
				for v in self.get_possible_tags(k):
					P[k,u,v],prev_w = max([(P[k-1,w,u]*self.Q[w,u,v]*self.E[word,v],w) for w in self.get_possible_tags(k-2)])
					BP[k,u,v] = prev_w			
			
		val,yn_1,y_n = max([(P[n,u,v]*self.Q[u,v,'STOP'],u,v) for u in self.get_possible_tags(n-1) for v in self.get_possible_tags(n)])
		y.insert(0,y_n)
		y.insert(0,yn_1)

		for k in range(n-2,0,-1):
			yk = BP[k+2,y[0],y[1]]
			y.insert(0,yk)
		return y


#python hmm.py Data/Brown_tagged_train.txt Data/sample_test.txt Data/log.txt
if __name__ == "__main__":
	#argv[1] : tagged train data
	#argv[2] : test data
	#argv[3] : log file
	hmm = HMM(sys.argv[1],sys.argv[2],sys.argv[3])
	#hmm = HMM('Data/Brown_tagged_train.txt','Data/Brown_train.txt')
	hmm.tagger('Data/result','UNK')




# class runner(HMM):
# 	def run_MORPHO(self):
# 		self.get_counts()
# 		self.get_parameters('MORPHO')
# 		fout = open('MORPHO_out','w')
# 		best = {}
# 		besttag = ''
# 		raremarkers = ['<PUNCS>','<CAPITAL>','<NUM>','<NOUNLIKE>','<VERBLIKE>','<JJLIKE>','<OTHER>']

# 		#get the best tag for each raremarker
# 		pivot = 0
# 		tag = ''
# 		for raremarker in raremarkers:
# 			for (word,tag) in self.E:
# 				if word == raremarker:
# 					if self.E[(word,tag)] > pivot:
# 						pivot = self.E[(word,tag)]
# 						besttag = tag
# 			best[raremarker] = tag
# 			print raremarker,tag

		
# 		for l in open(self.ftest,'r'):
# 			l = l.strip()

# 			for ll in l.split(' '):
# 				if ll == '.':
# 					fout.write('\n')
# 				else:
# 					if ll in best:
# 						fout.write(ll + '/' + best[ll])
# 					else:
# 						pivot = 0
# 						besttag = ''
# 						if ll not in self.words:
# 							fout.write(w + '/' + best[self.subcategorize(ll)])
# 						else:
# 							for (word,tag) in self.E:
# 								if word == ll:
# 									if self.E[(word,tag)] > pivot:
# 										pivot = self.E[(word,tag)]
# 										besttag = tag
# 							best[ll] = besttag	