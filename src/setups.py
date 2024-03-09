
from hall_of_fame_pokemon import HallOfFamePokemon
from hall_of_fame_record import HallOfFameRecord
from hall_of_fame import HallOfFame

from simulator import Simulation

import abc

class Setup(abc.ABC):
    """
    Abstract class for a setup
    """
    @abc.abstractmethod
    def run(self) -> None:
        """
        Run the setup
        """
        pass


class GyaradosSetup(Setup):
    """
    The current best setup, using an RNG'd Gyarados.
    """
    def __init__(self):
        self.name = 'RNG-based Gyarados setup'
        self.version = '0.0.1'
        self.author = "Jorik Devreese (RETIREglitch)"


    def run(self) -> None:
        # TM slot in item data of backup save file
        # This is the memory section used in current ASE setups
        execution_offsets = {
            "min_offset": 0x110000,
            "max_offset": 0x1102E8
        }

        pokemon = HallOfFamePokemon(species="Gyarados",
                                    level=0x16,
                                    forme=0,
                                    pid=0xE1656,
                                    trainer_id=0xffff,
                                    secret_id=0xffff,
                                    name="h",
                                    trainer_name="kh", 
                                    move1="Thunder", 
                                    move2=0x0, 
                                    move3=0x0, 
                                    move4=0x0
                                    )


        record = HallOfFameRecord(party=[pokemon], year=2076, month=1, day=1)

        # put 30 if you want to fill the entire hall of fame, with record_start = 0
        # Since only records 28-30 are used, I only fill those 3 records. 
        # Note that the code expects 0-indexed records, so record_start = 27

        records = [record] * 3
        hall_of_fame = HallOfFame(records=records, record_start=27)
        simulation = Simulation(execution_offsets=execution_offsets, hall_of_fame=hall_of_fame)
        success_log = simulation.simulate_full()
        simulation.plot_simulations(success_log)


class KakunaSetup(Setup):
    """
    The current best setup if the user does not want to perform RNG manipulation.
    It requires the user to have a Kakuna, which can be traded from another game.
    """
    def __init__(self):
        self.name = 'Kakuna setup'
        self.version = '0.0.1'
        self.author = "Jorik Devreese (RETIREglitch)"


    def run(self) -> None:
        # TM slot in item data of backup save file
        # This is the memory section used in current ASE setups
        execution_offsets = {
            "min_offset": 0x110000,
            "max_offset": 0x1102E8
        }

        pokemon = HallOfFamePokemon(species="Kakuna",
                                    level=0x16,
                                    forme=0,
                                    pid=0x12345678,
                                    trainer_id=0xffff,
                                    secret_id=0xffff,
                                    name="h",
                                    trainer_name="kh", 
                                    move1="Bug Bite",
                                    move2=0x0, 
                                    move3=0x0, 
                                    move4=0x0
                                    )
    
        record_28 = HallOfFameRecord(party=[pokemon], year=2022, month=12, day=23)
        record_29 = HallOfFameRecord(party=[pokemon], year=2022, month=12, day=22)
        record_30 = HallOfFameRecord(party=[pokemon])

        records = [record_28, record_29, record_30]
        # put 30 if you want to fill the entire hall of fame, with record_start = 0
        # Since only records 28-30 are used, I only fill those 3 records. 
        # Note that the code expects 0-indexed records, so record_start = 27

        hall_of_fame = HallOfFame(records=records, record_start=27)
        simulation = Simulation(execution_offsets=execution_offsets, hall_of_fame=hall_of_fame)
        success_log = simulation.simulate_full()
        simulation.plot_simulations(success_log)