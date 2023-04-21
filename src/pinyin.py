from __future__ import annotations
import os, math, json
from pathlib import Path
from typing import List, Dict, Callable
from tqdm import tqdm
from models import BinaryModel, TripleModel
from argparse import ArgumentParser

ROOT = Path(__file__).parent.parent

def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "-i", "--input",
        type=str,
        dest="input",
        help="Input pinyin file path",
        default="../data/input.txt"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        dest="output",
        help="Output file path",
        default="../data/output.txt"
    )
    parser.add_argument(
        "-d","--std-output",
        type=str,
        dest="std_output",
        help="Standard output file (answer) path",
        default="../data/std_output.txt"
    )
    parser.add_argument(
        "-c","--corpus",
        type=str,
        dest="corpus",
        help="Corpus data to be used",
        default=""
    )
    parser.add_argument(
        "-m", "--model",
        type=int,
        choices=[2, 3],
        dest="model",
        help="Model type: Binary Model (2) / Triple Model (3)",
        default=2
    )
    parser.add_argument(
        "-k",
        type=int,
        dest="k",
        help="Top k choice",
        default=3
    )
    parser.add_argument(
        "-a", "--alpha",
        type=float,
        dest="alpha",
        help="Smoothing factor in Binary Model",
        default=0.99999
    )
    parser.add_argument(
        "-b","--beta",
        type=float,
        dest="beta",
        help="Smoothing factor in Triple Model",
        default=0.9
    )
    parser.add_argument(
        "-t","--total",
        type=int,
        dest="total",
        help="Estimated total character number in the training corpus",
        default=1000000
    )
    args = parser.parse_args()
    return args.input, args.output, args.std_output, args.corpus, args.model, args.k, args.alpha, args.beta, args.total

if __name__ == "__main__":
    input, output, std_output, corpus, model_type, k, alpha, beta, total = parse_args()
    input, output, std_output = Path(input), Path(output), Path(std_output)
    data_path = ROOT / "src"
    if corpus:
        data_path = data_path / corpus
    if model_type == 2:
        model = BinaryModel(k, alpha, total, data_path)
    else:
        assert model_type == 3
        model = TripleModel(k, alpha, beta, total, data_path)
    correct_char_count, correct_line_count_top1, correct_line_count_topk = 0, 0, 0
    total_char, total_line = 0, 0
    
    with open(input, "r") as fin:
        with open(output, "w") as fout:
            with open(std_output, "r", encoding="utf8") as std:
                for line in tqdm(fin.readlines()):
                    model.reset()
                    results = model.inference(line.strip().split(" "))
                    answer = std.readline().strip()
                    
                    total_line += 1
                    correct_line_count_top1 += (results[0] == answer)
                    correct_line_count_topk += sum(result == answer for result in results)
                    total_char += len(answer)
                    correct_char_count += sum(map(lambda c1, c2: c1 == c2, results[0], answer))
                    
                    if k == 1:
                        fout.write(str(results[0]) + '\n')
                    else:
                        fout.write(str(results) + '\n')
                
    print(f"字准确率：{(correct_char_count / total_char) * 100:.2f}%")
    print(f"Top1句准确率：{(correct_line_count_top1 / total_line) * 100:.2f}%")
    print(f"Top{k}句准确率：{(correct_line_count_topk / total_line) * 100:.2f}%")