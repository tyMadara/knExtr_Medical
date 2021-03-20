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
from mycluster import *

def process1(infile,outfile):
    #利用依存分析分析句子,只取含有SVB和VOB的句子
    #输入格式为[目录，全句]
    #输出格式为[全句，前句，动词，后句，三元组，目录]
    mulu,yuanju  = 0, 1
    reslist = csv2list(infile,'gbk')
    outfile = open(outfile, 'w', encoding='utf-8-sig', newline='')
    writer = csv.writer(outfile)
    for line in tqdm(reslist):
        hlp = HanlpTree()
        hlp.parse(line[yuanju])
        hed=-1
        flag1,flag2=0,0
        for i in range(len(hlp.arcs)):
            if hlp.arcs[i].relation=='ROOT':
                hed=i
        for i in range(len(hlp.arcs)):
            if hlp.arcs[i].relation=='SBV' and hlp.arcs[i].head==hed+1:
                flag1=1
            if hlp.arcs[i].relation=='VOB'and hlp.arcs[i].head==hed+1:
                flag2=1
        if flag1==1 and flag2==1:
            zuoju=''.join(hlp.words[:hed]).strip()
            youju=''.join(hlp.words[hed+1:]).strip()
            triple=Dep(hlp)
            s=''
            tmp=[]
            for ele in triple:
                tmp.append('#'.join(ele))
            s='$'.join(tmp)
            writer.writerow([line[yuanju],zuoju,hlp.words[hed],youju,s,line[mulu]])
def process2(infile,outfile):
    #利用前后缀删除条目
    #输出格式为[全句，前句，前缀，动词，后句，后缀，标签，三元组，目录]
    yuanju, zuoju, dongci, youju,triple,cata = 0, 1, 2, 3,4,5
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
            self.cata=[]
            self.triple=[]
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
        verbdict[line[dongci]].triple.append(line[triple])
        verbdict[line[dongci]].cata.append(line[cata])
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
                if verbdict[verb].label[i]!=1:
                    verbdict[verb].label[i] = 2
    for verb in verbdict:
        for i in range(verbdict[verb].num):
            writer.writerow([verbdict[verb].sent[i], verbdict[verb].zuoju[i], verbdict[verb].prefix[i], verb,
                             verbdict[verb].youju[i], verbdict[verb].suffix[i], verbdict[verb].label[i],verbdict[verb].triple[i],verbdict[verb].cata[i]])
    for ele in del_parttern_pre:
        print(ele)
    for ele in del_parttern_suf:
        print(ele)
def clu(infile,outfile):
    #将动词聚类
    reslist=csv2list(infile)
    tmplist=[]
    verb,label=3,6
    for line in reslist:
        if line[label]=='0':
            tmplist.append(line[verb])
    cluster(tmplist,outfile)
def process4(input, output, datapath):
    '''
    利用聚类的关系词将三元组.csv转化成方便后续处理的格式
    :param input: csv文件,每行是一个聚类的动词集，动词用空格分开
    :param output:xlsx文件，每个sheet里的条目的动词属于一个聚类
    :param datapath:三元组文件
    :return:
    '''
    #输出格式为[左句,动词,右句,原句,三元组,目录]
    #第一行有标题
    ifh=open(input,'r',encoding='utf-8-sig')
    datafile=open(datapath,'r',encoding='utf-8')
    lines=csv.reader(ifh)
    workbook = openpyxl.Workbook()
    yuanju, zuoju, dongci, youju,label,triple,cata = 0, 1, 3, 4,6,7,8
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
        sheet.cell(row=1, column=5, value='三元组')
        sheet.cell(row=1, column=6, value='目录')
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
                    sheet.cell(row=Row, column=5, value=data[triple])
                    sheet.cell(row=Row, column=6, value=data[cata])
                    break

    sheet = workbook['Sheet']
    workbook.remove(sheet)
    workbook.save(output)
    ifh.close()
