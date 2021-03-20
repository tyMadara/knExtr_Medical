#从三元组中提取实体
import csv
from function import *
import pickle
from DepTree import *

'''从给定关系中提取左右实体'''


def Extract_universal(text,dict,rule=''):
        '''通用提取，输入一段文本，输出一个可能为实体的列表'''
        '''包含‘因为’提取，‘最后一个实体’提取，‘是’提取，括号提取，‘称’提取，‘引起’提取，‘的’提取，‘可以’提取，‘最开头的实体’提取，‘最近的实体’提取’’'''
        def Extract_yinwen(text,rule):
            resList=[]
            rule+='英文'
            if text!='' and re.search(r'[\u4e00-\u9fa5]',text)==None:
                match=re.search(r'^([^（(]*)[（(]([^)）]*)[^)）]',text)
                if match!=None and re.search(r'[^\w ]',match.group(1))==None and re.search(r'[^\w ]',match.group(2))==None:
                    resList.append(unity(match.group(1),rule))
                    resList.append(unity(match.group(2),rule))
                else:
                    resList.append(unity(text,rule))
            return resList
        def Extract_zuihou(text, dict,rule):
            '''找最后的实体'''
            resList = []
            rule+='最后的实体'
            uList_list = greedmatch([text], dict)
            if len(uList_list[0]) > 0:
                resList.append(unity(uList_list[0][-1].name,rule))
            return resList

        def Extract_shi(text,resList,rule):
            '''如果某部分存在（XXX）是XXXX的结构,且'是'前不是'不':
        		如果后面比前面长：
			        如果'是'后有':'，取后面的作为实体
			        如果括号里没有东西，就从按逗号分的之前的一句中找最后的实体(flag=1)
			        若之前不包含'其'，将是之前的XXX作为实体，然后如果'是'之前的部分包含实体，把该实体也加上
		        否则flag=2
            如果flag=2：
	            取'是'后面的内容作实体'''
            #resList = []
            rule+='是'
            sign=0
            matchobj = re.search(r'(.*)是(.+)', text)
            if matchobj != None and matchobj.group(1).endswith('不')==False:
                if len(matchobj.group(2))>len(matchobj.group(1)):
                    if matchobj.group(2)[0] in ['：',':']:
                        resList.append(unity(matchobj.group(2)[1:],rule))
                    elif matchobj.group(1).strip() == '' :
                        sign=1
                        #resList = None
                    else:
                        text1=matchobj.group(1).strip()
                        matchobj1=re.search(r'[:：](.*)', text1)
                        if matchobj1!=None:
                            resList.append(unity(matchobj1.group(1),rule))
                        elif re.search(r'[其该此]',text1)==None: #and re.search(r'[\u4e00-\u9fa5]',text1)!=None:
                            resList.append(unity(text1,rule))
                            uList_list=greedmatch([text1],dict)
                            for ele in uList_list[0]:
                                resList.append(unity(ele.name,rule))
                else:
                    resList.append(unity(matchobj.group(2),rule))
                    sign=2
            #return resList
            return sign

        def Extract_kuohao(text, dict,rule):
            def process(text1):
                '''取最长的，'（'之前的，紧靠‘（’的，且在实体列表里的实体
			若取不到，用分词处理，名词合并后从最后的词开始直到名词作为实体'''
                resList=[]
                s=''
                flag=1
                tmpi=len(text1)
                while flag==1:
                    for i in range(tmpi):
                        if text1[i:tmpi] in dict:
                            s=text1[i:tmpi]+s
                            tmpi=i
                            flag=1
                            if tmpi==0:
                                flag=0
                            break
                        else:
                            flag=0
                if s!='':
                    resList.append(unity(s,rule))
                if resList == []:
                    seg = posseg.cut(text1)
                    posList = gen2list(seg)
                    posList=listmerge(posList,['n', 'vn', 't', 'l', 'nr', 'ng', 'nz', 'd', 'b', 'i', 'g','eng','q'])
                    s=''
                    for i in range(len(posList)-1,-1,-1):
                        s=posList[i][0]+s
                        if posList[i][1] in ['n'] and i!=len(posList)-1:
                            break
                    resList.append(unity(s,rule))
                return resList

            '''以'（'结尾的，用分词处理'''
            resList = []
            rule+='括号'
            Kuohao=re.findall(r'[^\)）]*[\(（][^\)）]*[\)）]',text)
            for kuohao in Kuohao:
                matchobj=re.search(r'([^\)）]*)[\(（]([^\)）]*)[\)）]',kuohao)
                if len(re.findall(r'[a-z]',matchobj.group(2)))>3:
                    text1=matchobj.group(1)
                    if text1!='':
                        if text1[-1] in ['》', '\"','’','”']:
                            matchobj1=re.search(r'《(.*)》$',text1)
                            if matchobj1==None:
                                matchobj1 = re.search(r'‘(.*)’$', text1)
                            if matchobj1 == None:
                                matchobj1 = re.search(r'\"(.*)\"$', text1)
                            if matchobj1!=None:
                                resList.append(unity(matchobj1.group(1),rule))
                        elif '\u4e00' <= matchobj.group(1)[-1] <= '\u9fff':
                            for ele in process(text1):
                                resList.append(ele)
                else:
                    matchobj = re.search(r'(.*)[\(（]', text)
                    if matchobj!=None:
                        text1=matchobj.group(1)
                        if text1!='':
                            if text1[-1] in ['》', '\"','’','”']:
                                matchobj1=re.search(r'《(.*)》$',text1)
                                if matchobj1==None:
                                    matchobj1 = re.search(r'‘(.*)’$', text1)
                                if matchobj1 == None:
                                    matchobj1 = re.search(r'\"(.*)\"$', text1)
                                if matchobj1!=None:
                                    resList.append(unity(matchobj1.group(1),rule))
                            else:
                                resList=process(text1)

            return resList

        def Extract_cheng(text,rule):
            '''	如果某句中存在称xxx，称之？为xxx这种的，将XXX作为实体'''
            resList = []
            rule+='称'
            matchobj = re.search(r'称[其之]?[为作]([\u4e00-\u9fa5a-zA-Z \-‘’\"“”]+)', text)
            if matchobj != None:
                resList.append(unity(matchobj.group(1),rule))
            else:
                matchobj = re.search(r'(.*)[又简]称([\u4e00-\u9fa5a-zA-Z \-]+)', text)
                if matchobj != None:
                    uList_list=greedmatch([matchobj.group(1)],dict)
                    if len(uList_list[0])>0 and matchobj.group(1).endswith(uList_list[0][-1].name):
                            resList.append(unity(uList_list[0][-1].name,rule))
                    else:
                        resList.append(unity(matchobj.group(2),rule))
            return resList

        def Extract_yinqi(text,rule):
            rule+='引起'
            matchobj=re.search(r'(由.*(引起.*))',text)
            if matchobj!=None:
                resList.append(unity(matchobj.group(1),rule))
                resList.append(unity(matchobj.group(2),rule))

            return resList

        def Extract_de(text,dict,rule):
            def process(text):
                resList=[]
                s=''
                flag=1
                tmpi=len(text)
                while flag==1:
                    for i in range(tmpi):
                        if text[i:tmpi] in dict:
                            s=text[i:tmpi]+s
                            tmpi=i
                            flag=1
                            if tmpi==0:
                                flag=0
                            break
                        else:
                            flag=0
                resList.append(unity(s,rule))
                return s
            resList=[]
            rule+='的'
            matchobj=re.search(r'(.+)(的[\u4e00-\u9fa5]*)',text)
            if matchobj!=None:
                s=process(matchobj.group(1))
                if s!='':
                    resList.append(unity(process(matchobj.group(1))+matchobj.group(2),rule))
            return resList
        def Extract_keyi(text,dict,rule):
            resList=[]
            rule+='可以'
            wordset=['可以']
            for word in wordset:
                matchobj=re.search(r'(.+)'+word,text)
                if matchobj!=None:
                    text1=matchobj.group(1)
                    if text1[-1]=='也':
                        text1=text1[:-1]
                    for i in range(len(text1)):
                        if text1[i:] in dict:
                            resList.append(unity(text1[i:],rule))
                            break
            return resList
        def Split(text):
            '''将文本按逗号和分号分开，除去在括号内的情况'''
            def sub(match):
                '''‘\u5f41’无意义汉字，用来防止括号被‘，’分割'''
                return match.group(1) + '\u5f41' + match.group(3)
            text = re.sub(r'([（\(][^\)）]*?)([,，])([^（\(]*?[\)）])', sub, text)
            textlist = re.split(r'[,，;；]', text)
            for i in range(len(textlist)):
                textlist[i] = re.sub(r'\u5f41', ',', textlist[i])
            return textlist
        def Extract_zuijin(text,dict,rule):
            resList=[]
            rule+='离关系词最近的实体'
            uList_list = greedmatch([text], dict)
            if len(uList_list[0])>0:
                for ele in uList_list[0]:
                    if len(ele.name)>len(text)/2:
                        resList.append(unity(ele.name,rule))
                        #for word in pattern_daici:
                        #    if re.search(word,text)!=None:
                        #        print(text,ele.name)
                if resList==[]:
                    if text.endswith(uList_list[0][-1].name):
                        resList.append(unity(uList_list[0][-1].name,rule))
                        #for word in pattern_daici:
                        #    if re.search(word,text)!=None:
                        #        print(text,ele.name)
                    elif len(text)>1 and ('\u4e00'>text[-1] or text[-1]>'\u9fa5') and text[:-1].endswith(uList_list[0][-1].name):
                        resList.append(unity(uList_list[0][-1].name, rule))
            return resList
        def Extract_zuiqian(text,dict,rule):
            resList=[]
            rule+='最前的实体'
            uList_list=greedmatch([text],dict)
            if len(uList_list[0]) > 0:
                if text.startswith(uList_list[0][0].name):
                    resList.append(unity(uList_list[0][0].name,rule))
            return resList

        resList=[]
        textlist=Split(text)

        resList=Extract_yinwen(text,rule)
        if resList==[]:
            resList=Extract_zuijin(textlist[-1],dict,rule)
        if resList==[]:
            resList=Extract_zuiqian(textlist[0],dict,rule)
        sign_shi=0
        tmpList_shi=[]
        if resList==[]:
            for i in range(len(textlist) - 1, -1, -1):
                resList = Extract_cheng(textlist[i],rule)
                if resList == []:
                    resList = Extract_kuohao(textlist[i], dict,rule)
                if resList == []:
                    sign=Extract_shi(textlist[i],resList,rule)
                    if sign==2:
                        tmpList_shi=resList
                        resList=[]
                    if sign == 1:
                        if i != 0:
                            resList = Extract_zuihou(textlist[i - 1], dict,rule)
                        else:
                            resList = []
                    if sign!=0:
                        sign_shi=sign
                if resList != []:
                    break
        if resList==[] and sign_shi==2:
            resList=tmpList_shi
        if resList == []:
            resList=Extract_de(textlist[-1],dict,rule)
        if resList==[]:
            for i in range(len(textlist) - 1, -1, -1):
                resList = Extract_yinqi(textlist[i],rule)
                if resList!=[]:
                    break
        if resList==[]:
            for i in range(len(textlist) - 1, -1, -1):
                resList=Extract_keyi(textlist[i],dict,rule)
                if resList!=[]:
                    break
        return resList
