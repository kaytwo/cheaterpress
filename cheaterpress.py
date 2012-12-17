import copy
from collections import defaultdict
from pprint import pprint
import random
import sys
import time

def debug(s):
    print s

isatty = sys.stdout.isatty()

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
  
  def find_letter_on_board(self,letter):
    hits = []
    for i in range(5):
      for j in range(5):
        if self.board[i,j]['letter'] == letter:
          hits.append((i,j))
    return hits

  def test_play(self,player,spaces):
    testboard = copy.deepcopy(self)
    testboard.play_word(player,spaces)
    return testboard

  def play_word(self,player,spaces):
    for x,y in spaces:
      space = self.board[x,y]
      if space['owner'] != player and space['defended'] == False:
        self.board[x,y]['owner'] = player
    # update defense status
    for i in range(5):
      for j in range(5):
        owner = self.board[x,y]['owner']
        if owner == 'nobody':
          continue
        # top row
        if i != 0:
          pass
        else:
          if self.board[i-1,j] != owner:
            self.board[i,j]['defended'] = False
            continue
        # bottom row
        if i != 4:
          pass
        elif self.board[i+1,j] != owner:
          self.board[i,j]['defended'] = False
          continue
        # left column
        if j != 0:
          pass
        elif self.board[i,j-1] != owner:
          self.board[i,j]['defended'] = False
          continue
        if j != 4:
          pass
        elif self.board[i,j+1] != owner:
          self.board[i,j]['defended'] = False
        self.board[i,j]['defended'] = True

  def game_over(self):
    stats = defaultdict(int)
    for i in range(5):
      for j in range(5):
        owner = self.board[i,j]['owner']
        if owner == 'nobody':
          return False
        else:
          stats[owner] += 1
    return stats
  
  def hilite(string, status):
      attr = []
      if status:
          # green
          attr.append('32')
      else:
          # red
          attr.append('31')
      return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)

  def __str__(self):
    s = []
    for i in range(5):
      for j in range(5):
        fmtstr = '%s'
        if self.board[i,j]['owner'] == 'player1':
          fmtstr = '\x1b[35m%s\x1b[0m'
        elif self.board[i,j]['owner'] == 'player2':
          fmtstr = '\x1b[36m%s\x1b[0m'
        s.append(fmtstr % self.board[i,j]['letter'])
      s.append('\n')
    return ''.join(s)

class Player(object):
  def __init__(self,c):
    self.c = c

  def choose_next_move(self):
    ''' simple interactive move chooser, sublcass Player to write an AI '''
    word_choice = ''
    while word_choice == '':
      choose = raw_input("what word do you want to play? ")
      if choose not in self.c.playable_words:
        print "that's not a word :("
      elif choose in self.c.played_words:
        print "that word has been played"
      else:
        word_choice = choose
    # remove ambiguity
    this_move = []
    for letter in word_choice:
      choices = c.board.find_letter_on_board(letter)
      if len(choices) == 1:
        this_move.append(choices)
      else:
        goodmove = ''
        while goodmove not in choices:
          print letter
          print choices
          goodmove = raw_input("which %s? choices are %s" % (letter,'; '.join([str(x) for x in choices])))
        this_move.append(goodmove)

      


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
    self.playable_words = {}
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
        # assume a prefix will never be considered
        for p in range(len(word)):
          testprefix = word[:p]
          if testprefix in self.words and testprefix not in prefixes:
            prefixes[word[:p]] = True
        self.playable_words[word] = True

  
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

    self.played_words = []

    self.initialize_wordlist(wordfile)
    debug('instantiated wordlist of length %d' % len(self.words))
    self.instantiate_game(board)
    debug(self.board)
    t1 = time.time()
    self.find_all_words()
    t2 = time.time()
    # debug('found %d possible words in %.2f seconds' % (len(self.playable_words.keys()),t2-t1))

  def next():
    if self.currentplayer== self.player1:
      self.currentplayer = self.player2
    else:
      self.currentplayer = self.player1

  def play(self,player1,player2):
    self.player1 = player1(self)
    self.player2 = player2(self)
    self.currentplayer = self.player1
    
    pprint(self.playable_words.keys()[:10])
    while not self.board.game_over():
      self.player1.choose_next_move()
      self.next()


if __name__ == '__main__':
  c = Cheaterpress('words.txt')
  c.play(Player,Player)
