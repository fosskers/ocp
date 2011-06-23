# file:    ocp.py
# author:  Colin Woodbury
# contact: colingw AT gmail
# about:   Obsessive Compulsive Python
#          Does code not lined up all pretty-like bother you?
#          Does your Haskell experience make you want to line up all your
#          assignment operators? If so, you've come to the right script.
#          ocp will line up all your code where possible with the goal
#          to make your code as visually pleasing at it deserves to be.

# DONE: Blocks right under each other of same key but different 
#       nest depth will no longer be aligned.
# DONE: Reworked the key_by() function.

# TODO: Make the keywords assignable by the user, so that they can use
#       this script on any type of text file.

# BUG FORESEEN: Comments are going to fuck things up.
# BUG FORESEEN: Alignments throwing lines over the char limit.

# syshelp is available in my python-libs repo.
from syshelp   import get_args as _get_args
from functools import reduce   as _reduce

def get_lines(filename):
    '''Gets all lines from the file.'''
    with open(filename, encoding='utf-8') as lines:
        contents = lines.readlines()
    return contents

def fix_by(key, lines):
    '''Scans a file, straightening any block of lines that contains the key.'''
    block = []
    nest  = None  # This will become an int below before it is ever used.
    for pos, line in enumerate(lines):
        if block:  # We are mid-way through a block already.
            if key in line and nest_match(nest, line):
                block.append((pos, line))
            else:  # Block over. Process it.
                lines = process_block(key, block, lines)
                block = []
        # This should not be an 'elif'. 
        # Blocks of different nest depth can be right under each other.
        if not block and key in line:  # We found the start of a new block.
            if not line.lstrip().startswith(key.lstrip()):
                # If the key is the first non-whitespace char in the line,
                # then IT defines the nest depth! No correction will be made.
                block.append((pos, line))  # Fire it in.
                nest = get_nest(line)      # Set the nest limit.
    if block:
        lines = process_block(key, block, lines)  # Catch stragglers.
    return lines

def nest_match(nest, line):
    '''True if the first non-white space char of line is at index 'nest'.'''
    if get_nest(line) == nest:
        return True
    return False

def get_nest(line):
    '''Calculates how nested the given line is.'''
    return len(line) - len(line.lstrip())
            
def process_block(key, block, lines):
    '''Handles the process of a block of lines.'''
    block = align_by_key(key, block)    # Edit lines to align by key.
    return replace_lines(block, lines)  # Replace the original lines.
    
def align_by_key(key, block):
    '''Given a block of lines that all contain a key, aligns them all
    neatly according to the position of the key.
    TODO: Holy crap make this prettier.
    '''
    line_tokens = [line.split(key, 1) for pos, line in block]
    firsts      = list(map(lambda tokens: tokens[0].rstrip(), line_tokens))
    # Is there a way to do a Haskell-like 'let' in a Python lambda?
    longest = _reduce(lambda ac, i: len(i) if len(i) > ac else ac, firsts, 0)
    for pos, line in enumerate(line_tokens):  # Perform alignment.
        start            = firsts[pos] + (' ' * (longest - len(firsts[pos])))
        line_tokens[pos] = ''.join((start, key, line[1].lstrip()))
    for pos, line in enumerate(block):  # Repair 'block'.
        block[pos] = (block[pos][0], line_tokens[pos])
    return block

def replace_lines(block, lines):
    '''Given a block and lines, replaces the master lines in 'lines' with
    the ones fixed in 'block'.
    '''
    for pos, line in block:
        lines[pos] = line
    return lines
        
def write_changes(filename, lines):
    '''Writes a copy of the file given, with the changes included.'''
    with open('ocp-' + filename, 'w', encoding='utf-8') as output:
        for line in lines:
            output.write(line)

keywords = (' import ', ' as ', ' = ', '  # ')  # Add more later.

if __name__ == '__main__':
    filename = _get_args()
    if filename:
        lines = get_lines(filename[0])
        for key in keywords:
            lines = fix_by(key, lines)
        write_changes(filename[0], lines)
        print('Prettification Complete.')

