#分词正确度统计

from function import *
import os
import csv

def gen2list(seg):
    '''将词性标注结果转化为词性列表'''
    resList=[]
    for ele in seg:
        resList.append(ele.word)
    return resList
'''
def main2(infile,inulist):
    sentences = sentence_Readfromdoc(infile)
    with open(r'D:\study\NLP\研究\个性化学习系统的课程知识图谱构建研究\实体提取2\有字典分词.txt', 'w', encoding='utf-8') as ofh:
        dict=dict_readformuList(inulist)
        ulist_List=[]
        for i,sentence in enumerate(sentences):
            print(i)
            tmplist=[]
            for word in dict:
                if word in sentence:
                    tmplist.append(word)
            tmplist2=tmplist.copy()
            for word in tmplist:
                for word2 in tmplist:
                    if word in word2 and word!=word2:
                        while word in tmplist2:
                            tmplist2.remove(word)
            ulist_List.append(tmplist2)
        for ulist in ulist_List:
            for ele in ulist:
                ofh.write(ele+' ')
            ofh.write('\n')

def func1(infile,infile2):
    ulist_List=[]
    with open(infile, 'r', encoding='utf-8') as ifh:
        for line in ifh.readlines():
            ulist_List.append(line.strip().split(' '))
    sentences = sentence_Readfromdoc(infile2)

    with open(r'D:\study\NLP\研究\个性化学习系统的课程知识图谱构建研究\实体提取2\相同.txt', 'w', encoding='utf-8') as ofh:
        with open(r'D:\study\NLP\研究\个性化学习系统的课程知识图谱构建研究\实体提取2\不相同.txt', 'w', encoding='utf-8') as ofh2:
            for i, sentence in enumerate(sentences):
                print(i)
                seg = posseg.cut(sentence)
                poslist=gen2list(seg)
                flag=1
                for ele in ulist_List[i]:
                    if ele not in poslist:
                        flag=0
                if flag==0:
                    for word in poslist:
                        ofh2.write(word+' ')
                    ofh2.write('\n')
                else:
                    for word in poslist:
                        ofh.write(word+' ')
                    ofh.write('\n')
'''
def fun2(path,inulist):
    def statistics(dir):
        sentences = sentence_Readfromdoc(dir)
        num = {}
        num_right = {}
        num_wrong = {}
        for word in Dict:
            num[word] = 0
            num_right[word] = 0
            num_wrong[word] = 0
        for i, sentence in enumerate(sentences):
            print(i)
            tmplist = []
            for word in Dict:
                if word in sentence:
                    tmplist.append(word)
            tmplist2 = tmplist.copy()
            for word in tmplist:
                for word2 in tmplist:
                    if word in word2 and word != word2:
                        while word in tmplist2:
                            tmplist2.remove(word)
            seg = posseg.cut(sentence)
            posList = gen2list(seg)
            for word in tmplist2:
                num[word] += 1
                if word in posList:
                    num_right[word] += 1
                else:
                    num_wrong[word] += 1
        ofh = open(os.path.dirname(dir)+'\\'+os.path.splitext(os.path.basename(dir))[0]+'_统计.csv', 'w', encoding='utf-8-sig', newline='')
        writer = csv.writer(ofh)
        writer.writerow(['实体', '出现次数', '分词正确次数', '错误次数'])
        for word in Dict:
            writer.writerow([word, num[word], num_right[word], num_wrong[word]])

    Dict=dict_readformuList(inulist)
    for dir in os.listdir(path):
        if os.path.splitext(dir)[1]=='.docx':
            statistics(path+'\\'+dir)






#func1(r'D:\study\NLP\研究\个性化学习系统的课程知识图谱构建研究\实体提取2\有字典分词.txt',r'D:\study\NLP\研究\个性化学习系统的课程知识图谱构建研究\医学相关\医学相关docx\CT诊断学.docx')
#main2(r'D:\study\NLP\研究\个性化学习系统的课程知识图谱构建研究\医学相关\医学相关docx\CT诊断学.docx',r'D:\study\NLP\研究\个性化学习系统的课程知识图谱构建研究\医学相关\实体\dict_医学.txt')
fun2(r'..\医学相关\医学相关docx',r'..\医学相关\实体\dict_规则过滤.txt')