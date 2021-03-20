'''
@Author: wxin
@Date: 2020-04-01 15:44:25
@LastEditTime: 2020-04-02 10:15:12
@LastEditors: Please set LastEditors
@Description: 关于依存树的class
@FilePath: /关系抽取/NLP.py
'''
'''
做了修改，变更了子树中节点的结构，从namedturple改为class便于debug
'''
from pyhanlp import *
import os
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer
from nltk import Tree
from nltk import DependencyGraph
from nltk.draw.util import CanvasFrame
from nltk.draw import TreeWidget
from nltk.draw import TreeView
from collections import namedtuple
from tqdm import tqdm
from tools import *

# 根据自己的模型位置进行更改
MODELDIR = "/Users/wangxin/Packages/ltp_data"


class DepTree():
    # 包含words以及arcs的一个类，可以绘制依存树以及其它功能
    def __init__(self):
        self.words = []
        self.arcs = []
        self.postags = []

    def parse(self, sentence):
        pass

    def _check(self):
        # 检查是否调用过parse函数
        if len(self.words) == 0:
            print('please call the function parse first')
            return True

    def _get_root(self):
        for i in range(len(self.arcs)):
            if self.arcs[i].head == 0:
                return i

    def extract_svb(self):
        # 对当前words以及arcs
        if self._check():
            return None
        sbvs, vobs = [], []
        for i in range(len(self.arcs)):
            if self.arcs[i].relation == 'SBV':
                sbvs.append(self.words[i])
            elif self.arcs[i].relation == 'VOB':
                vobs.append(self.ords[i])
        return sbvs, vobs

    def build_dep_graph(self):
        if self._check():
            return None
        par_result = ''
        for i in range(len(self.words)):
            if self.arcs[i].head == 0:
                pass
                # self.arcs[i].relation = "ROOT"
            par_result += "\t" + self.words[i] + "(" + self.arcs[i].relation + ")" + "\t" + self.postags[
                i] + "\t" + str(self.arcs[i].head) + "\t" + self.arcs[i].relation + "\n"
        # print(par_result)
        conlltree = DependencyGraph(par_result)  # 转换为依存句法图
        tree = conlltree.tree()  # 构建树结构
        tree.draw()  # 显示输出的树

    def _build_subtree(self, node_index):
        # 从node_index建立子树

        #Node = namedtuple('Node', ['children', 'word', 'relation', 'index'])
        class Node():
            def __init__(self,children,word,relation,index):
                self.children=children
                self.word=word
                self.relation=relation
                self.index=index
        def get_children(node_index):
            # 获取某个节点的所有孩子节点的index
            children = []
            for i in range(len(self.arcs)):
                if self.arcs[i].head - 1 == node_index:
                    children.append(i)
            return children

        children = get_children(node_index)
        node_word = self.words[node_index]
        node_relation = self.arcs[node_index].relation
        node_children = []
        for child in children:
            cnode = self._build_subtree(child)
            node_children.append(cnode)
        node = Node(node_children, node_word, node_relation, node_index)

        return node

    def _build_tree(self):
        root = self._get_root()
        return self._build_subtree(root)

    def _group_sb_obj(self):
        # 将句子中的主语宾语进行分组，并将其index存入字典中
        sb_obj_keys = ['SBV', 'VOB', 'IOB', 'FOB', 'POB']
        sb_obj_map = {}
        sb_objs = {}
        root = self._build_tree()

        def get_posterity(node):
            # 获取某个节点的所有后代节点index,包括本身
            posterity_index = [node.index]
            for child in node.children:
                posterity_index += get_posterity(child)

            return posterity_index

        def find_sb_obj(node):
            # 寻找所有某条路径上"第一次出现"的sbj,obj
            if node.relation in sb_obj_keys:
                key = node.relation
                if key not in sb_objs:
                    sb_objs[key] = []
                sb_objs[key].append(node)
                return None
            for child in node.children:
                find_sb_obj(child)

        find_sb_obj(root)
        for key in sb_objs:
            for node in sb_objs[key]:
                posterity_index = get_posterity(node)
                posterity_index.sort()
                # print(posterity_index)
                if key not in sb_obj_map:
                    sb_obj_map[key] = []
                head_index = self.arcs[node.index].head - 1
                sb_obj_map[key].append((head_index, posterity_index))

        return sb_obj_map

    def get_sb_obj_phrases(self):
        # 获取句子中所有主宾语短语
        if self._check():
            return None
        sb_obj_map = self._group_sb_obj()
        sb_obj_phrases = {}
        for key in sb_obj_map:
            for group_item in sb_obj_map[key]:
                head_index, posterity_index = group_item
                imin, imax = posterity_index[0], posterity_index[-1] + 1
                phrase = ''.join(self.words[imin:imax])
                head = self.words[head_index]
                if key not in sb_obj_phrases:
                    sb_obj_phrases[key] = []
                sb_obj_phrases[key].append((head, phrase))

        return sb_obj_phrases

    def to_nltk_tree(self, node_index):
        if self._check():
            return None
        children = []
        noed_desc = self.words[node_index]
        for i in range(len(self.arcs)):
            print(self.words[i], self.arcs[i].head)
            if self.arcs[i].head - 1 == node_index:
                children.append(i)
        print(children)
        if len(children) > 0:
            return Tree(noed_desc, [to_nltk_tree(child) for child in children])
        else:
            return noed_desc

    def get_tag_words(self):
        # 返回list((word,tag))
        word_tag = []
        for word, tag in zip(self.words, self.postags):
            word_tag.append((word, tag))

        return word_tag