'''从关系中提取左右实体'''

def lunity(infile,outfile,ufile):
    def Extract_universal(text,dict):
        '''通用提取，输入一段文本，输出一个可能为实体的列表'''
        '''包含‘因为’提取，‘最后一个实体’提取，‘是’提取，括号提取，‘称’提取，‘引起’提取，‘的’提取，‘可以’提取，‘最开头的实体’提取，‘最近的实体’提取’’'''
        def Extract_yinwen(text):
            resList=[]
            rule='英文'
            if text!='' and re.search(r'[\u4e00-\u9fa5]',text)==None:
                match=re.search(r'^([^（(]*)[（(]([^)）]*)[^)）]',text)
                if match!=None and re.search(r'[^\w ]',match.group(1))==None and re.search(r'[^\w ]',match.group(2))==None:
                    resList.append(unity(match.group(1),rule))
                    resList.append(unity(match.group(2),rule))
                else:
                    resList.append(unity(text,rule))
            return resList
        def Extract_zuihou(text, dict):
            '''找最后的实体'''
            resList = []
            rule='最后的实体'
            uList_list = greedmatch([text], dict)
            if len(uList_list[0]) > 0:
                resList.append(unity(uList_list[0][-1].name,rule))
            return resList

        def Extract_shi(text,resList):
            '''如果某部分存在（XXX）是XXXX的结构,且'是'前不是'不':
        		如果后面比前面长：
			        如果'是'后有':'，取后面的作为实体
			        如果括号里没有东西，就从按逗号分的之前的一句中找最后的实体(flag=1)
			        若之前不包含'其'，将是之前的XXX作为实体，然后如果'是'之前的部分包含实体，把该实体也加上
		        否则flag=2
            如果flag=2：
	            取'是'后面的内容作实体'''
            #resList = []
            rule='是'
            sign=0
            matchobj = re.search(r'(.*)是(.+)', text)
            if matchobj != None and matchobj.group(1).endswith('不')==False:
                if len(matchobj.group(2))>len(matchobj.group(1)):
                    if matchobj.group(2)[0] in ['：',':']:
                        resList.append(unity(matchobj.group(2)[1:],rule))
                    elif matchobj.group(1).strip() == '' :
                        sign=1
                        #resList = None
                    else:
                        text1=matchobj.group(1).strip()
                        matchobj1=re.search(r'[:：](.*)', text1)
                        if matchobj1!=None:
                            resList.append(unity(matchobj1.group(1),rule))
                        elif re.search(r'[其该此]',text1)==None: #and re.search(r'[\u4e00-\u9fa5]',text1)!=None:
                            resList.append(unity(text1,rule))
                            uList_list=greedmatch([text1],dict)
                            for ele in uList_list[0]:
                                resList.append(unity(ele.name,rule))
                else:
                    resList.append(unity(matchobj.group(2),rule))
                    sign=2
            #return resList
            return sign

        def Extract_kuohao(text, dict):
            def process(text1):
                '''取最长的，'（'之前的，紧靠‘（’的，且在实体列表里的实体
			若取不到，用分词处理，名词合并后从最后的词开始直到名词作为实体'''
                resList=[]
                s=''
                flag=1
                tmpi=len(text1)
                while flag==1:
                    for i in range(tmpi):
                        if text1[i:tmpi] in dict:
                            s=text1[i:tmpi]+s
                            tmpi=i
                            flag=1
                            if tmpi==0:
                                flag=0
                            break
                        else:
                            flag=0
                if s!='':
                    resList.append(unity(s,rule))
                if resList == []:
                    seg = posseg.cut(text1)
                    posList = gen2list(seg)
                    posList=listmerge(posList,['n', 'vn', 't', 'l', 'nr', 'ng', 'nz', 'd', 'b', 'i', 'g','eng','q'])
                    s=''
                    for i in range(len(posList)-1,-1,-1):
                        s=posList[i][0]+s
                        if posList[i][1] in ['n'] and i!=len(posList)-1:
                            break
                    resList.append(unity(s,rule))
                return resList

            '''以'（'结尾的，用分词处理'''
            resList = []
            rule='括号'
            Kuohao=re.findall(r'[^\)）]*[\(（][^\)）]*[\)）]',text)
            for kuohao in Kuohao:
                matchobj=re.search(r'([^\)）]*)[\(（]([^\)）]*)[\)）]',kuohao)
                if len(re.findall(r'[a-z]',matchobj.group(2)))>3:
                    text1=matchobj.group(1)
                    if text1!='':
                        if text1[-1] in ['》', '\"','’','”']:
                            matchobj1=re.search(r'《(.*)》$',text1)
                            if matchobj1==None:
                                matchobj1 = re.search(r'‘(.*)’$', text1)
                            if matchobj1 == None:
                                matchobj1 = re.search(r'\"(.*)\"$', text1)
                            if matchobj1!=None:
                                resList.append(unity(matchobj1.group(1),rule))
                        elif '\u4e00' <= matchobj.group(1)[-1] <= '\u9fff':
                            for ele in process(text1):
                                resList.append(ele)
                else:
                    matchobj = re.search(r'(.*)[\(（]', text)
                    if matchobj!=None:
                        text1=matchobj.group(1)
                        if text1!='':
                            if text1[-1] in ['》', '\"','’','”']:
                                matchobj1=re.search(r'《(.*)》$',text1)
                                if matchobj1==None:
                                    matchobj1 = re.search(r'‘(.*)’$', text1)
                                if matchobj1 == None:
                                    matchobj1 = re.search(r'\"(.*)\"$', text1)
                                if matchobj1!=None:
                                    resList.append(unity(matchobj1.group(1),rule))
                            else:
                                resList=process(text1)

            return resList

        def Extract_cheng(text):
            '''	如果某句中存在称xxx，称之？为xxx这种的，将XXX作为实体'''
            resList = []
            rule='称'
            matchobj = re.search(r'称[其之]?[为作]([\u4e00-\u9fa5a-zA-Z \-‘’\"“”]+)', text)
            if matchobj != None:
                resList.append(unity(matchobj.group(1),rule))
            else:
                matchobj = re.search(r'(.*)[又简]称([\u4e00-\u9fa5a-zA-Z \-]+)', text)
                if matchobj != None:
                    uList_list=greedmatch([matchobj.group(1)],dict)
                    if len(uList_list[0])>0 and matchobj.group(1).endswith(uList_list[0][-1].name):
                            resList.append(unity(uList_list[0][-1].name,rule))
                    else:
                        resList.append(unity(matchobj.group(2),rule))
            return resList

        def Extract_yinqi(text):
            rule='引起'
            matchobj=re.search(r'(由.*(引起.*))',text)
            if matchobj!=None:
                resList.append(unity(matchobj.group(1),rule))
                resList.append(unity(matchobj.group(2),rule))

            return resList

        def Extract_de(text,dict):
            def process(text):
                resList=[]
                s=''
                flag=1
                tmpi=len(text)
                while flag==1:
                    for i in range(tmpi):
                        if text[i:tmpi] in dict:
                            s=text[i:tmpi]+s
                            tmpi=i
                            flag=1
                            if tmpi==0:
                                flag=0
                            break
                        else:
                            flag=0
                resList.append(unity(s,rule))
                return s
            resList=[]
            rule='的'
            matchobj=re.search(r'(.+)(的[\u4e00-\u9fa5]*)',text)
            if matchobj!=None:
                s=process(matchobj.group(1))
                if s!='':
                    resList.append(unity(process(matchobj.group(1))+matchobj.group(2),rule))
            return resList
        def Extract_keyi(text,dict):
            resList=[]
            rule='可以'
            wordset=['可以']
            for word in wordset:
                matchobj=re.search(r'(.+)'+word,text)
                if matchobj!=None:
                    text1=matchobj.group(1)
                    if text1[-1]=='也':
                        text1=text1[:-1]
                    for i in range(len(text1)):
                        if text1[i:] in dict:
                            resList.append(unity(text1[i:],rule))
                            break
            return resList
        def Split(text):
            '''将文本按逗号和分号分开，除去在括号内的情况'''
            def sub(match):
                '''‘\u5f41’无意义汉字，用来防止括号被‘，’分割'''
                return match.group(1) + '\u5f41' + match.group(3)
            text = re.sub(r'([（\(][^\)）]*?)([,，])([^（\(]*?[\)）])', sub, text)
            textlist = re.split(r'[,，;；]', text)
            for i in range(len(textlist)):
                textlist[i] = re.sub(r'\u5f41', ',', textlist[i])
            return textlist
        def Extract_zuijin(text,dict):
            resList=[]
            rule='离关系词最近的实体'
            uList_list = greedmatch([text], dict)
            if len(uList_list[0])>0:
                for ele in uList_list[0]:
                    if len(ele.name)>len(text)/2:
                        resList.append(unity(ele.name,rule))
                        #for word in pattern_daici:
                        #    if re.search(word,text)!=None:
                        #        print(text,ele.name)
                if resList==[]:
                    if text.endswith(uList_list[0][-1].name):
                        resList.append(unity(uList_list[0][-1].name,rule))
                        #for word in pattern_daici:
                        #    if re.search(word,text)!=None:
                        #        print(text,ele.name)
                    elif len(text)>1 and ('\u4e00'>text[-1] or text[-1]>'\u9fa5') and text[:-1].endswith(uList_list[0][-1].name):
                        resList.append(unity(uList_list[0][-1].name, rule))
            return resList
        def Extract_zuiqian(text,dict):
            resList=[]
            rule='最前的实体'
            uList_list=greedmatch([text],dict)
            if len(uList_list[0]) > 0:
                if text.startswith(uList_list[0][0].name):
                    resList.append(unity(uList_list[0][0].name,rule))
            return resList

        resList=[]
        textlist=Split(text)

        resList=Extract_yinwen(text)
        if resList==[]:
            resList=Extract_zuijin(textlist[-1],dict)
        if resList==[]:
            resList=Extract_zuiqian(textlist[0],dict)
        sign_shi=0
        tmpList_shi=[]
        if resList==[]:
            for i in range(len(textlist) - 1, -1, -1):
                resList = Extract_cheng(textlist[i])
                if resList == []:
                    resList = Extract_kuohao(textlist[i], dict)
                if resList == []:
                    sign=Extract_shi(textlist[i],resList)
                    if sign==2:
                        tmpList_shi=resList
                        resList=[]
                    if sign == 1:
                        if i != 0:
                            resList = Extract_zuihou(textlist[i - 1], dict)
                        else:
                            resList = []
                    if sign!=0:
                        sign_shi=sign
                if resList != []:
                    break
        if resList==[] and sign_shi==2:
            resList=tmpList_shi
        if resList == []:
            resList=Extract_de(textlist[-1],dict)
        if resList==[]:
            for i in range(len(textlist) - 1, -1, -1):
                resList = Extract_yinqi(textlist[i])
                if resList!=[]:
                    break
        if resList==[]:
            for i in range(len(textlist) - 1, -1, -1):
                resList=Extract_keyi(textlist[i],dict)
                if resList!=[]:
                    break
        return resList
    def Extract_gu(text):
        resList=[]
        rule='故'
        '''2.按逗号分：'''
        textlist = re.split(r'[,，；;]', text)
        '''2.2如果最后一部分如果含有‘故’：'''
        matchobj = re.search(r'故(.*)', textlist[-1])
        if matchobj != None:
            uList_list = greedmatch(textlist, dict)
            '''2.2.1如果最后一部分中含有实体（故字后面的部分），那么实体就是该实体；'''
            for ele in uList_list[-1]:
                if re.search(str(ele.name), matchobj.group(1)) != None:
                    resList.append(unity(ele.name,rule))
                    '''感觉效果不太好'''
            '''否则向前搜索，如果有称(之)?为XXX;称XXX,那么XXX作为实体，'''
            if resList == []:
                for i in range(len(textlist) - 2, -1, -1):
                    matchobj1 = re.search(r'称[之其]?为(.+)', textlist[i])
                    if matchobj1 != None:
                        resList.append(unity(matchobj1.group(1),rule))
                        break
                    matchobj1 = re.search(r'[又简]称(.+)', textlist[i])
                    if matchobj1 != None:
                        resList.append(unity(matchobj1.group(1),rule))
                        break
            '''如果含结构XXX是XXXX，则在是之前的部分寻找实体（在实体列表中），'''
            if resList == []:
                for i in range(len(textlist) - 2, -1, -1):
                    matchobj1 = re.search(r'(.+)是(.+)', textlist[i])
                    if matchobj1 != None:
                        for ele in uList_list[i]:
                            if re.search(str(ele.name), matchobj.group(1)) != None:
                                resList.append(unity(ele.name,rule))
                    break
        return resList
    def Extract_benbing(text):
        resList=[]
        rule='本病'
        if re.search(r'本病', text) != None:
            if re.search(r'[，,]', line[0]) == None and len(line[0]) <= 15:
                resList.append(unity(line[0], rule))
            if resList == []:
                uList_list = greedmatch([line[0]], dict)
                if len(uList_list[0]) > 0:
                    resList.append(unity(uList_list[0][-1].name, rule))
        return resList
    def Extract_zuihou(text, dict):
        '''找最后的实体'''
        resList = []
        rule = '最后的实体'
        uList_list = greedmatch([text], dict)
        if len(uList_list[0]) > 0:
            resList.append(unity(uList_list[0][-1].name, rule))
        return resList
    def Extract_ru(text):
        resList=[]
        rule='如'
        matchobj = re.search(r'如([\u4e00-\u9fa5a-zA-Z \-]+)', text)
        if matchobj != None:
            resList.append(unity(matchobj.group(1), '如'))
        return resList
    def Process_resList():
        tmpList=[]
        for ele in resList:
            list=re.split(r'[和或、]',ele.name)
            for text in list:
                tmpList.append(unity(text,ele.rule))
        return tmpList
    def Process_intext(line):
        line[0] = re.sub(r'【.*】', '', line[0]).strip()
        line[1] = re.sub(r'\u3000', '', line[1]).strip()
        for pattern in Pattern_ignore:
            if re.search(pattern, line[1]) != None:
                line[1] = re.sub(pattern, '', line[1]).strip()
                break
            if re.search(pattern, line[0]) != None:
                line[0] = re.sub(pattern, '', line[0]).strip()
                break
        for word in word_ignore:
            line[1] = re.sub(word, '是', line[1]).strip()
            line[0] = re.sub(word, '是', line[0]).strip()

        if len(line[1]) > 0 and line[1][-1] in ['，', ',']:
            line[1] = line[1][:-1]

    Pattern_ignore = ['^【.*】', '^[①②③④⑤⑥⑦⑧⑨⑩]', '^（[a-z]）', r'^（\d+）', r'^\d+）', r'^\d+[\.．]', r'^（[一二三四五六七八九十]+）',
                   r'^[一二三四五六七八九十]+、']
    word_ignore = ['尤其是', '多数学者认为是', '则是', '这是', '如果是', '主要是']
    word_fuci=['可能']
    pattern_daici = ['上述', '本病', '其[^实中]', '[该它]','[^因]此']

    with open(infile, 'r', encoding='utf-8') as ifh:
        ofh = open(outfile, 'w', encoding='utf-8-sig', newline='')
        writer = csv.writer(ofh)
        lines = csv.reader(ifh)
        dict = dict_readformuList(ufile)

        for line in lines:
            if len(line)<2:
                break
            #matchobj = re.search(r'硬膜下水瘤，是指硬膜下', line[0])
            #if matchobj == None:
            #    continue

            Process_intext(line)
            print(line[1])
            resList = []

            text=line[1]
            if resList==[]:
                textlist = re.split(r'[,，；;]', text)
                matchobj = re.search(r'故(.*)', textlist[-1])
                if matchobj != None:
                    resList=Extract_gu(text)
                    '''如果上述情况均不符合，就将前句按，分开进行上述判断，'''
                    if resList==[]:
                        text=line[0]
                        textlist = re.split(r'[,，；;]', text)
                        matchobj = re.search(r'故(.*)', textlist[-1])
                        if matchobj != None:
                            resList=Extract_gu(text)
                    '''如果再均不符合，就将前句中含有的最后一个实体作为实体'''
                    if resList==[]:
                        resList=Extract_zuihou(line[0],dict)
                        #uList_list = greedmatch([line[0]], dict)
                        #if len(uList_list[0])>0:
                        #    resList.append(unity(uList_list[0][-1].name,'故'))
                tmpList=[]
                for ele in resList:
                    if len(ele.name)<=10:
                        tmpList.append(ele)
                resList=tmpList

            text=line[1]
            if resList==[]:
                resList=Extract_benbing(text)
            #if re.search(r'本病',text)!=None:
            #    if re.search(r'[，,]', line[0]) == None and len(line[0]) <= 15:
            #        resList.append(unity(line[0],'本病'))
            #    if resList == []:
            #        uList_list = greedmatch([line[0]], dict)
            #        if len(uList_list[0]) > 0:
            #            resList.append(unity(uList_list[0][-1].name,'本病'))
            if resList==[]:
                resList=Extract_universal(text)
            if resList==[]:
                matchobj=re.search(r'(.*)[其本该此它]',text)
                if matchobj!=None and matchobj.group(1)!='':
                    resList=Extract_universal(matchobj.group(1),dict)
                if resList==[]:
                    text=line[0]
                    resList=Extract_universal(text,dict)
                if resList == []:
                     resList = Extract_zuihou(line[0], dict)
                        #uList_list = greedmatch([line[0]], dict)
                        #if len(uList_list[0]) > 0:
                        #    resList.append(unity(uList_list[0][-1].name,'前句'))
            if resList==[]:
                resList=Extract_ru(line[1])
                #matchobj=re.search(r'如([\u4e00-\u9fa5a-zA-Z \-]+)',line[1])
                #if matchobj!=None:
                #    resList.append(unity(matchobj.group(1),'如'))
            if resList==[]:
                resList = Extract_zuihou(line[1], dict)
                #uList_list=greedmatch([line[1]],dict)
                #if len(uList_list[0])>0:
                #    resList.append(unity(uList_list[0][-1].name,'最后'))

            for i in range(len(resList)):
                for pattern in Pattern_ignore:
                    resList[i] = unity(re.sub(pattern, '', resList[i].name).strip(),resList[i].rule)
            resList=Process_resList()

            s = ''
            for ele in resList:
                s += ele.name +'('+ele.rule+ ') '
            line.insert(2, s)

            s = '('
            u = greedmatch([line[0]], dict)
            for ele in u:
                for ele2 in ele:
                    s += ele2.name + ' '
            s += ')('
            u = greedmatch([line[1]], dict)
            for ele in u:
                for ele2 in ele:
                    s += ele2.name + ' '
            s += ')'
            line.insert(3,s)

            s = '('
            u = greedmatch([line[5]], dict)
            for ele in u:
                for ele2 in ele:
                    s += ele2.name + ' '
            s += ')'
            line.insert(5,s)

            writer.writerow(line)
