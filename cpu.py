import random
import binascii
import pygame

rom_name = "test_opcode.ch8"
log_enabled = True
# 1 = print everything
# 2 = print few stuff
# 3 = print fewer stuff
log_level = 1

screen_width = 64
screen_height = 32
screen_scale_factor = 8

def log(message, message_type="info", level=3):
    if not log_enabled:
        return

    log_message_type_symbols = {
        "info": "[*]",
        "warning": "[!]",
        "error": "[x]",
        "success": "[+]",
    }

    # Errors and warnings are logged anyways
    if(message_type == "error" or message_type == "warning"):
        print(log_message_type_symbols[message_type], message)
    else:
        if (level >= log_level):
            print(log_message_type_symbols[message_type], message)


class cpu():
    def main(self):
        self.initialize()
        self.load_rom(rom_name)

        while self.running:
            # TODO: self.handle_events()
            self.cycle()
            self.draw()
            # TODO: temp. artificial break
            if (self.ops_run > 10000):
                break

    def initialize(self):
        self.memory = [0] * 4096            # 4096 Bytes of memory
        self.gpio = [0] * 16                # registers
        self.display_buffer = [0] * screen_width * screen_height
        self.stack = []
        self.key_inputs = [0] * 16          # Input keys state - 1 = down position/pressed
        self.opcode = 0
        self.index = 0
        self.ops_run = 0 # Temporary - number of ops

        self.running = True # power switch

        self.delay_timer = 0
        self.sound_timer = 0
        self.should_draw = False

        self.pc = 0x200  # Program counter

        # Mapping opcodes to functions
        self.func_map = {
            0x0: self.ins_0XXX,
            0x1: self.ins_1XXX,
            0x2: self.ins_2XXX,
            0x3: self.ins_3XXX,
            0x4: self.ins_4XXX,
            0x5: self.ins_5XXX,
            0x6: self.ins_6XXX,
            0x7: self.ins_7XXX,
            0x8: self.ins_8XXX,
            0x9: self.ins_9XXX,
            0xa: self.ins_AXXX,
            0xb: self.ins_BXXX,
            0xc: self.ins_CXXX,
            0xd: self.ins_DXXX,
            0xe: self.ins_EXXX,
            0xf: self.ins_FXXX
        }

        self.fonts = [
            0xF0,0x90,0x90,0x90,0xF0,
            0x20,0x60,0x20,0x20,0x70,
            0xF0,0x10,0xF0,0x80,0xF0,
            0xF0,0x10,0xF0,0x10,0xF0,
            0x90,0x90,0xF0,0x10,0x10,
            0xF0,0x80,0xF0,0x10,0xF0,
            0xF0,0x80,0xF0,0x90,0xF0,
            0xF0,0x10,0x20,0x40,0x40,
            0xF0,0x90,0xF0,0x90,0xF0,
            0xF0,0x90,0xF0,0x10,0xF0,
            0xF0,0x90,0xF0,0x90,0x90,
            0xE0,0x90,0xE0,0x90,0xE0,
            0xF0,0x80,0x80,0x80,0xF0,
            0xE0,0x90,0x90,0x90,0xE0,
            0xF0,0x80,0xF0,0x80,0xF0,
            0xF0,0x80,0xF0,0x80,0x80
        ]

        i = 0
        while i < 80:
            # load 80-char font set
            self.memory[i] = self.fonts[i]
            i += 1

        # initialize display
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width * screen_scale_factor, screen_height * screen_scale_factor))

    def load_rom(self, rom_path):
        log("Loading ROM %s" % rom_path, "info", 2)

        piece_size = 1 # How many bytes to read at once
        with open(rom_path, "rb") as rom_file:
            for i in range(len(self.memory)):
                piece = rom_file.read(piece_size)
                if piece == b'':
                    break

                hex_piece = binascii.hexlify(piece)
                as_int = int(hex_piece, 16)
                self.memory[0x200 + i] = as_int

    def cycle(self):
        op_bytes = self.memory[self.pc: self.pc+2]
        self.opcode = op_bytes[0] * 0x100 + op_bytes[1]
        # log("[OPCODE] %04x" % self.opcode, "info", 1)

        self.vx = (self.opcode & 0x0f00) >> 8
        self.vy = (self.opcode & 0x00f0) >> 4
        # an opcode is 2 bytes long
        self.pc += 2

        extracted_op = (self.opcode & 0xf000 )>> 12  # shouldn't shift?
        self.ops_run += 1 # Temporary

        try:
            # Call the necessary method
            # self.func_map[extracted_op]()
            self.func_map[extracted_op]()
        except:
            log("Unknown instruction: %x" % self.opcode, "error")

        # decrement timers
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1
            if self.sound_timer != 0:
                # TODO play sound here, while sound timer is on
                pass

    # TODO implement this stub
    # Actually draws the pixels
    def draw(self):
        if self.should_draw:
            log("[DRAW] Drawing...", "info", 1)
            for i in range(len(self.display_buffer)):
                pixel = self.display_buffer[i]
                if pixel == 1:
                    print("index", i)
                    row = i // screen_width
                    col = i - (row * screen_width)
                    print("row", row, "col", col)
                    xpos = col * screen_scale_factor
                    ypos = row * screen_scale_factor
                    print("xpos", xpos, "ypos", ypos)
                    side = screen_scale_factor
                    pygame.draw.rect(self.screen, (255, 0, 255), pygame.Rect(xpos, ypos, side, side))
            pygame.display.flip()

        # Once finished, reset the variable
        self.should_draw = False

    # TODO stub
    # Marks which pixels to draw or erase
    # returns whether collision was true or not
    def mark_pixels(self, sprite):
        log("[DRAW] Marking...", "info", 1)
        row = self.vy
        col = self.vx
        index = row * screen_width + col
        bits = "".join([bin(i)[2:] for i in sprite])
        bit_length = len(bits)
        collision = False
        for i in range(bit_length):
            current = self.display_buffer[index + i]
            if current != bits[i]:
                collision = True
            self.display_buffer[index+i] = 1 if bits[i] == '1' else 0
        return collision

    # TODO stub
    # Halt all execution and wait until a key is pressed
    def wait_for_key(self):
        log("[INPUT] Waiting for key", "info", 1)
        return 0x1

    def ins_0XXX(self):
        if (self.vx == 0x0 and self.vy == 0xe):
            nibble = self.opcode & 0x000f
            if (nibble == 0x0):
                self.ins_00E0()
            elif (nibble == 0xe):
                self.ins_00EE()
            else:
                log("[00EX] Ignoring unknown instruction: %04x" % self.opcode, "info", 2)
        else:
            log("[0XXX] Ignoring unknown instruction: %04x" % self.opcode, "info", 2)

    def ins_1XXX(self):
        self.ins_1nnn()

    def ins_2XXX(self):
        self.ins_2nnn()

    def ins_3XXX(self):
        self.ins_3xkk()

    def ins_4XXX(self):
        self.ins_4xkk()

    def ins_5XXX(self):
        nibble = self.opcode & 0x000f
        if (nibble == 0x0):
            self.ins_5xy0()
        else:
            log("[5XXX] Ignoring unknown instruction: %04x" % self.opcode, "info", 2)

    def ins_6XXX(self):
        self.ins_6xkk()

    def ins_7XXX(self):
        self.ins_7xkk()

    def ins_8XXX(self):
        nibble = self.opcode & 0x000f
        if (nibble == 0x0):
            self.ins_8xy0()
        elif (nibble == 0x1):
            self.ins_8xy1()
        elif (nibble == 0x2):
            self.ins_8xy2()
        elif (nibble == 0x3):
            self.ins_8xy3()
        elif (nibble == 0x4):
            self.ins_8xy4()
        elif (nibble == 0x5):
            self.ins_8xy5()
        elif (nibble == 0x6):
            self.ins_8xy6()
        elif (nibble == 0x7):
            self.ins_8xy7()
        elif (nibble == 0xE):
            self.ins_8xyE()
        else:
            log("[8XXX] Ignoring unknown instruction: %04x" % self.opcode, "info", 2)


    def ins_9XXX(self):
        self.ins_9xy0()

    def ins_AXXX(self):
        self.ins_Annn()

    def ins_BXXX(self):
        self.ins_Bnnn()

    def ins_CXXX(self):
        self.ins_Cxkk()

    def ins_DXXX(self):
        self.ins_Dxyn()

    def ins_EXXX(self):
        low_byte = self.opcode & 0x00ff
        if (low_byte == 0x9E):
            self.ins_Ex9E()
        elif (low_byte == 0xA1):
            self.ins_ExA1()
        else:
            log("[EXXX] Ignoring unknown instruction: %04x" % self.opcode, "info", 2)


    def ins_FXXX(self):
        low_byte = self.opcode & 0x00ff
        if (low_byte == 0x07):
            self.ins_Fx07()
        elif (low_byte == 0x0A):
            self.ins_Fx0A()
        elif (low_byte == 0x15):
            self.ins_Fx15()
        elif (low_byte == 0x18):
            self.ins_Fx18()
        elif (low_byte == 0x1E):
            self.ins_Fx1E()
        elif (low_byte == 0x29):
            self.ins_Fx29()
        elif (low_byte == 0x33):
            self.ins_Fx33()
        elif (low_byte == 0x55):
            self.ins_Fx55()
        elif (low_byte == 0x65):
            self.ins_Fx65()
        else:
            log("[FXXX] Ignoring unknown instruction: %04x" % self.opcode, "info", 2)

    # CLS
    # Clear the display
    def ins_00E0(self):
        log("[INS] 00E0", "info", 1)
        self.display_buffer = [0] * 64 * 32
        self.should_draw = True

    # RET
    # Return from a subroutine
    def ins_00EE(self):
        log("[INS] 00EE", "info", 1)
        self.pc = self.stack.pop()

    # JP addr
    # Jump to location nnn
    def ins_1nnn(self):
        addr = self.opcode & 0x0fff
        log("[INS] 1nnn JP %x" % addr, "info", 1)
        self.pc = addr

    # CALL addr
    # Call subroutine at nnn
    def ins_2nnn(self):
        log("[INS] 2nnn", "info", 1)
        addr = self.opcode & 0x0fff
        self.stack.append(self.pc)
        self.pc = addr

    # SE Vx, byte
    # Skip next instruction if Vx = kk
    def ins_3xkk(self):
        log("[INS] 3xkk", "info", 1)
        kk = self.opcode & 0x00ff
        if (kk == self.gpio[self.vx]):
            self.pc += 2

    # SNE Vx, byte
    # Skip next instruction if Vx != kk
    def ins_4xkk(self):
        log("[INS] 4xkk", "info", 1)
        kk = self.opcode & 0x00ff
        if (kk != self.gpio[self.vx]):
            self.pc += 2

    # SE Vx, Vy
    # Skip next instruction if Vx = Vy
    def ins_5xy0(self):
        log("[INS] 5xy0", "info", 1)
        if (self.gpio[self.vx] == self.gpio[self.vy]):
            self.pc += 2

    # LD Vx, byte
    # Set Vx = kk
    def ins_6xkk(self):
        log("[INS] 6xkk", "info", 1)
        kk = self.opcode & 0x00ff
        self.gpio[self.vx] = kk

    # ADD Vx, byte
    # Set Vx = Vx + kk
    def ins_7xkk(self):
        log("[INS] 7xkk", "info", 1)
        kk = self.opcode & 0x00ff
        self.gpio[self.vx] += kk

    # LD Vx, Vy
    # Set Vx = Vy
    def ins_8xy0(self):
        log("[INS] 8xy0", "info", 1)
        self.gpio[self.vx] = self.gpio[self.vy]

    # OR Vx, Vy
    # Set Vx = Vx OR Vy
    def ins_8xy1(self):
        log("[INS] 8xy1", "info", 1)
        self.gpio[self.vx] = self.gpio[self.vx] | self.gpio[self.vy]

    # AND Vx, Vy
    # Set Vx = Vx AND Vy
    def ins_8xy2(self):
        log("[INS] 8xy2", "info", 1)
        self.gpio[self.vx] = self.gpio[self.vx] & self.gpio[self.vy]

    # XOR Vx, Vy
    # Set Vx = Vx XOR Vy
    def ins_8xy3(self):
        log("[INS] 8xy3", "info", 1)
        self.gpio[self.vx] = self.gpio[self.vx] ^ self.gpio[self.vy]

    # ADD Vx, Vy
    # Set Vx = Vx + Vy, set VF = carry
    def ins_8xy4(self):
        log("[INS] 8xy4", "info", 1)
        result = self.gpio[self.vx] + self.gpio[self.vy]
        self.gpio[self.vx] = result & 0xff
        # Setting the carry flag
        if (result > 0xff):
            self.gpio[0xf] = 0x1
        else:
            self.gpio[0xf] = 0x0

    # SUB Vx, Vy
    # Set Vx = Vx - Vy, set VF = NOT borrow
    def ins_8xy5(self):
        log("[INS] 8xy5", "info", 1)
        if self.gpio[self.vx] > self.gpio[self.vy]:
            self.gpio[0xf] = 0x1
        else:
            self.gpio[0xf] = 0x0
        self.gpio[self.vx] = self.gpio[self.vx] - self.gpio[self.vy]
        self.gpio[self.vx] &= 0xff # Wrap values above 0xff to 8 bits

    # SHR Vx {, VY}
    # Set Vx = Vx SHR 1
    def ins_8xy6(self):
        log("[INS] 8xy6", "info", 1)
        lsb = self.gpio[self.vx] & 0x0001
        if (lsb == 0x1):
            self.gpio[0xf] = 0x1
        else:
            self.gpio[0xf] = 0x0

        # NOTE: This line might have to be changed.
        # Because SHR means shift right, not divide
        self.gpio[self.vx] //= 2

    # SUBN Vx, Vy
    # Set Vx = Vy - Vx, set VF = NOT borrow
    def ins_8xy7(self):
        log("[INS] 8xy7", "info", 1)
        if (self.gpio[self.vy] > self.gpio[self.vx]):
            self.gpio[0xf] = 0x1
        else:
            self.gpio[0xf] = 0x0
        result = self.gpio[self.vy] - self.gpio[self.vx]
        self.gpio[self.vx] = result & 0xff

    # SHL Vx {, Vy}
    # Set Vx = Vx SHL 1
    def ins_8xyE(self):
        log("[INS] 8xyE", "info", 1)
        msb = self.gpio[self.vx] & 0x8000
        if (msb == 0x1):
            self.gpio[0xf] = 0x1
        else:
            self.gpio[0xf] = 0x0

        # NOTE: This line might have to be changed.
        # Because SHL means shift left, not multiply
        result = self.gpio[self.vx] * 2
        self.gpio[self.vx] =  result & 0xff

    # SNE Vx, Vy
    # Skip next instruction if Vx != Vy
    def ins_9xy0(self):
        log("[INS] 9xy0", "info", 1)
        if self.gpio[self.vx] != self.gpio[self.vy]:
            self.pc += 2

    # LD I, addr
    # Set I = nnn
    def ins_Annn(self):
        log("[INS] Annn", "info", 1)
        addr = self.opcode & 0x0fff
        self.index = addr

    # JP V0, addr
    # Jump to location nnn + V0
    def ins_Bnnn(self):
        log("[INS] Bnnn", "info", 1)
        addr = self.opcode & 0x0fff
        self.pc = 0x200 + addr + self.gpio[0x0] # Note: remove 0x200 offset?

    # RND Vx, byte
    # Set Vx = random byte AND kk
    def ins_Cxkk(self):
        log("[INS] Cxkk", "info", 1)
        random_byte = random.randint(0x0, 0xff)
        kk = self.opcode & 0x00ff
        self.gpio[self.vx] = random_byte & kk

    # DRW Vx, Vy, nibble
    # Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision
    def ins_Dxyn(self):
        log("[INS] Dxyn", "info", 1)

        self.should_draw = True
        size = self.opcode & 0x000f
        start = self.index
        sprite = self.memory[start:start+size]
        collision = self.mark_pixels(sprite)

        if (collision):
            self.gpio[0xf] = 0x1
        else:
            self.gpio[0xf] = 0x0

    # SKP Vx
    # Skip next instruction if key with the value of Vx is pressed
    def ins_Ex9E(self):
        log("[INS] Ex9E", "info", 1)
        if(self.key_inputs[self.vx] == 1):
            self.pc += 2

    # SKNP Vx
    # Skip next instruction if key with the value of Vx is not pressed
    def ins_ExA1(self):
        log("[INS] ExA1", "info", 1)
        if (self.key_inputs[self.vx] == 0):
            self.pc +=2

    # LD Vx, DT
    # Set Vx = delay timer value
    def ins_Fx07(self):
        log("[INS] Fx07", "info", 1)
        self.gpio[self.vx] = self.delay_timer

    # LD Vx, K
    # Wait for a key press, store the value of the key in Vx
    def ins_Fx0A(self):
        log("[INS] Fx0A", "info", 1)
        key = self.wait_for_key()
        self.gpio[self.vx] = key

    # LD DT, Vx
    # Set delay timer = Vx
    def ins_Fx15(self):
        log("[INS] Fx15", "info", 1)
        self.delay_timer = self.gpio[self.vx]

    # LD ST, Vx
    # Set sound timer = Vx
    def ins_Fx18(self):
        log("[INS] Fx18", "info", 1)
        self.sound_timer = self.gpio[self.vx]

    # ADD I, Vx
    # Set I = I + Vx
    def ins_Fx1E(self):
        log("[INS] Fx1E", "info", 1)
        self.index =+ self.vx

    # LD F, Vx
    # Set I = location of sprite for digit Vx
    def ins_Fx29(self):
        log("[INS] Fx29", "info", 1)
        font_index = self.vx * 5
        self.index = font_index

    # LD B, Vx
    # Store BCD representation of Vx in memory locations I, I+1, and I+2
    def ins_Fx33(self):
        log("[INS] Fx33", "info", 1)
        ones = self.vx % 10
        tens = self.vx % 100 // 10
        hundreds = self.vx // 100
        self.memory[self.index + 2] = ones
        self.memory[self.index + 1] = tens
        self.memory[self.index] = hundreds

    # LD [I], Vx
    # Store registers V0 through Vx in memory starting at location I
    def ins_Fx55(self):
        log("[INS] Fx55", "info", 1)
        limit = self.vx
        for i in range(limit):
            self.memory[self.index + i] = self.gpio[i]

    # LD Vx, [I]
    # Read registers V0 through Vx from memory starting at location I.
    def ins_Fx65(self):
        log("[INS] Fx65", "info", 1)
        limit = self.vx
        for i in range(limit):
            self.gpio[i] = self.memory[self.index + 1]
