from pypresence import Presence, exceptions
from Launcher import Logger
import os


class DiscordPresence:
    def __init__(self, logger: Logger, application_id: str):
        self.logger: Logger = logger
        self.application_id: str = application_id

        self.presence: Presence = Presence(application_id)
        self.show_discord_activity: bool = False

    def connect(self) -> bool:
        try:
            self.presence.connect()
            self.logger.log('DISCORD', f'Connected to discord application {self.application_id}')
            return True
        except exceptions.DiscordNotFound:
            self.logger.log('DISCORD', 'Connection failed (application is closed or modified)')
            self.show_discord_activity = False
        return False

    def update(self, pid: int = os.getpid(),
               state: str = None, details: str = None,
               start: int = None, end: int = None,
               large_image: str = None, large_text: str = None,
               small_image: str = None, small_text: str = None,
               party_id: str = None, party_size: list = None,
               join: str = None, spectate: str = None,
               match: str = None, buttons: list = None,
               instance: bool = True, payload_override: dict = None):
        try:
            self.presence.update(pid, state, details, start, end, large_image, large_text, small_image, small_text,
           party_id, party_size, join, spectate, match, buttons, instance, payload_override)
        except exceptions.PipeClosed:
            self.logger.log('DISCORD', f'Discord connection isn\'t open, switched to offline mode')
            self.show_discord_activity = False