def runity(infile,outfile,ufile):
    with open(infile, 'r', encoding='utf-8') as ifh:
        ofh = open(outfile, 'w', encoding='utf-8-sig', newline='')
        writer = csv.writer(ofh)
        lines = csv.reader(ifh)
        dict = dict_readformuList(ufile)
        for line in lines:
            #matchobj = re.search(r'休克治疗指南', line[1])
            #if matchobj == None:
            #    continue
            text=line[3].strip()
            resList=[]
            if len(text)>0:
                if text[0]=='为':
                    text=text[1:]
                if text[-1]=='等':
                    text=text[:-1]
                matchobj=re.search(r'(^[^（\(]+)[）\)].*',text)
                if matchobj!=None:
                    text=matchobj.group(1)
                resList=re.split(r'[或、和]',text)
            s=''
            for ele in resList:
                s+=ele+' '
            line.insert(4,s)
            writer.writerow(line)
def runity_chengwei(infile,outfile,ufile):
    with open(infile, 'r', encoding='utf-8') as ifh:
        ofh = open(outfile, 'w', encoding='utf-8-sig', newline='')
        writer = csv.writer(ofh)
        lines = csv.reader(ifh)
        dict = dict_readformuList(ufile)
        ignore_word = ['是', '其为']
        for line in lines:
            #matchobj = re.search(r'模式（damage associate', line[3])
            #if matchobj == None:
            #   continue

            text=line[3]
            text=text.strip()
            for s in ignore_word:
                if text.startswith(s):
                    text=text[len(s):]
            #textList=re.split(r'，',text)
            #text = textList[0].strip()

            #print(text)
            resList = []
            if resList==[]:
                matchobj=re.search(r'^[\"“‘]([^\"”’]*)[\"”’]([\u4e00-\u9fa5]*)',text)
                if matchobj!=None:
                    #print(text)
                    if matchobj.group(2)=='':
                        resList.append(matchobj.group(1))
                    else:
                        resList.append('“'+matchobj.group(1)+'”'+matchobj.group(2))
                else:
                    print(text)
            if resList==[]:
                #matchobj=re.search(r'^[\u4e00-\u9fa5a-zA-z \-]+',text)
                matchobj = re.search(r'^([^;；。,，）)—]*.)',text)
                if matchobj!=None:

                    if matchobj.group(1)[-1] in ['）',')'] and re.search(r'[(（]',matchobj.group(1))!=None:
                        #print(text)
                        matchobj1=re.search(r'^[^;；。,，—]*[(（][^)）]*[)）][^;；。,，—]*', text)
                        if matchobj1!=None:
                            resList.append(matchobj1.group())
                    elif matchobj.group(1)[-1] in ['，',','] and re.search(r'[(（]',matchobj.group(1))!=None:
                        matchobj1 = re.search(r'^[^;；。,，—]*[(（][^)），,]*[,，][^)）]*[)）][^;；。,，—]*', text)
                        if matchobj1!=None:
                            resList.append(matchobj1.group())
                    else:
                        if matchobj.group(1)[-1] in [';','；',',','，','。',')','）','—']:
                            resList.append(matchobj.group()[:-1])
                        else:
                           resList.append(matchobj.group())


            tmpList=[]
            for ele in resList:
                tmpList.append(re.sub(r'[(（][^)）]*[)）]','',ele))
            resList=tmpList

            tmpList=[]
            for ele in resList:
                tmpList.extend(re.split(r'[、或和]',ele))
            resList=tmpList

            s=''
            for ele in resList:
                s+=ele+' '
            line.insert(4,s)
            writer.writerow(line)
