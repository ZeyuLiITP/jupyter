
import urllib
import re
import random
import string
import operator
from collections import Counter,defaultdict

#function that calculates unigram prob:
def unigram_prob(word_list_string, used_letter_list):
    
    deleted_string = re.sub('[@#]','',word_list_string) #delete @ and #
    
    for used_letter in used_letter_list:
        #delete the letters which are used 
        deleted_string = re.sub(used_letter,'',deleted_string)
        
    deleted_string_len = len(deleted_string)
    uniproblist = defaultdict(float);
    count_letter = Counter(deleted_string).most_common();
    
    for letter , number in count_letter :
        uniproblist[letter] = number/deleted_string_len
        
    return uniproblist


def slide_word_with_pos(text: str, l: int = 5) -> list:
    
    text_len = len(text)
    # 使用切片操作生成滑动窗口
    result = [(tuple(range(i,i + l)), text[i:i + l] ) for i in range(text_len - l + 1)]
    
    return result


def bigramprob_with_pos(bigram_pattern_with_pos, bigram_count):
    '''
    given a bigram_pattern_with_pos '((1,2), 'a.')',
    output the possibility for each letter in the masked letter 
    '''
    pos = bigram_pattern_with_pos[0] #position tuple
    bigram_pattern = bigram_pattern_with_pos[1] #pattern
    
    knownletter = re.sub('\.','',bigram_pattern)
    
    
    bigram_pattern_matched =list(filter(lambda x: (re.match(bigram_pattern,x[0][1])) and \
                                        (not (re.match(knownletter+knownletter,x[0][1]))) and \
                                        (pos == x[0][0]), bigram_count))
    
    bigramproblist = defaultdict(float);
    total_len = sum([ii[1] for ii in bigram_pattern_matched]);
    
    for bigram , number in bigram_pattern_matched :
        bigramproblist[re.sub(knownletter,'',bigram[1])] = number/total_len
        
    return bigramproblist


def trigramprob_with_pos(trigram_pattern_with_pos, trigram_count):
    '''
    given a trigram_pattern_with_pos '((1,2,3), 'ab.')',
    output the possibility for each letter in the masked letter 
    '''
    pos = trigram_pattern_with_pos[0] #position tuple
    trigram_pattern = trigram_pattern_with_pos[1] #pattern
    
    knownletter = set(re.sub('\.','',trigram_pattern))
    
    trigram_pattern_matched = list( filter(lambda x: (pos == x[0][0]) and \
                                           (re.match(trigram_pattern,x[0][1])) and \
                                           (not set(x[0][1]).issubset(knownletter) ) , trigram_count) )
    trigramproblist = defaultdict(float);
    total_len = sum([ii[1] for ii in trigram_pattern_matched]);
    
    for trigram , number in trigram_pattern_matched :
        trigramproblist[re.sub(str(list(knownletter)) , '' ,trigram[1]) ] = number/total_len
    
    return trigramproblist

def fourgramprob_with_pos(four_gram_pattern_with_pos, four_gram_count):
    '''
    given a fourgram_pattern_with_pos '((1,2,3,4), 'abc.')',
    output the possibility for each letter in the masked letter 
    '''
    pos = four_gram_pattern_with_pos[0] #position tuple
    fourgram_pattern = four_gram_pattern_with_pos[1] #pattern
    
    knownletter = set(re.sub('\.','',fourgram_pattern))
    
    fourgram_pattern_matched = list( filter(lambda x: (pos == x[0][0]) and \
                                           (re.match(fourgram_pattern,x[0][1])) and \
                                           (not set(x[0][1]).issubset(knownletter) ) , fourgram_count) )
    
    fourgramproblist = defaultdict(float);
    total_len = sum([ii[1] for ii in fourgram_pattern_matched]);
    
    for fourgram , number in fourgram_pattern_matched :
        fourgramproblist[re.sub(str(list(knownletter)) , '' ,fourgram[1]) ] = number/total_len
    return fourgramproblist

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
        
        pattern_list.append((tuple(poslist),pattern))
        
    pattern_list = list(filter(lambda x: x[1].count('.') == 1 ,pattern_list))
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
                
        #pattern_list_all[inx] = [(i,j) for j in pattern_list_all[inx]]
            
    return pattern_list_all


