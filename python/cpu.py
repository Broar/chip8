import struct

"""

An emulated CPU for the CHIP-8 virtual machine

@author Steven Briggs
@version 2015.05.17

"""

# Constants
MEMORY = 4096
REGISTERS = 16
STACK = 16
PROGRAM_COUNTER_START = 0x200

class CPU(object):
    """

    A class representing the CHIP-8 CPU that follows the below specifications:

    http://en.wikipedia.org/wiki/CHIP-8#Virtual_machine_description
    http://devernay.free.fr/hacks/chip8/C8TECH10.HTM

    """

    def __init__(self):
        """

        Create a new CPU object for the CHIP-8 virtual machine.

        """

        # Main memory
        self.memory = [0 for x in range(MEMORY)]

        # Registers. 16 general purpose and an address index
        self.v = [0 for x in range(REGISTERS)]
        self.i = 0

        # Program counter
        self.pc = PROGRAM_COUNTER_START

        # Stack. The 16 level stack itself and a stack pointer
        self.stack = [0 for x in range(STACK)]
        self.sp = 0

        # Timers. A delay timer and sound timer that both count down at 60 Hz.
        # The sound timer makes a beeping noise while it is non-zero
        self.delay = 0
        self.sound = 0

        self.load_font()

    def load(self, path, offset=0):
        """

        Read the file specified by path into main memory

        @param path the location of the file to read in
        @param offset the memory address to start writing at

        """

        # Read the file into main memory byte-by-byte
        with open(path, "rb") as f:
            b = f.read(1)
            while b:
                self.memory[offset] = struct.unpack("B", b)[0]
                offset += 1
                b = f.read(1)

    def load_rom(self, path):
        """

        Read a specified ROM into main memory

        @param path the path to the ROM to be read
        @pre path must be valid and point to a CHIP-8 ROM

        """

        # Read the CHIP-8 ROM into memory starting at address 0x200
        self.load(path, PROGRAM_COUNTER_START)

    def load_font(self):
        """

        Read the font set into main memory

        """

        # Read the CHIP-8 fontset into memory from addresses 0x0 - 0x50
        self.load("../res/font.chip8")