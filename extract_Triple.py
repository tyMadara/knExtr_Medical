'''
@Author:CLZ
@Date:2020-05-03 13:27
@LastEditTime
@Description:利用聚类的关系动词从文本中提取三元组
'''
from function import *
from DepTree import *
from tqdm import tqdm
from collections import Counter
from Dep import *

ignore_word=['可以','可']
negtive_word=['不能','很难','不']
def Extract(input,output,datapath):
    '''
    利用聚类的关系词将三元组.csv转化成方便后续处理的格式
    :param input: csv文件,每行是一个聚类的动词集，动词用空格分开
    :param output:xlsx文件，每个sheet里的条目的动词属于一个聚类
    :param datapath:三元组文件，每行应有【100多年来放射诊断学获得了迅猛的发展。\t放射诊断学\t获得\t迅猛的发展\t[SBV] & [VOB] & [RAD] & [WP] & [ADV]\tpyltp】这样的格式
    :return:
    '''

    ifh=open(input,'r',encoding='utf-8-sig')
    datafile=open(datapath,'r',encoding='utf-8')
    lines=csv.reader(ifh)
    workbook = openpyxl.Workbook()
    yuanju, zuoju, dongci, youju,label = 0, 1, 3, 4,6
    kindlist=[]
    for line in lines:
        if line[0]=='数量':
            continue
        words=line[1].split(' ')
        for i in range(len(words)):
            words[i]=words[i].rstrip('0123456789')
        kindlist.append(words)
    for i in range(len(kindlist)):
        workbook.create_sheet(kindlist[i][0])
        sheet=workbook[kindlist[i][0]]
        sheet.cell(row=1, column=1, value='前句')
        sheet.cell(row=1, column=2, value='动词')
        sheet.cell(row=1, column=3, value='后句')
        sheet.cell(row=1, column=4, value='全句')

    datas = csv.reader(datafile)
    for data in datas:
        print(data[0])
        #if '尿道手术或生殖道手' not in data[0]:
        #    continue
        if data[label]=='0':
            for words in kindlist:
                if data[dongci].strip() in words:
                    sheet=workbook[words[0]]
                    Row=sheet.max_row+1
                    sheet.cell(row=Row, column=1, value=data[zuoju])
                    sheet.cell(row=Row, column=2, value=data[dongci])
                    sheet.cell(row=Row, column=3, value=data[youju])
                    sheet.cell(row=Row, column=4, value=data[yuanju])
                    break

    sheet = workbook['Sheet']
    workbook.remove(sheet)
    workbook.save(output)
    ifh.close()
