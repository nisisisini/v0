# utils/theme_manager.py
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

class ThemeManager:
    def __init__(self, settings):
        self.settings = settings
        self.themes = {
            "light": {
                "primary": "#FF69B4",  # Pink
                "secondary": "#FFFFFF",  # White
                "background": "#F5F5F5",
                "text": "#333333",
                "accent": "#FF1493"  # Deep Pink
            },
            "dark": {
                "primary": "#9370DB",  # Medium Purple
                "secondary": "#333333",  # Dark Gray
                "background": "#1E1E1E",
                "text": "#FFFFFF",
                "accent": "#FF00FF"  # Magenta
            }
        }
    
    def get_current_theme(self):
        theme_name = self.settings.get_setting("theme", "light")
        return self.themes[theme_name]
    
    def set_theme(self, theme_name, force_refresh=False):
        if theme_name in self.themes:
            self.settings.set_setting("theme", theme_name)
            self.apply_theme()
            if force_refresh:
                from PyQt6.QtWidgets import QApplication
                app = QApplication.instance()
                if app:
                    app.processEvents()  # Force immediate UI update
    
    def apply_theme(self):
        from PyQt6.QtWidgets import QApplication
        
        theme = self.get_current_theme()
        app = QApplication.instance()
        
        if not app:
            return
        
        palette = QPalette()
        
        # Set window background
        palette.setColor(QPalette.ColorRole.Window, QColor(theme["background"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(theme["text"]))
        
        # Set base colors (for input fields, etc.)
        palette.setColor(QPalette.ColorRole.Base, QColor(theme["secondary"]))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme["background"]))
        
        # Set text colors
        palette.setColor(QPalette.ColorRole.Text, QColor(theme["text"]))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(theme["accent"]))
        
        # Set button colors
        palette.setColor(QPalette.ColorRole.Button, QColor(theme["primary"]))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme["secondary"]))
        
        # Set highlight colors
        palette.setColor(QPalette.ColorRole.Highlight, QColor(theme["accent"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(theme["secondary"]))
        
        # Set link colors
        palette.setColor(QPalette.ColorRole.Link, QColor(theme["accent"]))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(theme["primary"]))
        
        # Apply the palette
        app.setPalette(palette)
        
        # Apply stylesheet for additional styling
        self._apply_stylesheet(theme)
    
    def _apply_stylesheet(self, theme):
        from PyQt6.QtWidgets import QApplication
        
        app = QApplication.instance()
        
        if not app:
            return
        
        # Create a stylesheet with the theme colors
        stylesheet = f"""
        QMainWindow, QDialog {{
            background-color: {theme["background"]};
            color: {theme["text"]};
        }}
        
        QPushButton {{
            background-color: {theme["primary"]};
            color: {theme["secondary"]};
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }}
        
        QPushButton:hover {{
            background-color: {theme["accent"]};
        }}
        
        QPushButton:pressed {{
            background-color: {theme["primary"]};
        }}
        
        QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateEdit, QTimeEdit {{
            background-color: {theme["secondary"]};
            color: {theme["text"]};
            border: 1px solid {theme["primary"]};
            border-radius: 4px;
            padding: 4px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus, QTimeEdit:focus {{
            border: 2px solid {theme["accent"]};
        }}
        
        QTableWidget {{
            background-color: {theme["secondary"]};
            color: {theme["text"]};
            gridline-color: {theme["primary"]};
            selection-background-color: {theme["accent"]};
            selection-color: {theme["secondary"]};
        }}
        
        QHeaderView::section {{
            background-color: {theme["primary"]};
            color: {theme["secondary"]};
            padding: 4px;
            border: 1px solid {theme["secondary"]};
        }}
        
        QCalendarWidget QToolButton {{
            background-color: {theme["primary"]};
            color: {theme["secondary"]};
        }}
        
        QCalendarWidget QMenu {{
            background-color: {theme["secondary"]};
            color: {theme["text"]};
        }}
        
        QCalendarWidget QSpinBox {{
            background-color: {theme["secondary"]};
            color: {theme["text"]};
        }}
        
        QCalendarWidget QAbstractItemView:enabled {{
            background-color: {theme["secondary"]};
            color: {theme["text"]};
        }}
        
        QCalendarWidget QAbstractItemView:disabled {{
            color: gray;
        }}
        
        QTabWidget::pane {{
            border: 1px solid {theme["primary"]};
            background-color: {theme["background"]};
        }}
        
        QTabBar::tab {{
            background-color: {theme["background"]};
            color: {theme["text"]};
            border: 1px solid {theme["primary"]};
            padding: 6px 12px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {theme["primary"]};
            color: {theme["secondary"]};
        }}
        
        QTabBar::tab:hover {{
            background-color: {theme["accent"]};
            color: {theme["secondary"]};
        }}
        
        QGroupBox {{
            border: 1px solid {theme["primary"]};
            border-radius: 4px;
            margin-top: 8px;
            font-weight: bold;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 5px;
            color: {theme["text"]};
        }}
        """
        
        app.setStyleSheet(stylesheet)
