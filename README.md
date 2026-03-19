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
        <a href="https://github.com/mishamyrt/dohome_rgb/tags">
            <img src="https://img.shields.io/github/v/tag/mishamyrt/dohome_rgb.svg?sort=semver" />
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

### [hapm](https://github.com/mishamyrt/hapm)

Add this repository to your `hapm.yaml` by running:

```sh
hapm add mishamyrt/dohome_rgb@latest
```

### HACS

Add this repo as HACS [custom repository](https://hacs.xyz/docs/faq/custom_repositories).

```
https://github.com/mishamyrt/dohome_rgb
```

Then find the integration in the list and press "Download".

### Manual

Copy `dohome_rgb` folder from latest release to `/config/custom_components` folder.

## Configuration

Devices are configured using config flow.

1. Go integrations dashboard (/config/integrations/dashboard)
2. Click "Add integration"
3. Find "DoHome RGB"
4. Enter light hostname

## Thanks

* Rave — for the [original component](https://github.com/SmartArduino/DoHome/tree/master/DoHome_HassAssistant_Component) development
