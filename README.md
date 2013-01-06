cheaterpress
============

python based letterpress simulator

This is a letterpress simulator meant to be used to evaluate different
strategies for the ios game Letterpress. Currently, the code enumerates all
possible plays of all remaining words (less words which are prefixes of other
playable words), and all an AI needs to do is choose which next state of the
board is most preferable, i.e. one which maximizes the number of owned squares,
or the number of defended squares, or prefers owned edges over owned middle
squares, etc. This is implemented by a `play_quality` function which takes a
prospective next board state and assigns it an integer score. These scores are
then compared across all possible plays to find the best next word to play.



TODOS
=====

easy
----
* include 'pass' as a possible play for scoring
* treat different words spelled with the same letters as an equivalence class
  for finding all possible plays (i.e. after ploy's board states have been
  computed, skip computing them for poly as it will be the same thing)
* parallelize executing the ranking function
* profile execution to see where I should try to optimize

hard
----
* use a different data structure for the master word file to optimize searches
  for all possible words with a given board.
* optimize the 'next board' computation
* 

fun!
----
* Create an AI that prevents the opposing player from being able to finish the
  game with a winning move, i.e. taking enough unclaimed tiles such that there
  exists a word for the opponent to play that will result in the opponent
  winning.
* Create an AI that breaks ties among best options by minimizing the number of
  tiles that the opponent could possibly take on the next turn.




current timing for test board 12/25/2012:
real  1m39.089s
user  1m36.155s
sys 0m8.093s

timing with deepcopy removed, 12/25/2012:
real  0m15.459s
user  0m14.435s
sys 0m1.357s

timing with alternative choice refactored to once per game, 12/25/2012:
real  0m9.470s
user  0m8.755s
sys 0m0.711s
