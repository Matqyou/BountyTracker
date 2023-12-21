from pypresence import Presence
from datetime import datetime
from time import sleep, time
from WindowsRender import *
from FunMessage import *
import pytesseract
import pyautogui
import traceback
import threading
import random
import os
import re

LOGS_DIRECTORY = 'logs/'
APPLICATION_ID = 1185231216211918900
SAVE_FILE = 'LastBounty'
MESSAGE_DURATION: float = 45
LAST_MESSAGE_UPDATE: float = time()
LAST_VALID_BOUNTY: int = None
CURRENT_BOUNTY: int = None
BOUNTY_TIMESTAMP: float = None
CURRENT_FUN_MESSAGES: list[FunMessage] = []
CURRENT_FUN_MESSAGE: FunMessage = None
RICH_PRESENCE: Presence = None
WINDOWS_RENDER = WindowsRender()

# Options read from Capture.txt file
BOUNTY_LOCATION_ON_SCREEN: tuple = None
DRAW_RECTANGLE_AROUND_CAPTURE: bool = None


def Print(text) -> None:
    print(f'[{datetime.now().strftime("%m/%d/%Y %H:%M:%S")}] {text}')


def ShowCaptureRectangle() -> None:
    WINDOWS_RENDER.DrawRectangle(BOUNTY_LOCATION_ON_SCREEN)


def ThreadShowCaptureRectangle() -> None:
    while True:
        ShowCaptureRectangle()


def PickNewMessage() -> None:
    global CURRENT_FUN_MESSAGE, LAST_MESSAGE_UPDATE
    while not (filtered_selection := [fun_message for fun_message in CURRENT_FUN_MESSAGES]):
        CURRENT_FUN_MESSAGES.clear()
        CURRENT_FUN_MESSAGES[:] = [msg for msg in FUN_MESSAGES if random.random() < msg.chance]
    CURRENT_FUN_MESSAGE = random.choice(filtered_selection)
    CURRENT_FUN_MESSAGES.remove(CURRENT_FUN_MESSAGE)
    LAST_MESSAGE_UPDATE = time()


def UpdateBounty(bounty: int, update_just_message: bool) -> None:
    global BOUNTY_TIMESTAMP

    amount = None
    if CURRENT_FUN_MESSAGE.item_price > 0:
        if CURRENT_FUN_MESSAGE.item_price > CURRENT_BOUNTY:
            fraction = bounty / CURRENT_FUN_MESSAGE.item_price * 100
            percision_places = int(fraction < 10)
            amount = f'{fraction:.{percision_places}f}% of a'
            first_letter_index = CURRENT_FUN_MESSAGE.message_format.find('{}') + 3
            first_letter = CURRENT_FUN_MESSAGE.message_format[first_letter_index:first_letter_index + 1]
            if first_letter.lower() in 'aeiou':
                amount += 'n'
        else:
            amount = bounty // CURRENT_FUN_MESSAGE.item_price

    suffix = None
    if (suffix_info := CURRENT_FUN_MESSAGE.suffix_info) is not None:
        index = type(amount) == str or amount == 1
        suffix = suffix_info[index]

    state_text = CURRENT_FUN_MESSAGE.message_format.format(amount, suffix)
    details_text = f'Current bounty: ${bounty:,}'
    image_text = f'Dead bounty: ${round(bounty * 0.4):,}'

    if not update_just_message:
        BOUNTY_TIMESTAMP = int(time())
    bounty_timestamp = BOUNTY_TIMESTAMP

    image_kwargs = (
        {'small_image': CURRENT_FUN_MESSAGE.icon_key, 'small_text': image_text},
        {'large_image': CURRENT_FUN_MESSAGE.icon_key, 'large_text': image_text}
    )[CURRENT_FUN_MESSAGE.image_size]
    RICH_PRESENCE.update(details=details_text, state=state_text, start=bounty_timestamp, **image_kwargs)

    if not update_just_message:
        with open(SAVE_FILE, 'w') as update_file:
            update_file.write(f'{bounty}\n{bounty_timestamp}')


