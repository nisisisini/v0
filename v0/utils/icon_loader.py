import os

ICON_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icons')

def load_icon(icon_name):
    """
    Load an icon by its name from the icons directory.
    
    Args:
        icon_name (str): The name of the icon file (e.g., 'add.png').
    
    Returns:
        str: The full path to the icon file if it exists.
    
    Raises:
        FileNotFoundError: If the icon does not exist.
    """
    icon_file = os.path.join(ICON_PATH, icon_name)
    if not os.path.exists(icon_file):
        raise FileNotFoundError(f"Icon '{icon_name}' not found in {ICON_PATH}")
    return icon_file

# Example usage
if __name__ == "__main__":
    try:
        print(load_icon("add.png"))  # Example: Load 'add.png'
    except FileNotFoundError as e:
        print(e)
