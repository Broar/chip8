"""

A simple disassembler for CHIP-8 ROMS

@author Steven Briggs
@version 2015.05.24

"""

import sys
import struct

# Constants
REQUIRED_ARGS = 2
MAX_LENGTH = 4096
PROGRAM_START = 512

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

        self.load_rom(rom, PROGRAM_START)

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
        return self.opcodes[(opcode & 0xF000)](opcode)

    def disassemble(self):
        """

        Transform a CHIP-8 ROM into a human-readable text file

        """
        for i in range(PROGRAM_START, MAX_LENGTH, 2):
            opcode = self.fetch_opcode(i)

            # We treat a blank opcode as a signal that the program has ended
            if opcode == 0x0:
                break

            try:
                trans = self.lookup_opcode(opcode)
            except KeyError:
                print "ERROR {0:X}".format(opcode)

            hi = self.get_hi(opcode)
            lo = self.get_lo(opcode)

            print("{0:X} {1:X} {2:01X} {3}".format(i, hi, lo, trans))

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

    def get_nnn(self, opcode):
        """

        Get the lowest 12 bits (nnn or addr) of an instruction

        @param opcode the opcode
        @returns lowest 12 bits of an instruction representing a memory address

        """
        return opcode & 0x0FFF

    def get_nn(self, opcode):
        """

        Get the lowest 8 bits (nn or byte) of an instruction
        
        @param opcode the opcode
        @returns the lowest 8 bits of an instruction
        
        """
        return opcode & 0x00FF

    def get_n(self, opcode):
        """

        Get the lowest 4 bits (n or nibble) of an instruction

        @param opcode the opcode
        @returns lowest 4 bits of an instruction

        """
        return opcode & 0x000F

    def get_x(self, opcode):
        """

        Get the lower 4 bits of the high byte (x) of an instruction
        
        @param opcode the opcode
        @returns the lower 4 bits of the high byte of an instruction

        """
        return (opcode & 0x0F00) >> 8

    def get_y(self, opcode):
        """

        Get the higher 4 bits of the low byte (y) of an instruction
        
        @param opcode the opcode
        @returns the higher 4 bits of the low byte of an instruction
        
        """
        return (opcode & 0x00F0) >> 4

    # Opcode functions for disassembly    
    def _0KKK(self, opcode):
        return self.subroutine[self.get_n(opcode)]()

    def _00E0(self):
        return "CLS"

    def _00EE(self):
        return "RET"

    def _1NNN(self, opcode):
        return "JP {0:X}".format(self.get_nnn(opcode))

    def _2NNN(self, opcode):
        return "CALL {0:X}".format(self.get_nnn(opcode))
    
    def _3XNN(self, opcode):
        return "SE V{0:X}, {1:X}".format(self.get_x(opcode), self.get_nn(opcode))

    def _4XNN(self, opcode):
        return "SNE V{0:X}, {1:X}".format(self.get_x(opcode), self.get_nn(opcode))

    def _5XY0(self, opcode):
        return "SE V{0:X}, V{1:X}".format(self.get_x(opcode), self.get_y(opcode))

    def _6XNN(self, opcode):
        return "LD V{0:X}, {1:X}".format(self.get_x(opcode), self.get_nn(opcode))

    def _7XNN(self, opcode):
        return "ADD V{0:X}, {1:X}".format(self.get_x(opcode), self.get_nn(opcode))

    def _8XYK(self, opcode):
        return self.arthimetic[self.get_n(opcode)](self.get_x(opcode), self.get_y(opcode))

    def _8XY0(self, x, y):
        return "LD V{0:X}, V{1:X}".format(x, y)

    def _8XY1(self, x, y):
        return "OR V{0:X}, V{1:X}".format(x, y)

    def _8XY2(self, x, y):
        return "AND V{0:X}, V{1:X}".format(x, y)

    def _8XY3(self, x, y):
        return "XOR V{0:X}, V{1:X}".format(x, y)

    def _8XY4(self, x, y):
        return "ADD V{0:X}, V{1:X}".format(x, y)

    def _8XY5(self, x, y):
        return "SUB V{0:X}, V{1:X}".format(x, y)

    def _8XY6(self, x, y):
        return "SHR V{0:X} {{, V{1:X}}}".format(x, y)

    def _8XY7(self, x, y):
        return "SUBN V{0:X}, V{1:X}".format(x, y)

    def _8XYE(self, x, y):
        return "SHL V{0:X}, {{, V{1:X}}}".format(x, y)

    def _9XY0(self, opcode):
        return "SNE V{0:X}, V{1:X}".format(self.get_x(opcode), self.get_y(opcode))

    def _ANNN(self, opcode):
        return "LD I, {0:X}".format(self.get_nnn(opcode))

    def _BNNN(self, opcode):
        return "JP V0, {0:X}".format(self.get_nnn(opcode))

    def _CXNN(self, opcode):
        return "RND V{0:X}, {1:X}".format(self.get_x(opcode), self.get_nn(opcode))

    def _DXYN(self, opcode):
        x = self.get_x(opcode)
        y = self.get_y(opcode)
        n = self.get_n(opcode)
        return "DRW V{0:X}, V{1:X}, {2:X}".format(x, y, n)

    def _EXKK(self, opcode):
        return self.skip_keys[self.get_n(opcode)](self.get_x(opcode))

    def _EX9E(self, x):
        return "SKP V{0:X}".format(x)

    def _EXA1(self, x):
        return "SKNP V{0:X}".format(x)

    def _FXKK(self, opcode):
        return self.misc[self.get_nn(opcode)](self.get_x(opcode))

    def _FX07(self, x):
        return "LD V{0:X}, DT".format(x)

    def _FX0A(self, x):
        return "LD V{0:X}, K".format(x)

    def _FX15(self, x):
        return "LD DT, V{0:X}".format(x)

    def _FX18(self, x):
        return "LD ST, V{0:X}".format(x)

    def _FX1E(self, x):
        return "ADD I, V{0:X}".format(x)

    def _FX29(self, x):
        return "LD F, V{0:X}".format(x)

    def _FX33(self, x):
        return "LD B, V{0:X}".format(x)

    def _FX55(self, x):
        return "LD [I], V{0:X}".format(x)

    def _FX65(self, x):
        return "LD V{0:X}, [I]".format(x)

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

    Requires a single argument that specifies the CHIP-8 ROM to be disassembled.

    @param argv the arguments for invoking the program

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