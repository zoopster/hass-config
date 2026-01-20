"""Registry."""


class RegistryDict:
    """Registry dict."""

    register = {}

    def add(self, key, value):
        """Add to the Registry."""
        self.register[key] = value

    def remove(self, key):
        """Remove from Registry."""
        if key in self.register:
            del self.register[key]


class RegistryList:
    """Registry list."""

    register = []

    def add(self, value):
        """Add to the Registry."""
        self.register.append(value)

    def remove(self, value):
        """Remove from Registry."""
        if value in self.register:
            self.register.remove(value)
