# Third-party components

The desktop shell dynamically uses PySide6 / Qt 6.12 and Qt WebEngine, including
Chromium. These components retain their respective licenses. Qt for Python is
available under LGPLv3/GPLv3/commercial terms; see
https://doc.qt.io/qtforpython-6/licenses.html and the installed PySide6 package.
Qt / PySide6 source: https://code.qt.io/pyside/pyside-setup.git/ and
https://code.qt.io/qt/qtwebengine.git/ . The application does not prevent users
from replacing the dynamically loaded Qt libraries with compatible builds.
Chromium licensing: https://www.chromium.org/chromium-os/licensing/ .

The Horizon orb renderer, watercolor texture, original ChatGPT UI stylesheet
OpenAI Sans fonts, original PowerSlider component and its original runtime
dependency bundles are **not** part of this
repository or release payload and are **not** covered by this project's MIT
license. At first use, the application retrieves the public resources identified
in `runtime_manifest.json` directly from their original ChatGPT CDN, verifies
their pinned SHA-256 digests and caches them locally. No OpenAI authentication,
cookies or conversation content are used. Availability and rights in these
resources remain with their respective owner. This project is not affiliated
with OpenAI.

The power slider executes the original component function and its original
React/Radix/Motion dependencies. A narrowly scoped export shim exposes its
entry point without rewriting the component body. It evaluates only the
generic dependency closure needed for the independent slider; it does not
start the authenticated ChatGPT app or account/business modules. Desktop
placement, blue accent variables, allowed option data, accessibility bindings
and local preset events are supplied by this project.

The Edge extension manifest contains a public key solely to keep its identifier
stable. No corresponding private key or account credential is included.
