rom_name = "test_opcode.ch8"
log_enabled = True
# 1 = print everything
# 2 = print few stuff
# 3 = print fewer stuff
log_level = 1


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

    def initialize(self):
        self.memory = [0] * 4096            # 4096 Bytes of memory
        self.gpio = [0] * 16                # registers
        self.display_buffer = [0] * 64 * 32  # 64x32 screen
        self.stack = []
        self.key_inputs = [0] * 16          # Input keys state
        self.opcode = 0
        self.index = 0

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

        # TODO implement this
        self.fonts = [i for i in range(80)]

        i = 0
        while i < 80:
            # load 80-char font set
            self.memory[i] = self.fonts[i]
            i += 1

    def load_rom(self, rom_path):
        log("Loading ROM %s" % rom_path, "info", 2)
        binary = open(rom_path, "rb").read()
        i = 0
        while i < len(binary):
            # Previously ord(binary[i])
            # But since open() with "rb" mode gives bytes
            # we won't cast it to an int
            self.memory[i+0x200] = binary[i]
            i += 1

    def cycle(self):
        self.opcode = self.memory[self.pc]

        self.vx = (self.opcode & 0x0f00) >> 8
        self.vy = (self.opcode & 0x00f0) >> 4
        # an opcode is 2 bytes long
        self.pc += 2

        extracted_op = self.opcode & 0xf000 >> 12  # shouldn't shift?

        try:
            # Call the necessary method
            # self.func_map[extracted_op]()
            # For testing, call the same op
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
    def draw(self):
        pass

    def ins_0XXX(self):
        if (self.vx == 0x0 and self.vy == 0xe):
            nibble = self.opcode & 0x000f
            if (nibble == 0x0):
                self.ins_00E0()
            elif (nibble == 0xe):
                self.ins_00EE()
            else:
                log("[00EX] Ignoring unknown instruction: %s" % self.opcode, "info", 2)
        else:
            log("[0XXX] Ignoring unknown instruction: %s" % self.opcode, "info", 2)

    def ins_1XXX(self):
        self.ins_1nnn()

    def ins_2XXX(self):
        self.ins_2nnn()

    def ins_3XXX(self):
        self.ins_3xkk()

    def ins_4XXX(self):
        self.ins_4xkk()

    def ins_5XXX(self):
        log("Instruction Not implemented: 5XXX: %s" % self.opcode, "error")
        nibble = self.opcode & 0x000f
        if (nibble == 0x0):
            self.ins_5xy0()
        else:
            log("Ignoring unknown instruction: %s" % self.opcode, "info", 2)

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
            log("[8XXX] Ignoring unknown instruction: %s" % self.opcode, "info", 2)


    def ins_9XXX(self):
        log("Instruction Not implemented: 9XXX: %s" % self.opcode, "error")

    def ins_AXXX(self):
        log("Instruction Not implemented: AXXX: %s" % self.opcode, "error")

    def ins_BXXX(self):
        log("Instruction Not implemented: BXXX: %s" % self.opcode, "error")

    def ins_CXXX(self):
        log("Instruction Not implemented: CXXX: %s" % self.opcode, "error")

    def ins_DXXX(self):
        log("Instruction Not implemented: DXXX: %s" % self.opcode, "error")

    def ins_EXXX(self):
        log("Instruction Not implemented: EXXX: %s" % self.opcode, "error")

    def ins_FXXX(self):
        log("Instruction Not implemented: FXXX: %s" % self.opcode, "error")

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
        log("[INS] 1nnn", "info", 1)
        addr = self.opcode & 0x0fff
        self.pc = 0x200 + addr # 0x200 part because it has to be in ROM?

    # CALL addr
    # Call subroutine at nnn
    def ins_2nnn(self):
        log("[INS] 2nnn", "info", 1)
        addr = self.opcode & 0x0fff
        self.stack.append(self.pc)
        self.pc = 0x200 + addr # 0x200 part because it has to be in ROM?

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
