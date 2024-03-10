from hall_of_fame import HallOfFame
from hall_of_fame_record import HallOfFameRecord
from hall_of_fame_pokemon import HallOfFamePokemon
from common import Memory

import logging
import json
import numpy as np
from typing import Union, List, Tuple, Dict

class CommandSimulator:
    @staticmethod
    def advance_execution(memory: np.ndarray[np.uint8], address: int, command: Dict) -> Tuple[int, bool]:
        parameters = command.get("parameters")
        address, success = CommandSimulator.advance_parameters(memory, address, parameters)
        return address, success
    
    @staticmethod
    def advance_parameters(memory: np.ndarray[np.uint8], address: int, parameters: Dict) -> int:
        for param, size in parameters.items():
            param_value, address = Memory.get_value_as_int(memory, address, size)
            if (CommandSimulator.param_aborts_execution(param, param_value)):
                return address, False
        return address, True
    
    @staticmethod
    def param_aborts_execution(param:str, param_value: int) -> bool:
        """
        Checks if a parameter value should abort execution.
        The implementation is incomplete and does not cover all cases.
        However, most aborts occur due to invalid work values, which are checked.
        """
        for param_name in ["wk","work"]:
            if param_name in param.lower():
                if param_value < 0x4000:
                    return True
                if param_value > 0x8054:
                    return True
        return False
    
class JumpCommandSimulator(CommandSimulator):
    @staticmethod
    def advance_execution(memory: np.ndarray[np.uint8], address: int, command: Dict) -> Tuple[int, bool]:
        parameters = command.get("parameters")
        address, success = JumpCommandSimulator.advance_parameters(memory, address, parameters)
        return address, success
    
    @staticmethod
    def advance_parameters(memory: np.ndarray[np.uint8], address: int, parameters: Dict) -> int:
        """
        Advances the execution of the jump command.
        Note that conditional jumps are not yet supported, and default to true.
        """
        for param, size in parameters.items():
            param_value, address = Memory.get_value_as_int(memory, address, size)
            for param_name in ["jmp","jump"]:
                if param_name in param.lower():
                    if param_value >= 0x80000000:
                        param_value -= 0x100000000
                    address = address + param_value   
        return address, True

class ScriptSimulator:
    def __init__(self):
        self.script_data = self.__load_script_data()

    def __load_script_data(self) -> Dict:
        with open("./data/script_data.json") as f:
            data = json.load(f)

        script_data = {}
        for key, value in data.items():
            command_id = int(key, 16)
            command = value.get("command")
            parameters = value.get("parameters")
            parser_class = value.get("parser_class", None)
            parameters_formatted = {}
            for param in parameters:
                if param in parameters_formatted:
                    parameters_formatted[param] = parameters_formatted[param] + 1
                else:
                    parameters_formatted[param] = 1
            script_data[command_id] = {
                "id": command_id,
                "command": command,
                "parameters": parameters_formatted,
                "parser_class": parser_class
            }
        return script_data


    def advance_execution(self, memory: np.ndarray[np.uint8], address: int) -> Tuple[int, bool]:
        """
        Advances the execution of the script.

        Execution aborts if a return command or invalid command is encountered.
        Some commands may require additional processing or conditions to be met.

        Args:
            memory (np.ndarray[np.uint8]): The memory array.
            address (int): The address to advance the execution from.

        Returns:
            int: The new address to execute from.
            bool: Whether the execution should continue.
        
        """
        command_id, address = Memory.get_value_as_int(memory, address, 2)
        command = self.script_data.get(command_id, None)

        if (self.command_aborts_execution(command)):
            return address, False # abort execution
        parser_class = command.get("parser_class", None)
        if (parser_class is not None):
            # convert parser_class string to class and call advance_execution method
            _class = globals()[parser_class]
            if (not issubclass(_class, CommandSimulator)): # check if class is a subclass of CommandSimulator
                logging.warning(f"Invalid parse condition class: {parser_class}")
                return address, False
            return _class.advance_execution(memory, address, command)
        else:
            return CommandSimulator.advance_execution(memory, address, command)
        
    def command_aborts_execution(self, command: Dict) -> bool:
        if command is None:
            return True # invalid command
        if command.get("command").lower() in ["end", "return"]:
            return True # return command
        return False

