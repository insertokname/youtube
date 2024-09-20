def __check_word_appears_at_index(string: str, word: str, index: int):
    for i in range(0, len(word)):
        if index + i>=len(string):
            return False
        if string[index+i]!=word[i]:
            return False
    return True

def find_links_str(input: str):
    links = []
    for i in range(len(input) - 4):
        if input[i:i+5] == "https":
            #found link!
            
            seq_end = i+5
            while (seq_end<len(input) 
                   and not __check_word_appears_at_index(input, "https", seq_end)
                   and not __check_word_appears_at_index(input, "watch", seq_end)
                   and not __check_word_appears_at_index(input, "shorts", seq_end)
                   and not __check_word_appears_at_index(input, "youtu.be", seq_end)
                   and not input[seq_end]=='\n'):
                seq_end+=1
            try:    
                if(__check_word_appears_at_index(input,"watch",seq_end) and ("youtu" in input[i:seq_end])):
                    links.append(input[i:seq_end+14+len("watch")])
                if(__check_word_appears_at_index(input,"shorts",seq_end) and ("youtu" in input[i:seq_end])):
                    links.append(input[i:seq_end+12+len("shorts")])
                if(__check_word_appears_at_index(input,"youtu.be",seq_end)):
                    links.append(input[i:seq_end+12+len("youtu.be")])
            except Exception as e:
                print("String cut off too suddenly, poorly formated link cut off by end of file!")
    return links

def find_links_file(filename: str):
    chat = ""
    with open(filename, "r") as file:
        chat = file.read()
    return find_links_str(chat)