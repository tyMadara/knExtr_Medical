#利用依存分析从三元组提取实体

from DepTree import *
from function import *
#hlp中的head从1开始计，head=1表示第一个词，0表示root
#index从0开始计
def Dep(text):
    def Get_posterity(node):
        # 获取某个节点的所有后代节点(不包括COO和标点符号)index,包括本身
        posterity_index = [node.index]
        for child in node.children:
            if child.relation in ['SBV', 'VOB', 'ATT', 'ADV']:
                posterity_index += Get_posterity(child)
        return posterity_index

    def Get_text(node, relation_node=None):
        # 根据后代index获取文本
        # 若有关系词，则只会提取关系词之后的文本
        posterity_index = Get_posterity(node)
        posterity_index.sort()
        # imin, imax = posterity_index[0], posterity_index[-1] + 1
        if relation_node == None:
            list = [hlp.words[index] for index in posterity_index]
        else:
            list = []
            for index in posterity_index:
                if index > relation_node.index:
                    list.append(hlp.words[index])
        phrase = ''.join(list)
        return phrase

    def SBV_binglie(node):
        # 提取左实体
        #输入根节点，也就是核心动词
        lunity_List = []
        SBV_List = Get_part(node, 'SBV')
        for sbvchild in SBV_List:
            apposition_List = Get_COO(sbvchild)
            for appchild in apposition_List:
                lunity_List.append(Get_text(appchild))
        return lunity_List

    def Get_COO(node):
        List = [node]
        for tmpnode in Get_part(node, 'COO'):
            List.extend(Get_COO(tmpnode))
        return List

    def ATT_binglie(obnode, vnode):
        # 如果宾语有并列的修饰成分的时候
        # 这里node是OB
        # 返回宾语
        text_List = []
        ATT_List = Get_part(obnode, 'ATT')
        for attchild in ATT_List:
            COO_List = Get_COO(attchild)
            if len(COO_List) > 1:
                for coochild in COO_List:
                    text_List.append(Get_text(coochild) + obnode.word)
        if text_List == []:
            text_List.append(Get_text(obnode, vnode))
        return text_List

    def VOB_binglie(vnode):
        # 这里node是V，给定动词
        # 如果宾语有并列成分，将该并列成分同作为右实体
        # 如果某个成分没有ATT,SBV,ADV成分，就将其之前最近的含有此成分作为该实体的ATT加以连接。
        def Sort(nodelist):
            # 将子树结点按照index排序
            flag = 1
            while (flag == 1):
                flag = 0
                for i in range(len(nodelist) - 1):
                    if nodelist[i].index > nodelist[i + 1].index:
                        tmp = nodelist[i]
                        nodelist[i] = nodelist[i + 1]
                        nodelist[i + 1] = tmp
                        flag = 1
            return nodelist

        def Preword(node):
            s = ''
            posterity_index = Get_posterity(node)
            posterity_index.sort()
            for index in posterity_index:
                if index < node.index:
                    s += hlp.words[index]
            return s

        runity_List = []
        OB_List = Get_part(vnode, 'VOB')
        for obchild in OB_List:
            preword = ''
            apposition_List = Get_COO(obchild)
            apposition_List = Sort(apposition_List)
            for appchild in apposition_List:
                tmp_List = ATT_binglie(appchild, vnode)
                if len(tmp_List) == 1:
                    s = Preword(appchild)
                    if s == '':
                        tmp_List[0] = preword + tmp_List[0]
                    else:
                        preword = s
                else:
                    preword = ''
                runity_List.extend(tmp_List)
        return runity_List

    def HED_binglie(node):
        runity_LList = {}
        apposition_List = Get_COO(node)
        for appchild in apposition_List:
            runity_LList[appchild.word] = VOB_binglie(appchild)
        return runity_LList

    def Modify(hlp):
        myhlp = HanlpTree()
        arc = namedtuple('acr', ['relation', 'head'])
        myhlp.sentence = hlp.sentence
        myhlp.postags = hlp.postags
        flag_List = []
        for i in range(len(hlp.arcs)):
            if i == 0:
                node = arc(hlp.arcs[i].relation, hlp.arcs[i].head)
                myhlp.arcs.append(node)
                myhlp.words.append(hlp.words[i])
            else:
                if hlp.arcs[i].relation == hlp.arcs[i - 1].relation and hlp.arcs[i].head == hlp.arcs[i - 1].head:
                    myhlp.words[-1] += hlp.words[i]
                    myhlp.arcs[-1] = arc(myhlp.arcs[-1].relation, myhlp.arcs[-1].head - 1)
                    # flag_List记录发生合并的前一个节点的index（从1开始计算）
                    flag_List.append(i)
                else:
                    sum = 0
                    for j in flag_List:
                        if hlp.arcs[i].head > j:
                            sum += 1
                    tmpnode = arc(hlp.arcs[i].relation, hlp.arcs[i].head - sum)
                    myhlp.arcs.append(tmpnode)
                    myhlp.words.append(hlp.words[i])
        return myhlp

    # def bulid_nodelist(hlp):
    #    node_List=[]
    #    Node = namedtuple('Node', ['children', 'parent', 'word', 'relation', 'index'])
    #    for
    #    return node_List

    def Get_part(node, part):
        # 提取某一成分子树
        List = []
        for child in node.children:
            if child.relation == part:
                List.append(child)
        return List

    def secondSBV(node):
        triple = []
        VOB_List = Get_part(node, 'VOB')
        for vobchild in VOB_List:
            ATT_List = Get_part(vobchild, 'ATT')
            for attchild in ATT_List:
                SBV_List = Get_part(attchild, 'SBV')
                for sbvchild in SBV_List:
                    runity_List = VOB_binglie(node)
                    triple.append([Get_text(sbvchild), attchild.word, '/'.join(runity_List)])
        return triple

    hlp = HanlpTree()
    hlp.parse(text)
    root = hlp._build_tree()
    runity_LList = HED_binglie(root)
    lunity_List = SBV_binglie(root)
    triplelist=[]
    for lunity in lunity_List:
        for relation in runity_LList:
            for runity in runity_LList[relation]:
                triplelist.append([lunity, relation, runity])