def lunity_chengwei(infile,outfile,ufile):
    def Process_lianjie(text1,text2):
        word_lianjie = ['又', '常', '多', '也','统','亦']
        for word in word_lianjie:
            if text1.endswith(word):
                text2=word+text2
                text1=text1[:-1]
        return text1,text2
    def Process_input(text):
        text=text.strip()
        ignore_pattern = ['^【.*】', '^[①②③④⑤⑥⑦⑧⑨⑩]', '^（[a-z]）', r'^（\d+）', r'^\d+）', r'^\d+[\.．]', r'^（[一二三四五六七八九十]+）',
                       r'^[一二三四五六七八九十]+、',r'\u3000']
        #line[0] = re.sub(r'【.*】', '', line[0]).strip()
        #line[1] = re.sub(r'\u3000', '', line[1]).strip()
        for pattern in ignore_pattern:
            if re.search(pattern, text) != None:
                text = re.sub(pattern, '', text).strip()
                break
        if len(text) > 0 and text[-1] in ['，', ',']:
            text = text[:-1]
        text=text.strip()
        return text
    def Process_zuihou(text):
        word_ignore=['统','因此','一般','常','学者','亦','被','又','也','可','则','人们','故']
        if len(text)>0 and re.search(r'[A-Za-z0-9ⅠⅡⅢ]',text)==None:
            uList_list = greedmatch([text], Dict)
            if len(uList_list[0])==0 and len(text)<5:
                print(text)
                text=''
            elif len(uList_list[0])==0:
                for word in word_ignore:
                    if re.search(word,text)!=None:
                        #print(text)
                        text=''
                        break
        return text
    word_daici = ['上述', '本病', '其', '该']
    with open(infile, 'r', encoding='utf-8') as ifh:
        ofh = open(outfile, 'w', encoding='utf-8-sig', newline='')
        writer = csv.writer(ofh)
        lines = csv.reader(ifh)
        Dict = dict_readformuList(ufile)
        for line in lines:
            #if len(line)<2:
            #    continue
            #matchobj = re.search(r'鼻.管', line[0])
            #if matchobj == None:
            #   continue
            line[1],line[2]=Process_lianjie(line[1],line[2])
            line[1]=Process_input(line[1])
            line[0]=Process_input(line[0])

            resList=[]
            text = line[1]
            #print(text)

            matchobj=re.search(r'(.*)([,，;；])([^,，;；]*)$',text)
            if matchobj!=None:
                tmptext=Process_zuihou(matchobj.group(3))
                if tmptext=='':
                    text=matchobj.group(1)
                else:
                    text=matchobj.group(1)+matchobj.group(2)+tmptext
            else:
                text=Process_zuihou(text)

            textList = re.split(r'[,，;；]', text)
            if text=='':
                resList.append(line[0])
            if resList==[]:
                for word in word_daici:
                    if re.search(word,textList[0]):
                        resList.append(line[0]+'。'+text)
            if resList==[]:
                uList_list=greedmatch(textList,Dict)
                flag=0
                for i in range(len(uList_list)):
                    if len(uList_list[i])!=0:
                        flag=1
                if flag==0:
                    resList.append(line[0] + '。' +text)
            if resList==[]:
                resList.append(text)

            s = ''
            for ele in resList:
                s += ele + ' '
            line.insert(2, s)
            writer.writerow(line)
