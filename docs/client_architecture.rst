Client Architecture
===================

This document outlines the thin client architecture of ``bib-ami``.

Client-Server Model
-------------------

``bib-ami`` operates as a thin client that delegates citation parsing, registry matching, and verification heuristics to the remote cloud engine. By keeping the local footprint minimal, users are provided access to the latest upstream catalog integrations that include CrossRef, DataCite, and Open Library, without needing to update local parsing logic.

SDK vs. Web Application
-----------------------

- **Web Application:** An interactive UI accessed via the browser for visually managing, deduplicating, and cleaning extensive bibliography libraries.
- **CLI / SDK:** A lightweight interface designed for terminal automation, script integration, and programmatic API access to the core verification engine.