def process5(infile, outfile):
    #展开三元组
    def sheet2list(sheet):
        List = []
        for i in range(2, sheet.max_row + 1):
            List.append([sheet.cell(i, 1).value, '', sheet.cell(i, 2).value, sheet.cell(i, 3).value, '',
                         sheet.cell(i, 4).value,sheet.cell(i, 5).value,sheet.cell(i, 6).value])
        return List
    def extract(reslist):
        mrow = len(reslist)
        mcolumn=len(reslist[0])
        tmplist=[]
        tmplist.append(['前句', '左实体', '动词', '后句', '右实体', '全句','目录'])
        for i in range(mrow):
            #triplelist=Dep(reslist[i][quanju])
            triplelist=[]
            if reslist[i][triple]==None:
                tmplist.append([reslist[i][qianju], '', reslist[i][dongci], reslist[i][houju], '', reslist[i][quanju],
                                reslist[i][cata]])
            else:
                for ele in reslist[i][triple].split('$'):
                    triplelist.append(ele.split('#'))
                for j in range(len(triplelist)):
                    tmplist.append([reslist[i][qianju],triplelist[j][0],triplelist[j][1],reslist[i][houju],triplelist[j][2],reslist[i][quanju],reslist[i][cata]])
                    #print(tmplist[-1])
        return tmplist
    qianju,zuo,dongci,houju,you,quanju,triple,cata=0,1,2,3,4,5,6,7
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
def process7(infile, unitylist, outfile):
    #从左,右实体中查找实体列表里的实体
    workbook=openpyxl.load_workbook(infile)
    workbook2 = openpyxl.Workbook()
    sheetlist=workbook.get_sheet_names()
    unitylist=dict_readformuList(unitylist)
    leftunity,rightunity=1,4
    for sheetname in tqdm(sheetlist):
        sheet=workbook[sheetname]
        workbook2.create_sheet(sheetname)
        sheet2 = workbook2[sheetname]
        reslist=sheet2list(sheet)
        reslist[0]=['目录结构','左句子','左实体','左实体标签','关系','右实体','右实体标签','右边句子','整句话']
        for i in range(1,len(reslist)):
            reslist[i][0],reslist[i][1],reslist[i][2],reslist[i][3],reslist[i][4],reslist[i][5],reslist[i][6]=reslist[i][6],reslist[i][0],reslist[i][1],reslist[i][2],reslist[i][4],reslist[i][3],reslist[i][5]
            str1=''
            str2=''
            for unity in unitylist:
                if unity in reslist[i][leftunity]:
                    str1+=unity+' '
                if unity in reslist[i][rightunity]:
                    str2 += unity + ' '
            reslist[i].insert(3,str1)
            reslist[i].insert(5,str2)
        Write2sheet(reslist, sheet2)
    sheet = workbook2['Sheet']
    workbook2.remove(sheet)
    workbook2.save(outfile)
def process6(infile, outfile):
    #删去条目较少的sheet
    workbook = openpyxl.load_workbook(infile)
    workbook2 = openpyxl.Workbook()
    sheetlist = workbook.get_sheet_names()
    tmplist=csv2list(r'../利用聚类的关系提取/聚类.csv')
    tmpf = open(r'../利用聚类的关系提取/聚类_删去部分sheet.csv', 'w', encoding='utf-8-sig', newline='')
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


def main(infile,tmp,outfile):
    '''
    :param infile:输入文件
    :param tmp: 缓冲目录
    :param outfile: 输出文件
    :return:
    '''
    path=tmp
    process1(infile,path+'三元组_分析.csv')
    print('第一步完成\n')
    process2(path+'三元组_分析.csv',path+'三元组_筛选.csv')
    print('第二步完成\n')
    clu(path+'三元组_筛选.csv', path+'聚类.csv')
    print('第三步完成\n')
    process4(path + '聚类.csv', path + '三元组_聚类.xlsx', path + '三元组_筛选.csv')
    print('第四步完成\n')
    process5(path + '三元组_聚类.xlsx', path + '三元组_结果.xlsx')
    print('第五步完成\n')
    process6(path + '三元组_结果.xlsx', path + '三元组_结果_删去部分sheet.xlsx')
    print('第六步完成\n')
    process7(path + '三元组_结果_删去部分sheet.xlsx', r'../dicts/dicts_dict.txt', outfile)
    print('第七步完成\n')
if __name__ == "__main__":
    main(r'../利用聚类的关系提取/目录结构_短句.csv',r'../利用聚类的关系提取/',r'../利用聚类的关系提取/三元组_结果__删去部分sheet_实体.xlsx')
    #process1(r'../利用聚类的关系提取/目录结构_短句.csv', r'../利用聚类的关系提取/三元组_中间结果.csv')
    #process2(r'../利用聚类的关系提取/三元组_中间结果.csv', r'../利用聚类的关系提取/三元组_筛选.csv')