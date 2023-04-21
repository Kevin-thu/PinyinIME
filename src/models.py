from __future__ import annotations
import os, math, json
from pathlib import Path
from typing import List, Dict
import pickle as pk
import abc

ROOT = Path(__file__).parent.parent

class CharNode:
    def __init__(self, char: str, topk_path: Dict[str, float] = {}) -> None:
        self.char = char
        self.topk_path = topk_path

class PinyinIMEModel(metaclass=abc.ABCMeta):
    def __init__(self, k: int = 1, total: int = 100000, data_path: Path = ROOT / "src") -> None:
        self.k = k
        self.total = total
        self.node_layer: List[CharNode] = [CharNode('<start>', {"": 0})]
        with open(data_path / "PINYIN_TABLE.pk", "rb") as f:
            self.PINYIN_TABLE: Dict[str, List[str]] = pk.load(f)
        with open(data_path / "CHAR_FREQ_TABLE.pk", "rb") as f:
            self.CHAR_FREQ_TABLE: Dict[str, int] = pk.load(f)
        
    def reset(self):
        self.node_layer: List[CharNode] = [CharNode('<start>', {"": 0})]
       
    @abc.abstractmethod
    def calc_path_cost(self, last_node: CharNode, cur_node: CharNode) -> float:
        pass   
    
    @abc.abstractmethod
    def inference(self, pinyin_sentence: List[str]) -> List[str]:
        pass

class BinaryModel(PinyinIMEModel):
    def __init__(self, k: int = 1, alpha: float = 0.99999, total: int = 100000, data_path: Path = ROOT / "src") -> None:
        super().__init__(k, total, data_path)
        self.alpha = alpha
        with open(data_path / "binary_freq_table.pk", "rb") as f:
            self.BINARY_FREQ_TABLE: Dict[str, Dict[str, int]] = pk.load(f)

    def calc_path_cost_wo_smoothing(self, last_node: CharNode, cur_node: CharNode) -> float:
        try:
            return -math.log(self.BINARY_FREQ_TABLE[last_node.char][cur_node.char] / self.CHAR_FREQ_TABLE[last_node.char])
        except KeyError:
            return math.inf
    
    def calc_path_cost(self, last_node: CharNode, cur_node: CharNode) -> float:
        '''
        Corpus: sina_news_gbk
        字准确率：84.47%
        Top1句准确率：40.92%
        Top3句准确率：58.28%   (~15s)
        Top5句准确率：63.67%
        Top10句准确率：68.66%  (~1min)

        Corpus: sina_news_gbk + baike_qa2019
        字准确率：84.97%    
        Top1句准确率：41.92%
        Top3句准确率：60.68%
        Top5句准确率：66.07%
        Top10句准确率：71.06%
        '''
        try:
            p_cur_on_last = self.BINARY_FREQ_TABLE[last_node.char][cur_node.char] / self.CHAR_FREQ_TABLE[last_node.char]
        except KeyError:
            p_cur_on_last = 0
        p_cur = self.CHAR_FREQ_TABLE[cur_node.char] / self.total if cur_node.char != '<end>' else 0
        try:
            return -math.log(self.alpha * p_cur_on_last + (1 - self.alpha) * p_cur)
        except ValueError:
            return math.inf
    
    def inference(self, pinyin_sentence: List[str]) -> List[str]:
        if not pinyin_sentence:             
            return []         
        pinyin_sentence.append('<end>')
        for pinyin in pinyin_sentence:
            new_node_layer: List[CharNode] = list(map(lambda char: CharNode(char, {}), self.PINYIN_TABLE[pinyin]))             
            for node in new_node_layer:                 
                for last_node in self.node_layer:                     
                    path_cost = self.calc_path_cost(last_node, node) 
                    if path_cost == math.inf:
                        continue                   
                    # dict将元组映射成字典中的键值对，实现对原始dict中的键、值同时更新的映射                     
                    update_topk_path = dict(map(lambda path, value: (path + node.char, value + path_cost), \
                                                 last_node.topk_path.keys(), last_node.topk_path.values()))                     
                    # 字典的或运算 <=> 求并                     
                    node.topk_path |= update_topk_path                 
                # 将字典中的元素按值从小到大排序：利用key=lambda函数给出排序准则                 
                node.topk_path = dict(sorted(node.topk_path.items(), key=lambda item: item[1]))                 
                if len(node.topk_path) > self.k:                     
                    # 取出字典topk项：.items -> slice -> dict                     
                    node.topk_path = dict(list(node.topk_path.items())[:self.k])                 
            self.node_layer = new_node_layer         
        end_node = self.node_layer[0]         
        # print(list(map(lambda key: key.strip("<end>"), end_node.topk_path.keys())))        
        return list(map(lambda key: key.strip('<end>'), end_node.topk_path.keys()))
    
