<p align="center">
    <img src="./docs/logo@2x.png" width="120" />
    <h3 align="center">DoHome RGB</h3>
    <p align="center">Home Assistant integration</p>
    <p align="center">
        <a href="https://github.com/mishamyrt/dohome_rgb/actions/workflows/qa.yaml">
            <img src="https://github.com/mishamyrt/dohome_rgb/actions/workflows/qa.yaml/badge.svg" />
        </a>
        <a href="https://github.com/custom-components/hacs">
            <img src="https://img.shields.io/badge/HACS-Custom-orange.svg" />
        </a>
    </p>
</p>

---

DoHome lights Home Assistant integration. Supports DoHome RGB bulb and strip.

## Supports

* RGB color
* White temperature
* State update
* Re-establishing a connection after disconnection
* Group control

## Installation

### HACS

Add this repo as HACS [custom repository](https://hacs.xyz/docs/faq/custom_repositories).

```
https://github.com/mishamyrt/dohome_rgb
```

Then find the integration in the list and press "Download".

### Manual

Copy `dohome_rgb` folder from latest release to `/config/custom_components` folder.

## Configuration

Devices are configured in groups. If you need to configure only one device, specify it in a separate group. Example:

```yaml
light:
  # Group of bulbs (e.g. a chandelier)
  # entity_id will be dohome_rgb_2b5a_13a1_e77a
  - platform: dohome_rgb
    sids:
      - '2b5a' # Last 4 symbols of device MAC-address
      - '13a1'
      - 'e77a'
  # Individual bulb
  # entity_id will be dohome_rgb_5f7e
  - platform: dohome_rgb
    sids:
      - '5f7e'
```

## Thanks

* Rave — for the [original component](https://github.com/SmartArduino/DoHome/tree/master/DoHome_HassAssistant_Component) development
