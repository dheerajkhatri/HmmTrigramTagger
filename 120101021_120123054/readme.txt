At first cd 120101021_120123054/Supplementary Material/src

Deliverable 1:
----------------------------------------------------------------
sample run:
python hmm.py ../Data/Brown_tagged_train.txt ../Data/sample_test.txt RARE Laplace

sys.argv[1]:fileName of tagged train data file
sys.argv[2]:fileName of test data file
sys.argv[3]:which method to use to estimate Q values : enter RARE for deliverable1
sys.argv[4]:smoothing technique: Laplace

results will be generated in resultfile folder:
ie tagger_out_RARE_Laplace.txt will be generated if you run RARE mapping and Laplace smoothing technique

Deliverable 2:
----------------------------------------------------------------
sample run:
python hmm.py ../Data/Brown_tagged_train.txt ../Data/sample_test.txt GROUP Interpolation

sys.argv[1]:fileName of tagged train data file
sys.argv[2]:fileName of test data file
sys.argv[3]:which method to use to estimate Q values : enter GROUP for deliverable2
sys.argv[4]:smoothing technique : Interpolation

results will be generated in resultfile folder:
ie tagger_out_GROUP_Interpolation.txt will be generated if you run GROUP mapping and Deleted Interpolation smoothing technique


Deliverable 3:
----------------------------------------------------------------
sample run:
python evaltagpos.py ../resultfiles/expected_out.txt ../resultfiles/tagger_out_RARE_Laplace.txt
python evaltagpos.py ../resultfiles/expected_out.txt ../resultfiles/tagger_out_GROUP_Interpolation.txt

sys.argv[1]:fileName of expected tag file
sys.argv[2]:fileName of model's outputed file

results will be generated on terminal itself.
----------------------------------------------------------------

Details:
There are two Out of Vocabulary mapping techniques. 
First matches each word which freuency is < MINFREQ to RARE word.
Second method has some classes and categorize word which is having < MINFREQ to one of those class.

Two smoothing techniques are used:
First is simple laplace smoothing
Second is deleted interpolation which seems to give better results.

Completed Corpus results:
This folder contains the result for different mapping method and smoothing technique when ran on completed brown corpus.
extra_results files contains tag for extra lines which are present in brown test data
please note,#lines in Brown_tagged_data.txt > #lines in Brown_train_data.txt

References:
https://web.stanford.edu/~jurafsky/slp3/9.pdf
http://stp.lingfil.uu.se/~nivre/statmet/haulrich.pdf
https://courses.engr.illinois.edu/cs498jh/Slides/Lecture03HO.pdf