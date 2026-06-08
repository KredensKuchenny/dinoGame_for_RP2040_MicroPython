import framebuf
import random


class Cacti:
    def __init__(
        self,
        width_big,
        height_big,
        width_small,
        height_small,
        x,
        y_big,
        y_small,
        start_x=None,
    ):
        self.width_big = width_big
        self.height_big = height_big
        self.width_small = width_small
        self.height_small = height_small
        self.x = x
        self.start_x = x if start_x is None else start_x
        self.current_x = self.start_x
        self.y_big = y_big
        self.y_small = y_small
        self.current_y_big = self.y_big
        self.current_y_small = self.y_small
        self.size = random.randint(0, 1)
        self.score = 0
        self.scored = False
        self.cacti_image_big = bytearray(
            b"\x0c\x00\x1e\x00\x1e\x00\x1e\x00\xde\x00\xde\x00\xde\x00\xde\xc0\xde\xc0\xfe\xc0\xfe\xc0\x7e\xc0\x1e\xc0\x1f\xc0\x1f\x80\x1e\x00\x1e\x00\x1e\x00\x1e\x00\x1e\x00\x1e\x00\x1e\x00\x1e\x00\x1e\x00"
        )
        self.cacti_image_small = bytearray(
            b"\x0e\x00\x1e\x00\x1e\x00\xde\x00\xde\x00\xde\xc0\xde\xc0\xfe\xc0\x7e\xc0\x1e\xc0\x1f\x80\x1e\x00\x1e\x00\x1e\x00\x1e\x00\x1e\x00\x1e\x00\x1e\x00"
        )

    @property
    def width(self):
        return self.width_big if self.size == 0 else self.width_small

    @property
    def current_y(self):
        return self.current_y_big if self.size == 0 else self.current_y_small

    def update(self, display):
        if self.size == 0:
            image_render = framebuf.FrameBuffer(
                self.cacti_image_big,
                self.width_big,
                self.height_big,
                framebuf.MONO_HLSB,
            )
            display.blit(image_render, self.current_x, self.current_y_big)
        else:
            image_render = framebuf.FrameBuffer(
                self.cacti_image_small,
                self.width_small,
                self.height_small,
                framebuf.MONO_HLSB,
            )
            display.blit(image_render, self.current_x, self.current_y_small)

        self.current_x -= 1

    def respawn(self, new_x):
        self.current_x = new_x
        self.size = random.randint(0, 1)
        self.scored = False

    def counter(self):
        if self.current_x < 0 and not self.scored:
            self.score += 1
            self.scored = True

    def reset(self):
        self.score = 0
        self.current_x = self.start_x
        self.size = random.randint(0, 1)
        self.scored = False
