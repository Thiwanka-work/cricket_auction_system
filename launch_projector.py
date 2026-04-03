# launch_projector.py
import sys
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    
    # List available screens
    screens = QApplication.screens()
    print("=" * 60)
    print("AVAILABLE SCREENS:")
    for i, screen in enumerate(screens):
        geom = screen.geometry()
        print(f"[{i}] {screen.name()}: {geom.width()}x{geom.height()} at ({geom.x()}, {geom.y()})")
    print("=" * 60)
    
    # Default to projector mode on second screen
    mode = 'projector'
    screen_index = 1 if len(screens) > 1 else 0
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'preview':
            mode = 'preview'
            screen_index = 0
        elif sys.argv[1] == 'projector':
            mode = 'projector'
            if len(sys.argv) > 2:
                try:
                    screen_index = int(sys.argv[2])
                    if screen_index >= len(screens):
                        screen_index = 1 if len(screens) > 1 else 0
                except:
                    pass
    
    # Import here to avoid import issues
    from display_window import DisplayWindow
    
    # Create window on selected screen
    selected_screen = screens[screen_index]
    print(f"\nCreating {mode} window on screen [{screen_index}]: {selected_screen.name()}")
    
    window = DisplayWindow(mode=mode, screen=selected_screen)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()