from hall_of_fame_record import HallOfFameRecord
from common import Memory

import logging
import numpy as np

class HallOfFame:
    def __init__(self, 
                 records: list[HallOfFameRecord] = None,
                 record_start: int = 0
                 ):
        self.records = records
        self.record_start = record_start
        self.__memory = None

    @property
    def memory(self) -> np.ndarray[np.uint8]:
        if self.__memory is None:
            logging.debug("Memory has not been generated. Calling parse().")
            self.parse()
        return self.__memory
    
    def parse(self) -> np.ndarray[np.uint8]:
        record_size = 0x3C * 6 + 4
        max_records = 30
        size = record_size * max_records
        self.__memory = np.zeros(size, dtype=np.uint8)
        for i, record in enumerate(self.records):
            index = ((i + self.record_start)%max_records) * record_size # FIFO
            Memory.set_value(self.__memory, index, record.memory)
        return self.__memory