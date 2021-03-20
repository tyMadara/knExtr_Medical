from DepTree_clz import *
from function import *
#利用依存分析提取一句话中的三元组
def Get_posterity(node):
    # 获取某个节点的所有后代节点(不包括COO和标点符号)index,包括本身
    posterity_index = [node.index]
    for child in node.children:
        if child.relation in ['SBV', 'VOB', 'ATT', 'ADV']:
            posterity_index += Get_posterity(child)
    return posterity_index


def Get_text(hlp,node, relation_node=None):
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

    def Get_COO(node):
        #提取所有与node直接或间接并列的节点
        List = [node]
        for tmpnode in Get_part(node, 'COO',False):
            List.extend(Get_COO(tmpnode))
        return List
    def Get_part(node, part,coo=True):
        # 提取node节点的一阶part成分子节点
        #若coo=True，还会对每个子节点提取其所有直接或间接的COO成分
        List = []
        for child in node.children:
            if child.relation == part:
                if coo==True:
                    List+=Get_COO(child)
                else:
                    List.append(child)
        return List
    def extract_SBV(node):
        # 提取左实体
        #输入根节点，也就是核心动词
        lunity_List = []
        SBV_List = Get_part(node, 'SBV')
        for sbvchild in SBV_List:
            lunity_List.append(Get_text(sbvchild))
        return lunity_List
    def ATT_binglie(obnode, vnode):
        # 如果宾语有并列的修饰成分的时候
        # 这里node是OB
        # 返回宾语
        text_List = []
        ATT_List = Get_part(obnode, 'ATT')
        for attchild in ATT_List:
            #COO_List = Get_COO(attchild)
            #if len(COO_List) > 1:
            #    for coochild in COO_List:
                    text_List.append(Get_text(attchild) + obnode.word)
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
            #获取node树中除了node本身词的所有前缀词
            s = ''
            posterity_index = Get_posterity(node)
            posterity_index.sort()
            for index in posterity_index:
                if index < node.index:
                    s += hlp.words[index]
            return s

        runity_List = []
        OB_List = Get_part(vnode, 'VOB')
        OB_List = Sort(OB_List)
        preword = ''
        for obchild in OB_List:
            tmp_List = ATT_binglie(obchild, vnode)
            s = Preword(obchild)
            if s=='':
                for i in range(len(tmp_List)):
                    tmp_List[i]=preword+tmp_List[i]
            else:
                preword=s
            runity_List.extend(tmp_List)

        '''
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
        '''
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
    if type(text)==type('0'):
        hlp = HanlpTree()
        hlp.parse(text)
    else:
        hlp=text
    root = hlp._build_tree()
    runity_LList = HED_binglie(root)
    lunity_List = extract_SBV(root)
    triplelist=[]
    for lunity in lunity_List:
        for relation in runity_LList:
            for runity in runity_LList[relation]:
                triplelist.append([lunity, relation, runity])
    return triplelist

if __name__ == '__main__':

    text='生育期妇女如子宫内膜厚度＞10mm、绝经后如＞5mm，为子宫内膜增厚。'
    list=Dep(text)
    for i in range(len(list)):
        print(list[i])