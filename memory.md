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
| `57f2b88` | **sonar: per-channel Boost & Smart Volume (Option A)** |
| `0d24d531` | **chore: bump fork version** (anfangs `1.4.27-fork.1`, invalid) |
| `55a7470d` | **fix: PEP 440 → `1.4.27+fork.1`** (wheel-Build-kompatibel; Backport siehe unten) |
| `559059e0` | docs(memory): Übersichtstabelle + Backport-Merge vermerkt |

*Fett = die commits, die im finalen Fork live sind.*

---

## Upstream-Check (2026-09-22)

Ergebnis: **Kein neuer funktionaler Upstream-Patch seit dem 1.4.27-Backport
(2026-09-21).** Letzter Release bleibt **v1.4.27** (2026-09-20); `main`-HEAD
(`925c720`) = v1.4.27 + nur `[skip ci]`-Chore/Usage-Stats (`c001b37`,
`45ba9b4`); `develop` spiegelt nur `main`. Fork liegt damit auf dem
funktionalen Stand — nichts einzupflegen, Lock bleibt auf `559059e0`.

Groundrule (unverändert): Nur Fixes in Kernbereichen (audio/loopback/sonar/EQ/
wireplumber) lösen einen Backport aus; Clips/GUI-Umbau/Arctis-5/Bluetooth
bleiben Dauer-Nein.

---

## 5. Upstream-1.4.27-Backport (2026-09-21, Branch `backport-1.4.27` → als Fast-Forward in `main` gemerged + gepusht)

### Kontext
Upstream (`loteran/Arctis-Sound-Manager`) hat v1.4.27 released (64 Commits über unserer
Basis `83c083ed` = v1.4.26). Nicht alles eingespielt — nur die **funktional relevanten
Fixes**, keine neuen Features (Clips/window-capture, GUI-Umbau, Arctis-5-Support).

