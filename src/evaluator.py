from typing import Dict, List
from components import Card, Rank, Suit
import csv
import os

"""
No Limit Texas Hold'em Poker Hand Evaluation Optimization Theory
----------------------------------------------------------------
In a single hand of NLHE, there are 5 distinct cards from a 52-card deck.
As a result, there are 52C5 = 2,598,960 distinct hands!

Even with a dictionary mapping of all distinct hands to their respective hand
valued ranks, the space complexity will be on the order of 

  2598960 * 2 (Key-Value Pairs) * 4 (Four Bytes Per Integer) = 20791680 B
                                                             =    19.83 MB !!

Furthermore, if relatively similar compute time is desired with both hole and
community cards, there are 7 distinct cards from a 52-card deck, meaning there
are 52C7 = 133,784,560 distinct hands to account for!

Looking at the dicitionary map size once again, the space complexity is around

    133784560 * 2 * 4 = 1.07e9 B = 1020.7 MB = 1.00 GB !!!

Clearly, a more compressive yet efficient method of evaluating hands is 
necessary.

===========================
REDUCING SEARCH STATE SPACE
===========================
Although there are 2598960 different distinct 5-card hands in NLHE, it is
possible to group multiple hands into a singular category. For example, suppose
there is one hand (H1) that has (AS, AD, 5H, 3D, 2C) and another hand (H2) that
has (AH, AC, 5H, 3D, 2C). Clearly, H1 and H2 are two distinct hands, but their
hand evaluation values are equivalent. If this grouping is applied to each
hand rank category in NLHE, then the search space can be reduced from 2598960
to simply 7462. To see this, consider the following

1. Flush Straights:
   There are exactly 10 straights possible for first values A to 10. Assuming
   that these straights are flushes, then there are exactly 10*4 = 40 different
   flush straights available. However, flush straights of differing suits but
   the same values are evaluated to be the same value. Thus, there are 10
   true distinct straight flushes.

2. TODO

The key insight about the hands is that the actual value-suit combination of
each card is not relevant to the hand's value. Specifically, the key information
determining a hand's value is the frequency of values and whether the hand
is flushed. In other words, we do not care that a 2D and 2S are in the hand but 
rather there are two 2s and they are not suited.

From here, consider the following representation of a card as 6 bytes:

  Card Signature
  +-----------------------------------------------------------------------+
  | xxxx cdhs | xxp xxpx | xpxx pxxp | xxpx xpxx | pxxp xxpx | xpxx pxxpx |
  +-----------------------------------------------------------------------+
  cdhs = suit bit
  p = rank bit

Using these card signatures, we can simply evaluate the 5 card signatures to 
construct the following hand signature using & and | operations

  +-----------------------------------------------------------------------+
  | xxxx xxxx | pppp pppp | pppp pppp | pppp pppp | pppp pppp | pppp pppf |
  +-----------------------------------------------------------------------+
  f = indicator bit whether hand is flush
  p = frequency of card (groups of 3 bits)

Given this definition of a hand value, we find that the size of our dictionary
mapping is now

    7462 * 2 * 8 (6 bytes + 2 bytes padding) = 119,392 B = 174.2 KB !
                                                           (170x smaller)

with a runtime on the order of 1e-06 ! (ARM-1 MacOS)

From here, we can calculate all 7C5 = 21 possible hands constructed from both
the player hole and the board community cards. The runtime should be on the 
order of 1e-05. Unfortunately, it is difficult to improve runtime without a
significant trade in space. This is because the unique combination created by 5
cards from the 7 card pool is important information that cannot be anonymized,
as it is possible for a simple 5 card hand.

"""


