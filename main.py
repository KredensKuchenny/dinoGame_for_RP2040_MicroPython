import time
from machine import Pin, I2C
from games.dino.dino import Dino
from games.dino.cacti import Cacti
from games.dino.cloud import Cloud
from games.dino.checker import Checker
import display.ssd1306 as ssd1306

is_interrupt = False
start_game = False
game_over = False
first_jump = True
oled_width = 128
oled_height = 64

# stala odleglosc miedzy kaktusami (w pikselach)
GAP = 80

# debounce przycisku - ignoruj zbocza w odstepie < DEBOUNCE_MS (drganie stykow)
DEBOUNCE_MS = 200
last_irq = 0


def handle_interrupt(pin):
    global is_interrupt
    global start_game
    global game_over
    global last_irq

    now = time.ticks_ms()
    if time.ticks_diff(now, last_irq) < DEBOUNCE_MS:
        return
    last_irq = now

    if game_over:
        # restart po przegranej -> przejscie do gry, BEZ skoku
        game_over = False
        start_game = True
    elif start_game:
        # nacisniecie w trakcie gry -> skok
        is_interrupt = True
    else:
        # ekran startowy -> rozpocznij gre, BEZ skoku
        start_game = True


button = Pin(2, mode=Pin.IN, pull=Pin.PULL_UP)
button.irq(trigger=Pin.IRQ_FALLING, handler=handle_interrupt)

i2c = I2C(1, sda=Pin(6), scl=Pin(7))
display = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

dino_obj = Dino(26, 26, 7, 38, 128)
cloud_obj = Cloud(32, 9, 48, 11, 128, 10)
# drugi kaktus startuje przesuniety o GAP, by od poczatku zachowac staly odstep
cacti_obj_1 = Cacti(10, 24, 10, 18, 128, 39, 45)
cacti_obj_2 = Cacti(10, 24, 10, 18, 128, 39, 45, start_x=128 + GAP)
cacti_list = [cacti_obj_1, cacti_obj_2]
checker_obj = Checker()


while True:
    display.fill(0)

    if game_over:
        display.fill(0)
        display.hline(0, 59, 127, 1)
        display.text("GAME OVER", 30, 20, 1)
        dino_obj.game_over(display)
        is_interrupt = False
        start_game = False
        first_jump = True
        score = 0
        dino_obj.reset()
        cacti_obj_1.reset()
        cacti_obj_2.reset()
    elif not start_game:
        display.hline(0, 59, 127, 1)
        display.text("DINO RUN", 32, 20, 1)
        dino_obj.game_logo(display)
        is_interrupt = False
    else:
        # zabezpieczenie: skasuj ewentualny skok wywolany w trakcie startu
        if first_jump:
            is_interrupt = False
            first_jump = False

        display.hline(0, 59, 127, 1)

        # rysuj i przesun oba kaktusy (rownomiernie, po 1 px)
        for cacti_obj in cacti_list:
            cacti_obj.update(display)

        # gdy kaktus zejdzie z ekranu, odradza sie GAP px za najdalszym kaktusem
        # -> dzieki temu odstep miedzy nimi jest zawsze taki sam
        for cacti_obj in cacti_list:
            if cacti_obj.current_x < -cacti_obj.width:
                furthest = max(c.current_x for c in cacti_list)
                cacti_obj.respawn(furthest + GAP)

        cloud_obj.update(display)
        dino_obj.update(display, 0)

        if is_interrupt:
            dino_obj.update(display, 1)
            is_interrupt = False

        for cacti_obj in cacti_list:
            cacti_obj.counter()

        score = cacti_obj_1.score + cacti_obj_2.score

        for cacti_obj in cacti_list:
            if cacti_obj.current_x < oled_width / 1.5:
                if cacti_obj.size == 0:
                    game_over = checker_obj.check(
                        display,
                        dino_obj.width,
                        dino_obj.height,
                        dino_obj.current_x,
                        dino_obj.current_y,
                        cacti_obj.width_big,
                        cacti_obj.height_big,
                        cacti_obj.current_x,
                        cacti_obj.current_y_big,
                    )
                elif cacti_obj.size == 1:
                    game_over = checker_obj.check(
                        display,
                        dino_obj.width,
                        dino_obj.height,
                        dino_obj.current_x,
                        dino_obj.current_y,
                        cacti_obj.width_small,
                        cacti_obj.height_small,
                        cacti_obj.current_x,
                        cacti_obj.current_y_small,
                    )
                # nie nadpisuj wykrytej kolizji sprawdzeniem drugiego kaktusa
                if game_over:
                    break

        if game_over:
            start_game = False

        info = len(str(score))
        move = 106 - (8 * info)
        display.text("S:" + str(score), move, 5, 1)

    display.show()
