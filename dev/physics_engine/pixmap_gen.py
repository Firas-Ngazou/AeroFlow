import math

import numpy as np
from PySide6.QtCore import QSize
from PySide6.QtGui import QImage, QPixmap, QPainter, qRgba, Qt, QPen, QColor

from dev.physics_engine import vector_obstacle
from dev.physics_engine.lattice_grid import LatticeGrid
from dev.physics_engine.vector_obstacle import VectorObstacle


class PixmapGen:
    @staticmethod
    def generate_heatmap(grid: LatticeGrid, obstacle: VectorObstacle) -> QPixmap:
        speeds = np.sqrt(grid.macro_velocity_x ** 2 + grid.macro_velocity_y ** 2)

        unaffected = speeds.shape[1] // 2
        base_speed = speeds[0, unaffected]

        if obstacle.binary_mask is not None:
            speeds[obstacle.binary_mask] = 0

        max_speed = np.max(speeds)
        if max_speed == 0:
            max_speed = 1

        base_index = int((base_speed / max_speed) * 255)
        normalized_speeds = np.clip((speeds / max_speed) * 255, 0, 255).astype(np.uint8)

        image_data = np.ascontiguousarray(normalized_speeds.T)
        im_height, im_width = image_data.shape
        bytes_per_line = im_width

        temp_image = QImage(image_data.data, im_width, im_height, bytes_per_line, QImage.Format.Format_Indexed8)

        color_table = []
        for i in range(256):
            f = i / 255.0
            r = int(255 * max(0, min(1, 1.5 - abs(1 - 4 * (f - 0.5)))))
            g = int(255 * max(0, min(1, 1.5 - abs(1 - 4 * (f - 0.25)))))
            b = int(255 * max(0, min(1, 1.5 - abs(1 - 4 * f))))

            if i == 0:
                alpha = 0

            else:
                difference = abs(i - base_index)
                alpha = int(np.clip(difference * difference, 0, 255))

            color_table.append(qRgba(r, g, b, alpha))

        temp_image.setColorTable(color_table)
        heatmap_pixmap = QPixmap.fromImage(temp_image.copy())

        width, height = obstacle.binary_mask.shape

        final_pixmap = QPixmap(width, height)
        final_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(final_pixmap)
        painter.drawPixmap(0, 0, heatmap_pixmap)

        painter.end()

        return final_pixmap

    @staticmethod
    def generate_density(grid: LatticeGrid, obstacle: VectorObstacle) -> QPixmap:
        densities = np.copy(grid.macro_density)

        unaffected = densities.shape[1] // 2
        base_density = densities[0, unaffected]

        if obstacle.binary_mask is not None:
            densities[obstacle.binary_mask] = base_density

        density_difference = densities - base_density
        max_difference = np.max(np.abs(density_difference))

        if max_difference == 0:
            max_difference = 1

        normalized_densities = np.clip(((density_difference / max_difference) * 127) + 127, 0, 255).astype(np.uint8)
        image_data = np.ascontiguousarray(normalized_densities.T)
        height, width = image_data.shape
        bytes_per_line = width

        temp_image = QImage(image_data.data, width, height, bytes_per_line, QImage.Format.Format_Indexed8)

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

        final_pixmap = QPixmap(QSize(width, height))
        final_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(final_pixmap)
        painter.drawPixmap(final_pixmap.rect(), stream_pixmap)
        painter.end()

        return final_pixmap

    @staticmethod
    def generate_curl(grid: LatticeGrid, obstacle: VectorObstacle) -> QPixmap:
        ux = grid.macro_velocity_x
        uy = grid.macro_velocity_y

        # curl = d(uy)/dx - d(ux)/dy
        curls = (np.roll(uy, -1, axis=0) - np.roll(uy, 1, axis=0) -
                 np.roll(ux, -1, axis=1) + np.roll(ux, 1, axis=1))

        if obstacle.binary_mask is not None:
            curls[obstacle.binary_mask] = 0

        max_curl = np.max(np.abs(curls))

        if max_curl == 0:
            max_curl = 1

        normalized_curls = np.clip(((curls / max_curl) * 127) + 127, 0, 255).astype(np.uint8)

        image_data = np.ascontiguousarray(normalized_curls.T)
        height, width = image_data.shape
        bytes_per_line = width

        temp_image = QImage(image_data.data, width, height, bytes_per_line, QImage.Format.Format_Indexed8)

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

        final_pixmap = QPixmap(QSize(width, height))
        final_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(final_pixmap)
        painter.drawPixmap(final_pixmap.rect(), curl_pixmap)
        painter.end()

        return final_pixmap

    @staticmethod
    def generate_stream(grid: LatticeGrid, obstacle: VectorObstacle) -> QPixmap:
        velocity_x = grid.macro_velocity_x
        velocity_y = grid.macro_velocity_y

        width_grid = velocity_x.shape[0]
        height_grid = velocity_y.shape[1]

        width, height = obstacle.binary_mask.shape

        final_pixmap = QPixmap(width, height)
        final_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(final_pixmap)

        pen = QPen(QColor(230, 230, 230, 150))
        pen.setWidth(2)
        painter.setPen(pen)

        spacing_y = 30  # la distance entre les lignes
        max_steps = 1920  # resolution max
        step_size = 3.0

        scale_x = width / width_grid
        scale_y = height / height_grid

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

                if obstacle.binary_mask[rounded_x, rounded_y]:
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