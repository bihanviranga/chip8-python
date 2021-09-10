import pyglet.window

rom_name = "test_opcode.ch8"
log_enabled = True
# 1 = print everything
# 2 = print few stuff
# 3 = print fewer stuff
log_level = 1


def log(message, message_type="info", level=1):
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


class cpu(pyglet.window.Window):
    def main(self):
        self.initialize()
        self.load_rom(rom_name)

        while not self.has_exit:
            self.dispatch_events()
            self.cycle()
            self.draw()

    def initialize(self):
        self.clear()
        self.memory = [0] * 4096            # 4096 Bytes of memory
        self.gpio = [0] * 16                # registers
        self.display_buffer = [0] * 64 * 32  # 64x32 screen
        self.stack = []
        self.key_inputs = [0] * 16          # Input keys state
        self.opcode = 0
        self.index = 0

        self.delay_timer = 0
        self.sound_timer = 0
        self.should_draw = False

        self.pc = 0x200  # Program counter

        # Mapping opcodes to functions
        self.func_map = {
            0x0: self.ins_0XXX,
            # 0x1: self.ins_1XXX,
            # 0x2: self.ins_2XXX,
            # 0x3: self.ins_3XXX,
            # 0x4: self.ins_4XXX,
            # 0x5: self.ins_5XXX,
            # 0x6: self.ins_6XXX,
            # 0x7: self.ins_7XXX,
            # 0x8: self.ins_8XXX,
            # 0x9: self.ins_9XXX,
            # 0xa: self.ins_AXXX,
            # 0xb: self.ins_BXXX,
            # 0xc: self.ins_CXXX,
            # 0xd: self.ins_DXXX,
            # 0xe: self.ins_EXXX,
            # 0xf: self.ins_FXXX
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
            self.func_map[0]()
        except:
            log("Unknown instruction: %x" % self.opcode, "error")

        # decrement timers
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1
            if self.sound_timer != 0:
                # play sound here, while sound timer is on
                pass

    # TODO implement this stub
    def draw(self):
        pass

    def ins_0XXX(self):
        log("Instruction recieved: %s" % self.opcode, "info", 1)
