#!/usr/bin/env bash
###
# reports for all variants in vcf aan allelic balance deviation from 20/80 ratio
#  usage: get_allele_balance -f filename -n true
#  optional argument -n true can be used if you have already split-multiallelics! This is essential for the script to 
#  work currently.
###


while getopts "f:n:o:" opt; do
	  declare "opt_$opt=${OPTARG:-0}"
done

infile=$opt_f
outfile=$opt_o

reference_seq="/humgen/1kg/reference/human_g1k_v37.fasta"

already_normalized=$opt_n


printer="cat"

if [ $infile=~"vcf.gz$" ]
then
	printer="zcat"
fi


if [ "$already_normalized" != "" ];
then

	bcftools query -f "%ID\t%AC\t%GQ_MEAN[\t%GT:%AD]\n" $infile | awk 'BEGIN{ FS="\t"; OFS="\t"; print "ID","AC","GQ","N","N_HET","N_HET","SUM_AB","AB","N_DEV_20_80","PROP_DEV_20_80"} { n_dev=0; n_hets=0; n_nonmissing=0; baf=0; for(i=4; i<=NF;i++) { split($i,dat,":"); if(dat[1]!="./.") { n_nonmissing+=1} if(dat[1]=="1/0"||dat[1]=="0/1" ) { n_hets+=1; split(dat[2],ab,","); balance=0; if(ab[1]+ab[2]>0) { balance=ab[1]/(ab[1]+ab[2]);baf+=balance;} if(balance<0.2 || balance>0.8) n_dev+=1 } } prop_dev=0; baf_dev=0; if(n_hets!=0) {prop_dev=n_dev/n_hets; baf_dev=baf/n_hets;} print $1,$2,$3,n_nonmissing,n_hets,baf,baf_dev,n_dev, prop_dev;  }' >$outfile

else
    
    $printer $infile | sed 's/^##FORMAT=<ID=AD,Number=\./##FORMAT=<ID=AD,Number=R/g' |  bcftools norm -Ou -m -any | bcftools norm -Ou -f $reference_seq | /home/unix/aganna/bcftools/bcftools annotate -Ob -x ID -I +'%CHROM:%POS:%REF:%ALT' | bcftools query -f "%ID\t%AC\t%GQ_MEAN[\t%GT:%AD]\n" | awk 'BEGIN{ FS="\t"; OFS="\t"; print "ID","AC","GQ","N","N_HET","SUM_AB","AB","N_DEV_20_80","PROP_DEV_20_80"} { n_dev=0; n_hets=0; n_nonmissing=0; baf=0; for(i=4; i<=NF;i++) { split($i,dat,":"); if(dat[1]!="./.") { n_nonmissing+=1} if(dat[1]=="1/0"||dat[1]=="0/1" ) { n_hets+=1; split(dat[2],ab,","); balance=0; if(ab[1]+ab[2]>0) { balance=ab[1]/(ab[1]+ab[2]); baf+=balance;} if(balance<0.2 || balance>0.8) n_dev+=1 } } prop_dev=0; baf_dev=0; if(n_hets!=0) {prop_dev=n_dev/n_hets; baf_dev=baf/n_hets;} print $1,$2,$3,n_nonmissing,n_hets,baf,baf_dev,n_dev, prop_dev;  }' >$outfile

fi