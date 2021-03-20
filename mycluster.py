from gensim.models import Word2Vec
from numpy import random
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter
from collections import namedtuple
import csv
def csv2list(path,encoding='utf-8'):
    list=[]
    infile = open(path, 'r',encoding=encoding)
    reader=csv.reader(infile)
    for line in reader:
        list.append(line)
    return list
def cluster(reslist,outfile):

    model = Word2Vec.load(r'../模型/model')
    ofh=open(outfile,'w',encoding='utf-8-sig',newline='')
    writer=csv.writer(ofh)
    writer.writerow(['数量','动词'])

    count_dict = dict(Counter(reslist))
    X=[]
    tmp={}
    for key in count_dict:
        if key in model.wv.vocab:
            tmp[key] = count_dict[key]
    count_dict=tmp

    for key in count_dict:
        X.append(model.wv[key])
    X = np.array(X)
    for i in range(len(X)):
        X[i]=X[i]/np.linalg.norm(X[i])

    kind=100
    estimator = KMeans(n_clusters=kind)
    estimator.fit(X)
    label_pred = estimator.labels_

    x=[]
    for i in range(kind):
        x.append([])
    for i,key in enumerate(count_dict):
        x[label_pred[i]].append(key+str(count_dict[key]))

    for i in range(kind):
        writer.writerow([len(x[i]),' '.join(x[i])])
    ofh.close()

def clu(infile,outfile):
    reslist=csv2list(infile)
    tmplist=[]
    verb, label = 3, 6
    for line in reslist:
        if line[label]=='0':
            tmplist.append(line[verb])
    cluster(tmplist,outfile)
if __name__ == '__main__':
    clu(r'../利用聚类的关系提取/三元组_筛选.csv',r'../聚类分析/聚类.csv')