def rlabel_yuanyin(infile,outfile,ufile):
    def Extract_zuiqian(text, dict):
        '''找最前的实体'''
        resList = []
        rule = '最前的实体'
        uList_list = greedmatch([text], dict)
        if len(uList_list[0]) > 0:
            #resList.append(unity(uList_list[0][0].name, rule))
            match=re.search('(.*)'+uList_list[0][0].name,text)
            if match!=None and 0<len(match.group(1))<3:
                resList.append(unity(match.group(1)+uList_list[0][0].name, rule+'_长度小于3的前缀'))
            else:
                resList.append(unity(uList_list[0][0].name, rule))
        return resList

    def Extract_zuihou(text, dict, rule):
        '''找最后的实体'''
        resList = []
        rule += '最后的实体'
        uList_list = greedmatch([text], dict)
        if len(uList_list[0]) > 0:
            resList.append(unity(uList_list[0][-1].name, rule))
        return resList
    def Extract_er(text):
        resList=[]
        rule='而_'
        match=re.match(r'(.+)而',text)
        if match!=None:

            if resList==[]:
                resList=Extract_DepTree(match.group(1),rule)
            #if resList==[]:
            #    if len(match.group(1))<5:
            #        resList.append(unity(match.group(1),rule+'长度小于5'))
            #if resList==[]:
            #    match2=re.search(r'(.+)的',match.group(1))
            #    if match2!=None:
            #        resList.append(unity(match2.group(1),rule+'的'))
            if resList==[]:
                resList = Extract_universal(match.group(1), dict, rule)
        return resList
    def Extract_dunhao(text,resList):
        match1=re.search(r'^([^、]*)、(.*)',text)
        if match1!=None:
            match2=re.search(r'(.*)、([^、]*)$','、'+match1.group(2))
            text1=match1.group(1)
            text2=match2.group(1)
            if len(text2)>0 and text2[0]=='、':
                text2=text2[1:]
            text3=match2.group(2)
            for ele in resList:
                s = ''
                if text1.endswith(ele.name):
                    ulist_List = greedmatch([text3], dict)
                    if len(ulist_List[0]) > 0:
                        match3=re.search(r'^.*'+ulist_List[0][0].name,text3)
                        s = ele.name + '、' + text2 + '、'+match3.group()
                    else:
                        s=ele.name+'、'+text2+'、'+text3
                elif text3.startswith(ele.name):
                    ulist_List = greedmatch([text1], dict)
                    if len(ulist_List[0]) > 0:
                        match3 = re.search(ulist_List[0][-1].name+'.*$', text1)
                        s = match3.group() + '、' + text2 + '、' + ele.name
                    else:
                        s =  text1+ '、' + text2 + '、' + ele.name
                elif ele.name in text2:
                    ulist_List = greedmatch([text1], dict)
                    if len(ulist_List[0]) > 0:
                        match3 = re.search(ulist_List[0][-1].name + '.*$', text1)
                        s=match3.group() + '、' + text2 + '、'
                    else:
                        s=text1+'、'+text2+'、'
                    ulist_List = greedmatch([text3], dict)
                    if len(ulist_List[0]) > 0:
                        match3 = re.search(r'^.*' + ulist_List[0][0].name, text3)
                        s+=match3.group()
                    else:
                        s+=text3
                    break
                if s!='':
                    s=re.sub(r'、、','、',s)
                    ele.name=s
                    ele.rule+='_顿号扩充'
        return resList
    def Extract_yinqi(text):
        resList = []
        rule = '引起_'
        match = re.search(r'(.+)引起', text)
        if match != None:
            '''
            seg=posseg.cut(match.group(1))
            posList=gen2list(seg)
            posList=listmerge(posList,['n', 't', 'l', 'nr', 'ng', 'nz', 'd', 'b', 'i', 'g','eng','q'])
            for i in range(len(posList)-1,-1,-1):
                if posList[i][1]=='n':
                    resList.append(unity(posList[i][0],rule))
                    break
            '''
            resList=Extract_zuihou(match.group(1),dict,rule)
            #resList.append(unity(match.group(1), rule))
        return resList
    def Extract_suozhi(textlist):
        resList=[]
        rule='所致_'
        for i in range(len(textlist)):
            match = re.search(r'(.+)所致', textlist[i])
            if match!=None:
                resList = Extract_DepTree(match.group(1), rule)
                if resList == []:
                    resList = Extract_universal(match.group(1), dict, rule)
                break
        return resList
    def Extract_DepTree(text,rule):
        resList=[]
        s=''
        rule+='依存'
        hlp = HanlpTree()
        hlp.parse(text)
        SBV_VOB = hlp.get_sb_obj_phrases()
        for key in SBV_VOB:
            s += key + ':'
            for ele in SBV_VOB[key]:
                s += ele[0] + '/' + ele[1] + ' '
        if s!='':
            resList.append(unity(s,rule))
        return resList

    with open(infile, 'r', encoding='utf-8') as ifh:
        ofh = open(outfile, 'w', encoding='utf-8-sig', newline='')
        writer = csv.writer(ofh)
        lines = csv.reader(ifh)
        dict = dict_readformuList(ufile)
        writer.writerow(['前句','本句','关系词','后句','标签','规则','分词','依存关系'])
        for line in lines:
            #matchobj = re.search(r'所致', line[3])
            #if matchobj == None:
            #   continue

            text=line[3]
            print(text)

            textlist = re.split(r'[,，]', text)
            resList=[]

            if resList==[]:
                resList=Extract_er(textlist[0])
            if resList==[]:
                resList=Extract_yinqi(text)
            if resList==[]:
                resList=Extract_suozhi(textlist)
            #if resList==[]:
            #    resList=Extract_DepTree(line[2]+line[3])
            #if resList==[]:
            #    resList=Extract_zuiqian(textlist[0],dict)
            #resList=Extract_dunhao(textlist[0],resList)

            s = ''
            for ele in resList:
                s += ele.name + ' '
            line.insert(4, s)
            s = ''
            for ele in resList:
                s += ele.rule + ' '
            line.insert(5,s)
            s = '('
            u = greedmatch([line[3]], dict,2,1)
            for ele in u:
                for ele2 in ele:
                    s += ele2.name + ' '
            s += ')'
            line.insert(6,s)

            s=''
            hlp = HanlpTree()
            hlp.parse(line[2]+line[3])
            SBV_VOB=hlp.get_sb_obj_phrases()
            for key in SBV_VOB:
                s+=key+':'
                for ele in SBV_VOB[key]:
                    s+=ele[0]+'/'+ele[1]+' '
            line.insert(7,s)
            writer.writerow(line)

