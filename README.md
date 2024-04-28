# Pod Point Home Assistant Component

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Community Forum][forum-shield]][forum]

_Unofficial component to integrate with [Pod Point][pod_point_web] Solo/Solo 3 charging points._

> **NOTE:** PodPoint have made changes to their authentication system in June 2023 which may result in existing connections reporting Invalid Credentials, and users being unable to log in again with their existing password. 
> This can be fixed by going to https://charge.pod-point.com/login and reseting your password, and then re-authenticate with the integration.

**This component will set up the following platforms and services.**

Platform | Description
-- | --
`binary_sensor` | Shows if the pod is connected to a vehicle.
`sensor` | Show info from Pod Point API.
`sensor` (Total Energy) | Show a combined KWh value from all charges for a given pod.
`sensor` (Current Charge Energy) | Show the KWh for the current charge session (or 0).
`sensor` (*Total Cost) | Show the total cost of all ***completed* charges.
`sensor` (Last ***Completed* Charge Cost) | Show the total cost of the last ***completed* charge.
`sensor` (Completed charge time) | Show a combined 'charge time' value from all charges for a given pod.
`sensor` (Balance) | Shows the balance on your PodPoint account.
`sensor` (Charge Mode) | Shows the charge mode your pod is currently in/
`sensor` (***Charge Override End Time) | Shows the end time for any configured 'charge now' override.
`sensor` (Signal Strength) | Shows WiFi signal strength of a given pod.
`sensor` (Last message received) | When was a message last received from a given pod.
`sensor` (Cloud connection status) | Status of pods connection to the cloud.
`switch` (****Allow Charging) | Enable/disable charging by enabling/disabling a schedule.
`switch` (Smart Charge Mode) | Enable the switch for 'Smart' charge mode, disable it for 'Manual' charge mode.
`update` (Firmware Update) | Shows the current firmware version for your device and alerts if an update is available

> ***Total cost is based on the energy provider and kWh cost set in Pod Point.**

> ****Charges are considered complete by Pod Point when you disconnect the vehicle, not when power delivery stops.**

> *****Charge override end time will be 'Unknown' if there is no charge override ('charge now') set. Or, the time when the charge override ends.**

> ******When in either `Manual` or `Override` charge mode, the `Allow Charging` switch is inactive. This is because setting a schedule will not affect the charge in these modes.**

Service | Params
---|---
`charge_now` - Set a charge override for a time period | `account` - Pod Point account we're setting `charge_now` for.
&nbsp; | `hours` (0-24) - How many hours should the charge override last for?
&nbsp; | `minutes` (0-59) - How many minutes should the charge override last for?
&nbsp; | `seconds` (0-59) - How many seconds should the charge override last for?

![example][exampleimg]
![example][chargetimeimg]

## Installation

> **NOTE:** Due to a breaking change in version 1.0.0, upgrading from previous versions (<= 0.4.4) will cause devices to be duplicated. This can be fixed by removing the configuration and then re-adding.

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

> **NOTE:** Due to a breaking change in version 1.0.0, upgrading from previous versions (<= 0.4.4) will cause devices to be duplicated. This can be fixed by removing the configuration and then re-adding.

Once you have installed either manually or via HACS, restart your home assistant instance and then setup the component by either choosing 'Add integration' and search for 'Pod Point', or through using an auto-discovered Pod on the integrations screen.

### Auto-discovered Pods

Pods are auto-discovered based on their DHCP host and client MAC address. Any device who's host starts with 'podpoint-*' whilst having a MAC address assigned to Espressif will trigger the auto-discovery feature.

## Statuses

Multiple statuses are reported by the main pod sensor. The statuses and their meaning are shown below:

status | display value | description
---|---|---
available | Available | Pod is available to charge, may now be replace with "idle"
unavailable | Unavailable | Pod is unavailable
charging | Charging | Pod is charging an EV
suspended-ev | Charged | Connected EV has suspended charging. Can mean 'Charged', or 'EV has a schedule set'. Will show as 'Charged' to align with the Pod Point app.
suspended-evse | Charging Paused | Charging has been paused by the Pod, could be a schedule, or the key at the bottom has been turned off, or the charger is balanging house power
idle | Ready | Pod is ready to charge when an EV is connected
pending | Pending | An action has been requested (disable charging, charge now, delete charge now, enable charging) but the Pod has not yet acknowledged it. Can take 10 minutes to update.
out-of-service | Out of service | This pod is not in service. Reach out to Pod Point for more information.
waiting-for-schedule | Waiting for schedule | Pod charging is currently blocked by schedule. Connecting your vehicle will *not* begin charging.
connected-waiting-for-schedule | Connected but waiting for schedule | Pod is connected to an EV but schedule is preventing charging
charge-override | Charging now (schedule override) | 'Charge now' has been used to override your pods schedule and start a charging session now.

