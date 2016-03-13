
At first cd 120101021_120123050/Supplementary Material/src

Deliverable 1:
----------------------------------------------------------------
python hmm.py ../Data/Brown_tagged_train.txt ../Data/sample_test.txt RARE

sys.argv[1]:fileName of tagged train data file
sys.argv[2]:fileName of test data file
sys.argv[3]:which method to use to estimate Q values : enter RARE for deliverable1

Deliverable 2:
----------------------------------------------------------------
python hmm.py ../Data/Brown_tagged_train.txt ../Data/sample_test.txt GROUP

sys.argv[1]:fileName of tagged train data file
sys.argv[2]:fileName of test data file
sys.argv[3]:which method to use to estimate Q values : enter GROUP for deliverable2


Deliverable 3:
----------------------------------------------------------------
python evaltagpos.py ../resultfiles/expected_out.txt ../resultfiles/tagger_RARE_out.txt
python evaltagpos.py ../resultfiles/expected_out.txt ../resultfiles/tagger_GROUP_out.txt

sys.argv[1]:fileName of expected tag file
sys.argv[2]:fileName of model's outputed file