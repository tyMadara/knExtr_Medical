import jieba.posseg as posseg
import jieba
import jieba.analyse as anls
import re

class unity(object):
    def __init__(self, uName = ''):
        self.proList = []
        self.addr = self
        self.name = uName

    def addProperty(self, proName):
        self.proList.append(proName)

    def modName(self, uName):
        self.name = uName

#利用结巴分词进行分词以及词性标注
def jiba_split(infile,outfile):
    jieba.load_userdict(r'dict\blx.txt')
    ofh = open(outfile,'w',encoding='utf-8')
    with open(infile,'r',encoding='utf-8') as ifh:
        for line in ifh.readlines():
            seg = posseg.cut(line.strip())
            for ele in seg:
                ofh.write(str(ele) + '\t')
            ofh.write('\n')
    ofh.close()

#合并相邻的名词，按照label_list中的词性进行合并
def nMerge(seg, label_list):
    flag = 0
    resList = []
    for ele in seg:
        if ele.flag not in label_list:
            flag = 0
            resList.append([ele.word,ele.flag])
        elif ele.flag in label_list :
            if flag == 0:
                flag = 1
                resList.append([ele.word,'n'])
            else:
                resList[-1][0] = resList[-1][0] + ele.word
    return resList

def nMerge2(seg, label_list, dLabel = 'n'):
    flag = 0
    resList = []
    for ele in seg:
        if ele[1] not in label_list:
            flag = 0
            resList.append([ele[0],ele[1]])
        elif ele[1] in label_list :
            if flag == 0:
                flag = 1
                resList.append([ele[0],dLabel])
            else:
                resList[-1][0] = resList[-1][0] + ele[0]
    return resList


#对分词后的目录标题进行实体提取,输入一个(word,flag)为元素的list，这个输入是一行的分词结果，word是单词，flag是词性，这里对
#['n','vn','t','l','nr','ng']进行了合并，把它们都看作了名词n，并且相邻的进行合并。
#病理学/n	的/uj	概念/n	和/c	任务/n
#活/vn	组织/n	和/c	细胞学/n	检查/vn
#细胞/n	和/c	组织/n	的/uj	适应/v	、/x	损伤/v
#病理学/n	在/p	医学/n	中/f	的/uj	作用/v
def extractFromTitle(wdlist):
    #如果只有一个就返回
    if len(wdlist) == 1:
        if len(wdlist[0][0]) > 2:
            return [unity(wdlist[0][0])]
        else:
            return []
    uList = []
    uj_flag = 0
    last_flag = ''
    #将这个列表按照'uj'词性的词进行剖分
    beforeList = []
    afterList = []
    lastEle = 'null'
    for ele in wdlist:
        if uj_flag == 0:
            if ele[1] != 'uj':
                beforeList.append(ele)
            else:
                uj_flag = 1
                continue
        else:
            afterList.append(ele)
    #词性列表
    beforeFlagList = []
    afterFlagList = []
    for ele in beforeList:
        beforeFlagList.append(ele[1])
    for ele in afterList:
        afterFlagList.append(ele[1])
    #有‘的’存在的句子
    if len(afterList) > 0:
        pass

        #属性处理
        tmp_pList = []
        newList = nMerge2(afterList, ['n','v'])
        for ele in newList:
            if ele[1] == 'n':
                tmp_pList.append(ele[0])
    ##病理学/n	在/p	医学/n	中/f	的/uj	作用/v
        if 'p' in beforeFlagList:
            if beforeFlagList[0] != 'p' :
                #实体处理
                i = 0
                llen = len(beforeFlagList)
                newList = nMerge2(beforeList,['n','v'])#这里把动词和名词合并
                pflag = 0
                for ele in newList:
                    if pflag == 0:
                        if ele[1] == 'n':
                            tmpUnity = unity(ele[0])
                            for ele2 in tmp_pList:
                                tmpUnity.addProperty(ele2)
                            uList.append(tmpUnity)
                        if ele[1] == 'p':
                            pflag = 1
                            continue
                    if pflag == 1:
                        if ele[1] == 'n':
                            uList.append(unity(ele[0]))
        else:
            newList = nMerge2(beforeList,['n','v'])
            for ele in newList:
                if ele[1] == 'n':
                    tmpUnity = unity(ele[0])
                    for ele2 in tmp_pList:
                        tmpUnity.addProperty(ele2)
                    uList.append(tmpUnity)

    #没有属性的标题,
    else:
        newList = nMerge2(beforeList,['n','v'])
        for ele in newList:
            if ele[1] == 'n' and len(ele[0]) > 2:
                tmpUnity = unity(ele[0])
                #print(ele[0])
                uList.append(tmpUnity)





    return uList


#转为dict
def list2dict(uList):
    resdict = {}
    for ele in uList:
        if not resdict.__contains__(ele.name):
            resdict[ele.name] = ele.proList
        else:
            for ele2 in ele.proList:
                resdict[ele.name].append(ele2)
    return resdict

#通过分词之后的词性模式进行实体抽取
def fenci_extract(infile,outfile):
    #jieba.load_userdict(r'dict\blx.txt')#自定义词典，可以忽略
    resList = []
    with open(infile,'r',encoding='utf-8') as ifh:
        for line in ifh.readlines():
            if '营养不良性萎缩' in line:
                q=1
            seg = posseg.cut(line.strip())#分词
            nList = nMerge(seg,['n','vn','t','l','nr','ng','nz','d','b','i','g'])#进行相邻名词合并
            uList = extractFromTitle(nList)#这两步是根据规则提取实体
            for ele in uList:
                resList.append(ele)
    uDict = list2dict(resList)
    resList = []
    for ele in uDict:
        unt = unity(ele)
        for ele2 in uDict[ele]:
            unt.addProperty(ele2)
        resList.append(unt)


    with open(outfile,'w',encoding='utf-8') as ofh:
        for ele in resList:
            if len(ele.name) == 1:
                continue
            ofh.write(ele.name + ' ')
            if len(ele.proList) > 0:
                ofh.write('(')
                for ele2 in ele.proList:
                    ofh.write(ele2+' ')
                ofh.write(')')
            ofh.write('\n')

    #generate_dict(resList,r'..\实体提取\dict.txt')
    return resList




#jiba_split(r'txt\病理学目录.txt',r'病理学目录_fenci.txt')
fenci_extract(r'..\医学相关\目录结构\病理学目录.txt',r'..\实体提取\unitylist.txt')
