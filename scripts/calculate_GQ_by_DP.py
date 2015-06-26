#!/bin/bash
### PLOT DP BY GQ GENOTYPE-SPECIFIC METRICS ###
### Argument 1: a file generated from bcftool including DP genotype-specific values 
###	e.g. /humgen/atgu1/fs03/wip/aganna/fin_seq/processed/seq/temp/DP_G77318RH_table_SNP_EX.txt
### Argument 2: a file generated from bcftool including GQ genotype-specific values 
###	e.g. /humgen/atgu1/fs03/wip/aganna/fin_seq/processed/seq/temp/GQ_G77318RH_table_SNP_EX.txt
### Argument 3: a path were to ouput the files


import sys
import pandas as pd
import numpy as np
from time import gmtime, strftime


in1=sys.argv[1]
in2=sys.argv[2]
out=sys.argv[3]

#in1='/humgen/atgu1/fs03/wip/aganna/fin_seq/processed/seq/temp/DP_G77318RH_table_SNP_EX.txt'
#in2='/humgen/atgu1/fs03/wip/aganna/fin_seq/processed/seq/temp/GQ_G77318RH_table_SNP_EX.txt'
#out='/humgen/atgu1/fs03/wip/aganna/fin_seq/processed/seq/temp/'

inlast = ("_").join(in1.split("_")[-2:])


print "Loading DP values"
dp1 = pd.read_csv(in1 ,delim_whitespace=True,engine='c', header=None, na_values='.')

print "Loading GQ values"
gq1 = pd.read_csv(in2 ,delim_whitespace=True,engine='c', header=None, na_values='.')


def f(x):
	return float((x[np.isfinite(x)]>30).sum())/float(len(x[np.isfinite(x)]))

def GQGT20byDP(gq,dp):
	Dagg = []
    Gqgt20dplt10 = []
	for i in xrange(len(gq.columns)):
		gqt=gq.ix[:,i]
		dpt=dp.ix[:,i]
		gqtnm = gqt[np.isfinite(gqt) & np.isfinite(dpt)]
		dptnm = dpt[np.isfinite(gqt) & np.isfinite(dpt)]
		assert len(gqtnm)==len(dptnm),"ERROR: different length"
		tf = gqtnm > 20
        gqgt20dplt10 = (gqtnm > 20 & dptnm < 10).sum() ## CHECK THIS ##
        
              
		agg=[]
		if (i % 100) == 0:
			print('Processing sample',i,'out of',len(gq1.loc[1,]))
			print strftime("%Y-%m-%d %H:%M:%S", gmtime())
		for j in xrange(100):
			df = dptnm < j
			newn = (tf & df).sum()
			agg.append(float(newn)/float(len(tf)))
		Dagg.append(agg)
        Gqgt20dplt10.append(gqgt20dplt10)
	return(Dagg)

print "Processing DGQ > 20 by DP combinations"
GQgt20byDP = pd.DataFrame(GQGT20byDP(gq1,dp1)).transpose()

dpgt30=dp1.apply(f,axis=0)

dpgt30.to_csv(out + 'DPgt30_' + inlast,sep=' ')
GQgt20byDP.to_csv(out + 'GQgt20byDP_' + inlast,sep=' ',header=None)

Gqgt20dplt10.to_csv(out + 'Gqgt20dplt10_' + inlast,sep=' ',header=None) ## CHECK THIS ###