### Cherry-gepickte Upstream-Commits (chronologisch)
| Fork-Hash | Upstream | Beschreibung |
|-----------|----------|--------------|
| `4e4b03d0` | `9408bc67` | stream-guard: recycled PID |
| `8fea6a6a` | `e6e09aa2` | router+guard: gemeinsames Singleton-Fix (`singleton.py`) |
| `2c2c8f1f` | `a47df5f5` | **GameDAC-Master-Volume-Rad synct auf Default-PipeWire-Sink** |
| `4a2f47f6` | `ba6f6f70` | **`percentage()` Doppel-Invertierung (GameDAC n. korrekt)** |
| `0cf973f0` | `3651e602` | core: Idle-Tracker + EIO-Counter |
| `0c2c554d` | `59683796` | **router: ASM eigene filter-chain-Nodes nicht als Apps (1.4.26-Regression)** |
| `cd2e5083` | `eda7b144` | GUI-Exit lässt PipeWire in Ruhe |
| `9665e55f` | `63a7ddbd` | Packaging: Upgrade startet Daemons neu, nie den Tray |
| `1a3c8f15` | `c2afa90c` | GUI: Same-Version-Rebuild als Upgrade erkennen |
| `2a0d6765` | `b60eff40` | GUI: sauberer Exit (kein SIGSEGV, kein Geist-Tray) |
| `6aa4ab1b` | `a5831f39` | GUI: Tray ohne offenes Fenster startet nach Upgrade neu |
| `08581d49` | `b232deec` | **audio: Output-Devices während Ketten-Rebuild stumm + Tray-Neustart** |
| `298516a4` | `c34863f8` | **sonar: EQ-Headroom (Senkung um größten Positiv-Gain, Conf v5)** |
| `66e87c62` | `93d791ed` | test: station_volume-Richtung an `percentage()`-Fix angepasst (PR #255) |

### Bewusst NICHT eingespielt
- **Clips/window-capture + clip-editor** (~20 Commits) — großes Feature, im Fork nicht genutzt.
- **GUI-Umbau** `9a0d9d36`/`182b4ec6`/`86a1aa4e`/`31a9ca23` — Konflikt mit unserem `sonar_page.py` (Boost/Smart-Volume-Widgets), nur manueller Backport möglich.
- **Arctis-5-Support** `8d6c8cb8`, **Bluetooth** `524f5cc8`/`e3770122` (GameDAC = USB), CI/Packaging/Usage-Stats.

### Versionsnummer: `1.4.27+fork.1` (WICHTIG)
- Grund: Fork ≠ Original (fehlender Clips-Teil + eigene Patches). `1.4.26` behalten würde
  den Update-Checker dauerhaft auf v1.4.27 nagen lassen.
- **PEP 440**: Nur `+` (local version) ist gültig — `1.4.27-fork.1` bricht den Wheel-Build
  ("Invalid metadata format"). Nixos-rebuild von nex ist daran 2026-09-21 gescheitert.
- `pyproject.toml` + Metainfo tragen `1.4.27+fork.1`. Nix-Paket liest Version automatisch aus
  pyproject (`nix/package.nix`).
- Nebeneffekt: `update_checker._VER_RE` matcht `^…[a-z]*$` → `+fork.1` nicht parse-bar →
  Update-Check bricht ab → **kein Nag, keine falsche Wheel-URL vom Upstream**.
- Beim nächsten Backport: `+fork.2` usw.

### Tests
- Voll-Lauf: 2920 passed, 5 failed, 35 skipped. Die 5 Failures sind **vorbestehend** auf
  origin/main (Umgebung: live-System-Marker `audio_reconfig`, pillow-Version, `bash`-PATH) —
  keine Regression durch den Backport.
- Achtung (Test-Pollution): Kombi-Läufe mit `tests/test_video_router.py` können durch den
  Live-Marker `/run/user/<uid>/arctis_manager/audio_reconfig` (echte Session) `_confirm_manual_move`-
  Tests fehlschlagen lassen. Einzeln grün, Voll-Lauf grün.

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

---

## 4. Per-Kanal Boost & Smart Volume (Option A)

**Problem:** `sonar_boost.json` und `sonar_smart_volume.json` waren **flache** Einzelwerte
(`{"enabled": …, "db": …}` / `{"enabled": …, "level": …, "loudness": …}`), die auf **alle**
EQ-Kanäle gleichzeitig angewandt wurden. Ein Boost für den leisen Discord-Kumpel hat damit
auch Game/Media/Aux laut gemacht — unbrauchbar. Smart Volume (SC4M-Kompressor) war dadurch
global invasiv und zusätzlich mit `level: 0.0`-Default faktisch ein No-Op (Ratio 1:1 = Bypass).

**Lösung (`gui/sonar_page.py`):**

- Beide Dateien sind jetzt **per-Kanal-Dicts**: `{"game": {…}, "chat": {…}, "media": {…}, "aux": {…}}`.
- `_load_boost(channel)` / `_save_boost(channel, state)` (analog `_load_smart_volume`/`_save_smart_volume`)
  lesen/schreiben nur den jeweiligen Kanal.
- **Migration**: `_read_boost_map()` / `_read_smart_map()` erkennen eine legacy Flat-Datei
  (Top-Level-Key `enabled` + `db` bzw. `level`) und expandieren sie in-place auf alle Kanäle —
  bestehende User-Werte bleiben erhalten (kein Datenverlust).
- **Defaults geändert**: Boost `db: 3.0` (statt 0.0 — +3 dB beim Aktivieren direkt brauchbar),
  Smart Volume `level: 50.0` (statt 0.0 — Kompressor tut beim Aktivieren tatsächlich etwas).
- Widgets (`BoostVolumeWidget`, `SmartVolumeWidget`) nehmen `channel` und persistieren pro Kanal.
- Apply-Pfade laden pro Kanal: `_ApplyWorker.run()` via `self._channel`, `_ApplyAllWorker.run()`
  via `channel` in der Loop. Micro-Chain bekommt `boost_db=0.0` (kein Boost-Widget dort).
- Aux-Widgets waren vorher **nicht** mit `_on_boost_changed`/`_on_smart_changed` verbunden
  (nur game/media/chat) — jetzt sind sie es, sonst hätte Aux seine per-Kanal-Slider gespeichert
  aber nie angewandt.

**Effekt:** Chat-Boost (+X dB) setzt die Sprecher vom Spiel ab, ohne Game/Media zu verändern;
Smart Volume komprimiert nur den gewählten Kanal. `sc4m_1916.so` (swh-plugins) ist auf nex
vorhanden (`/usr/lib/ladspa/` + nix-store), Smart Volume funktioniert also wirklich.