class TripleModel(BinaryModel):
    def __init__(self, k: int = 1, alpha: float = 0.99999, beta: float = 0.9, total: int = 100000, data_path: Path = ROOT / "src") -> None:
        super().__init__(k, alpha, total, data_path)
        self.beta = beta
        with open(data_path / "triple_freq_table.pk", "rb") as f:
            self.TRIPLE_FREQ_TABLE: Dict[str, Dict[str, Dict[str, int]]] = pk.load(f)
    
    def calc_path_cost_wo_smoothing(self, last_node: CharNode, cur_node: CharNode) -> float:
        try:
            if last_node.char == '<start>':
                return -math.log(sum(self.TRIPLE_FREQ_TABLE['<start>'][cur_node.char].values()) / self.CHAR_FREQ_TABLE['<start>'])
            elif last_node.char.startswith('<start>'):
                return -math.log(self.TRIPLE_FREQ_TABLE['<start>'][last_node.char.strip('<start>')][cur_node.char] \
                            / sum(self.TRIPLE_FREQ_TABLE['<start>'][last_node.char.strip('<start>')].values()))
            else:
                return -math.log(self.TRIPLE_FREQ_TABLE[last_node.char[0]][last_node.char[1]][cur_node.char] \
                            / sum(self.TRIPLE_FREQ_TABLE[last_node.char[0]][last_node.char[1]].values()))
        except KeyError:
            return math.inf
    
    def calc_path_cost(self, last_node: CharNode, cur_node: CharNode) -> float:
        '''
        Corpus: sina_news_gbk
        字准确率：93.45%
        Top1句准确率：72.26%  (~8min)
        Top3句准确率：82.04%  (~13min)
        Top5句准确率：84.63% (~20min)
        '''
        last_first = last_node.char[0] if not last_node.char.startswith('<start>') else '<start>'
        last_second = last_node.char[-1] if last_node.char != '<start>' else '<start>'
        try:
            p_cur_on_last_two = self.TRIPLE_FREQ_TABLE[last_first][last_second][cur_node.char] / self.BINARY_FREQ_TABLE[last_first][last_second]
        except KeyError:
            p_cur_on_last_two = 0
        try:
            p_cur_on_last = self.BINARY_FREQ_TABLE[last_second][cur_node.char] / self.CHAR_FREQ_TABLE[last_second]
        except KeyError:
            p_cur_on_last = 0
        p_cur = self.CHAR_FREQ_TABLE[cur_node.char] / self.total if cur_node.char != '<end>' else 0
        p_bin = self.alpha * p_cur_on_last + (1 - self.alpha) * p_cur
        try:
            if last_node.char == '<start>':
                return -math.log(p_bin)
            else:
                return -math.log(self.beta * p_cur_on_last_two + (1 - self.beta) * p_bin)
        except ValueError:
            return math.inf
        
    def inference(self, pinyin_sentence: List[str]) -> List[str]:
        if not pinyin_sentence:
            return []
        pinyin_sentence.append('<end>')
        for pinyin in pinyin_sentence:
            single_node_layer: List[CharNode] = list(map(lambda char: CharNode(char, {}), self.PINYIN_TABLE[pinyin]))
            new_node_layer_dict: Dict[str, CharNode] = {}
            for node in single_node_layer:
                for last_node in self.node_layer:
                    path_cost = self.calc_path_cost(last_node, node)
                    if path_cost == math.inf:
                        continue
                    update_topk_path = dict(map(lambda path, value: (path + node.char, value + path_cost), \
                                                last_node.topk_path.keys(), last_node.topk_path.values()))
                    if last_node.char == '<start>':
                        next_char = last_node.char + node.char
                    elif node.char == '<end>':  # 注意单独处理终止节点的char，保证全都收束到一个<end>
                        next_char = node.char
                    else:
                        next_char = last_node.char[-1] + node.char
                    if next_char in new_node_layer_dict:
                        new_node_layer_dict[next_char].topk_path |= update_topk_path
                    else:
                        new_node_layer_dict[next_char] = CharNode(next_char, update_topk_path)
            new_node_layer = list(new_node_layer_dict.values())
            for node in new_node_layer:
                node.topk_path = dict(sorted(node.topk_path.items(), key=lambda item: item[1]))
                if len(node.topk_path) > self.k:
                    node.topk_path = dict(list(node.topk_path.items())[:self.k])
            self.node_layer = new_node_layer
        end_node = self.node_layer[0]
        # print(list(map(lambda key: key.strip("<end>"), end_node.topk_path.keys())))
        return list(map(lambda key: key.strip("<end>"), end_node.topk_path.keys()))