def yicun(infile,outfile,ufile):
    def Extract_DepTree(line):
        s=''
        hlp = HanlpTree()
        hlp.parse(line[2] + line[3])
        SBV_VOB = hlp.get_sb_obj_phrases()
        for key in SBV_VOB:
            s += key + ':'
            for ele in SBV_VOB[key]:
                s += ele[0] + '/' + ele[1] + ' '
        return s
    with open(infile, 'r', encoding='utf-8') as ifh:
        ofh = open(outfile, 'w', encoding='utf-8-sig', newline='')
        writer = csv.writer(ofh)
        lines = csv.reader(ifh)
        dict = dict_readformuList(ufile)
        for line in lines:
            print(line[2])
            s=Extract_DepTree(line)
            line.insert(4, s)
            writer.writerow(line)
def Extract_runity(infile,outfile):
    '''提取实体'''
    with open(infile, 'r', encoding='utf-8') as ifh:
        with open(outfile,'w',encoding='utf-8') as ofh:
            lines = csv.reader(ifh)
            for line in lines:
                #matchobj = re.search(r'怜悯性杀亲', line[4])
                #if matchobj == None:
                #   continue
                text=line[4].strip()
                matchobj=re.findall(r'[\"“].*?[\"”]',text)
                for ele in matchobj:
                    matchobj1=re.search(r'[\u4e00-\u9fa5]+',ele[1:-1])
                    if matchobj1==None:
                        s=ele[1:-1].strip()
                        if len(s) > 1:
                            ofh.write(s+'\n')
                matchobj=re.findall(r'[\(（][^\)）]*[\)）]',text)
                for ele in matchobj:
                    matchobj1=re.search(r'[\u4e00-\u9fa5]+',ele[1:-1])
                    if matchobj1==None:
                        s = ele[1:-1].strip()
                        if s[0]!='图' and len(s)>1:
                            ofh.write(s+'\n')