def Modify(infile,outfile,print_file):
    '''暂时弃用'''
    def sheet2list(sheet):
        List=[]
        for i in range(1,sheet.max_row+1):
            tmplist=[]
            for j in range(1,sheet.max_column+1):
                tmplist.append(sheet.cell(i,j).value)

            List.append(tmplist)
        List[0].append('是否可以删去')
        for i in range(1,len(List)):
            List[i].append('')
        List[0].append('是否已处理')
        for i in range(1,len(List)):
            List[i].append('')
        return List
    def Write2sheet(reslist,sheet):
        for i in range(len(reslist)):
            sheet.append(reslist[i])
    def Verbset(reslist):
        mrow=len(reslist)
        if mrow==0:
            return
        mcolumn=len(reslist[0])
        col=-1
        for i in range(mcolumn):
            if reslist[0][i]=='动词':
                col=i
                break
        tmp=[]
        for i in range(mrow):
            tmp.append(reslist[i][col])
        return dict(Counter(tmp)).keys()
    def universal(reslist):
        mrow = len(reslist)
        mcolumn=len(reslist[0])
        for i in range(1,mrow):
            #if '临床医师可' not in reslist[i][1]:
            #    continue

            reslist[i][3]=reslist[i][3].strip()
            if reslist[i][3]=='':
                reslist[i][8]='没有后句'
            elif reslist[i][3][-1] in ['?','？','!','！']:
                reslist[i][8]='非陈述句'
            elif len(reslist[i][3].rstrip('，。,.;；')) < 2:
                reslist[i][8]='后句太短'
            poslist=Pos(reslist[i][0])
            prelength=0
            for j in range(len(poslist)):
                if prelength>len(reslist[i][1]):
                    reslist[i][8]='没有主语'
                    break
                else:
                    prelength+=len(poslist[j][0])
                    if poslist[j][1]=='n':
                        break

            for word in ignore_word:
                if reslist[i][1].endswith(word):
                    reslist[i][1]=reslist[i][1][:len(reslist[i][1])-len(word)]
                    reslist[i][9]+='_删去可以'

        return reslist
    def universal_binglie(reslist):
        for i in range(1,len(reslist)):
            text=reslist[i][3]
            unitylist=re.split(r'[或和]',text)
            if len(unitylist)>1:
                reslist[i][3]=' '.join(unitylist)
                reslist[i][9]+='_并列'
        return reslist

    def liru(reslist,verbset):
        #如果关系集中有例如：将后句按‘、’和'或'分段
        if '例如' not in verbset:
            return reslist
        #tmplist=[reslist[0]]
        for i in range(1,len(reslist)):
            text=reslist[i][3]
            unitylist=re.split(r'[、或和]',text)
            if len(unitylist)>0:
                match=re.search(r'(.*?)等',unitylist[-1])
                if match!=None:
                    unitylist[-1]=match.group(1)
                reslist[i][3]=' '.join(unitylist)

                reslist[i][9]='_并列'

        return reslist

    quanju,qianju,dongci,houju,SB,OB,textSB,textOB,shanqu,chuli=0,1,2,3,4,5,6,7,8,9
    workbook = openpyxl.load_workbook(infile)
    workbook2=openpyxl.Workbook()
    sheet_List=workbook.get_sheet_names()
    for sheetname in tqdm(sheet_List):
        sheet=workbook[sheetname]
        workbook2.create_sheet(sheetname)
        sheet2 = workbook2[sheetname]

        reslist=sheet2list(sheet)
        verbset=Verbset(reslist)
        reslist=universal(reslist)
        #reslist=liru(reslist,verbset)
        #reslist=universal_binglie(reslist)
        Write2sheet(reslist,sheet2)
    workbook2.save(outfile)
def process3(infile,outfile):
    #提取左右实体
    def sheet2list(sheet):
        List = []
        List.append(['前句', '左实体', '动词', '后句', '右实体', '全句'])
        for i in range(2, sheet.max_row + 1):
            List.append([sheet.cell(i, 1).value, '', sheet.cell(i, 2).value, sheet.cell(i, 3).value, '',
                         sheet.cell(i, 4).value])
        return List
    def extract(reslist):
        mrow = len(reslist)
        mcolumn=len(reslist[0])
        tmplist=[]
        tmplist.append(['前句', '左实体', '动词', '后句', '右实体', '全句'])
        for i in range(1,mrow):
            triplelist=Dep(reslist[i][quanju])
            for j in range(len(triplelist)):
                tmplist.append([reslist[i][qianju],triplelist[j][0],triplelist[j][1],reslist[i][houju],triplelist[j][2],reslist[i][quanju]])
                #print(tmplist[-1])
            if len(triplelist)==0:
                tmplist.append([reslist[i][qianju],'',reslist[i][dongci],reslist[i][houju],'',reslist[i][quanju]])
        return tmplist
    qianju,zuo,dongci,houju,you,quanju=0,1,2,3,4,5
    workbook = openpyxl.load_workbook(infile)
    workbook2 = openpyxl.Workbook()
    sheet_List = workbook.get_sheet_names()
    for sheetname in tqdm(sheet_List):
        sheet = workbook[sheetname]
        workbook2.create_sheet(sheetname)
        sheet2 = workbook2[sheetname]

        reslist = sheet2list(sheet)
        reslist = extract(reslist)
        Write2sheet(reslist, sheet2)
    sheet = workbook2['Sheet']
    workbook2.remove(sheet)
    workbook2.save(outfile)
