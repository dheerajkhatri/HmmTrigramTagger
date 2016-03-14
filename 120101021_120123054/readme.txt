At first cd 120101021_120123054/Supplementary Material/src

Deliverable 1:
----------------------------------------------------------------
python hmm.py ../Data/Brown_tagged_train.txt ../Data/sample_test.txt RARE Laplace

sys.argv[1]:fileName of tagged train data file
sys.argv[2]:fileName of test data file
sys.argv[3]:which method to use to estimate Q values : enter RARE for deliverable1
sys.argv[4]:smoothing technique: Laplace

Deliverable 2:
----------------------------------------------------------------
python hmm.py ../Data/Brown_tagged_train.txt ../Data/sample_test.txt GROUP Interpolation

sys.argv[1]:fileName of tagged train data file
sys.argv[2]:fileName of test data file
sys.argv[3]:which method to use to estimate Q values : enter GROUP for deliverable2
sys.argv[4]:smoothing technique : Interpolation


Deliverable 3:
----------------------------------------------------------------
python evaltagpos.py ../resultfiles/expected_out.txt ../resultfiles/tagger_out_RARE_Laplace.txt
python evaltagpos.py ../resultfiles/expected_out.txt ../resultfiles/tagger_out_GROUP_Interpolation.txt

sys.argv[1]:fileName of expected tag file
sys.argv[2]:fileName of model's outputed file


Details:
There are two Out of Vocabulary technique. 
First matches each word which freuency is < MINFREQ to RARE word.
Second method has some classes and categorize word which is having < MINFREQ to one of those class.

Two smoothing techniques are used:
First is simple laplace smoothing
Second is deleted interpolation which seems to give better results.