from datetime import timedelta, datetime

class Throttle:
    """Throttle."""

    interval = timedelta(seconds=60)
    last_run = None

    def set_last_run(self):
        """Set last run time."""
        self.last_run = datetime.now()

    @property
    def throttle(self):
        """Check if this should trhottle."""
        if self.last_run is None:
            self.last_run = datetime.now()
            return False

        if (self.last_run + self.interval) < datetime.now():
            return False

        return True