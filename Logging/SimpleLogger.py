import time

from Logging.BaseLogger import BaseLogger


class SimpleLogger(BaseLogger):
    def logDebug(self, obj):
        t1 = time.time()

        print(f'{t1 - self.startTime:.3f}s (+{t1 - self.previousLoggingTime: .3f}) {obj}')
        self.previousLoggingTime = t1