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

    Create a message describing how to invoke the program

    @param program name of the program being return
    @returns a string containing the usage message

    """

    return "Usage: python {0} rom".format(program)

def main(argv):
    """

    Driver for the CHIP-8 emulator

    @param argv the argument values

    """

    # Check that there are enough arguments to run the emulator
    if (len(argv) < REQUIRED_ARGS):
        exit(usage(argv[0]))

    print("chip8 emulator")
    print("argv: ", argv)

    cpu = CPU()


if __name__ == "__main__":
    sys.exit(main(sys.argv))