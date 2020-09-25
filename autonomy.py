import logging
import asyncio
import random
import time

from core.roverevent import RoverEvent


logger = logging.getLogger(__name__)
loop = asyncio.get_event_loop()

@RoverEvent.Thread(loop=loop)
def camera_sensor(signal):
    while True:
        if random.randint(0, 1000) < 5:
            signal("ar-tag", "AR TAG SPOTTED")
        elif 5 < random.randint(0, 1000) < 10:
            signal("ball-spotted", "BALL SPOTTED")
        time.sleep(0.016)


def handle_ar_tag(argument):
    logger.info(argument)


def handle_ball_spotted(argument):
    logger.info(argument)


def main():
    camera_sensor.add_event_handler("ar-tag", handle_ar_tag)
    camera_sensor.add_event_handler("ball-spotted", handle_ball_spotted)
    camera_sensor.start()
    loop.run_forever()


if __name__ == "__main__":
    rootlog = logging.getLogger()
    rootlog.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    rootlog.addHandler(handler)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s : %(message)s"
    ))
    main()
