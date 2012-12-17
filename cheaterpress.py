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
        if i == 0:
          pass
        elif self.board[i-1,j]['owner'] != owner:
            self.board[i,j]['defended'] = False
            continue
        # bottom row
        if i == 4:
          pass
        elif self.board[i+1,j]['owner'] != owner:
          self.board[i,j]['defended'] = False
          continue
        # left column
        if j == 0:
          pass
        elif self.board[i,j-1]['owner'] != owner:
          self.board[i,j]['defended'] = False
          continue
        if j == 4:
          pass
        elif self.board[i,j+1]['owner'] != owner:
          self.board[i,j]['defended'] = False
          continue
        self.board[i,j]['defended'] = True

  @staticmethod
  def hilite( is_player1, is_defended):
      attr = []
      if is_player1:
          attr.append('35')
      else:
          attr.append('36')
      if is_defended:
          attr.append('47')
      return '\x1b[%sm%%s\x1b[0m' % (';'.join(attr),)
  
  def __str__(self):
    s = []
    for i in range(5):
      for j in range(5):
        fmtstr = '%s'
        if not isatty or self.board[i,j]['owner'] == 'nobody':
          pass
        else:
          fmtstr = self.hilite(self.board[i,j]['owner'] == 'player1',
                          self.board[i,j]['defended'])
        s.append(fmtstr % self.board[i,j]['letter'])
      s.append('\n')
    return ''.join(s)

class Player(object):
  def __init__(self,c,name):
    self.c = c
    self.name = name

  def choose_next_move(self):
    ''' simple interactive move chooser, sublcass Player to write an AI '''
    word_choice = ''
    while word_choice == '':
      choose = raw_input("what word do you want to play? ").upper()
      if choose not in self.c.playable_words:
        print "that's not a word :("
      elif choose in self.c.played_words:
        print "that word has been played"
      else:
        word_choice = choose
    # remove ambiguity
    this_move = []
    for letter in word_choice:
      choices = self.c.board.find_letter_on_board(letter)
      for c in this_move:
        if c in choices:
          choices.remove(c)
      if len(choices) == 1:
        this_move.append(choices[0])
      else:
        pass
        goodmove = ''
        choicestring = '; '.join([str(x) + ': ' + str(choices[x]) for x in range(len(choices))])
        while goodmove not in range(len(choices)):
          goodmove = raw_input("which %s? choices are %s " % (letter,choicestring))
          try:
            goodmove = int(goodmove)
          except ValueError:
            continue
        this_move.append(choices[int(goodmove)])
    return this_move,word_choice
      


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
 
  def game_over(self):
    stats = defaultdict(int)
    for i in range(5):
      for j in range(5):
        # should make this less ugly...
        owner = self.board.board[i,j]['owner']
        if owner == 'nobody':
          return False
        else:
          stats[owner] += 1
    self.stats = stats
    return True
  

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
    self.passes = 0
    self.initialize_wordlist(wordfile)
    self.instantiate_game(board)
    debug(self.board)
    t1 = time.time()
    self.find_all_words()
    t2 = time.time()
    # debug('found %d possible words in %.2f seconds' % (len(self.playable_words.keys()),t2-t1))

  def next(self):
    if self.currentplayer== self.player1:
      self.currentplayer = self.player2
    else:
      self.currentplayer = self.player1

  def play(self,player1,player2):
    self.player1 = player1(self,'player1')
    self.player2 = player2(self,'player2')
    self.currentplayer = self.player1
    
    pprint(sorted(self.playable_words.keys(),key=lambda x:  len(x)))
    while not self.game_over():
      print self.board
      next_move,word_choice = self.currentplayer.choose_next_move()
      self.board.play_word(self.currentplayer.name,next_move)
      self.played_words.append(word_choice)
      self.next()
    print self.board
    print self.stats

if __name__ == '__main__':
  c = Cheaterpress('words.txt') # ,'FRPGBXTQMTPGRCBYKHSCZFXUA')
  c.play(Player,Player)