#lunity(r'..\别称\def_别称.csv',r'..\别称\def_别称_左实体.csv',r'..\医学相关\实体\unity.txt')
#runity(r'..\别称\def_别称.csv',r'..\别称\def_别称_右实体.csv',r'..\医学相关\实体\unity.txt')
#lunity_chengwei(r'..\别称\def_称为.csv',r'..\别称\def_称为_左实体.csv',r'..\医学相关\实体\my_unity.txt')
#runity_chengwei(r'..\别称\def_称为.csv',r'..\别称\def_称为_右实体.csv',r'..\医学相关\实体\my_unity.txt')
#lunity(r'..\别称\def_是指_定义为等.csv',r'..\别称\def_是指_定义为等_左实体.csv',r'..\医学相关\实体\unity.txt')
#lunity(r'..\别称\eq_是_待分析.csv',r'..\别称\eq_是_待分析_左实体.csv',r'..\医学相关\实体\unity.txt')
#lunity(r'..\别称\eq_英文名称.csv',r'..\别称\eq_英文名称_左实体.csv',r'..\医学相关\实体\unity.txt')
#lunity(r'..\别称\原因.csv',r'..\别称\原因_左实体.csv',r'..\医学相关\实体\unity.txt')
#rlabel_yuanyin(r'..\别称\原因.csv',r'..\别称\原因_右实体.csv',r'..\医学相关\实体\unity.txt')
yicun(r'..\别称\原因.csv',r'..\别称\原因_依存.csv',r'..\医学相关\实体\unity.txt')
#lunity(r'..\别称\使.csv',r'..\别称\使_左实体.csv',r'..\医学相关\实体\unity.txt')
#lunity(r'..\别称\因为.csv',r'..\别称\因为_左实体.csv',r'..\医学相关\实体\unity.txt')
#Extract_runity(r'..\别称\def_别称3.csv',r'..\别称\unity.txt')
