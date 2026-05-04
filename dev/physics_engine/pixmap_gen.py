import math
from datetime import time, datetime
import cv2

from scipy.ndimage import zoom
from numba import njit, prange

import numpy as np
from PySide6.QtCore import QSize
from PySide6.QtGui import QImage, QPixmap, QPainter, qRgba, Qt, QPen, QColor


class PixmapGen:
    @staticmethod
    @njit(parallel=True, fastmath=True)
    def _apply_heatmap_color_map(data: np.ndarray, base_index: int):
        w, h = data.shape
        rgba = np.empty((h, w, 4), dtype=np.uint8)

        for x in prange(w):
            for y in range(h):
                value = data[x, y]
                f = value / 255.0
                r = int(255 * max(0, min(1, 1.5 - abs(1 - 4 * (f - 0.5)))))
                g = int(255 * max(0, min(1, 1.5 - abs(1 - 4 * (f - 0.25)))))
                b = int(255 * max(0, min(1, 1.5 - abs(1 - 4 * f))))

                if value == 0:
                    a = 0
                else:
                    difference = abs(value - base_index)
                    a = min(difference**2, 255)

                rgba[y, x, 0] = r
                rgba[y, x, 1] = g
                rgba[y, x, 2] = b
                rgba[y, x, 3] = a

        return rgba

    @staticmethod
    def generate_heatmap(data: np.ndarray, target_height: int = 1080, target_width: int = 1920) -> QPixmap:
        macro_velocity_x, macro_velocity_y, macro_density, binary_mask = np.unstack(data, axis=-1)
        speeds = np.sqrt(macro_velocity_x**2 + macro_velocity_y**2)

        high_res_speeds = cv2.resize(speeds, (target_height, target_width), interpolation=cv2.INTER_LINEAR)

        if binary_mask is not None:
            high_res_mask = cv2.resize(binary_mask, (target_height, target_width),
                                       interpolation=cv2.INTER_LINEAR).astype(bool)
            high_res_speeds[high_res_mask] = 0

        unaffected = speeds.shape[1] // 2
        base_speed = speeds[0, unaffected]

        max_speed = np.max(high_res_speeds)
        if max_speed == 0:
            max_speed = 1

        base_index = int((base_speed / max_speed) * 255)
        normalized_speeds = np.clip((high_res_speeds / max_speed) * 255, 0, 255).astype(np.uint8)

        rgba_data = PixmapGen._apply_heatmap_color_map(normalized_speeds, base_index)

        im_height, im_width, _ = rgba_data.shape
        temp_image = QImage(rgba_data.data, im_width, im_height, im_width * 4, QImage.Format.Format_RGBA8888)
        heatmap_pixmap = QPixmap.fromImage(temp_image.copy())
        return heatmap_pixmap

    @staticmethod
    def generate_density(data: np.ndarray, target_height: int = 1080, target_width: int = 1920) -> QPixmap:
        _, _, macro_density, binary_mask = np.unstack(data, axis=-1)

        high_res_density = cv2.resize(macro_density, (target_height, target_width),
                                      interpolation=cv2.INTER_LINEAR)

        unaffected = macro_density.shape[1] // 2
        base_density = macro_density[0, unaffected]

        if binary_mask is not None:
            high_res_mask = cv2.resize(binary_mask, (target_height, target_width),
                                       interpolation=cv2.INTER_LINEAR).astype(bool)
            high_res_density[high_res_mask] = base_density

        density_difference = high_res_density - base_density
        max_difference = np.max(np.abs(density_difference))

        if max_difference == 0:
            max_difference = 1

        normalized_densities = np.clip(((density_difference / max_difference) * 127) + 127,
                                       0, 255).astype(np.uint8)
        image_data = np.ascontiguousarray(normalized_densities.T)
        height, width = image_data.shape

        temp_image = QImage(image_data.data, width, height, width, QImage.Format.Format_Indexed8)

        color_table = []
        base_index = 127
        for i in range(256):
            difference = abs(i - base_index)
            strength = difference / 127

            gray = int(255 * strength)
            alpha = int(np.clip(difference ** 2, 0, 255))
            color_table.append(qRgba(gray, gray, gray, alpha))

        temp_image.setColorTable(color_table)
        stream_pixmap = QPixmap.fromImage(temp_image.copy())

        return stream_pixmap

    @staticmethod
    def generate_curl(data: np.ndarray, target_height: int = 1080, target_width: int = 1920) -> QPixmap:
        ux, uy, _, binary_mask = np.unstack(data, axis=-1)

        # curl = d(uy)/dx - d(ux)/dy
        curls = (np.roll(uy, -1, axis=0) - np.roll(uy, 1, axis=0) -
                 np.roll(ux, -1, axis=1) + np.roll(ux, 1, axis=1))

        high_res_curls = cv2.resize(curls, (target_height, target_width), interpolation=cv2.INTER_LINEAR)

        if binary_mask is not None:
            high_res_mask = cv2.resize(binary_mask, (target_height, target_width),
                                       interpolation=cv2.INTER_LINEAR).astype(bool)
            high_res_curls[high_res_mask] = 0

        max_curl = np.max(np.abs(high_res_curls))

        if max_curl == 0:
            max_curl = 1

        normalized_curls = np.clip(((high_res_curls / max_curl) * 127) + 127, 0, 255).astype(np.uint8)

        image_data = np.ascontiguousarray(normalized_curls.T)
        height, width = image_data.shape

        temp_image = QImage(image_data.data, width, height, width, QImage.Format.Format_Indexed8)

        color_table = []
        base_index = 127
        for i in range(256):
            difference = abs(i - base_index)
            strength = difference / 127

            gray = int(255 * strength)
            alpha = int(np.clip(difference ** 2, 0, 255))

            color_table.append(qRgba(gray, gray, gray, alpha))

        temp_image.setColorTable(color_table)
        curl_pixmap = QPixmap.fromImage(temp_image.copy())

        return curl_pixmap

    @staticmethod
    def generate_stream(data: np.ndarray, target_height: int = 1080, target_width: int = 1920) -> QPixmap:
        velocity_x, velocity_y, macro_density, binary_mask = np.unstack(data, axis=-1)

        width_grid = velocity_x.shape[0]
        height_grid = velocity_y.shape[1]

        final_pixmap = QPixmap(target_width, target_height)
        final_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(final_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor(230, 230, 230, 150))
        pen.setWidth(2)
        painter.setPen(pen)

        spacing_y = 30  # la distance entre les lignes
        max_steps = 1920  # resolution max
        step_size = 3.0

        scale_x = target_width / width_grid
        scale_y = target_height / height_grid

        for start_y in range(spacing_y // 2, height_grid, spacing_y):
            x = 0.0
            y = float(start_y)

            last_x = None
            last_y = None

            for _ in range(max_steps):
                if not np.isfinite(x) or not np.isfinite(y):
                    break

                rounded_x = int(round(x))
                rounded_y = int(round(y))

                if rounded_x < 0 or rounded_x >= width_grid:
                    break

                if rounded_y < 0 or rounded_y >= height_grid:
                    break

                if binary_mask[rounded_x, rounded_y]:
                    break

                vx = velocity_x[rounded_x, rounded_y]
                vy = velocity_y[rounded_x, rounded_y]
                speed = math.sqrt(vx ** 2 + vy ** 2)

                screen_x = int(scale_x * x)
                screen_y = int(scale_y * y)

                if last_x is not None and last_y is not None:
                    painter.drawLine(last_x, last_y, screen_x, screen_y)

                last_x = rounded_x
                last_y = rounded_y

                x += (vx / speed) * step_size
                y += (vy / speed) * step_size

        painter.end()

        return final_pixmap