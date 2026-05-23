from PySide6.QtCore import QObject, QPropertyAnimation
from PySide6.QtWidgets import QWidget, QLayout, QHBoxLayout, QVBoxLayout, QFrame


def apply_all_wrappers():
    set_property = QObject.setProperty
    set_contents_margins = QLayout.setContentsMargins
    set_duration = QPropertyAnimation.setDuration
    set_geometry = QWidget.setGeometry

    def _wrapped_set_property(self, name, value):
        return set_property(self, name, value)

    def _wrapped_set_contents_margins(self, left, top, right, bottom):
        return set_contents_margins(self, left, top, right, bottom)

    def _wrapped_set_duration(self, duration):
        return set_duration(self, duration)

    def _wrapped_set_geometry(self, x, y, width, height):
        return set_geometry(self, x, y, width, height)

    QObject.set_property = _wrapped_set_property
    QObject.setProperty = _wrapped_set_property

    QHBoxLayout.set_contents_margins = _wrapped_set_contents_margins
    QHBoxLayout.setContentsMargins = _wrapped_set_contents_margins

    QVBoxLayout.set_contents_margins = _wrapped_set_contents_margins
    QVBoxLayout.setContentsMargins = _wrapped_set_contents_margins

    QPropertyAnimation.set_duration = _wrapped_set_duration
    QPropertyAnimation.setDuration = _wrapped_set_duration

    QFrame.set_geometry = _wrapped_set_geometry
    QFrame.setGeometry = _wrapped_set_geometry

    QWidget.set_geometry = _wrapped_set_geometry
    QWidget.setGeometry = _wrapped_set_geometry