class LtpTree(DepTree):
    def __init__(self, dict_path=None):
        super(DepTree, self).__init__()
        print("正在加载LTP模型... ...")
        self.segmentor = Segmentor()
        if dict_path is None:
            self.segmentor.load(os.path.join(MODELDIR, "cws.model"))
        else:
            self.segmentor.load_with_lexicon(os.path.join(MODELDIR, "cws.model"), dict_path)
        self.postagger = Postagger()
        self.postagger.load(os.path.join(MODELDIR, "pos.model"))
        self.parser = Parser()
        self.parser.load(os.path.join(MODELDIR, "parser.model"))
        print("加载模型完毕。")

    def parse(self, sentence):
        self.words = self.segmentor.segment(sentence)
        self.postags = self.postagger.postag(self.words)
        self.arcs = self.parser.parse(self.words, self.postags)
        for i in range(len(self.words)):
            if self.arcs[i].head == 0:
                self.arcs[i].relation = "ROOT"

    def release_model(self):
        # 释放模型
        self.segmentor.release()
        self.postagger.release()
        self.parser.release()


class HanlpTree(DepTree):
    def __init__(self):
        super(HanlpTree, self).__init__()
        self.sentence = None

    def parse(self, sentence):
        arc = namedtuple('acr', ['relation', 'head'])
        self.sentence = HanLP.parseDependency(sentence)
        for word in self.sentence.iterator():
            # 初始化self.words, self.arcs
            self.words.append(word.LEMMA)
            head = word.HEAD.ID
            dep_tag = word.DEPREL
            realtion = self._trans_tag(dep_tag) if head != 0 else "ROOT"
            node = arc(realtion, head)
            self.arcs.append(node)
            self.postags.append(word.POSTAG)

    def _trans_tag(self, tag):
        # hanlp的语法依存分析使用的符号是中文符号，为了与pyltp一致需要进行转换
        # 参考：https://ltp.readthedocs.io/zh_CN/latest/appendix.html#id5
        trans_dict = {'主谓关系': 'SBV', '动宾关系': 'VOB', '间宾关系': 'IOB', '前置宾语': 'FOB', '兼语': 'DBL', '定中关系': 'ATT',
                      '状中结构': 'ADV', '动补结构': 'CMP', '并列关系': 'COO', '介宾关系': 'POB', '左附加关系': 'LAD', '右附加关系': 'RAD',
                      '独立结构': 'IS', '核心关系': 'HED'}
        if tag in trans_dict:
            return trans_dict[tag]
        return tag

    def extract_entity(self):
        # 利用词典抽取出目前句子中的相关实体
        # 词典中的实体词性标注为nh，在hanlp中标识为医药疾病等健康相关名词
        # 参考：https://www.hankcs.com/nlp/part-of-speech-tagging.html#h2-8
        # return: list, 包含所有相关实体
        entities = []
        if self._check():
            return None
        for word, postag in zip(self.words, self.postags):
            # print(word, postag)
            if postag == 'nh':
                entities.append(word)
        return entities
