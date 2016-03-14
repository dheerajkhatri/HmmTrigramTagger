import re
import os
import sys
import numpy as np

class EVAL():
	
	def __init__(self,realoutFile,modeloutFile):
		self.fout = realoutFile
		self.fmodel = modeloutFile		

	def get_alltags(self):
		self.tags = set()
		for l in open(self.fout,'r'):
			l = l.strip()
			for ll in l.split(' '):
				word = ll.rsplit('/',1)[0]
				tag = ll.rsplit('/',1)[1]
				self.tags.add(tag)
		for l in open(self.fmodel,'r'):
			l = l.strip()
			for ll in l.split(' '):
				word = ll.rsplit('/',1)[0]
				tag = ll.rsplit('/',1)[1]
				self.tags.add(tag)		

	def map_tags(self):
		self.tag_map = {}
		counter = 0
		for tag in self.tags:
			self.tag_map[tag] = counter
			counter += 1

	def get_confusion_matrix(self):
		self.error_count = 0
		self.tagCount = len(self.tags)
		self.token_count = 0
		self.confusion_mat = np.zeros(shape=(self.tagCount,self.tagCount),dtype=np.int)
		with open(self.fout) as iter_out, open(self.fmodel) as iter_model:
			while True:
				try:
					outl = next(iter_out)
					modell = next(iter_model)

					outl = outl.strip()
					modell = modell.strip()

					tokens1 = outl.split(' ')
					tokens2 = modell.split(' ')
	
					
					for i in range(0,len(tokens1)):
						tokens1[i] = tokens1[i].rsplit('/',1)[1]

					for i in range(0,len(tokens2)):
						tokens2[i] = tokens2[i].rsplit('/',1)[1]

					if(len(tokens1)!=len(tokens2)):
						sys.stderr.write('error in ' + str(outl) + '\n')
						self.error_count += 1
					else:
						self.token_count += len(tokens1)
						for i in range(0,len(tokens1)):
							tokval1 = self.tag_map[tokens1[i]]
							tokval2 = self.tag_map[tokens2[i]]
							self.confusion_mat[tokval1][tokval2] += 1							


				except StopIteration:
					break

	def get_all_counts(self):

		#matrix of tags*3, for each tag it contains TP,FP,FN values
		self.count_matrix = np.zeros(shape=(self.tagCount,3),dtype=np.int)
		for i in range(0,len(self.confusion_mat)):
			for j in range(0,len(self.confusion_mat)):
				if i == j:
					self.count_matrix[i][0] += self.confusion_mat[i][j]
				elif i > j:
					self.count_matrix[i][1] += self.confusion_mat[i][j]
				elif i < j:
					self.count_matrix[i][2] += self.confusion_mat[i][j]

	def get_class_parameters(self):

		#get pre,rec,f1 values for each class
		self.class_parameters = np.zeros(shape=(self.tagCount,3),dtype=np.double)
		for i in range(0,self.tagCount):
			for j in range(0,3):
				#get precision of ith class
				#precision = TP/(TP+FP)
				if j == 0:					
					self.class_parameters[i][j] = (self.count_matrix[i][0])/float(self.count_matrix[i][0]+self.count_matrix[i][1])
				#recall = TP/(TP+FN)					
				elif j == 1:
					self.class_parameters[i][j] = (self.count_matrix[i][0])/float(self.count_matrix[i][0]+self.count_matrix[i][2])
				#F1 value = (2*PRE*REC)/(PRE+REC)
				elif j == 2:
					self.class_parameters[i][j] = (2*self.class_parameters[i][0]*self.class_parameters[i][1])/float(self.class_parameters[i][0]+self.class_parameters[i][1])

	def get_overall_parameters(self):		

		total_tp = 0
		total_fp = 0
		total_fn = 0
		for i in range(0,self.tagCount):
			total_tp += self.count_matrix[i][0]
			total_fp += self.count_matrix[i][1]
			total_fn += self.count_matrix[i][2]

		self.pre_micro = total_tp/float(total_tp + total_fp)
		self.rec_micro = total_tp/float(total_tp+total_fn)
		
		total_pre = 0
		total_rec = 0
		total_f1 = 0

		for i in range(0,len(self.class_parameters)):
			total_pre += self.class_parameters[i][0]
			total_rec += self.class_parameters[i][1]
			total_f1 += self.class_parameters[i][2]

		self.pre_macro = total_pre/float(self.tagCount)
		self.rec_macro = total_rec/float(self.tagCount)

		self.f1_micro = (2 * self.pre_micro * self.rec_micro)/float(self.pre_micro + self.rec_micro)
		self.f1_macro = (2 * self.pre_macro * self.rec_macro)/float(self.pre_macro + self.rec_macro)		

	def print_confusion_mat(self):

		for key,val in self.tag_map.items():
			print key + '\t',			
		print '\n'		

		for i in range(0,self.tagCount):
			for j in range(0,self.tagCount):
				print str(self.confusion_mat[i][j]) + '\t',				
			print '\n'			
		print 'all tokens count is :' + str(self.token_count)
		print 'sum of all elements is :' + str(self.confusion_mat.sum())
		print 'error count is :' + str(self.error_count)		

	def print_count_mat(self):
		print 'TP \t FP \t FN'		
		for i in range(0,self.tagCount):
			print str(self.count_matrix[i][0]) + '\t' + str(self.count_matrix[i][1]) + '\t' + str(self.count_matrix[i][2])
		print '\n'

	def print_class_parameters(self):
		print 'PRE \t REC \t F1'		
		for i in range(0,self.tagCount):
			print str(float(format(self.class_parameters[i][0],'0.2f'))) + '\t' + str(float(format(self.class_parameters[i][1],'0.2f'))) + '\t' + str(float(format(self.class_parameters[i][2],'0.2f')))
		print '\n'

	def print_overall_parameters(self):
		print '\n'
		print 'PRECISION (micro) : ' + str(self.pre_micro)
		print 'PRECISION (macro) : ' + str(self.pre_macro)
		print 'RECALL (micro) : ' + str(self.rec_micro)
		print 'RECALL (macro) : ' + str(self.rec_macro)
		print 'F1 score (micro) : ' + str(self.f1_micro)
		print 'F1 score (macro) : ' + str(self.f1_macro)
		print '\n'


#python evaltagpos.py ../resultfiles/expected_out.txt ../resultfiles/tagger_out_RARE_Laplace.txt
#python evaltagpos.py ../resultfiles/expected_out.txt ../resultfiles/tagger_out_GROUP_Interpolation.txt
if __name__ == "__main__":
	#argv[1] contains expected tag values 
	#argv[2] contains model's tag values
	
	if len(sys.argv) != 3:
		print 'Please provide all file names: \n'
		print 'argv[1]:expectedTagValueFile.txt'
		print 'argv[2]:modelTagValueFile.txt\n'
		print 'Program exiting now.'
		exit()


	eval = EVAL(sys.argv[1],sys.argv[2])
	#eval.readFiles()
	eval.get_alltags()
	#print eval.tags
	eval.map_tags()

	eval.get_confusion_matrix()
	print 'printing confusion matrix....\n'
	eval.print_confusion_mat()

	eval.get_all_counts()
	print 'printing count matrix....\n'
	eval.print_count_mat()

	eval.get_class_parameters()
	print 'printing class parameteres....\n'
	eval.print_class_parameters()

	eval.get_overall_parameters()
	print 'printing overall parameters for the classifier.....'
	eval.print_overall_parameters()