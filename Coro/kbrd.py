""" 


"""
import time
import RPi.GPIO as GPIO
import threading


class kbrd:
    X_KEY = 0
    CIRCLE_KEY = 1
    TRIANGLE_KEY = 2
    SQUARE_KEY = 3
    R_KEY = 4
    L_KEY = 5
    NO_KEY = 99

    def __init__(self):
        # Key pins

        GPIO.setmode(GPIO.BCM)
        # Up, Down, left, right, fire
        self.pin_map = [5, 23, 24, 22, 4, 17]
        GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Trigon Button for GPIO24
        GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # X Button for GPIO5
        GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Circle Button for GPIO23
        GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Square Button for GPIO22
        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # R Button for GPIO4
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP) # L Button for GPIO17

        self.key_pressed = kbrd.NO_KEY
        self.long_press = False
        self.run = True

        x = threading.Thread(target=self.__thread_process, args=())
        x.daemon = True
        x.start()

    def __thread_process(self):
        """ Read the keyboard """
        state = "IDLE"
        last_key = kbrd.NO_KEY
        inicio_de_tiempo = time.time()
        while self.run:
            key = self.get_pressed()
            if state == "IDLE":
                if key != kbrd.NO_KEY:
                    last_key = key
                    inicio_de_tiempo = time.time()
                    # time.sleep(0.1)
                    state = "PRESSED"
            elif state == "PRESSED":
                if key == kbrd.NO_KEY:
                    # time.sleep(0.1)
                    state = "RELEASE"
                elif time.time() - inicio_de_tiempo > 1:
                    self.key_pressed = last_key
                    self.long_press = True
                    state = "WAIT"
            elif state == "RELEASE":
                tiempo_final = time.time()
                tiempo_transcurrido = tiempo_final - inicio_de_tiempo
                if tiempo_transcurrido < 0.5:
                    long_press = False
                else:
                    long_press = True
                self.key_pressed = last_key
                self.long_press = long_press
                state = "IDLE"
            elif state == "WAIT":
                if key == kbrd.NO_KEY:
                    state = "IDLE"
            time.sleep(0.1)

    def get_pressed(self):
        for key in range(6):
            if not GPIO.input(self.pin_map[key]):
                return key
        return kbrd.NO_KEY

    def get_key(self):
        ret = (self.key_pressed, self.long_press)
        if ret[0] != kbrd.NO_KEY:
            self.key_pressed = kbrd.NO_KEY
        return ret

    def stop(self):
        self.run = False



