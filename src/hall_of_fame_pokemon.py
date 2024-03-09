from typing import Union, List, Tuple
import numpy as np
import logging

from common import SpeciesParser, MoveParser, CharacterParser, Memory, CHAR_ENCODINGS


class HallOfFamePokemon:
    """Class representing a Pokemon."""


    def __init__(self,
                 species: Union[str, int] = 0,
                 level: int = 0,
                 forme: int = 0,
                 pid: int = 0,
                 trainer_id: int = 0,
                 secret_id: int = 0,
                 name: CHAR_ENCODINGS = "",
                 trainer_name: CHAR_ENCODINGS = "",
                 move1: Union[str, int] = 0,
                 move2: Union[str, int] = 0,
                 move3: Union[str, int] = 0,
                 move4: Union[str, int] = 0
                 ):
        """Initialize the Pokemon with its attributes."""
        self.species = species
        self.level = level
        self.forme = forme
        self.pid = pid
        self.trainer_id = trainer_id
        self.secret_id = secret_id
        self.name = name
        self.trainer_name = trainer_name
        self.move1 = move1
        self.move2 = move2
        self.move3 = move3
        self.move4 = move4

        self.__memory = None


    @property
    def memory(self) -> np.ndarray[np.uint8]:
        """Get the memory array."""
        if self.__memory is None:
            logging.debug("Memory has not been generated. Calling parse().")
            self.parse(SpeciesParser(), MoveParser(), CharacterParser())
        return self.__memory


    def parse(self, species_parser: SpeciesParser, move_parser: MoveParser, character_parser: CharacterParser) -> np.ndarray[np.uint8]:
        """Parse the Pokemon attributes into raw data."""
        self.species = species_parser.parse_species(self.species)
        self.level = np.uint8(self.level)
        self.forme = np.uint8(self.forme)
        self.pid = np.uint32(self.pid)
        self.trainer_id = np.uint16(self.trainer_id)
        self.secret_id = np.uint16(self.secret_id)
        self.name = character_parser.parse_character(self.name, 0xB)
        self.trainer_name = character_parser.parse_character(self.trainer_name, 0x8)
        self.move1 = move_parser.parse_move(self.move1)
        self.move2 = move_parser.parse_move(self.move2)
        self.move3 = move_parser.parse_move(self.move3)
        self.move4 = move_parser.parse_move(self.move4)

        return self.__create_memory()


    def __create_memory(self) -> np.ndarray[np.uint8]:
        """Create a memory array to store the data."""
        self.__memory = np.zeros(0x3C, dtype=np.uint8)
        attributes = self.__dict__
        index = 0
        for key, value in attributes.items():
            # Skip the memory attribute
            if key == "_HallOfFamePokemon__memory":
                continue
            if isinstance(value, np.ndarray):
                logging.debug(f"Setting {key} at index {hex(index)} with value {value}")
            else:
                logging.debug(f"Setting {key} at index {hex(index)} with value {hex(value)}")
            index = Memory.set_value(self.__memory, index, value)
        return self.__memory