# coding: utf-8
# python 3.5
from itertools import product
from sklearn.metrics import accuracy_score
from multiprocessing import Pool
from multiprocessing import freeze_support
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/../MLEM2')
#sys.path.append('/Users/ooki/git/research_dr/python/MLEM2')
sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/../RuleClustering')
#sys.path.append('/Users/ooki/git/research_dr/python/RuleClustering')
import logging
logging.basicConfig(filename=os.path.dirname(os.path.abspath(__file__))+'/ExperimentsMLEM2.log',format='%(asctime)s,%(message)s',level=logging.DEBUG)
import importlib
import mlem2
importlib.reload(mlem2)  
import LERS
importlib.reload(LERS) 
import clustering
importlib.reload(clustering) 

# ====================================
# MLEM2 - LERS による正答率実験
# ====================================
def MLEM2_LERS(FILENAME, iter1, iter2) :
          
    # rule induction
    rules = mlem2.getRulesByMLEM2(FILENAME, iter1, iter2)

    # test data setup
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-test'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table_test = mlem2.getDecisionTable(filepath)
    decision_table_test = decision_table_test.dropna()
    decision_class = decision_table_test[decision_table_test.columns[-1]].values.tolist()

    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = mlem2.getNominalList(filepath)
    list_judgeNominal = mlem2.getJudgeNominal(decision_table_test, list_nominal)
    
    # predict by LERS
    predictions = LERS.predictByLERS(rules, decision_table_test, list_judgeNominal)
    
    # 正答率を求める
    accuracy = accuracy_score(decision_class, predictions)
    
    #print('{FILENAME} : {iter1} {iter2}'.format(FILENAME=FILENAME,iter1=iter1,iter2=iter2))    
    logging.info('MLEM2-LERS,{FILENAME},{iter1},{iter2},{acc}'.format(FILENAME=FILENAME,iter1=iter1,iter2=iter2,acc=accuracy))
    
    return(accuracy)

# ====================================
# MLEM2 - LERS による正答率実験
# ====================================
def MLEM2_RuleClusteringBySim_LERS(FILENAME, iter1, iter2, k) :
          
    # rule induction
    rules = mlem2.getRulesByMLEM2(FILENAME, iter1, iter2)

    # rule clustering
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-train'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table = mlem2.getDecisionTable(filepath)
    colnames = mlem2.getColNames(decision_table)
    
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = mlem2.getNominalList(filepath)
    list_judgeNominal = mlem2.getJudgeNominal(decision_table, list_nominal)

    rules = clustering.getRuleClusteringBySimilarity(rules, colnames, list_judgeNominal, k=k)

    # test data setup
    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'-test'+str(iter1)+'-'+str(iter2)+'.tsv'
    decision_table_test = mlem2.getDecisionTable(filepath)
    decision_table_test = decision_table_test.dropna()
    decision_class = decision_table_test[decision_table_test.columns[-1]].values.tolist()

    filepath = '/data/uci/'+FILENAME+'/'+FILENAME+'.nominal'
    list_nominal = mlem2.getNominalList(filepath)
    list_judgeNominal = mlem2.getJudgeNominal(decision_table_test, list_nominal)
    
    # predict by LERS
    predictions = LERS.predictByLERS(rules, decision_table_test, list_judgeNominal)
    
    # 正答率を求める
    accuracy = accuracy_score(decision_class, predictions)
    
    #print('{FILENAME} : {iter1} {iter2}'.format(FILENAME=FILENAME,iter1=iter1,iter2=iter2))    
    logging.info('MLEM2-RuleClusteringBySim_-LERS,{k},{FILENAME},{iter1},{iter2},{acc}'.format(FILENAME=FILENAME,k=k,iter1=iter1,iter2=iter2,acc=accuracy))
    
    return(accuracy)

# ========================================
# listの平均と分散を求める
# ========================================
def getEvalMeanVar(result):
    ans = '{mean}±{std}'.format(mean=('%.3f' % round(np.mean(results),3)), std=('%.3f' % round(np.std(results),3)))
    return(ans)

# ========================================
# results を saveする
# ========================================
def saveResults(results, FILENAME):
    filename = FILENAME
    outfile = open(filename, 'w')  
    for x in results:
        outfile.write(str(x) + "\n")
    outfile.close()
    
# ========================================
# multi に実行する
# ========================================
def multi_main(proc,FILENAMES, FUN):
    pool = Pool(proc)
    multiargs = []

    # MLEM2_LERS 用
    if FUN == MLEM2_LERS :
        for FILENAME, iter1, iter2 in product(FILENAMES, range(1,11), range(1,11)):            
            multiargs.append((FILENAME,iter1,iter2))
    # MLEM2_RuleClusteringBySim_LERS 用
    elif FUN == MLEM2_RuleClusteringBySim_LERS :
        for FILENAME, iter1, iter2, k in product(FILENAMES, range(1,11), range(1,11), range(2,11)):
            multiargs.append((FILENAME,iter1,iter2,k))
    # その他
    else :
        print("I dont' know the function.")        
  
    results = pool.starmap(FUN, multiargs)
    return(results)
      
# ========================================
# main
# ========================================
if __name__ == "__main__":

    FILENAMES = ['hayes-roth']    

    # シングルプロセスで実行
    #for FILENAME, iter1, iter2 in product(FILENAMES, range(1,11), range(1,11)):    
    #    print('{filename} {i1} {i2}'.format(filename=FILENAME, i1=iter1, i2=iter2))
    #    print(MLEM2_LERS(FILENAME, iter1, iter2))

    # 実行したい実験関数
    FUN = MLEM2_LERS
    #FUN = MLEM2_RuleClusteringBySim_LERS

    # 並列実行    
    proc=4
    freeze_support()
    results = multi_main(proc, FILENAMES, FUN)
    
    # 平均と分散
    print(getEvalMeanVar(results))
    
    # 保存する
    #saveResults(results, "/data/uci/hayes-roth/accuracy.txt")
