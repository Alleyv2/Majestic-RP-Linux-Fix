# Security policy

- External executable code is never presented as first-party code.
- The runner archive is pinned to a full Git commit and verified with SHA-256 before extraction.
- Archive members are checked against path traversal before extraction.
- The original third-party license is preserved.
- Proton Experimental is copied before patching; the Steam-managed original is not modified.
- Steam configuration is backed up before modification.
- Destructive cleanup targets only explicit staging or backup paths.
- Logs shown in the GUI must not expose bearer tokens, cookies, passwords or account identifiers.

Before changing a pinned dependency, review its source, update the commit and digest together, and run the downloader and end-to-end launch tests.