def LoadBounty() -> None:
    global BOUNTY_TIMESTAMP, CURRENT_BOUNTY, LAST_VALID_BOUNTY
    if not os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'w') as f:
            CURRENT_BOUNTY = LAST_VALID_BOUNTY = 0
            BOUNTY_TIMESTAMP = int(time())
            f.write(f'0\n{BOUNTY_TIMESTAMP}')
    else:
        with open(SAVE_FILE, 'r') as f:
            CURRENT_BOUNTY, BOUNTY_TIMESTAMP = [int(num) for num in f.read().splitlines(keepends=False)]
            LAST_VALID_BOUNTY = CURRENT_BOUNTY
    Print(f'Loaded bounty ${CURRENT_BOUNTY:,}')


def main() -> None:
    global BOUNTY_LOCATION_ON_SCREEN, DRAW_RECTANGLE_AROUND_CAPTURE, RICH_PRESENCE, CURRENT_BOUNTY, LAST_VALID_BOUNTY

    with open('Capture.txt', 'r') as capture_file:
        capture_options = [line for line in capture_file.read().splitlines(keepends=False)
                           if line and not line.startswith('#')]

    num_capture_options = 2
    if len(capture_options) == num_capture_options:
        BOUNTY_LOCATION_ON_SCREEN = [int(param) for param in capture_options[0].split(',')]
        DRAW_RECTANGLE_AROUND_CAPTURE = capture_options[1].lower() == 'true'
    else:
        raise ValueError(f'Capture.txt options must match {num_capture_options}, found: {capture_options}')

    x, y, w, h = BOUNTY_LOCATION_ON_SCREEN
    Print(f'Will be reading pixel coordinates: {x}x {y}y {w}w {h}h')
    Print(f'Showing capture rectangle on screen: {DRAW_RECTANGLE_AROUND_CAPTURE}')

    if DRAW_RECTANGLE_AROUND_CAPTURE:
        threading.Thread(target=ThreadShowCaptureRectangle).start()

    bounty_regular_expression = re.compile(r'\$\d+\sBounty')
    LoadBounty()

    RICH_PRESENCE = Presence(str(APPLICATION_ID))
    RICH_PRESENCE.connect()
    Print(f'Connected to application {APPLICATION_ID}')

    while True:
        if CURRENT_FUN_MESSAGE is None or time() - LAST_MESSAGE_UPDATE >= CURRENT_FUN_MESSAGE.exposure_time * MESSAGE_DURATION:
            PickNewMessage()
            UpdateBounty(CURRENT_BOUNTY, True)
        screenshot = pyautogui.screenshot(region=BOUNTY_LOCATION_ON_SCREEN).resize((w * 3, h * 3))

        if detected_text := pytesseract.image_to_string(screenshot).strip():
            dollar_at = detected_text.find('$')
            bounty_at = detected_text.find('Bounty')
            if -1 < dollar_at < bounty_at and bounty_regular_expression.match(detected_text):  # $d Bounty
                CURRENT_BOUNTY = detected_text[dollar_at + 1:bounty_at - 1]
                CURRENT_BOUNTY = int(CURRENT_BOUNTY)
                if LAST_VALID_BOUNTY != CURRENT_BOUNTY:
                    LAST_VALID_BOUNTY = CURRENT_BOUNTY
                    Print(f'New bounty: ${CURRENT_BOUNTY:,} | `{detected_text}`')
                    UpdateBounty(CURRENT_BOUNTY, update_just_message=False)

        sleep(1)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log_filename = datetime.now().strftime("%m-%d-%Y %H-%M-%S")
        error_string = traceback.format_exc()
        if not os.path.exists(LOGS_DIRECTORY):
            os.mkdir(LOGS_DIRECTORY)
        with open(f'{LOGS_DIRECTORY}{log_filename}', 'w') as log_file:
            log_file.write(error_string)
        Print(f'An error has occurred: {e}\n{error_string}')
        os.system('pause')
