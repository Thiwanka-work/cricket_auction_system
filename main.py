"""
Main application entry point
"""

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# Enable High DPI support with PassThrough policy for native scaling
# MUST be set before QApplication is created
QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

class AuctionApp:
    """Main application controller"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.admin_window = None
        self.display_window = None
        
        # Check and setup required directories
        self.setup_directories()
    
    def setup_directories(self):
        """Setup required directories"""
        directories = ["database", "images", "images/players", "images/teams"]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def run(self):
        """Run the application"""
        from admin_window import AdminWindow
        from display_window import DisplayWindow
        
        # Create admin window
        self.admin_window = AdminWindow()
        
        # Get available screens
        screens = self.app.screens()
        
        # Create display window
        if len(screens) > 1:
            # Use second screen for display
            self.display_window = DisplayWindow(screens[1])
        else:
            # Use primary screen (will be full screen)
            self.display_window = DisplayWindow()
        
        # Show windows
        self.admin_window.show()
        self.display_window.show()
        
        # Connect admin signals to display updates
        self.admin_window.data_updated.connect(self.display_window.update_display)
        
        print("\n" + "="*70)
        print("TPL AUCTION - UNIVERSITY OF VAVUNIYA")
        print("="*70)
        print("\nCurrency: LKR (Sri Lankan Rupees) only")
        print("Image Support: Upload player images and team logos")
        print("Player Display: Image in center, big text details")
        print("Bid History: Shows only sold prices (winning bids)")
        print("\nADMIN CONTROLS:")
        print("  • ADD PLAYER: Upload image, set player types")
        print("  • ADD TEAM: Upload logo, set budget")
        print("  • BID HISTORY: Shows only winning bids")
        print("  • DISPLAY: Player image in center of screen")
        print("\nDISPLAY SCREEN:")
        print("  • Player image large in center")
        print("  • Leading team shown during bidding")
        print("  • Team logo shown when player sold")
        print("  • ESC: Exit full screen, F11: Toggle, F5: Refresh")
        print("\nQUICK START:")
        print("  1. Add players with images and player types")
        print("  2. Add teams with logos")
        print("  3. Start auction")
        print("  4. Next player → Place bids → Mark sold/unsold")
        print("  5. Check bid history for sold prices only")
        print("\n" + "="*70)
        
        # Start application
        return self.app.exec_()

def main():
    """Main entry point"""
    print("Starting TPL Auction - University of Vavuniya...")
    print("Setting up image directories...")
    
    # Check for database
    if not os.path.exists("database/auction.db"):
        print("Database not found. Creating new database...")
        from create_database import create_database
        create_database()
    
    app = AuctionApp()
    sys.exit(app.run())

if __name__ == "__main__":
    main()