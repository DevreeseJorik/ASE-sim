from typing import Union, List, Tuple
import numpy as np
import json
import logging

CHAR_ENCODINGS = Union[str, List[int], Tuple[int], np.ndarray]

class SpeciesParser:
    """Parser class for species data."""
    
    def __init__(self):
        """Initialize the SpeciesParser."""
        self.specie_names = None

    def parse_species(self, species: Union[str, int]) -> np.uint16:
        """Parse the species name or ID into a 16-bit unsigned integer."""
        if isinstance(species, str):
            species = self.__get_species_from_name(species)
        return np.uint16(species)
    
    def __get_species_from_name(self, name: str) -> int:
        """Get the species ID from its name."""
        self.__load_species()
        return self.specie_names.index(name)

    def __load_species(self) -> None:
        """Factory method to load species names from a JSON file."""
        if self.specie_names is not None:
            return
        with open("./data/species_names.json") as f:
            self.specie_names = json.load(f)

class MoveParser:
    """Parser class for move data."""
    
    def __init__(self):
        """Initialize the MoveParser."""
        self.move_names = None

    def parse_move(self, move: Union[str, int]) -> np.uint16:
        """Parse the move name or ID into a 16-bit unsigned integer."""
        if isinstance(move, str):
            move = self.__get_move_from_name(move)
        return np.uint16(move)
    
    def __get_move_from_name(self, name: str) -> int:
        """Get the move ID from its name."""
        self.__load_moves()
        return self.move_names.index(name)

    def __load_moves(self) -> None:
        """Factory method to load move names from a JSON file."""
        if self.move_names is not None:
            return
        with open("./data/move_names.json") as f:
            self.move_names = json.load(f)

class CharacterParser:
    """Parser class for character data."""
    
    def __init__(self, enforce_terminator: bool = True):
        """Initialize the CharacterParser."""
        self.character_map = None
        self.enforce_terminator = enforce_terminator

    def parse_character(self, characters: CHAR_ENCODINGS, max_length) -> np.ndarray[np.uint16]:
        """Parse characters into a 16-bit unsigned integer array."""
        if isinstance(characters, str):
            return self.__convert_characters(characters, max_length)
        return self.__convert_enumerable(characters, max_length)
    
    def __convert_enumerable(self, characters: Union[List[int], Tuple[int], np.ndarray], max_length) -> np.ndarray[np.uint16]:
        """Convert an enumerable into a 16-bit unsigned integer array."""
        character_array = np.zeros(max_length, dtype=np.uint16)
        for i, char in enumerate(characters):
            if i >= max_length -1:
                logging.warning(f"Enumerable is too long, truncating to {max_length}")
                break
            character_array[i] = char
        return self.__enforce_terminator(character_array, i)
    
    def __convert_characters(self, characters: str, max_length) -> np.ndarray[np.uint16]:
        """Convert characters into a 16-bit unsigned integer array."""
        self.__load_characters()
        character_array = np.zeros(max_length, dtype=np.uint16)
        for i, char in enumerate(characters):
            if i >= max_length -1: # -1 for terminator
                logging.warning(f"String is too long, truncating to {max_length}")
                break
            character_array[i] = self.character_map[char]

        return self.__enforce_terminator(character_array, i)
    
    def __enforce_terminator(self, character_array: np.ndarray[np.uint16], last_char_index: int) -> np.ndarray[np.uint16]:
        """Enforce terminator if specified."""
        if self.enforce_terminator:
            last_char_index = min(last_char_index, len(character_array) - 1)
            if character_array[last_char_index] != 0xFFFF:
                if last_char_index == len(character_array) - 1:
                    logging.warning("Overwriting last character with terminator")
                    character_array[last_char_index] = 0xFFFF
                else:
                    character_array[last_char_index + 1] = 0xFFFF
        return character_array

    def __load_characters(self) -> None:
        """Factory method to load character mappings from a JSON file."""
        if self.character_map is not None:
            return
        with open("./data/character_map.json", encoding="utf-16") as f:
            character_map = json.load(f)
            for key, value in character_map.items():
                if isinstance(value, list):
                    character_map[key] = int(value[0],16)
                else:
                    character_map[key] = int(value, 16)
            self.character_map = character_map


class Memory:
    def get_value(memory: np.ndarray[np.uint8], index: int = 0, size: int = 1) -> np.ndarray[np.uint8]:
        """Read the data from the memory array."""
        return memory[index:index + size], index + size
    
    def get_value_as_int(memory: np.ndarray[np.uint8], index: int = 0, size: int = 1) -> int:
        """Read the data from the memory array and convert it to an integer."""
        return int.from_bytes(memory[index:index + size], byteorder="little"), index + size

    def set_value(memory: np.ndarray[np.uint8], index: int = 0, value: int = 0) -> int:
        """Set the data value in the memory array."""
        if isinstance(value, np.ndarray):
            byte_array = value.view(dtype=np.uint8)
            length = len(byte_array)
        else:
            dtype = value.dtype
            length = np.dtype(dtype).itemsize
            byte_array = np.array([value], dtype=dtype).view(dtype=np.uint8)
        if index + length > len(memory):
            raise ValueError(f"Index {index} + length {length} is out of bounds for memory of length {len(memory)}")
        memory[index:index+length] = byte_array
        return index + length