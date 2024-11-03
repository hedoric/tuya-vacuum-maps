# Tuya Vacuum Maps

🏠 View Real-Time Vacuum Maps In Home Assistant.<br>
This component adds a new camera which polls the Tuya Cloud API for the latest realtime map data.<br>
This project is primarily focused on Lefant vacuums, but aims to support all Tuya vacuums.

## Installation

### Installing Manually

To install this component, add the contents of `custom_components` to your Home Assistants `custom_components` folder and reboot.

## Compatability List

This is a list of tested devices.
Create a new [issue](https://github.com/jaidenlab/tuya-vacuum-maps/issues) to add your device.

| Device                                                | Support                           |
| ----------------------------------------------------- | --------------------------------- |
| [Lefant M1](https://www.lefant.com/en-ca/products/m1) | $${\color{lightgreen}Supported}$$ |

## Development Roadmap

This is a list of current development goals for this project:

- Feature parity with [Tuya Cloud Vacuum Map Extractor](https://github.com/oven-lab/tuya_cloud_map_extractor)
- Automated tests for each supported device

## Development Environment

It's recommended to set up a development environment if you want to make changes to this component.

### Prerequisites

- [A Visual Studio Code + devcontainer development environment](https://developers.home-assistant.io/docs/development_environment)

### Getting Started

1. Once the devcontainer is created, fork this repository.
2. Go to the folder containing the `homeassistant-core` folder, it should be called `workspaces`.
3. Once your fork is created, make sure your terminal path is set to `/workspaces` and run `git clone <url>`.
4. To make testing easier, create a symlink to the component in your Home Assistant devcontainer.
   - Example: `ln -s /workspaces/tuya-vacuum-maps/custom_components/tuya_vacuum_maps /workspaces/homeassistant-core/config/custom_components`
5. For development, it's recommended you use a virtual environment.
   1. Create a new virtual environment (Run in the root `/tuya-vacuum-maps` folder):
      - `python -m venv venv`
   2. Activate the virtual environment:
      - `source ./venv/bin/activate`

## Special Thanks

- [Tuya Cloud Vacuum Map Extractor](https://github.com/oven-lab/tuya_cloud_map_extractor) by [@oven-lab](https://github.com/oven-lab)
- [Xiaomi Cloud Map Extractor](https://github.com/PiotrMachowski/Home-Assistant-custom-components-Xiaomi-Cloud-Map-Extractor) by [@PiotrMachowski](https://github.com/PiotrMachowski)
