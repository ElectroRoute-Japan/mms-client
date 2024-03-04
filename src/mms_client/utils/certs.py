"""Contains functionality associated with certificates."""

from pathlib import Path
from typing import List
from typing import Optional
from typing import Self

# The default directory for certificates
BASE_DIR = Path(__file__).parent.parent.resolve()


class Certificate:
    """Describes a certificate composed of a cert file and a key file."""

    def __init__(self, crt_file: str, key_file: str):
        """Create a new Certificate.

        Creates a new certificate from the absolute path to the certificate file and
        the absolute path to the key file.

        Arguments:
        crt_file:   The absolute path to the cert file
        key_file:   The absolute path to the key file
        """
        self._cert = crt_file
        self._key = key_file

    @classmethod
    def from_directory(cls, cert_dir: Optional[Path] = None, name_pref: str = "") -> Self:
        """Create a new Certificate from a given directory.

        This method expects the certificates to be located in the same directory, and to have the same name.
        Furthermore, this method will assume that the cert will be suffixed with .crt.pem and the key will be suffixed
        with .key.pem. If these conditions are not met then an exception will be raised.

        Arguments:
        cert_dir:   The directory containing the certificate files. This must be a Path
                    object but may be relative or absolute
        name_pref:  The name prefix both certificate files should have. If the user
                    wants to retrieve any certificate, regardless of naming, this may
                    be omitted.
        """
        # First, check if we weren't provided with a default certificate directory. In
        # this case, we'll set it to the default base directory
        if cert_dir is None:
            cert_dir = BASE_DIR

        # Next, iterate over each of these and filter out any that aren't .PEM files
        # that are prefixed with our name value
        files = [
            f for f in cert_dir.iterdir() if f.is_file() and f.name.startswith(name_pref) and f.name.endswith(".pem")
        ]

        # Now, get the cert file and key file from the list
        crt = _find_with_extension(files, ".crt.pem")
        key = _find_with_extension(files, ".key.pem")

        # Finally, embed these in the certificate object and return it
        return cls(crt, key)

    @property
    def cert_file(self) -> str:
        """Return the full path to the cert file."""
        return self._cert

    @property
    def key_file(self) -> str:
        """Return the full path to the key file."""
        return self._key


def _find_with_extension(files: List[Path], ext: str) -> str:
    """Find the file with the given extension and return it.

    This method will raise an exception if no file exists with the extension provided.

    Arguments:
    files:  The list of files to search
    ext:    The extension we're looking for
    """
    try:
        return str(next(filter(lambda f: f.name.endswith(ext), files)))
    except StopIteration as inner:
        raise RuntimeError(f"Expected to find file with extension '{ext}' in directory") from inner
