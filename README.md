<div align="center">

# Trin Vehicle Pack Rebirth — Modernized Trin Vehicles

Immersive Vehicles (MTS/IV) content pack with updated Trin vehicle models, improved animations, and part tone support.

</div>

## Overview

This pack includes modernized versions of Trin civil vehicles with default parts pre-installed, new door mechanics, and part tone support. Other categories may be in-progress.

## Download

- GitHub Actions artifacts: each CI run uploads JARs for 1.12.2 and 1.16.5.
- Releases: push a tag (e.g., `v1.0.0`) to trigger a release with attached JARs.

## Requirements

- Minecraft with Immersive Vehicles (MTS/IV)
- Trin Part Pack (required for parts)

## Installation (Players)

1. Install Immersive Vehicles (MTS/IV).
2. Download the JAR for your MC version.
3. Place it into your `mods` folder.
4. Launch the game.

## Building (Developers)

Prereqs:
- JDK 8
- Git and Gradle wrapper (included)

Quick build:
- Windows: `gradlew.bat buildForge1122 && gradlew.bat buildForge1165`
- Linux/macOS: `./gradlew buildForge1122 && ./gradlew buildForge1165`

Artifacts appear under `out/`.

CI:
- GitHub Actions builds on push/PR, uploads artifacts, and publishes releases on tags.

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history.

## License & Credits

- Content and branding © TheOddlySeagull and contributors. All rights reserved unless otherwise stated.
- Immersive Vehicles by its respective authors.

## Community

- Discord: https://discord.gg/ujQR3wf
- Issues: Use this repo’s Issues for bugs and feature requests.