# Pod Point Home Assistant Component

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Community Forum][forum-shield]][forum]

_Unofficial component to integrate with [Pod Point][pod_point_web] Solo/Solo 3 charging points._

**This component will set up the following platforms.**

Platform | Description
-- | --
`binary_sensor` | Shows if the pod is connected to a vehicle
`sensor` | Show info from Pod Point API.
`switch` | Enable/disable  charging.

![example][exampleimg]

## Installation

### HACS (recommended)

You can install this component via HACS by searching for 'Pod Point' and then install it from the main HACS integration screen.

_Note: You will need to restart before you can install Pod Point via the UI._ Within Home Assistant go to "Configuration" -> "Integrations" click "+" and search for "Pod Point".


### Manually

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `pod_point`.
4. Download _all_ the files from the `custom_components/pod_point/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Pod Point"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_compoenets/pod_point/static/...
custom_components/pod_point/translations/en.json
custom_components/pod_point/translations/sensor.en.json
custom_components/pod_point/__init__.py
custom_components/pod_point/api.py
custom_components/pod_point/binary_sensor.py
custom_components/pod_point/config_flow.py
custom_components/pod_point/const.py
custom_components/pod_point/entity.py
custom_components/pod_point/errors.py
custom_components/pod_point/manifest.json
custom_components/pod_point/sensor.py
custom_components/pod_point/switch.py
```

## Configuration is done in the UI

Once you have installed either manually or via HACS, restart your home assistant instance and then setup the component by choosing 'Add integration' and search for 'Pod Point.

## Lovelace examples

### Header Images

In the example below, and for the sensors created by this integration, there are a number of pod 'images' that are included for use in the UI, each image and model is listed below.

For the sensor that comes installed we will add the image based on your pod model number.

Pod Model | Image Link
--- | ---
Solo Universal | /api/pod_point/static/uc.png
Solo Tethered | /api/pod_point/static/2c.png
Solo 3 Universal | /api/pod_point/static/uc-03.png
Solo 3 Tethered | /api/pod_point/static/2c-03.png

#### Which pod do I have?

![which pod][whichpodimg]

### Entities YAML example:

```yaml
type: entities
entities:
  - entity: sensor.pod_status
    name: Status
  - entity: binary_sensor.cable_status
    name: Cable
  - entity: switch.charging_allowed
title: Pod Point
header:
  type: picture
  image: /api/pod_point/static/uc-03.png # See above for options per-model
  tap_action:
    action: none
  hold_action:
    action: none
state_color: true
```

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[pod_point_web]: https://pod-point.com
[pod_point]: https://github.com/mattrayner/pod-point-home-assistant-component
[buymecoffee]: https://www.buymeacoffee.com/mattrayner
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/mattrayner/pod-point-home-assistant-component.svg?style=for-the-badge
[commits]: https://github.com/mattrayner/pod-point-home-assistant-component/commits/master
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[exampleimg]: https://github.com/mattrayner/pod-point-home-assistant-component/raw/ef2c39788cdcd85d08a9adab1c06d74c51d38993/example.png
[whichpodimg]: https://github.com/mattrayner/pod-point-home-assistant-component/raw/ef2c39788cdcd85d08a9adab1c06d74c51d38993/which_pod.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/mattrayner/pod-point-home-assistant-component.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Matt%20Rayner-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/mattrayner/pod-point-home-assistant-component.svg?style=for-the-badge
[releases]: https://github.com/mattrayner/pod-point-home-assistant-component/releases
[hacs-add-repo]: https://hacs.xyz/docs/faq/custom_repositories
