import os, json, ast
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
from tqdm import tqdm
import pickle as pk
from argparse import ArgumentParser

CHAR_FREQ_TABLE = {}
SEP = ['，', '。', '：', '、', ' ', '\n']
THERESHOLD = 2

def build_binary_freq_table(file: Path, keys: List[str], encoding="gbk", \
                          freq_table: Dict[str, Dict[str, int]]=defaultdict(lambda : defaultdict(lambda: 0))) \
        -> Dict[str, Dict[str, int]]:
    with open(file, "r", encoding=encoding) as f:
        for line in tqdm(f.readlines()):
            data = ast.literal_eval(line)
            for key in keys:
                try:
                    text = data.get(key, "")
                    if not text:
                        continue
                    text = " " + text + " "
                    for i in range(len(text)-1):
                        if text[i] in CHAR_FREQ_TABLE:
                            CHAR_FREQ_TABLE[text[i]] += 1
                        # 前后都在汉字表中
                        if text[i] in CHAR_FREQ_TABLE and text[i+1] in CHAR_FREQ_TABLE:
                            freq_table[text[i]][text[i+1]] += 1
                        # 前面字在分隔符中，后面字在汉字表中，说明后面字为句子开头
                        if text[i] in SEP and text[i+1] in CHAR_FREQ_TABLE:
                            freq_table['<start>'][text[i+1]] += 1
                        # 前面字在汉字表中，后面字在分隔符中，说明前面字为句子结尾
                        if text[i] in CHAR_FREQ_TABLE and text[i+1] in SEP:
                            freq_table[text[i]]['<end>'] += 1
                except Exception as e:
                    print(e)
                    pass
    return freq_table

def build_triple_freq_table(file: Path, keys: List[str], encoding="gbk", \
                freq_table: Dict[str, Dict[str, Dict[str, int]]]=defaultdict(lambda : defaultdict(lambda: defaultdict(lambda: 0)))) \
        -> Dict[str, Dict[str, int]]:
    with open(file, "r", encoding=encoding) as f:
        for line in tqdm(f.readlines()):
            data = ast.literal_eval(line)
            for key in keys:
                try:
                    text = data.get(key, "")
                    if not text:
                        continue
                    text = " " + text + "  "
                    for i in range(len(text)-2):
                        # if text[i] in CHAR_FREQ_TABLE:
                        #     CHAR_FREQ_TABLE[text[i]] += 1
                        if text[i] in CHAR_FREQ_TABLE and text[i+1] in CHAR_FREQ_TABLE and text[i+2] in CHAR_FREQ_TABLE:
                            freq_table[text[i]][text[i+1]][text[i+2]] += 1
                        if text[i] in SEP and text[i+1] in CHAR_FREQ_TABLE and text[i+2] in CHAR_FREQ_TABLE:
                            freq_table['<start>'][text[i+1]][text[i+2]] += 1
                        if text[i] in CHAR_FREQ_TABLE and text[i+1] in CHAR_FREQ_TABLE and text[i+2] in SEP:
                            freq_table[text[i]][text[i+1]]['<end>'] += 1
                        if text[i] in SEP and text[i+1] in CHAR_FREQ_TABLE and text[i+2] in SEP:
                            freq_table['<start>'][text[i+1]]['<end>'] += 1
                except Exception as e:
                    print(e)
                    pass
    return freq_table

