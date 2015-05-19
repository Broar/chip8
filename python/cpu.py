import struct
import os

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
    http://devernay.free.fr/hacks/chip8/C8TECH10.HTM

    Variable Legend:

    nnn or addr - A 12-bit value, the lowest 12 bits of the instruction
    n or nibble - A 4-bit value, the lowest 4 bits of the instruction
    x - A 4-bit value, the lower 4 bits of the high byte of the instruction
    y - A 4-bit value, the upper 4 bits of the low byte of the instruction
    kk or byte - An 8-bit value, the lowest 8 bits of the instruction

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

        # Opcode tables
        self.opcodes = {
            0x1000 : self.jump,
            0x2000 : self.call,
            0x3000 : self.skip_vx_equals_kk,
            0x4000 : self.skip_vx_not_equal_kk,
            0x5000 : self.skip_vx_equal_vy,
            0x6000 : self.set_vx_to_kk,
            0x7000 : self.add_kk_to_vx}

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
        if (self.delay > 0):
            self.delay -= 1

        if (self.sound > 0):
            if (self.sound == 1):
                print("Beep!")
            self.sound -= 1

    def get_addr(self, opcode):
        """

        Get the lowest 12 bits (nnn or addr) of an instruction

        @param opcode the opcode
        @returns lowest 12 bits of an instruction representing a memory address

        """
        return opcode & 0x0FFF

    def get_nibble(self, opcode):
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

    def get_byte(self, opcode):
        """

        Get the lowest 8 bits (kk or byte) of an instruction
        
        @param opcode the opcode
        @returns the lowest 8 bits of an instruction
        
        """
        return opcode & 0x00FF

    def jump(self, opcode):
        """

        1nnn - JP addr
        Jump to location nnn.

        Set the program counter to nnn.

        @param opcode the opcode

        """
        self.pc = self.get_addr(opcode)

    def call(self, opcode):
        """
        
        2nnn - CALL addr
        Call subroutine at nnn.

        Increment the stack pointer and puts the current PC on the top of the
        stack. The PC is then set to nnn.

        @param opcode the opcode

        """
        self.sp += 1
        self.stack[self.sp] = self.pc
        self.pc = self.get_addr(opcode)

    def skip_vx_equals_kk(self, opcode):
        """

        3xkk - SE Vx, byte
        Skip next instruction if Vx = kk.

        Compare register Vx to kk, and if they are equal, increment the 
        program counter by 2.

        @param opcode the opcode

        """
        x = self.get_x(opcode)
        if (self.v[x] == self.get_byte(opcode)):
            self.pc += 2

    def skip_vx_not_equal_kk(self, opcode):
        """

        3xkk - SE Vx, byte
        Skip next instruction if Vx != kk.

        Compare register Vx to kk, and if they are not equal, increment the 
        program counter by 2.

        @param opcode the opcode

        """
        x = self.get_x(opcode)
        if (self.v[x] == self.get_byte(opcode)):
            self.pc += 2

        self.pc += 2

    def skip_vx_equal_vy(self, opcode):
        """

        5xy0 - SE Vx, Vy
        Skip next instruction if Vx = Vy.

        Compare register Vx to register Vy, and if they are equal, increment 
        the program counter by 2.

        @param opcode the opcode

        """
        x = self.get_x(opcode)
        y = self.get_y(opcode)
        if (self.v[x] == self.v[y]):
            self.pc += 2

        self.pc += 2

    def set_vx_to_kk(self, opcode):
        """

        6xkk - LD Vx, byte
        Set Vx = kk.

        Put the value kk into register Vx.

        @param opcode the opcode

        """
        x = self.get_x(opcode)
        self.v[x] = self.get_byte(opcode)
        self.pc += 2

    def add_kk_to_vx(self, opcode):
        """

        7xkk - ADD Vx, byte
        Set Vx = Vx + kk.

        Adds the value kk to the value of register Vx, then stores the result in Vx.

        @param opcode the opcode

        """
        x = self.get_x(opcode)
        self.v[x] += self.get_byte(opcode)
        self.pc += 2