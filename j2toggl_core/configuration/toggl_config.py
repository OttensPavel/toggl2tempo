from typing import Optional


class TogglConfig:
    def __init__(self):
        self.token: Optional[str] = None
        self.user_agent: Optional[str] = None

    def validate(self) -> bool:
        if self.token is None or \
           len(self.token) == 0 or \
           self.user_agent is None or \
           len(self.user_agent) == 0:
            return False

        return True
