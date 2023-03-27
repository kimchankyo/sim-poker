from typing import Tuple, List, Dict
import numpy as np
import random


"""Classes"""
# Card Sub-Classes
class Suit:
  # Suit is (Bit Location, String)
  SPADES = (0, '\u2664')
  HEARTS = (1, '\u2665')
  DIAMONDS = (2, '\u2666')
  CLUBS = (3, '\u2667')

  asList = [SPADES, HEARTS, DIAMONDS, CLUBS]


class Rank:
  # Rank is (Value, Grade, String)
  ACE = (12, 'A')
  TWO = (0, '2')
  THREE = (1, '3')
  FOUR = (2, '4')
  FIVE = (3, '5')
  SIX = (4, '6')
  SEVEN = (5, '7')
  EIGHT = (6, '8')
  NINE = (7,'9')
  TEN = (8, '10')
  JACK = (9, 'J')
  QUEEN = (10, 'Q')
  KING = (11, 'K')

  asList = [ACE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, 
            EIGHT, NINE, TEN, JACK, QUEEN, KING]


# Card
class Card:
  def __init__(self, rank: Tuple[int, str], 
               suit: Tuple[int, str]) -> None:
    suitBit, self.suit = suit
    grade, self.value = rank
    self._sig = self._constructSignature(suitBit, grade)

  def _constructSignature(self, suitBit: int, grade: int) -> int:
    """
    Output Integer
    +-----------------------------------------------------------------------+
    | xxxx cdhs | xxp xxpx | xpxx pxxp | xxpx xpxx | pxxp xxpx | xpxx pxxpx |
    +-----------------------------------------------------------------------+
    cdhs = suit bit
    p = rank bit
    """
    r =  1 << ((grade * 3) + 1)
    s = 1 << suitBit
    return (s << 40) + r
  
  def getSignature(self) -> int:
    return self._sig


# Deck
class Deck:
  def __init__(self) -> None:
    self._stack = [Card(r, s) for s in Suit.asList for r in Rank.asList]
    self._loc = 0
    random.shuffle(self._stack)

  def __len__(self) -> int:
    return len(self._stack) - self._loc

  def canDraw(self) -> bool:
    return self._loc < len(self._stack)

  def countRemaining(self) -> int:
    return self.__len__()

  def draw(self) -> Card:
    if self.canDraw():
      card = self._stack[self._loc]
      self._loc += 1
      return card
    return None      # TODO: Proper error handling

  def reset(self) -> None:
    random.shuffle(self._stack)
    self._loc = 0