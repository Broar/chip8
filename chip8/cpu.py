import struct
from random import randint

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
HEIGHT = 64
WIDTH = 32

class CPU(object):
    """

    A class representing the CHIP-8 CPU that follows the below specifications:

    http://en.wikipedia.org/wiki/CHIP-8#Virtual_machine_description
    http://mattmik.com/chip8.html

    """

    def __init__(self):
        """

        Create a new CPU object for the CHIP-8 virtual machine.

        """

        # Graphics
        self.gfx = [[0 for x in range(WIDTH)] for y in range(HEIGHT)]

        # Main memory
        self.memory = [0 for x in range(MEMORY)]

        # Registers: 16 general purpose and an address index
        self.v = [0 for x in range(REGISTERS)]
        self.i = 0

        # Program counter
        self.pc = PROGRAM_COUNTER_START

        # Stack: The 16 level stack itself and a stack pointer
        self.stack = [0 for x in range(STACK)]
        self.sp = 0

        # Timers: A delay timer and sound timer that both count down at 60 Hz.
        # The sound timer makes a beeping noise while it is non-zero
        self.delay = 0
        self.sound = 0

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
            0xC000 : self._CXNN}

        # Subroutine table
        self.subroutine = {
            0x0000 : self._00E0, 
            0x000E : self._00EE}

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
            0x000E : self._8XYE}

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

    def execute_cycle(self):
        """

        Perform a single cycle of the CHIP-8 CPU

        """
        execute_opcode(fetch_opcode())
        update_timers()

    def fetch_opcode(self):
        """
        
        Fetch the next opcode in memory

        @returns the next opcode in memory

        """
        return (self.memory[self.pc] << 8) | self.memory[self.pc + 1]

    def decode_opcode(self, opcode):
        """

        Decode the specified opcode

        @param opcode the opcode to decode
        @returns the most significant nibble (4 bits) of the opcode

        """
        return opcode & 0xF000

    def execute_opcode(self, opcode):
        """

        Execute an action based on the decoded opcode

        @param opcode the opcode to decode

        """
        self.opcodes[self.decode_opcode(opcode)](opcode)

    def update_timers(self):
        """
        
        Perform any updates to the CPU's timers

        """
        if self.delay > 0:
            self.delay -= 1

        if self.sound > 0:
            if self.sound == 1:
                print("Beep!")
            self.sound -= 1

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

    def _0KKK(self, opcode):
        """

        Determine which subroutine action to perform based on the specified 
        opcode

        @param opcode the opcode

        """
        self.subroutine[self.get_n(opcode)]()

    def _00E0(self):
        """

        00E0
        Clear the screen

        """
        for x in range(HEIGHT):
            for y in range(WIDTH):
                self.gfx[x][y] = 0x0

        self.pc += 2

    def _00EE(self):
        """

        00EE
        Return from a subroutine

        """
        self.sp -= 1
        self.pc = self.stack[self.sp] + 2   

    def _1NNN(self, opcode):
        """

        1NNN
        Jump to address NNN

        @param opcode the opcode

        """
        self.pc = self.get_nnn(opcode)

    def _2NNN(self, opcode):
        """
        
        2NNN
        Execute subroutine starting at address NNN

        @param opcode the opcode

        """
        self.stack[self.sp] = self.pc
        self.sp += 1
        self.pc = self.get_nnn(opcode)

    def _3XNN(self, opcode):
        """

        3XNN
        Skip the following instruction if the value of register VX equals NN

        @param opcode the opcode

        """
        x = self.get_x(opcode)
        if self.v[x] == self.get_nn(opcode):
            self.pc += 2

        self.pc += 2

    def _4XNN(self, opcode):
        """

        4XNN
        Skip the following instruction if the value of register VX is not 
        equal to NN

        @param opcode the opcode

        """
        x = self.get_x(opcode)
        if (self.v[x] != self.get_nn(opcode)):
            self.pc += 2

        self.pc += 2

    def _5XY0(self, opcode):
        """

        5XY0
        Skip the following instruction if the value of register VX is 
        equal to the value of register VY

        @param opcode the opcode

        """
        x = self.get_x(opcode)
        y = self.get_y(opcode)
        if (self.v[x] == self.v[y]):
            self.pc += 2

        self.pc += 2

    def _6XNN(self, opcode):
        """

        6XNN
        Store number NN in register VX

        @param opcode the opcode

        """
        x = self.get_x(opcode)
        self.v[x] = self.get_nn(opcode)
        self.pc += 2

    def _7XNN(self, opcode):
        """

        7XNN
        Add the value NN to register VX

        @param opcode the opcode

        """
        x = self.get_x(opcode)
        self.v[x] += self.get_nn(opcode)
        self.v[x] %= 256
        self.pc += 2

    def _8XYK(self, opcode):
        """

        Determine which arthimetic to perform based on the specified opcode

        @param opcode the opcode

        """
        self.arthimetic[self.get_n(opcode)](self.get_x(opcode), self.get_y(opcode))

    def _8XY0(self, x, y):
        """

        8XY0
        Store the value of register VY in register VX

        @param x the index for VX
        @param y the index for VY

        """
        self.v[x] = self.v[y]
        self.pc += 2

    def _8XY1(self, x, y):
        """

        8XY1
        Set VX to VX OR VY

        @param x the index for VX
        @param y the index for VY

        """
        self.v[x] |= self.v[y]
        self.pc += 2

    def _8XY2(self, x, y):
        """

        8XY2
        Set VX to VX AND VY

        @param x the index for VX
        @param y the index for VY

        """
        self.v[x] &= self.v[y]
        self.pc += 2

    def _8XY3(self, x, y):
        """

        8XY2
        Set VX to VX XOR VY

        @param x the index for VX
        @param y the index for VY

        """
        self.v[x] ^= self.v[y]
        self.pc += 2

    def _8XY4(self, x, y):
        """

        8XY4
        Add the value of register VY to register VX
        Set VF to 01 if a carry occurs
        Set VF to 00 if a carry does not occur

        @param x the index for VX
        @param y the index for VY

        """
        if self.v[x] + self.v[y] > 255:
            self.v[0xF] = 1
        else:
            self.v[0XF] = 0

        self.v[x] += self.v[y]
        self.v[x] %= 256
        self.pc += 2

    def _8XY5(self, x, y):
        """

        8XY5
        Subtract the value of register VY from register VX
        Set VF to 00 if a borrow occurs
        Set VF to 01 if a borrow does not occur

        @param x the index for VX
        @param y the index for VY

        """
        if self.v[x] < self.v[y]:
            self.v[x] = 256 + (self.v[x] - self.v[y])
            self.v[0xF] = 0
        else:
            self.v[x] = self.v[x] - self.v[y]
            self.v[0xF] = 1

        self.pc += 2

    def _8XY6(self, x, y):
        """

        8XY6
        Store the value of register VY shifted right one bit in register VX
        Set register VF to the least significant bit prior to the shift

        @param x the index for VX
        @param y the index for VY

        """
        self.v[0xF] = self.v[y] & 0x01
        self.v[y] <<= 1
        self.v[x] = self.v[y]
        self.pc +=2 

    def _8XY7(self, x, y):
        """
        
        8XY7
        Set register VX to the value of VY minus VX
        Set VF to 00 if a borrow occurs
        Set VF to 01 if a borrow does not occur

        @param x the index for VX
        @param y the idnex for VY

        """
        if self.v[y] < self.v[x]:
            self.v[x] = 256 + (self.v[y] - self.v[x])
            self.v[0xF] = 0
        else:
            self.v[x] = self.v[y] - self.v[x]
            self.v[0xF] = 1

        self.pc += 2

    def _8XYE(self, x, y):
        """

        8XYE
        Store the value of register VY shifted left one bit in register VX
        Set register VF to the most significant bit prior to the shift

        @param x the index for VX
        @param y the index for VY

        """
        self.v[0xF] = (self.v[y] & 0x80) >> 7
        self.v[y] >>= 1
        self.v[x] = self.v[y]
        self.pc += 2

    def _9XY0(self, opcode):
        """

        9XY0
        Skip the following instruction if the value of register VX is 
        not equal to the value of register VY

        @param opcode the opcode

        """
        x = self.get_x(opcode)
        y = self.get_y(opcode)
        if self.v[x] != self.v[y]:
            self.pc += 2

        self.pc += 2

    def _ANNN(self, opcode):
        """

        ANNN
        Store memory address NNN in register I

        @param opcode the opcode

        """
        self.i = self.get_nnn(opcode)
        self.pc += 2

    def _BNNN(self, opcode):
        """

        BNNN
        Jump to address NNN + V0

        @param opcode the opcode

        """
        self.pc = self.get_nnn(opcode) + self.v[0]

    def _CXNN(self, opcode):
        """

        CXNN
        Set VX to a random number with a mask of NN

        @param opcode the opcode

        """
        x = self.get_x(opcode)
        self.v[x] = randint(0, 255) & self.get_nn(opcode)
        self.pc += 2