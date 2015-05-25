import sys
import pygame
from pygame import HWSURFACE
from time import sleep
from cpu import CPU, HEIGHT, WIDTH

"""

Contains the main driver function for the CHIP-8 emulator

@author Steven Briggs
@version 2015.05.17

"""

# Usage
REQUIRED_ARGS = 2

# Timing
DELAY = 0.001

# Screen display
SCALE = 10
DEPTH = 8
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

def usage(program):
    """

    Create a message describing how to invoke the program

    @param program name of the program being return
    @returns a string containing the usage message

    """

    return "Usage: python {0} rom".format(program)

def draw(screen, gfx):
    """

    Draw the graphics to the screen

    @param screen the screen to be drawn to
    @param gfx the graphics to draw to the screen

    """
    
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if gfx[(y * WIDTH) + x]:
                pygame.draw.rect(screen, WHITE, (x * SCALE, y * SCALE, SCALE, SCALE))
            else:
                pygame.draw.rect(screen, BLACK, (x * SCALE, y * SCALE, SCALE, SCALE))

    pygame.display.flip()

def main(argv):
    """

    Driver for the CHIP-8 emulator

    @param argv the argument values

    """

    # Check that there are enough arguments to run the emulator
    if len(argv) < REQUIRED_ARGS:
        exit(usage(argv[0]))

    # Prepare the emulator
    cpu = CPU()
    cpu.load_rom(argv[1])

    # Prepare the screen to be displayed
    pygame.init()
    screen = pygame.display.set_mode((WIDTH * SCALE, HEIGHT * SCALE), HWSURFACE, DEPTH)
    pygame.display.set_caption("CHIP-8")

    # Emulation loop
    running = True
    while running:
        cpu.execute_cycle()

        if cpu.shouldDraw:
            draw(screen, cpu.gfx)
            cpu.shouldDraw = False

        # Consume any events that occured in the past cycle
        for event in pygame.event.get():
            cpu.update_keys(pygame.key.get_pressed())
            
            if event.type == pygame.QUIT:
                running = False

        sleep(DELAY)

if __name__ == "__main__":
    sys.exit(main(sys.argv))