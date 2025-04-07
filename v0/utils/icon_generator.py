from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QBrush, QPen
from PyQt6.QtCore import Qt, QSize, QRect
import os

class IconGenerator:
    """Generates icons for the application."""
    
    def __init__(self):
        self.icons_dir = "resources/assets/icons"
        self._ensure_icons_dir()
    
    def _ensure_icons_dir(self):
        """Ensure the icons directory exists."""
        os.makedirs(self.icons_dir, exist_ok=True)
    
    def generate_app_icon(self, output_path=None):
        """Generate the application icon."""
        if not output_path:
            output_path = os.path.join(self.icons_dir, "app_icon.png")
        
        # Create a pixmap
        pixmap = QPixmap(512, 512)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Create a painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw a circle
        painter.setBrush(QBrush(QColor("#FF69B4")))  # Pink
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(56, 56, 400, 400)
        
        # Draw a letter
        painter.setPen(QPen(QColor("#FFFFFF")))  # White
        font = QFont("Arial", 250, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(QRect(56, 56, 400, 400), Qt.AlignmentFlag.AlignCenter, "G")
        
        # End painting
        painter.end()
        
        # Save the pixmap
        pixmap.save(output_path)
        
        return output_path
    
    def generate_user_icon(self, output_path=None):
        """Generate a user icon."""
        if not output_path:
            output_path = os.path.join(self.icons_dir, "user_icon.png")
        
        # Create a pixmap
        pixmap = QPixmap(128, 128)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Create a painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw a circle for the head
        painter.setBrush(QBrush(QColor("#CCCCCC")))  # Gray
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(44, 24, 40, 40)
        
        # Draw a body
        painter.setBrush(QBrush(QColor("#CCCCCC")))  # Gray
        painter.drawEllipse(34, 64, 60, 60)
        
        # End painting
        painter.end()
        
        # Save the pixmap
        pixmap.save(output_path)
        
        return output_path
    
    def generate_all_icons(self):
        """Generate all icons for the application."""
        icons = {
            "app_icon.png": self.generate_app_icon,
            "user_icon.png": self.generate_user_icon,
            # Add more icons as needed
        }
        
        generated_icons = {}
        
        for icon_name, generator_func in icons.items():
            output_path = os.path.join(self.icons_dir, icon_name)
            generated_icons[icon_name] = generator_func(output_path)
        
        return generated_icons