class Simulation:
    def __init__(self,
                 execution_offsets: Dict[str, int] = None,
                 script_simulator: ScriptSimulator = ScriptSimulator(),
                 hall_of_fame: HallOfFame = None,
                 hall_of_fame_offset: int = 0x2C2B8 # offset for DP
                 ):
        self.execution_offsets = execution_offsets
        self.script_simulator = script_simulator
        self.hall_of_fame = hall_of_fame
        self.hall_of_fame_offset = hall_of_fame_offset
        self.__memory_size = 0x2400000
        
    def __reset_memory(self) -> None:
        self.__memory = np.zeros(self.__memory_size, dtype=np.uint8)

    def __create_memory(self, base: int = 0x226D260) -> None:
        self.__reset_memory()
        index = base + self.hall_of_fame_offset
        size = self.hall_of_fame.memory.size
        self.__memory[index:index + size] = self.hall_of_fame.memory

    def get_success_rate(self, logs: Dict) -> float:
        total_successes = 0
        total_attempts = 0
        for base, log in logs.items():
            successes = len([x for x in log if x])
            total_successes += successes
            total_attempts += len(log)
        return total_successes/total_attempts

    def plot_simulations(self, logs: Dict, show_plot: bool = True) -> None:
        import matplotlib.pyplot as plt
        total_successes = 0
        total_attempts = 0
        min_base = 0
        for base, log in logs.items():
            if min_base == 0:
                min_base = int(base,16)
            successes = len([x for x in log if x])
            total_successes += successes
            total_attempts += len(log)

            logging.info(f"Base: {base}, Successes: {successes}/{len(log)}")
            logging.info(f"Success rate: {round(successes/len(log)*100,2)}%")

            plt.bar(int(base,16)-min_base,successes/len(log)*100,color="lightblue")

        logging.info(f"Total successes: {total_successes}/{total_attempts}")
        logging.info(f"Total success rate: {round(total_successes/total_attempts*100,2)}%")
            
        plt.title("Success rate per base")
        plt.xlabel("Base")
        plt.ylabel("Success rate (%)")

        if show_plot:
            plt.show()

    def simulate_full(self, min_base:int = 0x226D260) -> Dict:
        success_log = {}
        for base in range(min_base, min_base + 0x104, 4):
            success_log[hex(base)] = self.simulate_with_base(base)
        return success_log

    def simulate_with_base(self, 
                           base_pre_reset: int, 
                           min_base:int = 0x226D260) -> List:
        self.__create_memory(base_pre_reset)
        success_log = []
        for base in range(min_base, min_base + 0x104, 4):
            success_log.append(self.simulate(base))
        return success_log

    def simulate(self, 
                 base: int,
                 offset: int = 0x2EAF0,
                 range_limit: int = 0x800,
                 execution_limit: int = 1000
                 ) -> bool:
        start_address = base + offset
        address = start_address

        min_address = base + self.execution_offsets.get("min_offset")
        max_address = base + self.execution_offsets.get("max_offset")

        execution_count = 0
        while (address < start_address + range_limit) and (execution_count < execution_limit):
            address, success = self.script_simulator.advance_execution(self.__memory, address)
            if (not success):
                return False
            
            if (min_address <= address <= max_address):
                return True
            
            execution_count += 1
        return False
            

if __name__ == "__main__":
    np.set_printoptions(formatter={'int':hex})
    logging.basicConfig(level=logging.INFO)

    # TM slot in item data of backup save file
    # This is the memory section used in current ASE setups
    execution_offsets = {
        "min_offset": 0x110000,
        "max_offset": 0x1102E8
    }

    # Below are the simulation details for the current Gyarados RNG based setup
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
    
    hall_of_fame_record = HallOfFameRecord(party=[pokemon], year=2076, month=1, day=1)

    hall_of_fame_records = [hall_of_fame_record] * 30
    hall_of_fame = HallOfFame(records=hall_of_fame_records, record_start=0)
    simulation = Simulation(execution_offsets=execution_offsets, 
                            hall_of_fame=hall_of_fame)
    success_log = simulation.simulate_full()
    simulation.plot_simulations(success_log)
            

        
        
        

    