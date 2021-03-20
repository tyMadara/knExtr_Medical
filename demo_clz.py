'''
@Author: wxin
@Date: 2020-04-02 09:53:06
@LastEditTime: 2020-04-02 10:15:42
@LastEditors: Please set LastEditors
@Description: 测试模块
@FilePath: /关系抽取/demo.py
'''
from DepTree_clz import *

sentence = '定位扫描像有时可代替普通X线片，供诊断参考。'

def ltp_test():
    # 测试LtpTree
    dict_path = '../dicts/dict.txt'
    ltp = LtpTree(dict_path)
    # 也可以不指定dict_path
    ltp.parse(sentence)
    # 在进行其它函数操作前需要先进行parse操作
    print('分词以及词性:', ltp.get_tag_words())
    # 测试获取分词&词性list函数
    print('主、宾语短语:', ltp.get_sb_obj_phrases())
    # 测试获取主宾语函数
    ltp.build_dep_graph()
    # 测试依存树绘制函数
    ltp.release_model()
    # 对于LtpTree，在结束所有操作后需要释放模型

def hlp_test():
    # 测试HanlpTree
    hlp = HanlpTree()
    hlp.parse(sentence)
    # 在进行其它函数操作前需要先进行parse操作
    print('分词以及词性:', hlp.get_tag_words())
    # 测试获取分词&词性list函数
    print('主、宾语短语:', hlp.get_sb_obj_phrases())
    # 测试获取主宾语函数
    print('词典相关词语:', hlp.extract_entity())
    # 测试获取词典相关词函数
    hlp.build_dep_graph()
    # 测试依存树绘制函数

if __name__ == "__main__":
    hlp_test()
    #ltp_test()