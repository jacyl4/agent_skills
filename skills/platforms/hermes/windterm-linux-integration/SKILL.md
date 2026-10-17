---
name: windterm-linux-integration
description: Use when restoring, verifying, or modifying the user's WindTerm Linux
  desktop integration, launcher, icon, or input-method environment.
metadata:
  targets:
  - hermes
---

# WindTerm Linux Integration

Use this skill when a task involves WindTerm installation, desktop launcher registration, KDE/GNOME app menu integration, taskbar pinning, icons, or fcitx input-method behavior.

## Installed location

- WindTerm version: `2.7.0`
- App directory: `/home/jacyl4/1base/APP/WindTerm_2.7.0`

## User-level integration

- Desktop entry: `~/.local/share/applications/windterm.desktop`
- Icon: `~/.local/share/icons/hicolor/1024x1024/apps/windterm.png`
- PATH launcher symlink: `~/.local/bin/windterm`
- Symlink target: `windterm-launcher.sh`

## Launcher environment

The launcher forces:

```bash
QT_QPA_PLATFORM=xcb
# fcitx input-method variables
```

## Verify

```bash
readlink -f ~/.local/bin/windterm
test -f ~/.local/share/applications/windterm.desktop && grep -n 'Exec\|Icon\|Name' ~/.local/share/applications/windterm.desktop
test -f ~/.local/share/icons/hicolor/1024x1024/apps/windterm.png
```

## Refresh desktop caches

```bash
update-desktop-database ~/.local/share/applications || true
gtk-update-icon-cache ~/.local/share/icons/hicolor || true
```

## Pitfalls

- Use `QT_QPA_PLATFORM=xcb` for stable launch behavior in this setup.
- Preserve fcitx environment variables when editing the launcher.
- Prefer user-level desktop registration over system-wide writes unless explicitly requested.
