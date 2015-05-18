import sys
from cpu import CPU

"""

Contains the main driver function for the CHIP-8 emulator

@author Steven Briggs
@version 2015.05.17

"""

REQUIRED_ARGS = 2

def usage(program):
    """

    Prints a usage message to the command-line

    """

    print("Usage: python {0} rom".format(program))

def main(argv):
    """

    Driver for the CHIP-8 emulator

    @param argv the argument values

    """

    if (len(argv) < REQUIRED_ARGS):
        usage(argv[0])
        exit()

    print("chip8 emulator")
    print("argv: ", argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv))