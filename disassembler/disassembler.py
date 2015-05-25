"""

A simple disassembler for CHIP-8 ROMS

@author Steven Briggs
@version 2015.05.24

"""

import sys
import struct

# Constants
REQUIRED_ARGS = 2
MAX_LENGTH = 3854

class C8Disassembler(object):

    def __init__(self, rom):
        """

        Create a new C8Disassembler object

        """

        self.program = [0 for x in range(MAX_LENGTH)]

        # Opcode table: 'K' denotes an opcode with multiple matches
        self.opcodes = {
            0x0000 : self._0KKK,
            0x1000 : self._1NNN,
            0x2000 : self._2NNN,
            0x3000 : self._3XNN,
            0x4000 : self._4XNN,
            0x5000 : self._5XY0,
            0x6000 : self._6XNN,
            0x7000 : self._7XNN,
            0x8000 : self._8XYK,
            0x9000 : self._9XY0,
            0xA000 : self._ANNN,
            0xB000 : self._BNNN,
            0xC000 : self._CXNN,
            0xD000 : self._DXYN,
            0xE000 : self._EXKK,
            0xF000 : self._FXKK
        }

        # Subroutine table
        self.subroutine = {
            0x0000 : self._00E0, 
            0x000E : self._00EE
        }

        # Arthimetic table
        self.arthimetic = {
            0x0000 : self._8XY0,
            0x0001 : self._8XY1,
            0x0002 : self._8XY2,
            0x0003 : self._8XY3,
            0x0004 : self._8XY4, 
            0x0005 : self._8XY5,
            0x0006 : self._8XY6,
            0x0007 : self._8XY7,
            0x000E : self._8XYE
        }

        # Skip keys table
        self.skip_keys = {
            0x000E : self._EX9E,
            0x0001 : self._EXA1
        }

        # Misc table
        self.misc = {
            0x0007 : self._FX07,
            0x000A : self._FX0A,
            0x0015 : self._FX15,
            0x0018 : self._FX18,
            0x001E : self._FX1E,
            0x0029 : self._FX29,
            0x0033 : self._FX33,
            0x0055 : self._FX55,
            0x0065 : self._FX65
        }

        self.load_rom(rom)

    def load_rom(self, path, offset=0):
        """

        Read the file specified by path into the buffer

        @param path the location of the file to read in
        @param offset the memory address to start writing at

        """

        # Read the file into main memory byte-by-byte
        with open(path, "rb") as f:
            b = f.read(1)
            while b:
                self.program[offset] = struct.unpack("B", b)[0]
                offset += 1
                b = f.read(1)

    def fetch_opcode(self, i):
        """

        Get the instruction located in the program at i

        @param i the index of the instruction to fetch
        @returns the next instruction of the program

        """
        return (self.program[i] << 8) | self.program[i + 1]

    def lookup_opcode(self, opcode):
        """

        Search for the opcode function to perform

        @param opcode the opcode
        @returns the disassembled instruction in string format

        """
        self.opcodes[(opcode & 0xF000)](opcode)

    def disassemble(self):
        """

        Transform a CHIP-8 ROM into a human-readable text file

        """
        for i in range(MAX_LENGTH):
            opcode = self.fetch_opcode(i)

            # We treat a blank opcode as a signal that the program has ended
            if opcode == 0x0:
                break

            print("{0:#X}\t".format(i),)
            print("{0}\n".format(self.lookup_opcode(opcode)))
            i += 2

    # Helpful getter fuctions
    def get_hi(self, opcode):
        """

        Get the high byte of the opcode

        @param opcode the opcode
        @returns the high byte of the opcode

        """
        return (opcode & 0xFF00) >> 8

    def get_lo(self, opcode):
        """

        Get the low byte of the opcode

        @param opcode the opcode
        @returns the low byte of the opcode

        """
        return (opcode & 0x00FF)

def usage(name):
    """

    Create a message describing how to invoke the program

    @param name name of the program being run
    @returns a string containing the usage message

    """

    return "Usage: python {0} rom".format(name)


def main(argv):
    """

    Driver function for the disassembler. 

    Requires two arguments that specify the CHIP-8 ROM to be disassembled
    and a file to write the output.

    @param args the arguments for invoking the program

    """
    
    # Check that there are enough arguments to run the emulator
    if len(argv) < REQUIRED_ARGS:
        exit(usage(argv[0]))

    rom = argv[1]

    print("CHIP-8 Disassembler v.0.1")
    print("Input: {0}\n".format(rom))

    disassembler = C8Disassembler(rom)
    disassembler.disassemble()


if __name__ == "__main__":
    sys.exit(main(sys.argv))