def process1(infile,outfile):
    #利用依存分析将句子分为前句，动词，后句,只取含有SVB和VOB的句子
    def func(reslist):
        tmplist=[]
        for line in reslist:
            if line[6]=='hanlp' and re.search('SBV',line[4])!=None and re.search('VOB',line[4])!=None:
                tmplist.append(line)
        return tmplist
    yuanju, zuoshiti, dongci, youshiti, ruanjian = 0, 1, 2, 3, 6
    reslist = csv2list(infile)
    reslist = func(reslist)
    outfile = open(outfile, 'w', encoding='utf-8-sig', newline='')
    writer = csv.writer(outfile)
    for line in tqdm(reslist):
        hlp = HanlpTree()
        hlp.parse(line[yuanju])
        hed=-1
        for i in range(len(hlp.arcs)):
            if hlp.arcs[i].relation=='ROOT':
                hed=i
        zuoju=''.join(hlp.words[:hed]).strip()
        youju=''.join(hlp.words[hed+1:]).strip()
        writer.writerow([line[yuanju],zuoju,hlp.words[hed],youju])
def process2(infile,outfile):
    #利用前后缀删除条目
    yuanju, zuoju, dongci, youju = 0, 1, 2, 3
    reslist=csv2list(infile)
    outfile=open(outfile,'w',encoding='utf-8-sig',newline='')
    writer=csv.writer(outfile)
    class fix():
        def __init__(self,num):
            self.num=num
            self.prefix=[]
            self.suffix=[]
            self.sent=[]
            self.zuoju=[]
            self.youju=[]
            self.label=[]
    tmplist=[]
    for line in reslist:
        tmplist.append(line[dongci])
    verbdict=dict(Counter(tmplist))
    for verb in verbdict:
        verbdict[verb]=fix(verbdict[verb])
    for line in tqdm(reslist):
        verbdict[line[dongci]].zuoju.append(line[zuoju])
        verbdict[line[dongci]].youju.append(line[youju])
        verbdict[line[dongci]].prefix.append(line[zuoju][-2:])
        verbdict[line[dongci]].suffix.append(line[youju][:2])
        verbdict[line[dongci]].sent.append(line[yuanju].strip())
        verbdict[line[dongci]].label.append(0)
    del_parttern_pre=[]
    del_parttern_suf = []
    for verb in verbdict:
        tmpdict=dict(Counter(verbdict[verb].prefix))
        if verbdict[verb].num > 10:
            for key in tmpdict:
                 if tmpdict[key]/verbdict[verb].num>0.2:
                     del_parttern_pre.append([key,verb])
        tmpdict = dict(Counter(verbdict[verb].suffix))
        if verbdict[verb].num > 10:
            for key in tmpdict:
                if tmpdict[key] / verbdict[verb].num > 0.2:
                    del_parttern_suf.append([key, verb])


    for verb in verbdict:
        for i in range(verbdict[verb].num):
            if [verbdict[verb].prefix[i], verb] in del_parttern_pre or [verbdict[verb].suffix[i],
                                                                        verb] in del_parttern_suf:
                verbdict[verb].label[i] = 1
    for verb in verbdict:
        sum=0
        for i in range(verbdict[verb].num):
            if verbdict[verb].label[i]==0:
                sum+=1
        if sum<4:
            for i in range(verbdict[verb].num):
                verbdict[verb].label[i] = 2
    for verb in verbdict:
        for i in range(verbdict[verb].num):
            writer.writerow([verbdict[verb].sent[i], verbdict[verb].zuoju[i], verbdict[verb].prefix[i], verb,
                             verbdict[verb].youju[i], verbdict[verb].suffix[i], verbdict[verb].label[i]])
    for ele in del_parttern_pre:
        print(ele)
    for ele in del_parttern_suf:
        print(ele)
