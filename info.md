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
`binary_sensor` | Shows if the pod is connected to a vehicle.
`sensor` | Show info from Pod Point API.
`sensor` (Total Energy) | Show a combined KWh value from all charges for a given pod.
`sensor` (Current Charge Energy) | Show the KWh for the current charge session (or 0).
`switch` | Enable/disable  charging.

![example][exampleimg]
![example][chargetimeimg]

{% if not installed %}
## Installation

1. Click install.
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Pod Point".

{% endif %}

## Configuration is done in the UI

> **NOTE:** Due to support for energy sensors and multiple Pod Point accounts, upgrading from <0.3 is not supported. You should remove your pod point configuration and re-configure it after upgrading.

Once you have installed either manually or via HACS, restart your home assistant instance and then setup the component by choosing 'Add integration' and search for 'Pod Point.

## Satuses

Multiple statuses are reported by the main pod sensor. The statuses and their meaning are shown below:

status | description
---|---
available | The pod is available for charging. Connecting a vehicle will begin a charging session.
unavailable | The pod is unavailable for charging.
charging | Vehicle is connected and charging is possible. Note: If you car has completed charging but it still connected to the pod, the status will remain as 'connected'.
out-of-service | This pod is not in service. Reach out to Pod Point for more information.
waiting-for-schedule | Pod charging is currently blocked by schedule. Connecting your vehicle will *not* begin charging.
connected-waiting-for-schedule | Your vehicle is connected to the pod but charging is currently prevented due to a schedule.

## Energy sensors

We populate two energy sensors for each pod connected to your account. These are for the *total* energy you have charged on a given pod and the *current* energy if you are connected and have a charge session ongoing.

If you want to add Pod Point stats to the built in energy dashboard, you should add the `Current Charge Energy` sensor as a device. This sensor reports when the value is reset and should allow you to track the energy usage of your pod.

> *Note:* The Pod Point APIs perform some rounding on the kWh values returned meaning they may be sightly lower than the true energy consumed. We are unable to address this within the component.

### Known energy issues:

1. If you repeatedly restart your home assistant instance whilst actively charging, the energy dashboard will add your kWh together showning a higher value. e.g. 3.2kWh restarted twice would show 9.6kWh (3.2kWh + 3.2kWh + 3.2kWh).

## Lovelace examples

### Header images

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
  - entity: binary_sensor.psl_xxxxxx_cable_status
    name: Cable Status
  - entity: sensor.psl_xxxxxx_status
    name: Pod Status
  - entity: switch.psl_xxxxxx_charging_allowed
    name: Charging Allowed
  - entity: sensor.psl_xxxxxx_current_energy
    name: Current Energy
  - entity: sensor.psl_xxxxxx_total_energy
    name: Total Energy
    secondary_info: none
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

### Entity YAML examples:

#### Long format charge time
```yaml
type: entity
entity: sensor.psl_xxxxxx_completed_charge_time
attribute: long
name: Completed Charge Time (long)
```

#### Standard format charge time
```yaml
type: entity
entity: sensor.psl_266056_completed_charge_time
name: Completed Charge Time
attribute: formatted
```

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[pod_point_web]: https://pod-point.com
[pod_point]: https://github.com/mattrayner/pod-point-home-assistant-component
[buymecoffee]: https://www.buymeacoffee.com/mattrayner
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[chargetimeimg]: https://github.com/mattrayner/pod-point-home-assistant-component/raw/3c7ebf994caf8eb5814859edc724e418c3e5746a/charge_time.png
[commits-shield]: https://img.shields.io/github/commit-activity/y/mattrayner/pod-point-home-assistant-component.svg?style=for-the-badge
[commits]: https://github.com/mattrayner/pod-point-home-assistant-component/commits/master
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[exampleimg]: https://github.com/mattrayner/pod-point-home-assistant-component/raw/76752c0d0dbef64fc482140b7d0937c2b19faab0/example.png
[whichpodimg]: https://github.com/mattrayner/pod-point-home-assistant-component/raw/ef2c39788cdcd85d08a9adab1c06d74c51d38993/which_pod.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/mattrayner/pod-point-home-assistant-component.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Matt%20Rayner-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/mattrayner/pod-point-home-assistant-component.svg?style=for-the-badge
[releases]: https://github.com/mattrayner/pod-point-home-assistant-component/releases
[hacs-add-repo]: https://hacs.xyz/docs/faq/custom_repositories
