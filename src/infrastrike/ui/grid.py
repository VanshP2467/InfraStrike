from __future__ import annotations

from dataclasses import dataclass
import pygame


@dataclass(frozen=True)
class GridSpec:
    rect: pygame.Rect
    rows: int = 4
    cols: int = 4


def cell_rects(spec: GridSpec) -> list[list[pygame.Rect]]:
    """
    Return a rows×cols 2D list of pygame.Rects for each cell in the grid region.
    """
    rect = spec.rect
    rows, cols = spec.rows, spec.cols

    cell_w = rect.width / cols
    cell_h = rect.height / rows

    out: list[list[pygame.Rect]] = []
    for r in range(rows):
        row: list[pygame.Rect] = []
        for c in range(cols):
            # Use fractional boundaries but convert to ints in a way that tiles perfectly
            left = rect.left + int(c * cell_w)
            top = rect.top + int(r * cell_h)
            right = rect.left + int((c + 1) * cell_w)
            bottom = rect.top + int((r + 1) * cell_h)
            row.append(pygame.Rect(left, top, right - left, bottom - top))
        out.append(row)
    return out


def cell_at_point(spec: GridSpec, x: int, y: int) -> tuple[int, int] | None:
    """
    Convert a display-space point (x,y) into a (row,col) cell index, or None if outside.
    """
    rect = spec.rect
    if not rect.collidepoint(x, y):
        return None

    rel_x = x - rect.left
    rel_y = y - rect.top

    col = int(rel_x * spec.cols / rect.width)
    row = int(rel_y * spec.rows / rect.height)

    # Safety clamp (important when x==rect.right or y==rect.bottom)
    col = max(0, min(spec.cols - 1, col))
    row = max(0, min(spec.rows - 1, row))
    return (row, col)