def process4(infile,unitylist,outfile):
    #从左实体中查找实体列表里的实体
    workbook=openpyxl.load_workbook(infile)
    workbook2 = openpyxl.Workbook()
    sheetlist=workbook.get_sheet_names()
    unitylist=dict_readformuList(unitylist)
    leftunity=1
    for sheetname in tqdm(sheetlist):
        sheet=workbook[sheetname]
        workbook2.create_sheet(sheetname)
        sheet2 = workbook2[sheetname]
        reslist=sheet2list(sheet)
        reslist[0].append('实体列表里的实体')
        for i in range(1,len(reslist)):
            str=''
            for unity in unitylist:
                if unity in reslist[i][leftunity]:
                    str+=unity+' '
            reslist[i].append(str)
        Write2sheet(reslist, sheet2)
    sheet = workbook2['Sheet']
    workbook2.remove(sheet)
    workbook2.save(outfile)
def process5(infile,outfile):
    #删去条目较少的sheet
    workbook = openpyxl.load_workbook(infile)
    workbook2 = openpyxl.Workbook()
    sheetlist = workbook.get_sheet_names()
    tmplist=csv2list(r'../利用聚类的关系提取/聚类_hanlp.csv')
    tmpf = open(r'../利用聚类的关系提取/聚类2_hanlp.csv', 'w', encoding='utf-8-sig', newline='')
    writer = csv.writer(tmpf)
    proportion=0.005
    sum=0
    for sheetname in sheetlist:
        sheet=workbook[sheetname]
        sum+=sheet.max_row
    i=0
    for sheetname in tqdm(sheetlist):
        i+=1
        sheet=workbook[sheetname]
        if sheet.max_row>sum*proportion:
            workbook2.create_sheet(sheetname)
            sheet2 = workbook2[sheetname]
            reslist=sheet2list(sheet)
            Write2sheet(reslist,sheet2)
            writer.writerow(tmplist[i])
    sheet = workbook2['Sheet']
    workbook2.remove(sheet)
    workbook2.save(outfile)
def process1(infile,outfile):
    #利用依存分析将句子分为前句，动词，后句,只取含有SVB和VOB的句子
    def func(reslist):
        tmplist=[]
        for line in reslist:
            if line[6]=='hanlp' and re.search('SBV',line[4])!=None and re.search('VOB',line[4])!=None:
                tmplist.append(line)
        return tmplist
    mulu,yuanju  = 0, 1
    reslist = csv2list(infile)
    #reslist = func(reslist)
    outfile = open(outfile, 'w', encoding='utf-8-sig', newline='')
    writer = csv.writer(outfile)
    for line in tqdm(reslist):
        hlp = HanlpTree()
        hlp.parse(line[yuanju])
        hed=-1
        for i in range(len(hlp.arcs)):
            if hlp.arcs[i].relation=='ROOT':
                hed=i
        zuoju=''.join(hlp.words[:hed]).strip()
        youju=''.join(hlp.words[hed+1:]).strip()
        triple=Dep(hlp)
        s=''
        for ele in triple:
            s+='#'.join(ele)+'$'
        writer.writerow([line[yuanju],zuoju,hlp.words[hed],youju,s])
def fun():
    process1(r'../利用聚类的关系提取/三元组.csv',r'../利用聚类的关系提取/三元组_hanlp.csv')
    process2(r'../利用聚类的关系提取/三元组_hanlp.csv',r'../利用聚类的关系提取/三元组_筛选.csv')
    Extract(r'../利用聚类的关系提取/聚类_hanlp.csv',r'../利用聚类的关系提取/三元组_聚类.xlsx',r'../利用聚类的关系提取/三元组_筛选.csv')
    process3(r'../利用聚类的关系提取/三元组_聚类.xlsx',r'../利用聚类的关系提取/三元组_结果.xlsx')
    process4(r'../利用聚类的关系提取/三元组_结果.xlsx',r'../dicts/dicts_dict.txt',r'../利用聚类的关系提取/三元组_结果2.xlsx')
    process5(r'../利用聚类的关系提取/三元组_结果_有字典.xlsx', r'../利用聚类的关系提取/三元组_结果_有字典2.xlsx')
if __name__ == "__main__":
    fun()
    #hlp = HanlpTree()
    #hlp.parse('100多年来放射诊断学获得了迅猛的发展。')
    #print(Dep(hlp))