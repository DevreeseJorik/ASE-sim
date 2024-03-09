from typing import Union, List, Tuple
import numpy as np
import logging

from hall_of_fame_pokemon import HallOfFamePokemon, HallOfFamePokemon
from common import SpeciesParser, MoveParser, CharacterParser, Memory


class HallOfFameRecord:
    def __init__(self, party: List[HallOfFamePokemon],
                 year: int = 2000, 
                 month: int = 1, 
                 day: int = 1):
        self.party = party
        self.year = year % 2000
        self.month = month
        self.day = day

        self.__memory = None


    @property
    def memory(self) -> np.ndarray[np.uint8]:
        if self.__memory is None:
            logging.debug("Memory has not been generated. Calling parse().")
            self.parse()
        return self.__memory


    def parse(self) -> np.ndarray[np.uint8]:
        party_size = 0x3C * 6
        size = party_size + 4
        self.__memory = np.zeros(size, dtype=np.uint8)
        for i, pokemon in enumerate(self.party):
            Memory.set_value(self.__memory, i * 0x3C, pokemon.memory)
        Memory.set_value(self.__memory, party_size, np.uint16(self.year))
        Memory.set_value(self.__memory, party_size + 2, np.uint8(self.month))
        Memory.set_value(self.__memory, party_size + 3, np.uint8(self.day))
        return self.__memory
