"""Injest flat Markdown and segment into as specific a segment as possible

segment option ideas:
- h1
- h2
- h3
- footnote

- reference label (Rule 2.1.1, Corollary 4.6.2)
- reference body (needs better name)

- exposition (text)
- proof (text)
- list group
- list item

- table
- formula

"""
from models import Section
from utils import read_md_by_line
from config import CHAPTER_2_MD_FILE_PATH

def _split_into_blocks(lines: list[str]) -> list[str]:
    """Breaks markdown text into blocks based on hard delimiters"""
    # TODO how to handle tables?
    if not lines:
        return []

    # currently breaks up all lines which end in newline
    # AND lines entirely made of newline
    output = []
    delimeters = ("#",  "<sup>")
    curr_string = ""
    for line in lines:
        if line.lstrip().startswith(delimeters):
            output.append(line)
        elif line.strip() == "":
            if curr_string:
                output.append(curr_string)
            curr_string = ""
        else:
            curr_string += line
    if curr_string:
        output.append(curr_string)
    
    return output

def _classify(blocks: list[str]) -> list[Section]:
    """Classify text based on first matching format/content"""
    pass

def main():
    file_lines = read_md_by_line(CHAPTER_2_MD_FILE_PATH)
    blocks = _split_into_blocks(file_lines)
    for block in blocks:
        print("!"*49, "\n")
        print(block)

if __name__ == "__main__":
    main()