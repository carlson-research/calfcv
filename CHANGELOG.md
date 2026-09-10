# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-10

### Added
* **Thin Client Architecture:** Initial release of the lightweight `bib-ami` client, routing all citation verification logic to the proprietary backend engine.
* **CLI Interface:** Added `bib-ami lookup <identifier>` command to query citation metadata directly from the terminal.
* **Web App Launcher:** Added `bib-ami launch` command to easily open the interactive web interface in the system's default browser.
* **Authentication:** Implemented environment variable `BIB_AMI_API_KEY` injection for secure, authenticated requests.
* **Test Suite:** Established comprehensive unit and end-to-end test suite achieving 100% code coverage.
