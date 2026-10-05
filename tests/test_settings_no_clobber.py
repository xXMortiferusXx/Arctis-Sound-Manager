# Copyright (C) 2026 loteran
# SPDX-License-Identifier: GPL-3.0-or-later

"""A settings write must only persist what was changed.

``general_settings.yaml`` has more than one writer: the daemon loads it once at
startup and keeps that snapshot for its whole runtime, and the GUI keeps its own
copy. ``write_to_file`` used to dump the whole in-memory object, so a change
made by one process could silently resurrect a stale, unrelated value the other
process had since fixed on disk. That is the config-drift path that turned a
GameDAC mic into the onboard analog input and then killed the mic chain when the
Output device was changed.
"""
from unittest.mock import patch

from arctis_sound_manager.settings import GeneralSettings


def _write(tmp_path, text):
    (tmp_path / "general_settings.yaml").write_text(text)


def test_write_only_persists_changed_fields(tmp_path):
    with patch("arctis_sound_manager.settings.SETTINGS_FOLDER", tmp_path):
        _write(tmp_path,
               "micro_input_source: alsa_input.onboard\n"
               "external_output_device: HDMI\n")
        gui = GeneralSettings.read_from_file()

        # Another process (the daemon) fixes the mic back to the headset.
        daemon = GeneralSettings.read_from_file()
        daemon.micro_input_source = "Arctis_GameDAC"
        daemon.write_to_file()

        # The GUI, on its stale snapshot, changes only the theme.
        gui.theme = "nord"
        gui.write_to_file()

        on_disk = GeneralSettings.read_from_file()
        assert on_disk.theme == "nord"
        # The stale "onboard" must not have been resurrected by the theme write.
        assert on_disk.micro_input_source == "Arctis_GameDAC"
        assert on_disk.external_output_device == "HDMI"


def test_rewriting_the_same_value_is_not_a_change(tmp_path):
    with patch("arctis_sound_manager.settings.SETTINGS_FOLDER", tmp_path):
        _write(tmp_path, "micro_input_source: alsa_input.onboard\n")
        left = GeneralSettings.read_from_file()

        right = GeneralSettings.read_from_file()
        right.micro_input_source = "Arctis_GameDAC"
        right.write_to_file()

        # Assigning the value it already had must not count as an edit, so the
        # newer on-disk value survives.
        left.micro_input_source = "alsa_input.onboard"
        left.theme = "steel"
        left.write_to_file()

        on_disk = GeneralSettings.read_from_file()
        assert on_disk.micro_input_source == "Arctis_GameDAC"
        assert on_disk.theme == "steel"


def test_first_write_still_persists_defaults(tmp_path):
    with patch("arctis_sound_manager.settings.SETTINGS_FOLDER", tmp_path):
        gs = GeneralSettings(redirect_audio_on_connect=False)
        gs.write_to_file()

        on_disk = GeneralSettings.read_from_file()
        assert on_disk.redirect_audio_on_connect is False


def test_unknown_keys_are_still_ignored(tmp_path):
    with patch("arctis_sound_manager.settings.SETTINGS_FOLDER", tmp_path):
        gs = GeneralSettings(redirect_audio_on_connect=True)
        gs.not_a_real_setting = "nope"
        gs.write_to_file()

        on_disk = GeneralSettings.read_from_file()
        assert on_disk.redirect_audio_on_connect is True
        assert not hasattr(on_disk, "not_a_real_setting")
