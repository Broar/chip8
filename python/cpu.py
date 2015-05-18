"""

An emulated CPU for the CHIP-8 virtual machine

@author Steven Briggs
@version 2015.05.17

"""

# Constants
MEMORY = 4096
REGISTERS = 16

class CPU(object):
	"""

	A class representing the CHIP-8 CPU that uses the following specifications:

    http://en.wikipedia.org/wiki/CHIP-8#Virtual_machine_description
    http://devernay.free.fr/hacks/chip8/C8TECH10.HTM

	"""

	def __init__(self):
		"""

		Create a new CPU object for the CHIP-8 virtual machine.

        According to the specifications, the CHIP-8 CPU contains the following:

        * 4K (4096 bytes) of memory
        * 16 8-bit registers enumerated from V0 to VF
          * VF doubles as a carry flag
        * An address register called I
        * A program counter called PC

		"""

        # TODO: Add remaining CPU components
		self.memory = [0 for x in range(MEMORY)]
		self.v = [0 for x in range(REGISTERS)]
		self.i = 0
		self.pc = 0
