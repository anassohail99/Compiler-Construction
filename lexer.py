import re

class Lexical_Analyzer():
    def __init__(self): pass
    
    #split code into lines
    def line_splitter(self,source_code):
        code = {} #dict that will store line num as key and line as value
        source_index = 0
        line_num = 1
        word = ''
        #run loop until the whole source code parsing completed
        while(source_index<len(source_code)):
            #multiple line comment
            #checking for /*
            if source_code[source_index] == '/' and source_code[source_index+1] == '*':
                if word!='':
                    code[line_num]  = word
                    word=''
                word += ' '
                #run loop until we get */
                while(source_code[source_index]!='*' or source_code[source_index+1]!='/'):  
                    #check if line ends so we can increment line num
                    if(source_code[source_index]=='\n'):
                        line_num +=1
                    source_index +=1
                else:
                    #to pass the index from */
                    source_index +=2

            #single line comments
            #checking for //
            elif source_code[source_index] == '/' and source_code[source_index+1] == '/':
                #run loop until we get new line
                while(source_code[source_index]!='\n'):      
                    source_index +=1
                else:
                    if word!='':
                        code[line_num] = word.strip()
                        word = ''
                    line_num +=1
                    source_index +=1
                    

            #for string
            #checking for "
            elif source_code[source_index] == '"':
                #adding $$$ sign so we can combine string after passing through .split() in word_split() function
                word += ' $$$ '
                start = True
                #run loop until we get " but in first iteration we are on " that's why we use start=True
                while((source_code[source_index]!= '"' or start) and source_code[source_index]!='\n'): 
                    start = False   
                    #checking for \"
                    if source_code[source_index+1] == '\\' and source_code[source_index+2] == '"' and source_code[source_index]!='\\':
                        #adding \" in word and doing +2 increment in source_index so we can skip \" from loop
                        word += source_code[source_index:source_index+2]
                        source_index +=2
                    #adding our characters of string in word to get back our string 
                    word += source_code[source_index]   
                    source_index +=1
                if source_code[source_index] == '\n':
                    word += ' $$$ '
                    code[line_num] = word.strip()
                   # line_num +=1
                    word = ''
                else:
                    #when the loop breaks on " we will add " on our word to complete our string
                    word += source_code[source_index]
                    source_index +=1   
                    #adding $$$ sign so we can combine string after passing through .split() in word_split() function 
                    word += ' $$$ '
            
            #if the code is not comment and string 
            else:
                #if the line ends then we store our code in dict with line num as key and code as value
                if source_code[source_index] == '\n':
                    #avoiding empty lines
                    if word.strip() != '':
                        #storing code with removing useless spaces
                        code[line_num] = word.strip()
                        word = '' 
                    line_num +=1
                    source_index +=1
                else: 
                    #if line doesn't ends then continue parsing
                    word += source_code[source_index]
                    source_index +=1
        return code
    
    #change the invalid escape sequences readed from text file into valid one
    def correct_escape_sequence(self,lines):
        for key,value in lines.items():      
            temp_line = ''
            index=0
            while(index<len(value)):
                if value[index] == '\\':
                    if value[index+1] == '\\' and value[index+2]!='"':
                        temp_line += '\\'
                    elif value[index+1] == 'n':
                        temp_line += '\n'
                    elif value[index+1] == 't':
                        temp_line += '\t'
                    else:
                        temp_line += '\\'+ value[index+1]
                    index += 2
                else:
                    temp_line += value[index]
                    index +=1
            lines[key] = temp_line
        return lines
    
    #identify the characters from the code
    def mark_char(self,lines):
        for key,value in lines.items():
            temp_line = ''
            index = 0
            while(index<len(value)):
                if value[index:index+3]=='$$$':
                    temp_line += value[index:index+3]
                    index += 3
                    while(index<len(value)):
                        if value[index:index+3]=='$$$':
                            temp_line += value[index:index+3]
                            index += 3
                            break
                        else:
                            temp_line += value[index]
                            index +=1

                elif value[index]=='\'':
                    if value[index+1] == '\'':
                        temp_line += ' $$$ ' + value[index:index+2] + ' $$$ '
                        index += 2
                    else:
                        temp_line += ' $$$ ' + value[index:index+3] + ' $$$ '
                        index += 3
                else:
                    temp_line += value[index]
                    index +=1
            lines[key] = temp_line
        return lines
    
    #split code on the basis of space
    def space_split(self,word):
        temp_line=[]  
        temp_word=''
        working_on_string = False
        for i,char in enumerate(word):
            if word[i:i+3]=='$$$':
                working_on_string = not working_on_string
            if char == ' ':
                if temp_word!='':
                    temp_line.append(temp_word)
                if working_on_string:
                    temp_line.append(' ')
                temp_word=''
            else:
                temp_word += char     
        if temp_word!='':
            temp_line.append(temp_word)
        return temp_line
    
    #split code on the basis of operators
    def split_operators(self,word_list):
        operators = '+-*%/|&<>=!'
        double_operators = ['+=','-=','*=','/=','%=','++','--','<<','>>','!=','==','>=','<=','||','&&']
        for index,word in enumerate(word_list):
            #if word is  an operator like just continue loop
            if word in operators:
                continue
            else:
                new_word = '' #this new word will store just the first half of operator eg: store x from x+y
                char_index = 0
                new_index = index
                #run loop until the word completes
                while(char_index<len(word)):
                    #if character of word is an operator
                    if word[char_index] in operators:
                        #checking if the operator length is greater than 1 like ++ /=
                        if char_index+1<len(word) and word[char_index+1] in operators and word[char_index:char_index+2] in double_operators:  
                            #insert operator in list of words 
                            word_list.insert(new_index+1,word[char_index:char_index+2])
                            #checking that after opeartor it is something
                            if char_index+2 < len(word):
                                #checking that after opeartor it is something
                                if word[char_index+2]!='':
                                    #insert the second part of operator 
                                    word_list.insert(new_index+2,word[char_index+2:])
                            #if there is any first half of operator like sum in sum+=x then add it inplace of sum
                            if new_word !='':
                                word_list[new_index] = new_word
                            #if not then del the +=x else it will store null in it's place
                            else:
                                del word_list[new_index]
                            new_word = ''
                            break
                        
                        #if operator is of length one like + or -
                        else:
                            #insert operator in list
                            word_list.insert(new_index+1,word[char_index])
                            if char_index+1<len(word) and word[char_index+1]!='':
                                #add the second part of operator in list
                                word_list.insert(new_index+2,word[char_index+1:])                 
                            #add the first part of operator like x in x+y 
                            if new_word !='':
                                word_list[new_index] = new_word
                            else:
                                del word_list[new_index]               
                            new_word = ''
                            break
                    else:
                        #if the char. of word is not an operator than add it in new_word 
                        new_word += word[char_index]
                    char_index +=1
        return word_list             
    
    
    #split code on the basis of punctuators
    def split_punctuators(self,word_list):   
        punctuators = ';,:.(){}[]'
        for index,word in enumerate(word_list):
            if word in punctuators and len(word)<2:
                continue
            else:
                new_word = ''
                new_index = index
                i=0
                for char in word:  
                    if char in punctuators:                                            
                        #insert the punctuators in list
                        word_list.insert(new_index+1,char)
                        if word[i+1:]!='':
                            #insert the secod half of word after punc
                            word_list.insert(new_index+2,word[i+1:]) 
                        if new_word!='':
                            word_list[new_index] = new_word
                        else:
                            del word_list[new_index]  
                        new_word = ''
                        break
                    else:
                        new_word += char
                        i +=1
        return word_list
    
    #combine the splitted floating numbers
    def combine_floating(self,word_list):
        index = 0
        while(index<len(word_list)):
            if index+2<len(word_list):
                if re.match('[0-9]+$',word_list[index]) and word_list[index+1] == '.' and re.match('[0-9]+$',word_list[index+2]):
                    word_list[index] = word_list[index] + word_list[index+1] + word_list[index+2]
                    del word_list[index+1]
                    del word_list[index+1]
            index +=1
        return word_list
    
    #split words 
    def word_splitter(self,sc):     
        code_set = {} #store line num as a key and splitted word as a list of code
        for k,v in sc.items():
            #word_list = v.split() #split code on the basis of space
            word_list = self.space_split(v)
            word_list = self.split_operators(word_list) #split code on the basis of operators
            #this will split code on the basis of punctuators
            word_list = self.split_punctuators(word_list)
            word_list = self.combine_floating(word_list)
            code_set[k] = word_list
        return code_set
    
    #combine the splitted strings and characters
    def combine_string(self,code_set):
        for k,v in code_set.items():
            for index,words in enumerate(v):
                string = ''
                #if word start from $$$ means its our start of string
                if words[0:3] == '$$$':
                    string += words[3:]
                    new_index = index
                    iteration = 0
                    #run loop until we find the end of string
                    while(True):
                        new_index +=1
                        iteration +=1
                        words = v[new_index]
                        #if we get $$$ in the end means it is the last piece of our string
                        if(words[len(words)-3:len(words)] == '$$$'):
                            string += words[:len(words)-3]
                            string = string[1:len(string)-1].replace('\\\\','\\')
                            break
                        #if not then add the words to combine string
                        else:
                            #if words=='':
                                #string += ' '
                            string += words
                    #delete the words from word list that are the parts of string
                    for x in range(iteration):
                        del code_set[k][index+1]
                    code_set[k][index] = string
        return code_set
    
    
    #check that the word is valid or not
    def isValidWord(self,valid_words,word):
        for key in valid_words:
            if word in valid_words[key]:
                return True
            else:
                False
                
    #hence the word is valid not build it's token
    def build_token(self,line_num,valid_words,word):
        for key,values in valid_words.items():
            for x in values:
                if x == word:
                    return (key,word,line_num)
                
                
    #create tokens          
    def tokenization(self,source_code):
        tokens = []
        try:
            lines = self.line_splitter(source_code)
            lines = self.correct_escape_sequence(lines)
            lines = self.mark_char(lines)
            words = self.word_splitter(lines)
            code_set = self.combine_string(words)
        except Exception as e:
            print(e)         
        else:
            valid_words = {
                'Data Type' : ['int','double','char','bool','string'],
                'Access Modifier' : ['public', 'private', 'protected'],
                'Constant' : ['constant'],
                'Break' : ['break'],
                'Continue' : ['continue'],
                'Else' : ['else'],
                'Base' : ['base'],
                'Bool Constant' : ['true','false'],
                'For' : ['for'],
                'If' : ['if'],
                'Interface' : ['interface'],
                'Class' : ['class'],
                'New' : ['new'],
                'Null' : ['null'],
                'Override' : ['override'],
                'Reference' : ['ref'],
                'Return' : ['return'],
                'Sealed' : ['sealed'],
                'Static' : ['static'],
                'This' : ['this'],
                'Virtual' : ['virtual'],
                'Void' : ['void'],
                'While' : ['while'],
                'Abstract' : ['abstract'],
                'In' : ['in'],
                'Var' : ['var'],
                ';' : [';'],
                ',' : [','],
                '.' : ['.'],
                ':' : [':'],
                '{' : ['{'],
                '}' : ['}'],
                '(' : ['('],
                ')' : [')'],
                '[' : ['['],
                ']' : [']'],
                'Increment/Decrement Opeartor ' : ['++','--'],
                'Arithmetaic Operator' : ['+','-','*','/','%'],
                'Logical Operator' : ['&&','||','!'],
                'Relational Operator' : ['<','>','<=','>=','!=','=='],
                'Bitwise Operator' : ['&','|','~'],
                'Assignment Operator' : ['=','+=','-=','*=','%=','/='],
                'Shift Operator' : ['<<','>>']
            }

            
            #classify words
            for k,v in code_set.items():
                for word in v:
                    if word.strip() is '':
                        continue
                    if self.isValidWord(valid_words,word):
                        tokens.append(self.build_token(k,valid_words,word)) 
                    elif re.match('[+|-]?[0-9]+$',word):
                        tokens.append(('Integer Constant',word,k))
                    elif re.match('[+|-]?[0-9]*[.][0-9]+$',word):
                        tokens.append(('Float Constant',word,k))
                    else:
                        tokens.append(('Invalid Token', word, k))     
            return tokens