class Evaluator:

  _numKeys = 7462
  _mapFile = 'valtorank.csv'

  def __init__(self) -> None:
    self._valToRank = self._setValueToRankMap()

  @staticmethod
  def _getHandValue(hand: List[Card]) -> int:
    """
    Output Integer
    +-----------------------------------------------------------------------+
    | xxxx xxxx | pppp pppp | pppp pppp | pppp pppp | pppp pppp | pppp pppf |
    +-----------------------------------------------------------------------+
    f = indicator bit whether hand is flush
    p = frequency of card (groups of 3 bits)
    """
    c1, c2, c3, c4, c5 = [c.getSignature() for c in hand]
    v = 1 if (c1&c2&c3&c4&c5) >> 40 else 0
    v += (c1+c2+c3+c4+c5) & 0xFFFFFFFFFF
    return v

  def _setValueToRankMap(self) -> None:
    valToRank = dict()

    # Check if preloaded dictionary exists
    if os.path.exists(self._mapFile) and os.path.isfile(self._mapFile):
      with open(self._mapFile, 'r') as f:
        reader = csv.reader(f)
        items = [(int(r[0]), int(r[1])) for r in reader]
        valToRank = dict(items)
    else:
      valToRank = self._buildValueToRankMap()
      with open(self._mapFile, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(list(valToRank.items()))
      
  def _buildValueToRankMap(self) -> Dict:
    ranks = [r for r in Rank.asList]
    ranksBounded = ranks + [Rank.ACE]
    numRanks = len(ranks)
    listFlushStraight, listStraight, listFlush, listHigh, listFourKind, \
    listThreeKind, listFullHouse, listPair, listTwoPair = \
      [], [], [], [], [], [], [], [], []

    # Flush Straight and Straights
    numStraights = len(ranksBounded) - 4
    for i in reversed(range(numStraights)):
      h = [Card(r, Suit.CLUBS) for r in ranksBounded[i: i+5]]   # Arbitrary suit
      listFlushStraight.append(self._getHandValue(h))
      h[0] = Card(ranksBounded[i], Suit.SPADES)       # Arbitrary non flush suit
      listStraight.append(self._getHandValue(h))
    
    # Standard Flush and High Card
    ranksReversed = ranksBounded[::-1][:-1]
    numFlushStarts = len(ranksReversed) - 4
    for i in range(numFlushStarts):
      for j in range(i+1, numRanks):
        for k in range(j+1, numRanks):
          for m in range(k+1, numRanks):
            for n in range(m+1, numRanks):
              r1, r2, r3, r4, r5 = ranksReversed[i], ranksReversed[j], \
                ranksReversed[k], ranksReversed[m], ranksReversed[n]
              h = [Card(r1, Suit.CLUBS), Card(r2, Suit.CLUBS), 
                   Card(r3, Suit.CLUBS), Card(r4, Suit.CLUBS),
                   Card(r5, Suit.CLUBS)]
              fv = self._getHandValue(h)
              h[0] = Card(r1, Suit.SPADES)
              hv = self._getHandValue(h)
              if fv not in listFlushStraight: listFlush.append(fv)
              if hv not in listStraight: listHigh.append(hv)

    # Four, Three of a Kind and Two Pair, One Pair
    for i in range(numRanks):
      r1 = ranksReversed[i]

      # Four of a Kind
      template = [Card(r1, Suit.CLUBS), Card(r1, Suit.DIAMONDS), \
                  Card(r1, Suit.HEARTS), Card(r1, Suit.SPADES)]
      for j in range(numRanks):
        if j != i:
          h = template + [Card(ranksReversed[j], Suit.CLUBS)]
          v = self._getHandValue(h)
          if v not in listFourKind: listFourKind.append(v)
      
      # Three of a Kind
      template = template[:-1]
      for j in range(numRanks):
        for k in range(numRanks):
          if j != i and k != i:
            r2, r3 = ranksReversed[j], ranksReversed[k]
            h = template + [Card(r2, Suit.CLUBS), Card(r3, Suit.HEARTS)]
            v = self._getHandValue(h)
            if j == k and v not in listFullHouse:
              listFullHouse.append(v)
            elif v not in listThreeKind:
              listThreeKind.append(v)
      
      # Pair and Two Pair
      template = template[:-1]
      for j in range(numRanks):
        for k in range(numRanks):
          for m in range(numRanks):
            if j != i and k != i and m != i:
              # Pair
              if k != j and k != m and m != j:
                r2, r3, r4 = ranksReversed[j], ranksReversed[k], ranksReversed[m]
                h = template + [Card(r2, Suit.CLUBS), Card(r3, Suit.HEARTS), 
                                Card(r4, Suit.SPADES)]
                v = self._getHandValue(h)
                if v not in listPair: listPair.append(v)
              # Two Pair
              if j == k and j != m and k != m:
                r2, r3, r4 = ranksReversed[j], ranksReversed[k], \
                             ranksReversed[m]
                h = template + [Card(r2, Suit.CLUBS), Card(r3, Suit.HEARTS), 
                                Card(r4, Suit.SPADES)]
                v = self._getHandValue(h)
                if v not in listTwoPair: listTwoPair.append(v)

    # Assure no intersecting keys
    assert not len(set(listFlushStraight).intersection(set(listStraight))
                                        .intersection(set(listFlush))
                                        .intersection(set(listHigh))
                                        .intersection(set(listFourKind))
                                        .intersection(set(listThreeKind))
                                        .intersection(set(listPair))
                                        .intersection(set(listTwoPair))
                  )

    keys = listFlushStraight + listFourKind + listFullHouse + listFlush + \
           listStraight + listThreeKind + listTwoPair + listPair + listHigh
    values = list(range(self._numKeys))
    assert len(keys) == self._numKeys
    return dict(zip(keys, values))

  def evaluateHands(self, hands: List[List[Card]]) -> List[int]:
    bestHands = []
    bestScore = self._numKeys
    for n in range(len(hands)):
      val = self._valToRank
      val = self._valToRank[self._getHandValue(hands[n])]
      if val < bestScore: 
        bestHands = [n]
        bestScore = val
      elif val == bestScore:
        bestHands.append(n)
    return bestHands
