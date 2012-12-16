import random
import time


def debug(s):
    print s

class Board(object):
  def __init__(self,boardstring):
    self.board = {}
    
    for i in range(5):
      for j in range(5):
        self.board[i,j] = {
            'letter':boardstring[i*5 + j],
            'owner':'nobody',
            'defended':False
            }
  
  def __str__(self):
    s = []
    for i in range(5):
      for j in range(5):
        s.append(self.board[i,j]['letter'])
      s.append('\n')
    return ''.join(s)


class Cheaterpress(object):
  words = None
  letters='QWERTYUIOPASDFGHJKLZXCVBNM'

  @classmethod
  def initialize_wordlist(cls,wordfile):
    if cls.words is None:
      cls.words = {}
      with open(wordfile) as f:
        for line in f.readlines():
          cls.words[line.strip()] = True
 
  def find_all_words(self):
    self.playable_words = []
    prefixes = {}
    assert hasattr(self,'board')
    for word in self.words.keys():
      if word in prefixes:
        continue
      remaining_letters = list(self.boardstring)
      found = True
      for letter in word:
        if letter in remaining_letters:
          remaining_letters.remove(letter)
        else:
          found = False
          break
      if found:
        # assume a prefix will never be considered,
        for p in range(len(word)):
          testprefix = word[:p]
          if testprefix in self.words and testprefix not in prefixes:
            prefixes[word[:p]] = True
        self.playable_words.append(word)
    debug('threw out %d prefixes' % len(prefixes.keys()))

  
  def instantiate_game(self,boardstring):
    if boardstring is None:
      choices = []
      for i in range(24):
        choices.append(random.choice(Cheaterpress.letters))
        # guarantee game is winnable
        if 'q' in choices and 'i' not in choices:
          choices.append('i')
          random.shuffle(choices)
        else:
          choices.append(random.choice(Cheaterpress.letters))
      boardstring = ''.join(choices)
    self.boardstring = boardstring
    self.board = Board(boardstring)


  def __init__(self,wordfile,board=None):
    '''initialize an individual game of letterpress. 
    
    wordfile gets read in if this is the first game instantiated
    in this process.
    
    normal operation is to randomly generate a board, but if you
    want to play a specific game, input board as a 25 character string
    reading the board left to right and top to bottom.
    '''

    self.initialize_wordlist(wordfile)
    debug('instantiated wordlist of length %d' % len(self.words))
    self.instantiate_game(board)
    debug(self.board)
    t1 = time.time()
    self.find_all_words()
    t2 = time.time()
    debug('found %d possible words in %.2f seconds' % (len(self.playable_words),t2-t1))

if __name__ == '__main__':
  c = Cheaterpress('words.txt')
