"""Tests for UI theme/font loading helpers."""

from __future__ import annotations

import pygame

from infrastrike.path_utils import asset_path
from infrastrike.ui import theme


class TestThemeFontLoading:
    def setup_method(self):
        pygame.font.init()

    def teardown_method(self):
        pygame.font.quit()

    def test_embedded_pixel_font_file_exists(self):
        assert asset_path(*theme.PIXEL_FONT_FILE).exists()

    def test_load_pixel_font_falls_back_if_asset_lookup_fails(self, monkeypatch):
        def _raise(*_args, **_kwargs):
            raise RuntimeError("asset lookup failure")

        monkeypatch.setattr(theme, "asset_path", _raise)
        font = theme.load_pixel_font(18, bold=True)
        assert isinstance(font, pygame.font.Font)
