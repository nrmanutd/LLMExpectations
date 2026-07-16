import time
from abc import ABC, abstractmethod


class BaseLogger(ABC):
    def __init__(self):
        self.startTime = time.time()
        self.previousLoggingTime = self.startTime
    @abstractmethod
    def logDebug(self, obj):
        pass