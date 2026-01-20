"""
Version.

Holds version information.
Attributes:
 - major
 - minor
 - patch


properties:
 - version
"""


class Version:
    """Version."""

    def __init__(self, major=None, minor=None, patch=None):
        """
        Initialize.

        Usage:
        from integrationhelper.version import Version
        myversion = Version(1, 2, 3)
        myversion = Version(1, 2)
        myversion = Version(1)

        print(myversion.version)
        """
        self.major = major
        self.minor = minor
        self.patch = patch

    @property
    def version(self):
        """Return set version as a string."""
        version = []
        if self.major is not None:
            version.append(self.major)
        if self.minor is not None:
            version.append(self.minor)
        if self.patch is not None:
            version.append(self.patch)

        return ".".join(version)
