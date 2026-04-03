"""
CSS styles for the application with image support
"""

# Admin window styles - Modern Design
ADMIN_STYLE = """
QMainWindow {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #0f1419,
        stop:1 #1a1d2e
    );
}

QWidget {
    color: #ffffff;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
    font-weight: 600;
    background: transparent;
}

QPushButton {
    background-color: #4CAF50;
    border: none;
    color: white;
    padding: 16px 28px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 700;
    min-height: 48px;
    min-width: 140px;
}

QPushButton:hover {
    background-color: #45a049;
}

QPushButton:pressed {
    background-color: #3d8b40;
}

QPushButton:disabled {
    background-color: #3a3d4f;
    color: #6b6e7f;
}

QPushButton[class="success"] {
    background-color: #10b981;
}

QPushButton[class="success"]:hover {
    background-color: #059669;
}

QPushButton[class="danger"] {
    background-color: #ef4444;
}

QPushButton[class="danger"]:hover {
    background-color: #dc2626;
}

QPushButton[class="warning"] {
    background-color: #f59e0b;
}

QPushButton[class="warning"]:hover {
    background-color: #d97706;
}

QPushButton[class="info"] {
    background-color: #3b82f6;
}

QPushButton[class="info"]:hover {
    background-color: #2563eb;
}

QLabel {
    font-size: 15px;
    font-weight: 600;
    color: #e5e7eb;
}

QLineEdit, QTextEdit {
    background-color: #1f2937;
    border: 2px solid #374151;
    border-radius: 8px;
    padding: 12px 16px;
    color: #f3f4f6;
    font-size: 15px;
    font-weight: 500;
    min-height: 42px;
}

QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #3b82f6;
}

QComboBox {
    background-color: #1f2937;
    border: 2px solid #374151;
    border-radius: 8px;
    padding: 10px 16px;
    color: #f3f4f6;
    font-size: 15px;
    font-weight: 500;
    min-height: 42px;
}

QComboBox:hover {
    border: 2px solid #4b5563;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox QAbstractItemView {
    background-color: #1f2937;
    border: 2px solid #374151;
    color: #f3f4f6;
    font-size: 15px;
    selection-background-color: #3b82f6;
    selection-color: white;
    outline: none;
}

QDoubleSpinBox {
    background-color: #1f2937;
    border: 2px solid #374151;
    border-radius: 8px;
    padding: 10px 16px;
    color: #10b981;
    font-size: 18px;
    font-weight: 700;
    min-height: 42px;
}

QTableWidget {
    background-color: #1f2937;
    border: 2px solid #374151;
    border-radius: 10px;
    gridline-color: #374151;
    alternate-background-color: #111827;
    font-size: 14px;
    font-weight: 500;
}

QTableWidget::item {
    padding: 12px;
    border-bottom: 1px solid #374151;
    color: #e5e7eb;
}

QTableWidget::item:selected {
    background-color: #3b82f6;
    color: white;
}

QHeaderView::section {
    background-color: #111827;
    color: #9ca3af;
    padding: 14px;
    border: none;
    font-weight: 700;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 2px solid #374151;
}

QTabWidget::pane {
    border: none;
    background: transparent;
    padding: 0px;
}

QTabBar::tab {
    background-color: #1f2937;
    color: #9ca3af;
    padding: 14px 24px;
    margin-right: 4px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    font-weight: 600;
    font-size: 14px;
    border: 2px solid transparent;
}

QTabBar::tab:selected {
    background-color: #2d3748;
    color: #3b82f6;
    border: 2px solid #3b82f6;
    border-bottom: none;
}

QTabBar::tab:hover:!selected {
    background-color: #252a36;
}

QGroupBox {
    border: 2px solid #374151;
    border-radius: 16px;
    margin-top: 16px;
    font-weight: 700;
    font-size: 13px;
    color: #9ca3af;
    padding-top: 24px;
    padding-bottom: 16px;
    background-color: rgba(31, 41, 55, 0.5);
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 12px;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: 11px;
    font-weight: 700;
}

QScrollBar:vertical {
    background-color: #1f2937;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #4b5563;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #6b7280;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #1f2937;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #4b5563;
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #6b7280;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QStatusBar {
    background-color: #111827;
    color: #9ca3af;
    font-size: 13px;
    font-weight: 500;
    border-top: 1px solid #374151;
}
"""

# Display window styles - Updated for image display
DISPLAY_STYLE = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #0a0a2a, stop:1 #1a1a4a);
}

QWidget {
    background-color: transparent;
    color: #ffffff;
    font-family: "Arial Black", "Impact", sans-serif;
}

/* Main container */
.main-container {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #0a0a1a, stop:1 #1a1a3a);
    border: none;
}

