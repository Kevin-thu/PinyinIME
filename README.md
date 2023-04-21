# IAI 2023 Project: PinyinIME
> Kevin Zhang @ THU CST 2023 spring

## File structrue
```
│  README.md
│  REPORT.md
│  REPORT.pdf
│  
├─assets
│      binary.jpg
│      topk.png
│      triple.jpg
│      
├─corpus
│  ├─baike_qa2019
│  ├─sina_news_gbk
│  └─SMP2020
├─data
│      input.txt
│      output_binary.txt
│      output_bin_top10.txt
│      output_bin_top3.txt
│      output_triple.txt
│      std_output.txt
│      
├─example
│      input.txt
│      output.txt
│      README.txt
│      
├─src
│  │  binary_freq_table.pk
│  │  binary_freq_table_compress.pk
│  │  char_freq_table.pk
│  │  dataprocess.py
│  │  models.py
│  │  pinyin.py
│  │  pinyin_table.pk
│  │  plot.py
│  │  
│  ├─baike_qa2019
│  ├─combinition
│  └─sina_news_gbk
└─table
        README.txt
        一二级汉字表.txt
        拼音汉字表.txt
```
The freqency tables in `src` has been uploaded to [https://cloud.tsinghua.edu.cn/d/56fe2650c62b4022a4ec/](https://cloud.tsinghua.edu.cn/d/56fe2650c62b4022a4ec/). Please download to the correspondent path and use `-c` when runing `pinyin.py` to specifify which corpus data you want to use.

## Usage

### Data preprocess: build frequency table
`dataprocess.py` is a Python script that processes Chinese text data and builds frequency tables for Chinese characters and pinyin. This script takes in a corpus of Chinese text data and outputs binary and triple frequency tables for the characters in the corpus, as well as a Pinyin-to-Chinese character correspondence table.

To run `dataprocess.py`, navigate to the directory containing the script and run the following command:
```bash
python dataprocess.py --corpus <corpus_name> --keys <key1> <key2> ... --encoding <encoding> --table <table_path>
```
where:

+ `<corpus_name>` is the name of the corpus to be processed. This should be the name of a directory in the corpus folder.
+ `<key1> <key2> ...` are the keys in the corpus JSON files that contain the text data to be processed. These should be specified as separate arguments.
+ `<encoding>` is the encoding of the corpus files. This should be specified as a string, e.g. "gbk".
+ `<table_path>` is the path to a directory containing a pre-built character frequency table. This is an optional argument.

The script will output the following files in the `src/<corpus_name>` directory:

+ `binary_freq_table.pk`: a binary frequency table for the characters in the corpus.
+ `triple_freq_table.pk`: a triple frequency table for the characters in the corpus.
+ `binary_freq_table_compress.pk`: a compressed version of the binary frequency table.
+ `triple_freq_table_compress.pk`: a compressed version of the triple frequency table.
+ `char_freq_table.pk`: a frequency table for the characters in the corpus.
+ `pinyin_table.pk`: a Pinyin-to-Chinese character correspondence table.

Example:

To process the sina_news_gbk corpus with the title and html keys, using gbk encoding and a pre-built character frequency table located at ./table/, run the following command:
```bash
python dataprocess.py --corpus sina_news_gbk --keys title html --encoding gbk --table ./table
```

### Inference
`pinyin.py` is designed to take in a pinyin file and output a file with the top k choices for each pinyin input. The program uses either a binary or triple HMM model to make these predictions.

To run the program, navigate to the directory containing the pinyin.py file and run the following command:
```bash
python pinyin.py -i <input_file_path> -o <output_file_path> -d <standard_output_file_path> -m <model_type> -k <top_k> -a <alpha> -b <beta> -t <total_char_count>
```

The arguments are as follows:

+ `-i` or `--input`: Specifies the path to the input pinyin file. Default is `../data/input.txt`.
+ `-o` or `--output`: Specifies the path to the output file. Default is `../data/output.txt`.
+ `-d` or `--std-output`: Specifies the path to the standard output file (answer). Default is `../data/std_output.txt`.
+ `-c` or `--corpus`: Specifies the name of the corpus to be used for inference.
+ `-m` or `--model`: Specifies the type of model to use. Options are Binary Model (2) or Triple Model (3). Default is 2.
+ `-k`: Specifies the top k choice. Default is 3.
+ `-a` or `--alpha`: Specifies the smoothing factor in Binary Model. Default is 0.99999.
+ `-b` or `--beta`: Specifies the smoothing factor in Triple Model. Default is 0.9.
+ `-t` or `--total`: Specifies the estimated total character number in the training corpus. Default is 100000.

Example:
Here is an example of how to run the program with custom parameters:
```bash
python pinyin.py -i path/to/input.txt -o path/to/output.txt -d path/to/std_output.txt -c sina_news_gbk -m 3 -k 5 -a 0.999 -b 0.8 -t 50000
```

This will run the program with the following parameters:

+ Input file path: `path/to/input.txt`
+ Output file path: `path/to/output.txt`
+ Standard output file path: `path/to/std_output.txt`
+ Frequency tables from corpus: `sina_news_gbk`
+ Model type: Triple Model
+ Top k choice: 5
+ Smoothing factor in Binary Model: 0.999
+ Smoothing factor in Triple Model: 0.8
+ Estimated total character number in the training corpus: 50000

Besides output predictions, the programe will also print word accuracy, top1 sentence accurace and topk sentence accuracy in the console.