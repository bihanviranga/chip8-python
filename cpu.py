import sys
import pyglet.window

rom_name = sys.argv[1]
log_enabled = True


def log(message, level="info"):
    if not log_enabled:
        return

    log_level_symbols = {
        "info": "[*]",
        "warning": "[!]",
        "error": "[x]",
        "success": "[+]",
    }

    print(log_level_symbols[level], message)


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

        i = 0
        while i < 80:
            # load 80-char font set
            self.memory[i] = self.fonts[i]
            i += 1

    def load_rom(self, rom_path):
        log("Loading ROM %s" % rom_path)
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

        extracted_op = self.opcode & 0xf000 # >> 12 (should shift?)
        n = self.opcode & 0x000f

        try:
            # Call the necessary method
            self.funcmap[extracted_op]()
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