def build_pinyin_table(file: Path) -> Dict[str, List[str]]:
    with open(file, "r", encoding="gbk") as f:
        PINYIN_TABLE = {line.strip().split(" ")[0]: line.strip().split(" ")[1:] for line in f.readlines()}
    return PINYIN_TABLE

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        "--corpus",
        type=str,
        dest="corpus",
        help="Corpus name",
        default="sina_news_gbk",
    )
    parser.add_argument(
        "--keys",
        type=str,
        nargs="+",
        dest="keys",
        help="Corpus keys",
        default=["title", "html"],
    )
    parser.add_argument(
        "--encoding",
        type=str,
        dest="encoding",
        help="Corpus encoding",
        default="gbk"
    )
    parser.add_argument(
        "--table",
        type=str,
        dest="table",
        help="Origin freq table path",
        default=""
    )
    args = parser.parse_args()

    ROOT = Path(__file__).parent.parent
    CORPUS_PATH = ROOT / "corpus" / args.corpus
    DATA_PATH = ROOT / "src" / args.corpus
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
    DATA_PATH_2 = Path("C:/Download")

    BIN_FREQ_TABLE_PATH = DATA_PATH / "binary_freq_table.pk"
    TRI_FREQ_TABLE_PATH = DATA_PATH / "triple_freq_table.pk"
    BIN_FREQ_TABLE_COMPRESS_PATH = DATA_PATH / "binary_freq_table_compress.pk"
    TRI_FREQ_TABLE_COMPRESS_PATH = DATA_PATH / "triple_freq_table_compress.pk"
    CHAR_TABLE_PATH = DATA_PATH / "char_freq_table.pk"
    PINYIN_TABLE_PATH = DATA_PATH / "pinyin_table.pk"

    BIN_FREQ_TABLE_PATH_2 = DATA_PATH_2 / "binary_freq_table.pk"
    TRI_FREQ_TABLE_PATH_2 = DATA_PATH_2 / "triple_freq_table.pk"
    BIN_FREQ_TABLE_COMPRESS_PATH_2 = DATA_PATH_2 / "binary_freq_table_compress.pk"
    TRI_FREQ_TABLE_COMPRESS_PATH_2 = DATA_PATH_2 / "triple_freq_table_compress.pk"
    CHAR_TABLE_PATH_2 = DATA_PATH_2 / "char_freq_table.pk"
    PINYIN_TABLE_PATH_2 = DATA_PATH_2 / "pinyin_table.pk"

    if args.table:
        TABLE_PATH = Path(args.table)
        with open(TABLE_PATH / "char_freq_table.pk", "rb") as f:
            CHAR_FREQ_TABLE = pk.load(f)
            print("Char freq table loaded")
        with open(TABLE_PATH / "binary_freq_table.pk", "rb") as f:
            bin_freq_table = pk.load(f) 
            BIN_FREQ_TABLE = defaultdict(lambda : defaultdict(lambda: 0), {k: defaultdict(lambda : 0, v) for k, v in bin_freq_table.items()})
            print("Binary freq table loaded")
        with open(TABLE_PATH / "triple_freq_table.pk", "rb") as f:
            tri_freq_table = pk.load(f)
            TRI_FREQ_TABLE = defaultdict(lambda : defaultdict(lambda: defaultdict(lambda: 0)), {k1: defaultdict(lambda: defaultdict(lambda: 0), \
                                            {k2: defaultdict(lambda: 0, v2) for k2, v2 in v1.items()}) for k1, v1 in tri_freq_table.items()})
            print("Triple freq table loaded")
    else:
        with open(ROOT / "table" / "一二级汉字表.txt", "r", encoding="gbk") as f:
            CHAR_FREQ_TABLE = dict.fromkeys(list(f.read()), 0)
        BIN_FREQ_TABLE = defaultdict(lambda : defaultdict(lambda: 0))
        TRI_FREQ_TABLE = defaultdict(lambda : defaultdict(lambda: defaultdict(lambda: 0)))

    for file in os.listdir(CORPUS_PATH):
        if "README" not in file and ".DS_Store" not in file:
            print(file)
            BIN_FREQ_TABLE = build_binary_freq_table(CORPUS_PATH / file, args.keys, args.encoding, BIN_FREQ_TABLE)
            TRI_FREQ_TABLE = build_triple_freq_table(CORPUS_PATH / file, args.keys, args.encoding, TRI_FREQ_TABLE)
            # print(dict(FREQ_TABLE['<start>']))

    BIN_FREQ_TABLE = {k: dict(BIN_FREQ_TABLE[k]) for k in BIN_FREQ_TABLE}
    TRI_FREQ_TABLE = {k: {v: dict(TRI_FREQ_TABLE[k][v]) for v in TRI_FREQ_TABLE[k]} for k in TRI_FREQ_TABLE}
    BIN_FREQ_TABLE_COMPRESS = {k: {v: BIN_FREQ_TABLE[k][v] for v in BIN_FREQ_TABLE[k] if BIN_FREQ_TABLE[k][v] > THERESHOLD} \
                                    for k in BIN_FREQ_TABLE}
    TRI_FREQ_TABLE_COMPRESS = {k: {v: {c: TRI_FREQ_TABLE[k][v][c] for c in TRI_FREQ_TABLE[k][v] if TRI_FREQ_TABLE[k][v][c] > THERESHOLD} \
                                    for v in TRI_FREQ_TABLE[k]} for k in TRI_FREQ_TABLE}
    try:
        with open(BIN_FREQ_TABLE_PATH_2, "wb") as f:
            pk.dump(BIN_FREQ_TABLE, f)
        with open(TRI_FREQ_TABLE_PATH_2, "wb") as f:
            pk.dump(TRI_FREQ_TABLE, f)
        with open(BIN_FREQ_TABLE_COMPRESS_PATH_2, "wb") as f:
            pk.dump(BIN_FREQ_TABLE_COMPRESS, f)
        with open(TRI_FREQ_TABLE_COMPRESS_PATH_2, "wb") as f:
            pk.dump(TRI_FREQ_TABLE_COMPRESS, f)
    except Exception as e:
        print("e1", e)
        pass
    try:
        with open(BIN_FREQ_TABLE_PATH, "wb") as f:
            pk.dump(BIN_FREQ_TABLE, f)
        with open(TRI_FREQ_TABLE_PATH, "wb") as f:
            pk.dump(TRI_FREQ_TABLE, f)
        with open(BIN_FREQ_TABLE_COMPRESS_PATH, "wb") as f:
            pk.dump(BIN_FREQ_TABLE_COMPRESS, f)
        with open(TRI_FREQ_TABLE_COMPRESS_PATH, "wb") as f:
            pk.dump(TRI_FREQ_TABLE_COMPRESS, f)
    except Exception as e:
        print("e2", e)
        pass
    
    PINYIN_TABLE = build_pinyin_table(ROOT / "table" / "拼音汉字表.txt")
    CHAR_FREQ_TABLE['<start>'] = sum(BIN_FREQ_TABLE['<start>'].values())
    PINYIN_TABLE['<end>'] = ['<end>']
    try:
        with open(CHAR_TABLE_PATH_2, "wb") as f:
            pk.dump(CHAR_FREQ_TABLE, f)
        with open(PINYIN_TABLE_PATH_2, "wb") as f:
            pk.dump(PINYIN_TABLE, f)
    except Exception as e:
        print("e3", e)
        pass
    try:
        with open(CHAR_TABLE_PATH, "wb") as f:
            pk.dump(CHAR_FREQ_TABLE, f)
        with open(PINYIN_TABLE_PATH, "wb") as f:
            pk.dump(PINYIN_TABLE, f)
    except Exception as e:
        print("e4", e)
        pass