#define a fucntion that can calculate the posibility for fix pos
def prob_fix_pos(pattern_list:list, unigram_prob_list, bigram_count ,trigram_count,fourgram_count):
    
    unigram_case = list(filter(lambda x: len(x[1])==1,pattern_list))
    bigram_case = list(filter(lambda x: len(x[1])==2,pattern_list)) 
    trigram_case = list(filter(lambda x: len(x[1])==3,pattern_list))
    fourgram_case = list(filter(lambda x: len(x[1])==4,pattern_list))
    
    bigram_prob_list = []
    trigram_prob_list = []
    fourgram_prob_list = []
    
    for pattern in bigram_case:
        bigram_prob_list.append( bigramprob_with_pos(pattern,bigram_count))
        
    for pattern in trigram_case:
        trigram_prob_list.append( trigramprob_with_pos(pattern,trigram_count))
        
    for pattern in fourgram_case:
        fourgram_prob_list.append( fourgramprob_with_pos(pattern,trigram_count))
    
    ngram_prob_list = defaultdict(float);
    bigram_prob_list_ave = defaultdict(float);
    trigram_prob_list_ave = defaultdict(float);
    fourgram_prob_list_ave = defaultdict(float);
    
    if len(bigram_prob_list) == 1:
        bigram_prob_list_ave = bigram_prob_list[0]
        
    elif len(bigram_prob_list) > 1:
        for key in bigram_prob_list[0]:
            num = 0;
            for i in range(len(bigram_prob_list)):
                 num += bigram_prob_list[i][key]
                
            bigram_prob_list_ave[key] = num/len(bigram_prob_list)
            
    if len(trigram_prob_list) == 1:
        trigram_prob_list_ave = trigram_prob_list[0]
        
    elif len(trigram_prob_list) > 1:
        for key in trigram_prob_list[0]:
            num = 0;
            for i in range(len(trigram_prob_list)):
                 num += trigram_prob_list[i][key]
                
            trigram_prob_list_ave[key] = num/len(trigram_prob_list)
        
    if len(fourgram_prob_list) == 1:
        fourgram_prob_list_ave = fourgram_prob_list[0]
        
    elif len(fourgram_prob_list) > 1:
        for key in fourgram_prob_list[0]:
            num = 0;
            for i in range(len(fourgram_prob_list)):
                 num += fourgram_prob_list[i][key]
                
            fourgram_prob_list_ave[key] = num/len(fourgram_prob_list)
                
    
    if bigram_prob_list_ave == {}:
        ngram_prob_list = unigram_prob_list
        
    elif ((bigram_prob_list_ave) != {}) and ((trigram_prob_list_ave) == {}):
        for key in unigram_prob_list.keys():
            ngram_prob_list[key] = 0.3*unigram_prob_list[key] + 0.7*bigram_prob_list_ave[key]
        
    elif ((bigram_prob_list_ave) != {}) and ((trigram_prob_list_ave) != {}):
        for key in unigram_prob_list.keys():
            ngram_prob_list[key] = 0.1*unigram_prob_list[key] + 0.3*bigram_prob_list_ave[key] + \
                                                                0.6*trigram_prob_list_ave[key]
            
    elif ((fourgram_prob_list_ave) != {}):
        for key in unigram_prob_list.keys():
            ngram_prob_list[key] = 0.05*unigram_prob_list[key] + 0.15*bigram_prob_list_ave[key] + \
                                   0.3*trigram_prob_list_ave[key] + 0.5*fourgram_prob_list_ave[key]
    
    return ngram_prob_list


def guess_letter(allpattern,unigram_prob_list,bigram_count, trigram_count ,fourgram_count):
    letter_prob_dic_list = [];
    
    for i in allpattern:
        letter_prob_dic_list.append(prob_fix_pos(i,unigram_prob_list,bigram_count,trigram_count,
                                                 fourgram_count))
        
    letter_prob_list = defaultdict(float);
    
    for key in letter_prob_dic_list[0].keys():
        for i in range(len(letter_prob_dic_list)):
            letter_prob_list[key] += letter_prob_dic_list[i][key]
            
    letter_prob_list = sorted(letter_prob_list.items(), key = lambda item: item[1],reverse=True)
    
    return letter_prob_list[0][0]

