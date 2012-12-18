from itertools import combinations
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
            'i':i,
            'j':j,
            'letter':boardstring[i*5 + j],
            'owner':'nobody',
            'defended':False
            }

  def tiles(self):
    for i in range(5):
      for j in range(5):
        yield self.board[i,j]
  
  def find_letter_on_board(self,letter):
    hits = []
    for tile in self.tiles():
      if tile['letter'] == letter:
        hits.append(tile['i'],tile['j'])
    return hits
  
  def score(self):
    scoreboard = defaultdict(int)
    for tile in self.tiles():
      if tile['owner'] != 'nobody':
        scoreboard[tile['owner']] += 1

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
    for tile in self.tiles():
      i = tile['i']
      j = tile['j']
      owner = tile['owner']
      if owner == 'nobody':
        continue
      # top row
      if i == 0:
        pass
      elif self.board[i-1,j]['owner'] != owner:
          tile['defended'] = False
          continue
      # bottom row
      if i == 4:
        pass
      elif self.board[i+1,j]['owner'] != owner:
        tile['defended'] = False
        continue
      # left column
      if j == 0:
        pass
      elif self.board[i,j-1]['owner'] != owner:
        tile['defended'] = False
        continue
      if j == 4:
        pass
      elif self.board[i,j+1]['owner'] != owner:
        tile['defended'] = False
        continue
      tile['defended'] = True

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
    ctr = 0
    for tile in self.tiles():
      if  isatty and tile['owner'] != 'nobody':
        fmtstr = self.hilite(tile['owner'] == 'player1',
                        tile['defended'])
      else:
        fmtstr = '%s'
      s.append(fmtstr % tile['letter'])
      if ctr % 5 == 4:
        s.append('\n')
      ctr += 1
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
      
class AIPlayer(Player):
  def choose_next_move(self):
    best_plays = []
    for word in self.c.playable_words:
      if word not in self.c.played_words:
        for alternative in self.choose_spaces(playable_word):
          best_plays.append(alternative)
    best_plays.sort(key=play_quality,reverse=True)
    if len(best_plays) == 0:
      return None
    return best_plays[0]

  def choose_spaces(self,playable_word,board=None):
    if board is None:
      board = self.c.board
    '''for a given word, spit out all alternative play options
    as test_play boards for that word.'''
    this_move = []
    freq_table = defaultdict(int)
    alternative_subchoices = []
    for letter in playable_word:
      freq_table[letter] += 1
    for letter in freq_table.keys():
      choices = board.find_letter_on_board(letter)
      


  @staticmethod
  def play_quality(next_board):
    '''create a key for a sort function to compare the quality of diff
    moves (based on a Board object). this one attempts to maximize area owned,
    and breaks ties with num defended'''
    quality = [0,0]
    for square in self.c.board.board.values():
      if square['owner'] == self.name:
        quality[0] += 1
        if square['defended'] == True:
          quality[1] += 1
    return quality[0] * 25 + quality[1]


class Cheaterpress(object):
  words = None
  letters='QWERTYUIOPASDFGHJKLZXCVBNM'

  @classmethod
  def initialize_wordlist(cls,wordfile):
    assert cls.words or wordfile
    if cls.words is None:
      cls.words = {}
      with open(wordfile) as f:
        for line in f.readlines():
          cls.words[line.strip()] = True
 
  def game_over(self):
    if self.passes == 2:
      return True
    for tile in self.board.tiles():
      if tile['owner'] == 'nobody':
        return False
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
      for i in range(25):
        choices.append(random.choice(Cheaterpress.letters))
      boardstring = ''.join(choices)
    self.boardstring = boardstring
    self.board = Board(boardstring)


  def __init__(self,wordfile=None,board=None):
    '''initialize an individual game of letterpress. 
    
    wordfile gets read in if this is the first game instantiated
    in this process.
    
    normal operation is to randomly generate a board, but if you
    want to play a specific game, input board as a 25 character string
    reading the board left to right and top to bottom.
    '''
    self.num_players = 2
    self.players = []
    self.played_words = []
    self.passes = 0
    self.initialize_wordlist(wordfile)
    self.instantiate_game(board)
    # debug(self.board)
    t1 = time.time()
    self.find_all_words()
    t2 = time.time()
    # debug('found %d possible words in %.2f seconds' % (len(self.playable_words.keys()),t2-t1))

  def winner(self):
    stats = self.board.score()
    return max(stats.items(),lambda x: x[1])[0]

  def next(self):
    self.currentplayer = self.players[len(self.played_words) % self.num_players]

  def play(self,players):
    for playernum in range(len(players)):
      self.players.append(players[playernum](self,'player' + str(playernum)))
    self.currentplayer = self.players[0]
    # pprint(sorted(self.playable_words.keys(),key=lambda x:  len(x)))
    while not self.game_over():
      print self.board
      next_move,word_choice = self.currentplayer.choose_next_move()
      if next_move == None:
        self.passes += 1
      else:
        self.passes = 0
        self.board.play_word(self.currentplayer.name,next_move)
        self.played_words.append(word_choice)
      self.next()
    print self.winner(),'wins.'

if __name__ == '__main__':
  numwords = []
  for i in range(500):
    c = Cheaterpress('words.txt') # ,'FRPGBXTQMTPGRCBYKHSCZFXUA')
    num = len(c.playable_words.keys())
    print "%d possible words" % num
    numwords.append(num)
  print 'average: %10.2f, min: %10d, max: %10d' % (float(sum(numwords)/len(numwords)),min(numwords),max(numwords))
