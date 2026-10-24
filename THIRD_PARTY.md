# Third-party components

The desktop shell dynamically uses PySide6 / Qt 6.12 and Qt WebEngine, including
Chromium. These components retain their respective licenses. Qt for Python is
available under LGPLv3/GPLv3/commercial terms; see
https://doc.qt.io/qtforpython-6/licenses.html and the installed PySide6 package.
Qt / PySide6 source: https://code.qt.io/pyside/pyside-setup.git/ and
https://code.qt.io/qt/qtwebengine.git/ . The application does not prevent users
from replacing the dynamically loaded Qt libraries with compatible builds.
Chromium licensing: https://www.chromium.org/chromium-os/licensing/ .

The Horizon orb renderer and watercolor texture are **not** part of this
repository or release payload and are **not** covered by this project's MIT
license. At first use, the application retrieves the public resources identified
in `runtime_manifest.json` directly from their original ChatGPT CDN, verifies
their pinned SHA-256 digests and caches them locally. No OpenAI authentication,
cookies or conversation content are used. Availability and rights in these
resources remain with their respective owner. This project is not affiliated
with OpenAI.

The Edge extension manifest contains a public key solely to keep its identifier
stable. No corresponding private key or account credential is included.
