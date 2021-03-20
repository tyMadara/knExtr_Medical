#关系词聚类
import csv
from gensim.models import Word2Vec
from numpy import random
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter
import re
def cluster():
    def get_count_by_counter(l):
        count = Counter(l)  # 类型： <class 'collections.Counter'>
        count_dict = dict(count)  # 类型： <type 'dict'>
        return count_dict
    model = Word2Vec.load(r'../聚类分析/model')
    ifh=open(r'../聚类分析/三元组.csv','r',encoding='utf-8')
    ofh=open(r'../聚类分析/聚类.csv','w',encoding='utf-8-sig',newline='')
    writer=csv.writer(ofh)
    writer.writerow(['数量','动词'])
    lines=csv.reader(ifh)

    connection_word=[]
    #i=0
    for line in lines:
        if line[6]=='hanlp':
            #i+=1
            line[2]=line[2].strip()
            connection_word.append(line[2]) if line[2] in model.wv.vocab else None

    count_dict = get_count_by_counter(connection_word)
    X=[]
    for key in count_dict:
        X.append(model.wv[key])
    X = np.array(X)
    for i in range(len(X)):
        X[i]=X[i]/np.linalg.norm(X[i])
    kind=100
    estimator = KMeans(n_clusters=kind)#构造聚类器
    estimator.fit(X)#聚类
    label_pred = estimator.labels_ #获取聚类标签

    x=[]
    for i in range(kind):
        x.append([])
    for i,key in enumerate(count_dict):
        x[label_pred[i]].append(key+str(count_dict[key]))
    for i in range(kind):
        writer.writerow([len(x[i]),' '.join(x[i])])


    ifh.close()
    ofh.close()
if __name__ == "__main__":
    cluster()
