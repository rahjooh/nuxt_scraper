"""JavaScript snippets for Playwright to mask automation detection.

These scripts are designed to be injected via page.add_init_script() or context.add_init_script()
to modify browser properties that are commonly used for bot detection.
"""

from __future__ import annotations

STEALTH_SCRIPTS: list[str] = [
    """
    // Mask webdriver property
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
    });
    """,
    """
    // Mask chrome.runtime for Chrome-based browsers
    if (window.chrome) {
        window.chrome.runtime = {
            // Mock extension APIs that are not present in normal browsing
            connect: () => {},
            sendMessage: () => {},
        };
    }
    """,
    """
    // Mock permissions API to avoid bot detection
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
    );
    """,
    """
    // Mimic the order of plugins in a typical browser
    // This is a simplified example, a real one would be much longer
    Object.defineProperty(navigator, 'plugins', {
        get: () => [{
            0: {description: 'Portable Document Format', enabledPlugin: Plugin, filename: 'internal-pdf-viewer', name: 'PDF Viewer'},
            1: {description: '', enabledPlugin: Plugin, filename: 'mhjfbmdgcfjbbgchlofpdmkgcjopgied', name: 'Chrome PDF Plugin'},
            length: 2,
            item: function() {}, namedItem: function() {}
        }]
    });
    """,
    """
    // Spoof console.debug to prevent detection of debugging tools
    if (console.debug) {
        console.debug = () => {};
    }
    """,
    """
    // Override WebGL fingerprinting by reducing available parameters
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) { // UNMASKED_VENDOR_WEBGL
            return 'Intel Open Source Technology Center';
        }
        if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL
            return 'Mesa DRI Intel(R) Ivybridge Mobile '; // Or some other common renderer
        }
        return getParameter(parameter);
    };
    """,
    """
    // Override clientRects for a less accurate fingerprint (example, can be more complex)
    const originalGetClientRects = Element.prototype.getClientRects;
    Element.prototype.getClientRects = function() {
        const rects = originalGetClientRects.apply(this, arguments);
        if (rects.length > 0) {
            // Introduce a small random jitter to bounding box values
            return Array.from(rects).map(rect => ({
                bottom: rect.bottom + Math.random() * 0.1 - 0.05,
                height: rect.height + Math.random() * 0.1 - 0.05,
                left: rect.left + Math.random() * 0.1 - 0.05,
                right: rect.right + Math.random() * 0.1 - 0.05,
                top: rect.top + Math.random() * 0.1 - 0.05,
                width: rect.width + Math.random() * 0.1 - 0.05,
                x: rect.x + Math.random() * 0.1 - 0.05,
                y: rect.y + Math.random() * 0.1 - 0.05,
            }));
        }
        return rects;
    };
    """
]
