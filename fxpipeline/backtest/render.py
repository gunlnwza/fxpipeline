from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

if TYPE_CHECKING:
    from .data import Data


class Renderer:
    def __init__(self):
        pass

    def render(self, data: Data):
        truncated = False
        return truncated

    def close(self):
        pass


class PygameRenderer(Renderer):
    def __init__(self):
        pg.display.init()
        self.screen = pg.display.set_mode((500, 500))
        self.clock = pg.time.Clock()
        self.fps = 5

    def handle_events(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.close()
                return True
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_q:
                    self.close()
                    return True
                elif e.key == pg.K_a:
                    if self.fps - 4 > 0:
                        self.fps -= 4
                elif e.key == pg.K_d:
                    if self.fps + 4 <= 20:
                        self.fps += 4
        return False

    def render(self, data):
        truncated = self.handle_events()
        if truncated:
            return truncated

        info = data.get_info()
        closes = info["closes"]
        order = info.get("order")

        w = self.screen.get_width()
        h = self.screen.get_height()

        def to_screen_x(index):
            return 10 + (w // (len(closes) + 1)) * index

        def to_screen_y(price):
            return h - ((price - min_price * 0.99) / (max_price * 1.01 - min_price * 0.99)) * h

        self.screen.fill("black")
        max_price = max(closes)
        min_price = min(closes)
        for i in range(len(closes) - 1):
            start = (to_screen_x(i), to_screen_y(closes[i]))
            end = (to_screen_x(i + 1), to_screen_y(closes[i + 1]))
            pg.draw.line(self.screen, "white", start, end, 1)

        if order:
            start = (0, to_screen_y(order["open_price"]))
            end = (w, to_screen_y(order["open_price"]))
            color = "green" if order["type"] == "buy" else "red"
            pg.draw.line(self.screen, color, start, end)

        pg.display.flip()
        self.clock.tick(self.fps)

    def close(self):
        pg.quit()


class TerminalRenderer(Renderer):
    def __init__(self):
        pass

    def render(self, data):
        info = data.get_info()
        # order = info.get("order")
        print(f"i={info['i']}, total_profit={info['total_profit']:.4f}")
