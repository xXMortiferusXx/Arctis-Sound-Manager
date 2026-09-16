# Fork-Änderungen (Arctis-Sound-Manager Fork)

Dokumentation aller Änderungen, die wir an diesem Fork `xXMortiferusXx/Arctis-Sound-Manager` vorgenommen haben — unabhängig vom upstream `loteran/Arctis-Sound-Manager`.

---

## Übersicht Commits

| Hash | Beschreibung |
|------|-------------|
| `348255f` | **loopback: advertise 8ch 7.1 on Game/Media/Aux captures in Sonar mode** |
| `1d4f0e9` | loopback: disable channelmix on 8ch captures so stereo isn't upmixed |
| `38790d1` | **loopback: use channelmix.upmix=false instead of channelmix.disable on 8ch** |
| `d67e88e` | **pw_quirks: stop WirePlumber from restoring HeSuVi effect-node volumes** |

*Fett = die commits, die im finalen Fork live sind.*

---

## 1. 8ch Loopback Fix — echtes 7.1 über HeSuVi

**Problem:** Game/Media Sinks meldeten 2ch Stereo, obwohl Sonar und HeSuVi eine 7.1-Kette verarbeiten. Echte 7.1-Quellen (z.B. POE2) wurden auf Stereo runtergebrochen, die HeSuVi-Channelomics-Sektion war obsolet.

**Lösung (`loopback_manager.py`):**

- `LoopbackSpec` hat neue Attribute `capture_channels: int`, `capture_positions: list[str]`, `playback_channels: int`, `playback_positions: list[str]`.
- `_build_pw_loopback_argv()` nutzt diese Werte für `audio.position` und die Kanalzahl in capture/playback args.
- `make_specs()` setzt Game/Media/Aux in Sonar-Modus auf `8ch 7.1` (`FL FR FC LFE RL RR SL SR`), Chat bleibt `2ch`.
- Patchset im Fork: Commits `348255f` (Ankündigung), `38790d1` (Upmix-Fix).

**Live-Verifikation:** POE2 sendet echtes 7.1 (8 Links), voller Durchgang bis zum HeSuVi-Konvolutor.

---

## 2. Stereo-Upmix-Loudness Problem & channelmix.upmix=false

**Symptom:** Media-Kanal deutlich lauter als Game, obwohl gleiche Einstellungen.

**Analyse (korrigiert):**
1. *Erste Hypothese:* Stereo-Source (2ch) wird von PipeWire's `channelmix.upmix=true` automatisch auf 7.1 hochskaliert (synthetisierte FC/LFE/RL/RR/SL/SR aus FL/FR). Diese korrelierten Kopien flössen durch die HeSuVi-HRTF-Faltung und summierten sich auf der LR-Mix-Ebene → vermutete Lautstärkeerhöhung.
2. *Versuch `channelmix.disable=true`* (Commit `1d4f0e9`): Unterbindet den Channelmix komplett → **bricht alles** (kein Ton, kein Volume, kein Up/Down-Mix). WirePlumber knallt das 2↔8ch-Adaptionssystem ab. → wieder zurückgezogen.
3. *Finale Lösung `channelmix.upmix=false`* (Commit `38790d1`): Verhindert nur den Upmix (keine synthetische 2→7.1-Skalierung), hält den Mixer ansonsten am Leben. Stereo-Inhalte bleiben FL/FR, 7.1-Quellen weiterhin 8ch. **Dieser Commit ist live.**

**Korrektur (Erkenntnis):** Der gemessene Lautstärkeunterschied Media vs. Game kam **nicht vom Upmix**, sondern von dem in **Punkt 3** beschriebenen WirePlumber-Stale-Value (`0.2927` am Game-HeSuVi-Output ≈ −10.7 dB). Nach dem Fix dort sind beide Kanäle identisch laut. `channelmix.upmix=false` bleibt trotzdem die bessere Lösung und ist live: Es verhindert, dass synthetische korrelierte Kanäle durch die HRTF-Faltung laufen (physikalisch sauberer, keine Energieaufregung auf den Zusatzkanälen). Die `upmix=false`-Entscheidung ist also unabhängig von der Lautstärke-Begründung gerechtfertigt — nur die ursprüngliche *Begründung* dafür war falsch.

---

## 3. WirePlumber Stream-Restore Gotcha (Volume-Stale-Value-Fehler)

**Symptom:** Game-HeSuVi-Output stand auf `0.2927` (−10.7 dB) — nicht im GUI, sondern in WirePlumber's Backend.

**Mechanismus:**
- WirePlumber speichert `volume`/`mute`/`channelVolumes` **pro Node** in `~/.local/state/wireplumber/stream-properties`.
- Beim nächsten Recreate/Reconnect stellt WP diese Werte wieder her.
- Beim HRIR-Testen war einmal am Game-HeSuVi-Output (internes "Virtual Surround Sink") der Regler gedreht worden → WP hat den Wert `0.2927` dauerhaft persistiert → Game wurde nach jedem Recreate wieder leiser.
- **Abhörbar:** Eingemessene Lautstärken in Games schienen zu leise, Audio von Apps über Media schien im Vergleich laut.

