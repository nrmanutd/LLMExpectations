import time

from Logging.BaseLogger import BaseLogger


class SimpleLogger(BaseLogger):
    def logDebug(self, obj):
        t1 = time.time()

        print(f'{t1 - self.startTime}s (+{t1 - self.previousLoggingTime}) {obj}')
        self.previousLoggingTime = t1