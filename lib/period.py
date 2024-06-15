from datetime import datetime, timedelta 

class EventPeriod:

    def __init__(self, seconds):
        self.last = datetime.now() - timedelta(seconds=seconds)
        self.seconds = seconds

    def check(self):
        curr = datetime.now()
        period = curr - self.last
        if period.seconds >= self.seconds:
            self.last = curr
            return True
        return False


if __name__ == '__main__':
    import time
    event_period = EventPeriod(3)

    for i in range(20):
        print(event_period.check())
        time.sleep(1)

