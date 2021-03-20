import re
import jieba.posseg as posseg
import jieba
from function import *

def eliminate(uList,sentences):
    '''输入一个实体列表和文档，利用文档淘汰可能不是实体的部分并输出'''
    reslist=[]
    elilist=[]
    for ele in uList:
        if ele.name.startswith('的'):
            ele.name=ele.name[1:]
    #tmplist=uList.copy()
    #for ele in tmplist:
    #    if re.search(r'[性期]$',ele.name)!=None and len(ele.name)<4:
    #        print(ele.name)
    #        uList.remove(ele)
    for ele in uList:
        if len(ele.name)>1:
            sum=0
            #with open(infile, 'r', encoding='utf-8') as ifh:
            for line in sentences:
                sum += len(re.findall(str(ele.name),line))
            if sum>1:
                reslist.append(ele)
            else:
                elilist.append(ele)
                print(ele.name)
                pass
        else:
            elilist.append(ele)

    PrintuList(elilist)
    return reslist
def ulist_Addunity(uList, unity):
    '''将一个实体添加到uList里，同时合并属性（若已有）'''
    flag=0
    for ele in uList:
        if ele.name==unity.name:
            for pro in unity.proList:
                if pro not in ele.proList:
                    ele.proList.append(pro)
            flag=1
    if flag==0:
        uList.append(unity)
    if re.search('性肿大',unity.name)!=None:
        q=1
    return uList

def regular_extract(sentences,uList,infile):
    # cont_list是输入的要处理的句子列表，返回一个提取出的实体列表(元素是实体名)
    def extractFromContList(cont_list):
        uList = []
        # 中文（英文）
        reMode = re.compile(r'([\u4e00-\u9fa5]+)[（\(][a-zA-Z]+[a-zA-z\s]*[）\)]')
        for line in cont_list:
            a = reMode.findall(line)
            for ele in a:
                res = ''
                #print(line)
                seg1 = posseg.cut(ele)  # 借助分词来讲实体提取出来
                seg = []
                for ele in seg1:
                    seg.append(ele)
                slen = len(seg)
                i = slen - 1
                text = ''
                nlist = ['n', 'ng', 'nv', 'l', 'a', 'nz', 'h', 'nr', 'nz']
                text = seg[slen - 1].word
                i = i - 1
                if len(text) == 1 and i >= 0:  # 如果只有一个字，那么前面的一个分词基本也是实体一部分
                    text = seg[i].word + text
                    i = i - 1
                while (i >= 0 and seg[i].flag in nlist):
                    text = seg[i].word + text
                    i = i - 1
                if len(text) > 1:
                    uList.append(text)
        # XX的XX
        reslist = []
        for ele in uList:
            reslist = ulist_Addunity(reslist, unity(ele))

        return reslist
    def reExtract_chengwei(resList,sentence):
        '''称为减压后充血。'''
        matchobj = re.search(r'对?称之?为?([\u4e00-\u9fa5]+)', sentence)
        if matchobj != None and matchobj.group(1) != '为' and len(matchobj.group(1)) > 1 and matchobj.group()[0] != '对':
            matchobj1 = re.search(r'(.*)或(.*)', matchobj.group(1))
            if matchobj1 == None:
                ulist_Addunity(resList, unity(matchobj.group(1)))
            else:
                ulist_Addunity(resList, unity(matchobj1.group(1)))
                ulist_Addunity(resList, unity(matchobj1.group(2)))
        return resList
    def reExtract_fenwei(resList,sentence):
        '''骨折通常可分为外伤性骨折和病理性骨折两大类//，又可分为酶解性脂肪坏死和外伤性脂肪坏死'''
        matchobj = re.search(r'分为([\u4e00-\u9fa5]+)[和与]([\u4e00-\u9fa5]+)', sentence)
        if matchobj != None:
            matchobj1 = re.search(r'分为(.*)[和与](.*)两', matchobj.group())
            if matchobj1 == None:
                ulist_Addunity(resList, unity(matchobj.group(1)))
                ulist_Addunity(resList, unity(matchobj.group(2)))
            else:
                ulist_Addunity(resList, unity(matchobj1.group(1)))
                ulist_Addunity(resList, unity(matchobj1.group(2)))
        return resList
    def reExtract_ming(resList,sentence):
        matchobj = re.search(r'[又故别]名([\u4e00-\u9fa5]+)', sentence)
        if matchobj != None:
            ulist_Addunity(resList, unity(matchobj.group(1)))
        return resList
    def Extract_dunhao(resList,line):

        '''利用顿号提取实体'''
        matchobj = re.search(r'[\u4e00-\u9fa5]+、[\u4e00-\u9fa5、]+', line)
        if matchobj != None:
            #print(line)
            unitylist = matchobj.group().split('、')
            '''将首部‘的’之前，尾部‘的’之后的字符去掉'''
            for i in range(len(unitylist[0]) - 1, -1, -1):
                if unitylist[0][i] == '的':
                    unitylist[0] = unitylist[0][i + 1:]
                    break
            for i in range(len(unitylist[-1])):
                if unitylist[-1][i] == '的':
                    unitylist[-1] = unitylist[-1][:i]
                    break

            '''对于实体列表非两端字符串，若长度大于10的字符串且中间含有‘的’，就把它分成子实体列表；否则，若中间含有c，就把它分成子实体列表'''
            '''a、b的c、d分成a、b和c、d'''
            corlist = []
            if len(unitylist) > 2:
                '''flag记录是否有拆分，flag_de记录是否因'的'拆分'''
                flag, flag_de = 0, 0
                tmpstr = unitylist[0]
                last_i = 0
                for i in range(1, len(unitylist) - 1):
                    seg = posseg.cut(unitylist[i].strip())
                    poslist = gen2list(seg)
                    if len(unitylist[i]) > 10:
                        for j in range(len(poslist)):
                            if poslist[j][1] == 'uj':
                                flag, flag_de = 1, 1
                                tmplist = unitylist[last_i + 1:i]
                                tmplist.insert(0, poslist2str(tmpstr))
                                tmplist.append(poslist2str(poslist[:j]))
                                corlist.append(tmplist)
                                tmpstr = poslist2str(poslist[j + 1:])
                                last_i = i
                                break
                    if flag_de == 0:
                        for j in range(len(poslist)):
                            if poslist[j][1] == 'c':
                                flag = 1
                                tmplist = unitylist[last_i + 1:i]
                                tmplist.insert(0, poslist2str(tmpstr))
                                tmplist.append(poslist2str(poslist[:j]))
                                corlist.append(tmplist)
                                tmpstr = poslist2str(poslist[j + 1:])
                                last_i = i
                                break
                if flag == 1:
                    tmplist = unitylist[last_i + 1:]
                    tmplist.insert(0, poslist2str(tmpstr))
                    corlist.append(tmplist)
            if len(corlist) == 0:
                corlist.append(unitylist)

            '''对每个子实体列表'''
            for elelist in corlist:
                tmplist = elelist

                '''处理开头，从第一个顿号开始往前提取到n'''
                seg = posseg.cut(tmplist[0].strip())
                poslist = gen2list(seg)
                poslist = listmerge(poslist, ['n', 'a', 'l', 'nr', 'ng', 'nz', 'ns'])
                # poslist_Show(poslist)
                for i in range(len(poslist) - 1, -1, -1):
                    if poslist[i][1] == 'n':
                        tmplist[0] = poslist2str(poslist[i:])
                        break
                    if i == 0:
                        pass

                '''处理结尾，如果结尾有c，则将c前当作一个实体，c后提取到n作为一个实体；如果结尾没有c，则提取到n'''
                seg = posseg.cut(tmplist[-1].strip())
                poslist = gen2list(seg)
                poslist = listmerge(poslist, ['n', 'a', 'l', 'nr', 'ng', 'nz', 'ns'])
                flag = 0
                for i in range(len(poslist)):
                    if poslist[i][1] == 'c':
                        flag = 1
                        tmplist[-1] = poslist2str(poslist[:i])
                        for j in range(i, len(poslist)):
                            if poslist[j][1] == 'n':
                                tmplist.append(poslist2str(poslist[i + 1:j + 1]))
                                break
                        break
                if flag == 0:
                    for i in range(len(poslist)):
                        if poslist[i][1] == 'n':
                            tmplist[-1] = (poslist2str(poslist[:i + 1]))
                            break

                # print(unitylist)
                '''用已有实体和备选实体匹配，若有匹配到，则输出整个子实体列表'''
                flag = 0
                for str in tmplist:
                    for ele in uList:
                        if str == ele.name:
                            flag = 1
                            # tmpentity=ele.name
                if flag == 1:
                    for ele in tmplist:
                        if ele != '':
                            ulist_Addunity(resList, unity(ele))
        return resList

    resList=[]
    resList = extractFromContList(sentences)

    for sentence in sentences:
        if '小时到几天，称为迟发' in sentence:
            q=1
        resList=reExtract_chengwei(resList,sentence)
        resList = reExtract_fenwei(resList, sentence)
        resList = reExtract_ming(resList, sentence)
        resList=Extract_dunhao(resList,sentence)
    resList = eliminate(resList, sentences)
    #PrintuList(resList)

    return resList


