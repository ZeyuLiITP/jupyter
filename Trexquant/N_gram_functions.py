import urllib
import re
import random
import string
import operator
from collections import Counter,defaultdict
import numpy as np

def text_filter(text: str) -> str:
    """
    文本过滤器：过滤掉文本数据中的标点符号和其他特殊字符
    :param text: 待过滤的文本
    :return: 过滤后的文本
    """
    # 使用正则表达式去除标点符号和其他特殊字符
    cleaned_text = re.sub(r'[^\w\s]', '', text)
    
    # 将过滤后的文本转换为小写
    cleaned_text = cleaned_text.lower()
    
    return cleaned_text

def slide_word(text: str, l: int = 5) -> list:
    """
    滑动取词器
    Input: text='abcd',l=2
    Output: ['ab','bc','cd']
    :param text: 过滤后的文本 （只包含小写数字/字母）
    :param l: 滑动窗口长度，默认为 5
    :return:
    """
    # 使用正则表达式去除标点符号和其他特殊字符
    tf = re.sub(r'[^\w\s]', '', text)
    
    # 使用切片操作生成滑动窗口
    result = [tf[i:i + l] for i in range(len(tf) - l + 1)]
    
    return result


#function that calculates unigram prob:
def unigram_prob(word_list_string, used_letter_list):
    deleted_string = word_list_string
    for used_letter in used_letter_list:
        #delete the letters which are used 
        deleted_string = re.sub(used_letter,'',deleted_string)
        
    deleted_string_len = len(deleted_string)
    uniproblist = defaultdict(float);
    count_letter = Counter(deleted_string).most_common();
    
    for letter , number in count_letter :
        uniproblist[letter] = number/deleted_string_len
        
    return uniproblist


def bigramprob(bigram_pattern, bigram_count):
    '''
    given a bigram_pattern , output the possibility for each letter in the masked letter 
    '''
    
    knownletter = re.sub('\.','',bigram_pattern)
    bigram_pattern_matched = list(filter(lambda x: ((re.match(bigram_pattern,x[0])) and ((not (re.match(knownletter+knownletter,x[0]))))),bigram_count))

    bigramproblist = defaultdict(float);
    total_len = sum([ii[1] for ii in bigram_pattern_matched]);
    
    for bigram , number in bigram_pattern_matched :
        bigramproblist[re.sub(knownletter,'',bigram)] = number/total_len
        
    return bigramproblist


def possible_pattern_exact_pos(word,pos,n):
    '''
    give a masked word , and output all possible n-gram pattern for a exact masked letter 
    '''
    shift = n-1
    word_last_pos = len(word) - 1; 
    start = pos - shift;
    start_list = list(range(start,start+n))
    slice_list = [list(range(i,i+n)) for i in start_list ]
    slice_list = list(filter((lambda x: x[0]>=0 and x[-1]<=word_last_pos) ,slice_list));
    pattern_list = []
    for poslist in slice_list:
        pattern = '';
        for pos in poslist:
            pattern += word[pos]
        
        pattern_list.append(pattern)
        
    pattern_list = list(filter(lambda x: x.count('.') == 1 ,pattern_list))
    return pattern_list

#for a given masked word, we anaylse each masked letter's possion n-gram 


def possible_pattern(word):
    mask_id = [];
    for i in range(len(word)):
        if word[i] == '.':
            mask_id.append(i)
            
    pattern_list_all = [[] for i in mask_id];
    
    for inx , i in enumerate(mask_id):
        for n in range(1,3):
            pattern_list = possible_pattern_exact_pos(word,i,n)
            if pattern_list != []:
                pattern_list_all[inx] += pattern_list
                
        pattern_list_all[inx] = [(i,j) for j in pattern_list_all[inx]]
            
    return pattern_list_all


#define a fucntion that can calculate the posibility for fix pos
def prob_fix_pos(pattern_list:list,unigram_prob_list,bigram_count):
    unigram_case = list(filter(lambda x: len(x[1])==1,pattern_list))
    bigram_case = list(filter(lambda x: len(x[1])==2,pattern_list))
    
    bigram_prob_list = []
    for i, pattern in bigram_case:
        bigram_prob_list.append( bigramprob(pattern,bigram_count))
    
    ngram_prob_list = defaultdict(float);
    bigram_prob_list_ave = defaultdict(float);
    
    if len(bigram_prob_list) == 1:
        bigram_prob_list_ave = bigram_prob_list[0]
        
        
    elif len(bigram_prob_list) > 1:
        for key in bigram_prob_list[0]:
            num = 0;
            for i in range(len(bigram_prob_list)):
                 num += bigram_prob_list[i][key]
                    
            bigram_prob_list_ave[key] = num/len(bigram_prob_list)
                
    if bigram_prob_list_ave == {}:
        ngram_prob_list = unigram_prob_list
        
    else:
        for key in unigram_prob_list.keys():
            ngram_prob_list[key] = 0.3*unigram_prob_list[key] + 0.7*bigram_prob_list_ave[key]
    
    return ngram_prob_list


def guess_letter(allpattern,unigram_prob_list,bigram_count):
    letter_prob_dic_list = [];
    
    for i in allpattern:
        letter_prob_dic_list.append(prob_fix_pos(i,unigram_prob_list,bigram_count))
        
    letter_prob_list = defaultdict(float);
    
    for key in letter_prob_dic_list[0].keys():
        for i in range(len(letter_prob_dic_list)):
            letter_prob_list[key] += letter_prob_dic_list[i][key]
            
    letter_prob_list = sorted(letter_prob_list.items(), key = lambda item: item[1],reverse=True)
    
    return letter_prob_list[0][0]