def func():
    with open(r'..\依存提取\stand.csv','r',encoding='utf-8') as ifh:
        def Get_posterity(node):
            # 获取某个节点的所有后代节点(不包括COO和标点符号)index,包括本身
            posterity_index = [node.index]
            for child in node.children:
                if child.relation in ['SBV','VOB','ATT','ADV']:
                    posterity_index += Get_posterity(child)
            return posterity_index
        def Get_text(node,relation_node=None):
            #根据后代index获取文本
            #若有关系词，则只会提取关系词之后的文本
            posterity_index=Get_posterity(node)
            posterity_index.sort()
            #imin, imax = posterity_index[0], posterity_index[-1] + 1
            if relation_node==None:
                list=[hlp.words[index] for index in posterity_index]
            else:
                list=[]
                for index in posterity_index:
                    if index>relation_node.index:
                        list.append(hlp.words[index])
            phrase = ''.join(list)
            return phrase
        def SBV_binglie(node):
            #提取左实体
            lunity_List=[]
            SBV_List=Get_part(node,'SBV')
            for sbvchild in SBV_List:
                apposition_List = Get_COO(sbvchild)
                for appchild in apposition_List:
                    lunity_List.append(Get_text(appchild))
            return lunity_List
        def Get_COO(node):
            List=[node]
            for tmpnode in Get_part(node,'COO'):
                List.extend(Get_COO(tmpnode))
            return List
        def ATT_binglie(obnode,vnode):
            #如果宾语有并列的修饰成分的时候
            #这里node是OB
            #返回宾语
            text_List=[]
            ATT_List = Get_part(obnode, 'ATT')
            for attchild in ATT_List:
                COO_List = Get_COO(attchild)
                if len(COO_List)>1:
                    for coochild in COO_List:
                        text_List.append(Get_text(coochild)+obnode.word)
            if text_List==[]:
                text_List.append(Get_text(obnode,vnode))
            return text_List

        def VOB_binglie(vnode):
            #这里node是V，给定动词
            #如果宾语有并列成分，将该并列成分同作为右实体
            #如果某个成分没有ATT,SBV,ADV成分，就将其之前最近的含有此成分作为该实体的ATT加以连接。
            def Sort(nodelist):
                #将子树结点按照index排序
                flag=1
                while (flag==1):
                    flag=0
                    for i in range(len(nodelist)-1):
                        if nodelist[i].index>nodelist[i+1].index:
                            tmp=nodelist[i]
                            nodelist[i]=nodelist[i+1]
                            nodelist[i+1]=tmp
                            flag=1
                return nodelist
            def Preword(node):
                s=''
                posterity_index=Get_posterity(node)
                posterity_index.sort()
                for index in posterity_index:
                    if index<node.index:
                        s+=hlp.words[index]
                return s
            runity_List=[]
            OB_List=Get_part(vnode,'VOB')
            for obchild in OB_List:
                preword=''
                apposition_List=Get_COO(obchild)
                apposition_List=Sort(apposition_List)
                for appchild in apposition_List:
                    tmp_List=ATT_binglie(appchild,vnode)
                    if len(tmp_List)==1:
                        s=Preword(appchild)
                        if s=='':
                            tmp_List[0]=preword+tmp_List[0]
                        else:
                            preword=s
                    else:
                        preword=''
                    runity_List.extend(tmp_List)
            return runity_List
        def HED_binglie(node):
            runity_LList={}
            apposition_List=Get_COO(node)
            for appchild in apposition_List:
                runity_LList[appchild.word]=VOB_binglie(appchild)
            return runity_LList

        def Modify(hlp):
            myhlp=HanlpTree()
            arc = namedtuple('acr', ['relation', 'head'])
            myhlp.sentence=hlp.sentence
            myhlp.postags=hlp.postags
            flag_List=[]
            for i in range(len(hlp.arcs)):
                if i==0:
                    node=arc(hlp.arcs[i].relation, hlp.arcs[i].head)
                    myhlp.arcs.append(node)
                    myhlp.words.append(hlp.words[i])
                else:
                    if hlp.arcs[i].relation==hlp.arcs[i-1].relation and hlp.arcs[i].head==hlp.arcs[i-1].head:
                        myhlp.words[-1]+=hlp.words[i]
                        myhlp.arcs[-1] = arc(myhlp.arcs[-1].relation, myhlp.arcs[-1].head - 1)
                        #flag_List记录发生合并的前一个节点的index（从1开始计算）
                        flag_List.append(i)
                    else:
                        sum=0
                        for j in flag_List:
                            if hlp.arcs[i].head>j:
                                sum+=1
                        tmpnode = arc(hlp.arcs[i].relation, hlp.arcs[i].head-sum)
                        myhlp.arcs.append(tmpnode)
                        myhlp.words.append(hlp.words[i])
            return myhlp
        #def bulid_nodelist(hlp):
        #    node_List=[]
        #    Node = namedtuple('Node', ['children', 'parent', 'word', 'relation', 'index'])
        #    for
        #    return node_List

        def Get_part(node,part):
            #提取某一成分子树
            List=[]
            for child in node.children:
                if child.relation == part:
                    List.append(child)
            return List
        def secondSBV(node):
            triple=[]
            VOB_List=Get_part(node,'VOB')
            for vobchild in VOB_List:
                ATT_List=Get_part(vobchild,'ATT')
                for attchild in ATT_List:
                    SBV_List=Get_part(attchild,'SBV')
                    for sbvchild in SBV_List:
                        runity_List=VOB_binglie(node)
                        triple.append([Get_text(sbvchild),attchild.word,'/'.join(runity_List)])
            return triple
        ofh=open(r'..\依存提取\三元组_提取.csv','w',encoding='utf-8-sig',newline='')
        writer=csv.writer(ofh)
        lines=csv.reader(ifh)
        num=0
        for line in lines:
            #if '2004年GE公司' not in line[0]:
            #    continue
            #if num>1000:
            #    break
            num+=1
            print(line[0])
            hlp = HanlpTree()
            hlp.parse(line[0])
            #hlp=Modify(hlp)
            s=''
            for i in range(len(hlp.arcs)):
                s+=str(i+1)+'/'+hlp.words[i]+'/'+hlp.arcs[i].relation+'/'+str(hlp.arcs[i].head)+'\t'
            #hlp.build_dep_graph()
            root=hlp._build_tree()
            runity_LList=HED_binglie(root)
            lunity_List=SBV_binglie(root)
            for lunity in lunity_List:
                for relation in runity_LList:
                    for runity in runity_LList[relation]:
                        writer.writerow([lunity,relation,runity,s])
            triple=secondSBV(root)
            for ele in triple:
                ele.append(s)
                writer.writerow(ele)