def passage_extract(infile,outlist,inuList='',indict=''):
    '''输入需提取的文档infile 提取实体后将列表输出到outlist 可以选择输入已知实体列表inuList和已知字典indict'''
    '''运行后字典会被更新'''
    if indict=='':
        indict=os.path.dirname(outlist)+'\\'+'dict.txt'
    if inuList!='':
        uList = ulist_Readfromtxt(inuList)
        ulisttxt_Writefromulist(uList, outlist)
        dictfile_Writefromulist(uList, indict)
    else:
        uList=[]
    sentences=sentence_Readfromdoc(infile)
    for i in range(1):
        jieba.load_userdict(indict)
        resList=regular_extract(sentences,uList,infile)
        ulisttxt_Writefromulist(resList, outlist)
        uList=ulist_Readfromtxt(outlist)
        dictfile_Writefromulist(resList, indict)


if __name__ == '__main__':
    passage_extract(r'..\医学相关\医学相关docx\病理学.docx',r'..\实体提取\unitylist.txt', r'..\实体提取\ulist_known.txt')
    #eliminate2(r'..\医学相关\实体\unity.txt',r'..\医学相关\实体\my_unity.txt')
    #test(r'..\医学相关\医学相关docx\病理学.docx',r'..\实体提取\ulist.txt')
    #eliminate3(r'..\实体提取\unitylist.txt',r'..\医学相关\医学相关docx\病理学.docx',r'..\实体提取\dict.txt')
    #eliminate4(r'..\实体提取\unitylist.txt')
