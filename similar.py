#与同义词词林有关的算法
from collections import namedtuple
import tqdm
def read_cilin():
    #读于同义词词林
    infile=open(r'../哈工大社会计算与信息检索研究中心同义词词林扩展版/哈工大社会计算与信息检索研究中心同义词词林扩展版.txt','r')
    list=[]
    one, two, three, four, five = '', '', '', '', ''
    for line in tqdm(infile.readlines()):
        nowone,nowtwo,nowthree,nowfour,nowfive=line[0],line[1],line[2:4],line[4],line[5:7]
        if nowone!=one:
            list.append([[[[[]]]]])
        elif nowtwo!=two:
            list[-1].append([[[[]]]])
        elif nowthree!=three:
            list[-1][-1].append([[[]]])
        elif nowfour!=four:
            list[-1][-1][-1].append([[]])
        elif nowfive!=five:
            list[-1][-1][-1][-1].append([])
        kind=namedtuple('kind',['words','label'])
        list[-1][-1][-1][-1][-1]=kind(line[8:].strip().split(' '),line[7])
        one, two, three, four, five=nowone,nowtwo,nowthree,nowfour,nowfive
    return list
def similarword(word):
    #利用哈工大词林寻找近义词
    #词林每行格式为‘Aa01A01= 人 士 人物 人士 人氏 人选’
    infile = open(r'../哈工大社会计算与信息检索研究中心同义词词林扩展版/哈工大社会计算与信息检索研究中心同义词词林扩展版.txt', 'r')
    for line in infile.readlines():
        match=re.search(' '+word+' ',line[8:])
        if match!=None:
            return line[8:].strip().split(' ')
    return []