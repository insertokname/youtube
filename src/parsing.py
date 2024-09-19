def find_links_str(input: str):
    links = []
    for i in range(len(input) - 10):
        if input[i:i+11] == "https://you":
            #found link!
            seq_end = i
            while seq_end<len(input) and input[seq_end]!='\n' and input[seq_end]!='?':
                seq_end+=1
            links.append(input[i:seq_end])
    return links

def find_links_file(filename: str):
    chat = ""
    with open(filename, "r") as file:
        chat = file.read()
    return find_links_str(chat)