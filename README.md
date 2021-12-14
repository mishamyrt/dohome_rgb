# DoHome RGB [![Quality assurance](https://github.com/mishamyrt/dohome-rgb/actions/workflows/lint.yaml/badge.svg)](https://github.com/mishamyrt/dohome-rgb/actions/workflows/lint.yaml)

DoHome lights Home Assistant integration. Supports DoHome RGB bulb and strip.
## Supports

* RGB color
* White temperature
* State update
* Re-establishing a connection after disconnection

## Configuration

Add to your configuration file.

```yaml
light:
  - platform: dohome_rgb
    entities:
      kitchen_chandelier_1:
        sid: '797a'
        ip: '192.168.31.58'
      kitchen_chandelier_2:
        sid: '79c7'
        ip: '192.168.31.135'
      kitchen_chandelier_3:
        sid: '7a1b'
        ip: '192.168.31.62'
```

`sid` is the unique id of your device. It can be recognised by looking at the last 4 characters of the mac–address.

## Credits

* Rave — for the [original component](https://github.com/SmartArduino/DoHome/tree/master/DoHome_HassAssistant_Component) development