**Lösung (Commit `d67e88e`, pw_quirks.py):**
- Neue WirePlumber-Regel `93-asm-no-stream-restore.conf` mit `stream.rules`, die `state.restore-props = "false"` auf die 4 HeSuVi-Effect-Nodes setzt:
  - `effect_input.virtual-surround-7.1-hesuvi*`
  - `effect_output.virtual-surround-7.1-hesuvi*`
- **Nur diese internen Nodes** werden nicht mehr restauriert. HW-Sinks und ASM-Sinks (`Arctis_Game/Media/Chat`) behalten ihr normales Restore-Verhalten (da steuert `channel_volumes.json`).
- `stream.rules` wird von `state-stream.lua` Zeile 15 aus den gemergten `.conf.d`-Fragmenten gelesen (`Conf.get_section_as_json("stream.rules", ...)`). Kein Allowlist-Eintrag nötig.

**Live-Verifikation:**
1. HeSuVi-Output live auf `0.8` gesetzt → `stream-properties` blieb **unverändert** (WP speichert nicht mehr)
2. WP neu gestartet → Nodes wieder bei 1.0 (statt alter 0.2927)

**Diagnose-Helfer:**
```bash
grep -i "Virtual\|hesuvi" ~/.local/state/wireplumber/stream-properties
```
→ Jeder Wert ≠ `1.000000` dort ist ein manuell gesetzter Wert, der persistiert wurde. Vor dem Fix war das die Ursache.

**Architektur-Details:**
- Die Datei `pw_quirks.py` schreibt analog zu den bestehenden `91-asm-alsa-headroom.conf` und `92-asm-no-suspend.conf`.
- Der Aufruf erfolgt beim Daemon-Start in `core.py` (neben den anderen Quirks).
- Version-Gate: WirePlumber ≥ 0.5 (`_MIN_WIREPLUMBER_VERSION`), ältere Versionen werden geskippt.
- Idempotent: Bei unverändertem Inhalt kein Neustart von WirePlumber.

---

## Technische Details (als Referenz)

### ASM-Service-Symlink nach Rebuild (GELÖST — Wartungs-Falle entfernt)

**Früher (manueller Symlink):** `~/.config/systemd/user/arctis-manager.service` zeigte auf einen NixOS-Store-Pfad. Nach jedem Rebuild änderte sich der Store-Hash, aber der Symlink wurde nicht automatisch aktualisiert. Solange die alte Store-Generation existierte (NixOS räumt erst bei `nix-collect-garbage` auf), lief der Dienst scheinbar problemlos — nach einem GC verweist der Symlink ins Leere → ASM bricht ohne ersichtlichen Grund.

**Warum es nie auffiel:** User-Level-Symlink (`~/.config/systemd/user`) hat höhere Priorität als `/etc/systemd/user`. Selbst wenn NixOS die `/etc`-Ebene frisch aktualisierte, überdeckte der veraltete User-Link sie. Trotzdem funktionierte alles, solange der alte Store-Pfad noch existierte.

**Fix (2026-09-16):** Den manuellen Symlink `~/.config/systemd/user/arctis-manager.service` **komplett entfernt** → systemd lädt die von NixOS verwaltete `/etc/systemd/user/arctis-manager.service`, die bei jedem `switch` automatisch den frischen Store-Pfad übernimmt. **Kein manuelles Neulinken mehr nötig.**

```bash
# Der frühere (nicht mehr nötige) Workaround:
# NEW="/nix/store/$(ls /nix/store | grep 'unit-arctis-manager.service' | ...)/arctis-manager.service"
# ln -sfn "$NEW" ~/.config/systemd/user/arctis-manager.service
```

### WM/ASPCM-Kanal-Volume-Persistenz

ASM speichert Volumes in `~/.config/arctis_manager/channel_volumes.json`:
```json
{"Arctis_Game": 70, "Arctis_Media": 70, "Arctis_Chat": 100}
```
- Diese Werte werden beim Loopback-Recreate (#134) wiederhergestellt.
- Die Volumes dieser Sinks sind **nicht** von `93-asm-no-stream-restore.conf` betroffen — WP-Restore dort greift nur auf den `effect_*`-Nodes.
- Die Lineare→Kubische Umrechnung in PipeWire: `PA 70%` → `cVol 0.343` (≈0.7³).

### Warum `channelmix.disable=true` fehlschlug

`channelmix.disable=true` auf dem Capture-Sink killte den gesamten PipeWire-Channelmix:
- Kein 2↔8ch-Mapping mehr → Audiokanäle tot
- Kein Volume-Pfad mehr (`pulsectl.volume_set_all_chans` → keine Auswirkung)
- Kein Upmix/Downmix mehr
- **Ergebnis:** Komplett stille Kette, Volume-Regler ohne Auswirkung
- `channelmix.upmix=false` greift dagegen selektiv nur auf den Upmix-Pfad.

### HeSuVi-Kette (Momentanzustand)

```
[App/Game] → [Arctis_Game/Media (8ch pw-loopback)]
           → [sonar-game/media-eq (20 Band)] 
           → [virtual-surround-7.1-hesuvi (HRIR-Konvolutor)]
           → [alsa analog-stereo (GameDAC)]
```

- HRIR: `nahimic-` (502 Samples, Tilt 12.3 = neutral)
- EQ: Alle Bänder flach (0 dB), Media/Game identisch
- HeSuVi beider Ketten: byte-identische Konfigurationsdateien
- `effect_output.*` Volume: immer 1.0 (WP-Restore deaktiviert via `d67e88e`)
