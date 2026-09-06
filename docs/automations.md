# Automations

[Back to the README](../README.md) · [Configuration](configuration.md)

Use standard Home Assistant media-player actions for Devialet. Choose your own
entity in the automation editor; `media_player.devialet_speaker` below is a placeholder.

## Test an action first

In **Developer tools → Actions**, select **Media player: Set volume**, choose
the speaker, and use a low volume such as 20%. The YAML equivalent is:

```yaml
action: media_player.volume_set
target:
  entity_id: media_player.devialet_speaker
data:
  volume_level: 0.2
```

Home Assistant volume levels are fractions from `0` to `1`, not percentages
from 0 to 100. Verify that the action works on your current source before adding
it to an automation.

## Example: mute at a chosen time

This example mutes the speaker at 22:00. Change the time and entity to suit your
home. It does not turn the speaker on or start playback.

Paste it into a new automation's YAML editor:

```yaml
alias: Devialet evening mute
triggers:
  - trigger: time
    at: "22:00:00"
conditions:
  - condition: template
    value_template: "{{ states('media_player.devialet_speaker') not in ['unavailable', 'unknown', 'off'] }}"
actions:
  - action: media_player.volume_mute
    target:
      entity_id: media_player.devialet_speaker
    data:
      is_volume_muted: true
mode: single
```

## Other settings

Use standard `select.select_option`, `number.set_value`, or switch actions for
the setting entities your device exposes. Pick the entity and option in the UI
to avoid model-specific naming assumptions. Source selection and playback
support can differ by model and active input.

Do not include credentials in automation YAML. Firmware installation and other
maintenance operations should remain deliberate, supervised actions.