/* Auction Title */
.auction-title {
    font-size: 70px !important;
    font-weight: bold;
    color: #ffcc00;
    text-shadow: 5px 5px 15px rgba(0, 0, 0, 0.8);
    letter-spacing: 3px;
}

/* University Title */
.university-title {
    font-size: 50px !important;
    font-weight: bold;
    color: #ffffff;
    text-shadow: 3px 3px 10px rgba(0, 0, 0, 0.8);
}

/* Player name - CENTER OF ATTENTION */
.player-name-label {
    font-size: 90px !important;
    font-weight: bold;
    color: #00ff88;
    text-shadow: 5px 5px 20px rgba(0, 255, 136, 0.5);
    letter-spacing: 2px;
    margin: 20px 0;
}

/* Player image - CENTER OF SCREEN */
.player-image-center {
    border: 10px solid #00ff88;
    border-radius: 20px;
    background-color: rgba(0, 255, 136, 0.1);
    min-height: 600px;
    min-width: 600px;
    font-size: 60px;
    font-weight: bold;
    color: #ffffff;
}

/* Info containers */
.info-container {
    background-color: rgba(40, 40, 80, 0.7);
    border-radius: 15px;
    border: 4px solid #555588;
    padding: 20px;
    margin: 10px 0;
}

/* Faculty label */
.faculty-label {
    font-size: 45px !important;
    font-weight: bold;
    color: #ffcc00;
}

/* Player role label */
.player-role-label {
    font-size: 45px !important;
    font-weight: bold;
    color: #3366ff;
}

/* Batting label */
.batting-label {
    font-size: 40px !important;
    font-weight: bold;
    color: #ff9900;
}

/* Bowling label */
.bowling-label {
    font-size: 40px !important;
    font-weight: bold;
    color: #ff66ff;
}

/* Current bid - EXTRA LARGE */
.current-bid-container {
    background-color: rgba(255, 68, 68, 0.2);
    border-radius: 25px;
    border: 8px solid #ff4444;
    padding: 30px;
}

.current-bid-value {
    font-size: 120px !important;
    font-weight: bold;
    color: #ff4444;
    text-shadow: 0 0 50px #ff4444;
}

/* Base price */
.price-container {
    background-color: rgba(30, 30, 60, 0.8);
    border-radius: 20px;
    border: 6px solid #444488;
    padding: 25px;
}

.base-price-value {
    font-size: 70px !important;
    font-weight: bold;
    color: #ffffff;
    text-shadow: 0 0 20px #ffffff;
}

/* Status */
.status-label {
    font-size: 80px !important;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 10px;
    padding: 30px;
    border-radius: 20px;
    margin: 20px 0;
}

.status-auction {
    color: #ff4444 !important;
    background-color: rgba(255, 68, 68, 0.15);
    border: 8px solid #ff4444;
}

.status-sold {
    color: #00ff88 !important;
    background-color: rgba(0, 255, 136, 0.15);
    border: 8px solid #00ff88;
}

.status-unsold {
    color: #ff9900 !important;
    background-color: rgba(255, 153, 0, 0.15);
    border: 8px solid #ff9900;
}

.status-upcoming {
    color: #3366ff !important;
    background-color: rgba(51, 102, 255, 0.15);
    border: 8px solid #3366ff;
}

/* Countdown timer */
.countdown-container {
    background-color: rgba(0, 0, 0, 0.85);
    border-radius: 25px;
    border: 8px solid #ff9900;
    padding: 30px;
}

.countdown-label {
    font-size: 100px !important;
    font-weight: bold;
    color: #ffffff;
    text-shadow: 0 0 40px #ff9900;
}

/* Team info */
.team-info-container {
    background-color: rgba(40, 40, 80, 0.8);
    border-radius: 20px;
    border: 6px solid #3366ff;
    padding: 20px;
}

.sold-container {
    background-color: rgba(40, 40, 80, 0.9);
    border-radius: 20px;
    border: 8px solid #00ff88;
    padding: 25px;
}

/* Team name */
.team-name-label {
    font-size: 60px !important;
    font-weight: bold;
    color: #3366ff;
}

/* Sold price */
.sold-price-label {
    font-size: 80px !important;
    font-weight: bold;
    color: #00ff88;
    text-shadow: 0 0 35px #00ff88;
}

/* Info labels */
.info-label {
    font-size: 40px !important;
    color: #cccccc;
    font-weight: bold;
    letter-spacing: 3px;
}

/* Team logo */
.team-logo {
    border: 6px solid #3366ff;
    border-radius: 15px;
    background-color: rgba(51, 102, 255, 0.1);
    padding: 15px;
    font-size: 30px;
    font-weight: bold;
    color: #ffffff;
}"""