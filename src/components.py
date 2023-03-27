from typing import Tuple, List, Dict
import numpy as np
import time
import sys


"""Classes"""
# Card Sub-Classes
class Suit:
  # Suit is (Bit Location, String)
  SPADES = (0, '\u2664')
  HEARTS = (1, '\u2665')
  DIAMONDS = (2, '\u2666')
  CLUBS = (3, '\u2667')


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
    suitBit, self._suit = suit
    grade, self._value = rank
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