## Charge Modes

Charge modes can be one of the following values, their meanings can be found below:

mode | description
---|---
smart | This is your pods 'default' option, charging will follow your schedule, along with other smart functionality including randomly offsetting start and end times to help prevent grid shock.
override | Your pod is in 'smart' mode, but you have set an override (a time period where your pod will ignore the schedule and charge). This is designed to be used when you need to charge ourside your normal schedule, and dont want to modify the underlying schedule.
manual | This mode means your pod is not set to a schedule, and does not follow the offsets for start and end times, when you plug it in, it will charge.

## Energy sensors

We populate two energy sensors for each pod connected to your account. These are for the *total* energy you have charged on a given pod and the *current* energy if you are connected and have a charge session ongoing.

If you want to add Pod Point stats to the built in energy dashboard, you should add the `Current Charge Energy` sensor as a device. This sensor reports when the value is reset and should allow you to track the energy usage of your pod.

> *Note:* The Pod Point APIs perform some rounding on the kWh values returned meaning they may be sightly lower than the true energy consumed. We are unable to address this within the component.

## Cost sensors

In order to provide the `Total Cost` and `Last Completed Charge Cost` sensors, we are using `energy_cost` values provided from Pod Point per ***completed* charge. There are some caveats to bare in mind here:

* Energy use for each charge is rounded by Pod Point (see [Energy sensors](#energy-sensors) above) and energy costs are calculated on this rounded value.
* You must set an accurate kWh cost within the Pod Point app (and keep this up to date if your provider/cost per kWh changes

> Given the above rounding, in my opinion the cost values should be used as a guide rather than taken as gospel

>**Charges are considered complete by Pod Point when you disconnect the vehicle, not when power delivery stops.

## Firmware update notifications

If an update is detected for your device, a new repair entry will be created within Home Assistant, prompting you to update using the mobile app. Unforrunately, at this time it is not possible to trigger the firmware update from outside of the Pod Point app but to restrictions with the Pod Point APIs.

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
  - entity: sensor.psl_xxxxxx_status
    name: Pod Status
  - entity: sensor.psl_xxxxxx_charge_mode
    name: Charge Mode
  - entity: sensor.psl_xxxxxx_charge_override_end_time
    name: Charge Override Time Ends
  - entity: binary_sensor.psl_xxxxxx_cable_status
    name: Cable Status
  - entity: switch.psl_xxxxxx_charging_allowed
    name: Charging Allowed
  - entity: switch.psl_xxxxxx_smart_charge_mode
    name: Smart Charge Mode
  - entity: sensor.psl_xxxxxx_current_energy
    name: Current Energy
  - entity: sensor.psl_xxxxxx_total_energy
    name: Total Energy
  - entity: sensor.psl_xxxxxx_last_completed_charge_cost
    name: Last Completed Charge Cost
  - entity: sensor.psl_xxxxxx_total_cost
    name: Total Cost (completed charges)
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
entity: sensor.psl_xxxxxx_completed_charge_time
name: Completed Charge Time
attribute: formatted
```

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

### Development setup

If you want to develop with this locally and test within the devcontainer, ensure you follow the below setups (within the devcontainer):

```bash
make setup-debian
make setup
```

Once you have setup the environment with all of the dependencies, try running the tests:

```bash
make test
```

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
[exampleimg]: https://github.com/mattrayner/pod-point-home-assistant-component/raw/48fdfe237f68c22d4098e8904926f534fdd49819/example.png
[whichpodimg]: https://github.com/mattrayner/pod-point-home-assistant-component/raw/ef2c39788cdcd85d08a9adab1c06d74c51d38993/which_pod.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/mattrayner/pod-point-home-assistant-component.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Matt%20Rayner-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/mattrayner/pod-point-home-assistant-component.svg?style=for-the-badge
[releases]: https://github.com/mattrayner/pod-point-home-assistant-component/releases
[hacs-add-repo]: https://hacs.xyz/docs/faq/custom_repositories
