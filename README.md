# DoHome RGB Home Assistant intergration

[![Quality assurance](https://github.com/mishamyrt/dohome-rgb/actions/workflows/lint.yaml/badge.svg)](https://github.com/mishamyrt/dohome-rgb/actions/workflows/lint.yaml)

DoHome lights Home Assistant integration. Supports DoHome RGB bulb and strip.
## Supports

* RGB color
* White temperature
* State update
* Re-establishing a connection after disconnection

## Installation

### HACS

Add this repo as HACS [custom repository](https://hacs.xyz/docs/faq/custom_repositories).

```
https://github.com/mishamyrt/dohome-rgb
```

Then find the integration in the list and press "Download".

### Manual

Copy `dohome_rgb` folder from latest release to `/config/custom_components` folder.

## Configuration

Add to your configuration file.

```yaml
light:
  - platform: dohome_rgb
    entities:
      kitchen_bulb: '192.168.31.58'
      desk_strip: '192.168.31.59'
      desk_lamp: '192.168.31.60'
```

## Credits

* Rave — for the [original component](https://github.com/SmartArduino/DoHome/tree/master/DoHome_HassAssistant_Component) development
