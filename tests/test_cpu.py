import sys
import unittest

sys.path.append("..")

from chip8.cpu import CPU


"""

Simple unit tests for the CHIP-8 CPU module

@author Steven Briggs
@version 2015.05.19

"""

class TestCPU(unittest.TestCase):
    """

    A class for testing the instructions of the CHIP-8 CPU

    """

    def setUp(self):
        self.cpu = CPU()

    def test_00E0(self):
        # Draw to every other pixel on the screen
        for x in range(len(self.cpu.gfx)):
            for y in range(len(self.cpu.gfx[x])):
                if y % 2 == 0:
                    self.cpu.gfx[x][y] = 0x1

        # Clear the screen, then test it
        self.cpu._00E0()

        for x in range(len(self.cpu.gfx)):
            for y in range(len(self.cpu.gfx[x])):
                self.assertEqual(0x0, self.cpu.gfx[x][y])

    def test_00EE(self):
        # Enter a subroutine, then immediately exit
        # Check the values of the sp and pc
        self.cpu._2NNN(0x2300)
        self.cpu._00EE()
        self.assertEqual(0, self.cpu.sp)
        self.assertEqual(0x202, self.cpu.pc)

    def test_1NNN(self):
        self.cpu._1NNN(0x1100)
        self.assertEqual(0x100, self.cpu.pc)

    def test_2NNN(self):
        self.cpu._2NNN(0x2100)
        self.assertEqual(1, self.cpu.sp)

        # pc is initially located at 0x200, which is now stored on the stack
        self.assertEqual(0x200, self.cpu.stack[self.cpu.sp - 1])
        self.assertEqual(0x000, self.cpu.stack[self.cpu.sp])
        self.assertEqual(0x100, self.cpu.pc)

    def test_3XNN(self):
        # Test failure of v[x] == NN
        self.cpu._3XNN(0x3010)
        self.assertEqual(0x202, self.cpu.pc)

        # Test success of v[x] == NN
        self.cpu._6XNN(0x6010)
        self.cpu._3XNN(0x3010)

        # A successful skip moves the pc by 2 bytes
        # Since there were two instructions, pc is moved an additional 4 bytes
        # 0x202 + (3 * 0x2) = 0x208
        self.assertEqual(0x208, self.cpu.pc)

    def test_4XNN(self):
        # Test failure of v[x] != NN
        self.cpu._4XNN(0x4000)
        self.assertEqual(0x202, self.cpu.pc)

        # Test success of v[x] != NN
        self.cpu._6XNN(0x6010)
        self.cpu._4XNN(0x4000)

        # A successful skip moves the pc by 2 bytes
        # Since there were two instructions, pc is moved an additional 4 bytes
        # 0x202 + (3 * 0x2) = 0x208
        self.assertEqual(0x208, self.cpu.pc)

    def test_5XY0(self):
        # Test success of v[x] == v[y]
        # A successful skip moves the pc by 2 bytes
        # 0x200 + (2 * 0x2) = 0x204
        self.cpu._5XY0(0x5010)
        self.assertEqual(0x204, self.cpu.pc)

        # Test failure of v[x] == v[y]
        # Two instructions moves the pc by 4 bytes, so 0x204 + (2 * 0x2) = 0x208
        self.cpu._6XNN(0x6010)
        self.cpu._5XY0(0x5010)
        self.assertEqual(0x208, self.cpu.pc)

    def test_6XNN(self):
        self.cpu._6XNN(0x6010)
        self.assertEqual(0x10, self.cpu.v[0])
        self.assertEqual(0x202, self.cpu.pc)

    def test_7XNN(self):
        # Test without overflow
        self.cpu._7XNN(0x70FF)
        self.assertEqual(0xFF, self.cpu.v[0])
        self.assertEqual(0x202, self.cpu.pc)

        # Test with overflow
        self.cpu._7XNN(0x7001)
        self.assertEqual(0x00, self.cpu.v[0])
        self.assertEqual(0x204, self.cpu.pc)

    def test_8XY0(self):
        self.cpu._6XNN(0x61FF)
        self.cpu._8XY0(0, 1)
        self.assertEqual(0xFF, self.cpu.v[0])
        self.assertEqual(0x204, self.cpu.pc)

    def test_8XY1(self):
        # v[0] = 0xF0
        # v[1] = 0X0F
        self.cpu._6XNN(0x60F0)
        self.cpu._6XNN(0x610F)

        # v[0] | v[1] = 0XFF
        self.cpu._8XY1(0, 1)
        self.assertEqual(0xFF, self.cpu.v[0])
        self.assertEqual(0x206, self.cpu.pc)

    def test_8XY2(self):
        # v[0] = 0xF1
        # v[1] = 0x0F
        self.cpu._6XNN(0x60F1)
        self.cpu._6XNN(0x610F)

        # v[0] & v[1] = 0x01
        self.cpu._8XY2(0, 1)
        self.assertEqual(0x01, self.cpu.v[0])
        self.assertEqual(0x206, self.cpu.pc)

    def test_8XY3(self):
        # v[0] = 0x10
        # v[1] = 0x20
        self.cpu._6XNN(0x6010)
        self.cpu._6XNN(0x6120)

        # v[0] ^ v[1] = 0x01
        self.cpu._8XY3(0, 1)
        self.assertEqual(0x30, self.cpu.v[0])
        self.assertEqual(0x206, self.cpu.pc)

    def test_8XY4(self):
        # Test without carry
        self.cpu._6XNN(0x60F0)
        self.cpu._6XNN(0x610F)
        self.cpu._8XY4(0, 1)

        self.assertEqual(0xFF, self.cpu.v[0])
        self.assertEqual(0x00, self.cpu.v[0xF])
        self.assertEqual(0x206, self.cpu.pc)

        # Test with carry
        self.cpu._6XNN(0x6110)
        self.cpu._8XY4(0, 1)

        self.assertEqual(0x0F, self.cpu.v[0])
        self.assertEqual(0x01, self.cpu.v[0xF])
        self.assertEqual(0x20A, self.cpu.pc)

    def test_8XY5(self):
        # Test without borrow
        self.cpu._6XNN(0x60F0)
        self.cpu._6XNN(0x61E0)
        self.cpu._8XY5(0, 1)

        self.assertEqual(0x10, self.cpu.v[0])
        self.assertEqual(0x01, self.cpu.v[0xF])
        self.assertEqual(0x206, self.cpu.pc)

        # Test with borrow
        self.cpu._6XNN(0x61F0)
        self.cpu._8XY5(0, 1)

        self.assertEqual(0x20, self.cpu.v[0])
        self.assertEqual(0x00, self.cpu.v[0xF])
        self.assertEqual(0x20A, self.cpu.pc)

    def test_8XY6(self):
        # v[1] = 0x01
        self.cpu._6XNN(0x6101)
        self.cpu._8XY6(0, 1)
        self.assertEqual(0x01, self.cpu.v[0xF])
        self.assertEqual(0x2, self.cpu.v[1])
        self.assertEqual(0x2, self.cpu.v[0])
        self.assertEqual(0x204, self.cpu.pc)

    def test_8XY7(self):
        # Test without borrow
        self.cpu._6XNN(0x60E0)
        self.cpu._6XNN(0x61F0)
        self.cpu._8XY7(0, 1)

        self.assertEqual(0x10, self.cpu.v[0])
        self.assertEqual(0x01, self.cpu.v[0xF])
        self.assertEqual(0x206, self.cpu.pc)

        # Test with borrow
        self.cpu._6XNN(0x60F5)
        self.cpu._8XY7(0, 1)

        self.assertEqual(0xFB, self.cpu.v[0])
        self.assertEqual(0x00, self.cpu.v[0xF])
        self.assertEqual(0x20A, self.cpu.pc)

    def test_8XYE(self):
        # v[1] = 0x80
        self.cpu._6XNN(0x6180)
        self.cpu._8XYE(0, 1)
        self.assertEqual(0x01, self.cpu.v[0xF])
        self.assertEqual(0x40, self.cpu.v[1])
        self.assertEqual(0x40, self.cpu.v[0])
        self.assertEqual(0x204, self.cpu.pc)

    def test_9XY0(self):
        # Test failure of v[x] != v[y]
        self.cpu._9XY0(0x9010)
        self.assertEqual(0x202, self.cpu.pc)

        # Test success of v[x] != v[y]
        self.cpu._6XNN(0x6010)
        self.cpu._9XY0(0x9010)

        # A successful skip moves the pc by 2 bytes
        # Since there were two instructions, pc is moved an additional 4 bytes
        # 0x202 + (3 * 0x2) = 0x208
        self.assertEqual(0x208, self.cpu.pc)

    def test_ANNN(self):
        self.cpu._ANNN(0xAFFF)
        self.assertEqual(0xFFF, self.cpu.i)
        self.assertEqual(0x202, self.cpu.pc)

    def test_BNNN(self):
        self.cpu._6XNN(0x600F)
        self.cpu._BNNN(0xBFF0)
        self.assertEqual(0xFFF, self.cpu.pc)

    def test_CXNN(self):
        self.cpu._CXNN(0xC015)
        self.assertTrue(self.cpu.v[0] >= 0 and self.cpu.v[0] <= 255)
        self.assertEqual(0x202, self.cpu.pc)


if __name__ == "__main__":
    unittest.main()