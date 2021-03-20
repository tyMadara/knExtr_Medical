from passage_extract import *

def readfromdict(infile):
    dict=[]
    with open(infile, 'r', encoding='utf-8') as ifh:
        for line in ifh.readlines():
           dict.append(line[:-3])
    return dict
def make_train_test_data(infile,indict,trainfile,testfile):
    dict=readfromdict(indict)
    max_len=max(len(ele) for ele in dict)

    sentences=sentence_Readfromtxt(infile)
    with open(trainfile,'w',encoding='utf-8') as trainfh:
        with open(testfile,'w',encoding='utf-8') as testfh:
            flaglist=[]
            for sentence in sentences:
                sentence = sentence.strip().replace('\t', '')
                sen_len = len(sentence)
                loc = 0
                length = min(max_len, sen_len - loc)
                while (sen_len != loc):
                    if length == 1:
                        loc += 1
                        length = min(max_len, sen_len - loc)
                    elif sentence[loc:loc + length] in dict:
                        flaglist.append(1)
                        break
                    else:
                        length -= 1
                if sen_len==loc:
                    #print(sentence)
                    flaglist.append(0)

            j=0
            for sentence in sentences:
                flag=flaglist[j]
                j+=1
                print('处理第',j,'句')
                sentence=sentence.strip().replace('\t','')
                sen_len=len(sentence)
                loc = 0
                length=min(max_len,sen_len-loc)
                while(sen_len!=loc):
                    if length==1:
                        #print(line[loc]+'\tO\n')
                        if flag==1:
                            trainfh.write(sentence[loc]+'\tO\n')
                        else:
                            testfh.write(sentence[loc]+'\tB\n')
                        loc+=1
                        length=min(max_len,sen_len-loc)
                    elif sentence[loc:loc+length] in dict:
                        for i in range(length):
                            if i==0:
                                trainfh.write(sentence[loc+i]+'\tB\n')
                            elif i==length-1:
                                trainfh.write(sentence[loc+i]+'\tE\n')
                            else:
                                trainfh.write(sentence[loc+i]+'\tM\n')
                        loc+=length
                        length = min(max_len, sen_len - loc)
                    else:
                        length-=1

    return
def write_CRFresult2txt(infile,outfile):
    entity=[]
    s=''
    uList=[]
    with open(infile, 'r', encoding='utf-8') as ifh:
        with open(outfile, 'w', encoding='utf-8') as ofh:
            for line in ifh.readlines():
                if line.strip()!='':
                    if line[-2] in ['B','M']:
                        entity.append(line[0])
                    elif line[-2]=='E':
                        entity.append(line[0])
                        s=''
                        for char in entity:
                            s+=char
                        uList=ulist_Addunity(uList, unity(s))
                        entity=[]
    ulisttxt_Writefromulist(uList, outfile)



make_train_test_data(r'..\医学相关\医学相关txt\临床营养学.txt',r'..\实体提取\临床营养学_dict.txt',r'..\实体提取\临床营养学_train.txt',r'..\实体提取\临床营养学_test.txt')
#os.system(r'D:\study\CRFtool\crf_learn.exe -f 1 -c 3.0 D:\study\CRFtool\example\seg\template ..\实体提取\临床营养学_train.data  ..\实体提取\临床营养学_crf_model')
#os.system(r'D:\study\CRFtool\crf_test.exe -m ..\实体提取\临床营养学_crf_model ..\实体提取\临床营养学_test.data >>..\实体提取\临床营养学_result.txt')
#write_CRFresult2txt(r'..\实体提取\临床营养学_result.txt',r'..\实体提取\临床营养学_CRFresult.txt')