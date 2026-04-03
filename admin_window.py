"""
Admin control window with image upload support
"""
import sys
import os
import shutil
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from database import db
import styles

class AdminWindow(QMainWindow):
    """Main admin control window with all features"""
    
    data_updated = pyqtSignal()  # Signal to notify display window
    
    def __init__(self):
        super().__init__()
        self.display_window = None
        self.leading_team = None
        self.pass_count = 0
        self.team_buttons = {}
        self.setup_ui()
        self.setup_window_position()
        self.load_data()

    def show_message(self, kind, title, text, buttons=QMessageBox.Ok):
        """Show a topmost, application-modal message box and return the dialog result."""
        dlg = QMessageBox(self)
        if kind == 'info':
            dlg.setIcon(QMessageBox.Information)
        elif kind == 'warning':
            dlg.setIcon(QMessageBox.Warning)
        elif kind == 'critical':
            dlg.setIcon(QMessageBox.Critical)
        elif kind == 'question':
            dlg.setIcon(QMessageBox.Question)
        dlg.setWindowTitle(title)
        dlg.setText(text)
        dlg.setStandardButtons(buttons)
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.setWindowFlags(dlg.windowFlags() | Qt.WindowStaysOnTopHint)
        return dlg.exec_()
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Cricket Player Auction System - Admin Control")
        self.setGeometry(100, 100, 1200, 750)
        self.setMinimumSize(950, 600)
        self.setStyleSheet(styles.ADMIN_STYLE)
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabBar::tab {
                height: 35px;
                font-size: 13px;
                font-weight: bold;
                padding: 5px 15px;
            }
        """)
        main_layout.addWidget(tabs)
        
        # Add tabs
        tabs.addTab(self.create_auction_tab(), "🎯 AUCTION")
        tabs.addTab(self.create_players_tab(), "👤 PLAYERS")
        tabs.addTab(self.create_teams_tab(), "🏆 TEAMS")
        tabs.addTab(self.create_bids_tab(), "💰 BIDS HISTORY")
        tabs.addTab(self.create_summary_tab(), "📊 SUMMARY")
        
        # Status bar with buttons
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add buttons to status bar
        teams_summary_btn = QPushButton("📊 Teams Summary")
        teams_summary_btn.clicked.connect(self.open_teams_summary_window)
        teams_summary_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                padding: 5px 15px;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        self.status_bar.addPermanentWidget(teams_summary_btn)
        
        close_btn = QPushButton("❌ Close")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                border: none;
                padding: 5px 15px;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        self.status_bar.addPermanentWidget(close_btn)
        
        self.status_bar.showMessage("Ready")
    
    def setup_window_position(self):
        """Position admin window on primary screen"""
        try:
            screens = QApplication.screens()
            if screens:
                primary = screens[0]
                screen_geom = primary.geometry()
                # Center window on primary screen
                x = screen_geom.x() + (screen_geom.width() - self.width()) // 2
                y = screen_geom.y() + (screen_geom.height() - self.height()) // 2
                self.move(x, y)
        except Exception as e:
            print(f"Window positioning error: {e}")
    
    def create_auction_tab(self):
        """Create auction control tab - Compact Design"""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create scrollable container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # === DISPLAY VIEWS Section ===
        history_group = QGroupBox("DISPLAY VIEWS")
        history_layout = QHBoxLayout(history_group)
        history_layout.setSpacing(6)
        history_layout.setContentsMargins(10, 8, 10, 8)
        
        admin_view_btn = QPushButton("👤 ADMIN VIEW")
        admin_view_btn.clicked.connect(lambda: self.show_message('info', "Admin View", "Admin window is active"))
        admin_view_btn.setMinimumHeight(32)
        admin_view_btn.setProperty("class", "info")
        
        self.preview_display_btn = QPushButton("👁 PUBLIC VIEW")
        self.preview_display_btn.clicked.connect(self.open_display_preview)
        self.preview_display_btn.setMinimumHeight(32)
        self.preview_display_btn.setProperty("class", "info")
        
        server_status_btn = QPushButton("🌐 SERVER STATUS")
        server_status_btn.clicked.connect(lambda: self.show_message('info', "Server Status", "Server is running"))
        server_status_btn.setMinimumHeight(32)
        server_status_btn.setProperty("class", "success")
        
        history_layout.addWidget(admin_view_btn)
        history_layout.addWidget(self.preview_display_btn)
        history_layout.addWidget(server_status_btn)
        
        # === AUCTION CONTROLS ===
        control_group = QGroupBox("AUCTION CONTROLS")
        control_layout = QHBoxLayout(control_group)
        control_layout.setSpacing(6)
        control_layout.setContentsMargins(10, 8, 10, 8)
        
        self.start_btn = QPushButton("▶ START AUCTION")
        self.start_btn.clicked.connect(self.start_auction)
        self.start_btn.setProperty("class", "success")
        self.start_btn.setMinimumHeight(32)
        
        self.stop_btn = QPushButton("⏹ STOP")
        self.stop_btn.clicked.connect(self.stop_auction)
        self.stop_btn.setProperty("class", "danger")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(32)
        
        self.rerun_unsold_btn = QPushButton("🔄 RE-RUN")
        self.rerun_unsold_btn.clicked.connect(self.rerun_unsold_players)
        self.rerun_unsold_btn.setProperty("class", "info")
        self.rerun_unsold_btn.setMinimumHeight(32)
        
        self.end_auction_btn = QPushButton("🏁 END")
        self.end_auction_btn.clicked.connect(self.end_auction)
        self.end_auction_btn.setProperty("class", "danger")
        self.end_auction_btn.setMinimumHeight(32)
        
        self.reset_auction_btn = QPushButton("↻ RESET")
        self.reset_auction_btn.clicked.connect(self.reset_auction_data)
        self.reset_auction_btn.setProperty("class", "danger")
        self.reset_auction_btn.setMinimumHeight(32)
        
        # Projector button (hidden from main row, add to second row if needed)
        self.projector_display_btn = QPushButton("📺")
        self.projector_display_btn.clicked.connect(self.open_display_projector)
        self.projector_display_btn.setProperty("class", "info")
        self.projector_display_btn.setFixedSize(32, 32)
        self.projector_display_btn.setToolTip("Show Projector")
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.rerun_unsold_btn)
        control_layout.addWidget(self.end_auction_btn)
        control_layout.addWidget(self.reset_auction_btn)
        control_layout.addWidget(self.projector_display_btn)
        
        # === PLAYER INFO - Central Display ===
        player_group = QGroupBox("CURRENT PLAYER")
        player_layout = QVBoxLayout(player_group)
        player_layout.setSpacing(8)
        player_layout.setContentsMargins(10, 8, 10, 8)
        
        # Player name and role
        self.current_player_label = QLabel("No player selected")
        self.current_player_label.setStyleSheet("""
            font-size: 24px; 
            font-weight: 700; 
            color: #10b981;
        """)
        self.current_player_label.setAlignment(Qt.AlignCenter)
        
        self.player_role_label = QLabel("All-Rounder | Sri Lanka")
        self.player_role_label.setStyleSheet("font-size: 14px; color: #9ca3af;")
        self.player_role_label.setAlignment(Qt.AlignCenter)
        
        # Price info - Horizontal layout
        price_layout = QHBoxLayout()
        price_layout.setSpacing(20)
        
        base_price_container = QWidget()
        base_price_layout = QVBoxLayout(base_price_container)
        base_price_layout.setSpacing(2)
        base_price_layout.setContentsMargins(0, 0, 0, 0)
        
        base_label = QLabel("BASE PRICE")
        base_label.setStyleSheet("font-size: 11px; color: #6b7280; font-weight: 600;")
        base_label.setAlignment(Qt.AlignCenter)
        
        self.base_price_label = QLabel("Rs. 5,000")
        self.base_price_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #e5e7eb;")
        self.base_price_label.setAlignment(Qt.AlignCenter)
        
        base_price_layout.addWidget(base_label)
        base_price_layout.addWidget(self.base_price_label)
        
        current_bid_container = QWidget()
        current_bid_layout = QVBoxLayout(current_bid_container)
        current_bid_layout.setSpacing(2)
        current_bid_layout.setContentsMargins(0, 0, 0, 0)
        
        bid_label = QLabel("CURRENT BID")
        bid_label.setStyleSheet("font-size: 11px; color: #6b7280; font-weight: 600;")
        bid_label.setAlignment(Qt.AlignCenter)
        
        self.current_bid_label = QLabel("Rs. 5,000")
        self.current_bid_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #f59e0b;")
        self.current_bid_label.setAlignment(Qt.AlignCenter)
        
        current_bid_layout.addWidget(bid_label)
        current_bid_layout.addWidget(self.current_bid_label)
        
        price_layout.addStretch()
        price_layout.addWidget(base_price_container)
        price_layout.addWidget(current_bid_container)
        price_layout.addStretch()
        
        # Action buttons - Horizontal
        action_layout = QHBoxLayout()
        action_layout.setSpacing(6)
        
        self.prev_player_btn = QPushButton("⏮")
        self.prev_player_btn.clicked.connect(self.select_previous_player)
        self.prev_player_btn.setProperty("class", "info")
        self.prev_player_btn.setEnabled(False)
        self.prev_player_btn.setFixedSize(40, 32)
        self.prev_player_btn.setToolTip("Previous Player")
        
        self.next_player_btn = QPushButton("⏭ NEXT")
        self.next_player_btn.clicked.connect(self.select_next_player)
        self.next_player_btn.setProperty("class", "warning")
        self.next_player_btn.setEnabled(False)
        self.next_player_btn.setMinimumHeight(32)
        
        self.sold_btn = QPushButton("✅ SOLD")
        self.sold_btn.clicked.connect(self.mark_as_sold)
        self.sold_btn.setProperty("class", "success")
        self.sold_btn.setEnabled(False)
        self.sold_btn.setMinimumHeight(32)
        
        self.unsold_btn = QPushButton("❌ UNSOLD")
        self.unsold_btn.clicked.connect(self.mark_as_unsold)
        self.unsold_btn.setProperty("class", "danger")
        self.unsold_btn.setEnabled(False)
        self.unsold_btn.setMinimumHeight(32)
        
        action_layout.addWidget(self.prev_player_btn)
        action_layout.addWidget(self.next_player_btn)
        action_layout.addWidget(self.sold_btn)
        action_layout.addWidget(self.unsold_btn)
        
        # Status and Round info
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Status: UPCOMING")
        self.status_label.setStyleSheet("font-size: 13px; font-weight: 600;")
        self.round_label = QLabel("Round: 1")
        self.round_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #3b82f6;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.round_label)
        
        player_layout.addWidget(self.current_player_label)
        player_layout.addWidget(self.player_role_label)
        player_layout.addSpacing(8)
        player_layout.addLayout(price_layout)
        player_layout.addSpacing(8)
        player_layout.addLayout(action_layout)
        player_layout.addLayout(status_layout)
        
        # === FAST TEAM SELECTION ===
        team_group = QGroupBox("FAST TEAM SELECTION")
        team_layout = QHBoxLayout(team_group)
        team_layout.setSpacing(6)
        team_layout.setContentsMargins(10, 8, 10, 8)
        self.team_buttons_container = team_layout
        
        # === BID MANAGEMENT ===
        bid_group = QGroupBox("BID MANAGEMENT (LKR)")
        bid_layout = QVBoxLayout(bid_group)
        bid_layout.setSpacing(6)
        bid_layout.setContentsMargins(10, 8, 10, 8)
        
        # Team combo (hidden)
        self.team_combo = QComboBox()
        self.team_combo.setEnabled(False)
        self.team_combo.setMinimumHeight(32)
        self.team_combo.hide()
        
        # Custom amount input
        amount_layout = QHBoxLayout()
        amount_layout.setSpacing(6)
        
        amount_label = QLabel("ENTER CUSTOM AMOUNT")
        amount_label.setStyleSheet("font-size: 12px; font-weight: 600; color: #9ca3af;")
        
        self.bid_amount = QDoubleSpinBox()
        self.bid_amount.setRange(0, 10000000)
        self.bid_amount.setSingleStep(1000)
        self.bid_amount.setDecimals(0)
        self.bid_amount.setPrefix("Rs. ")
        self.bid_amount.setSuffix(" LKR")
        self.bid_amount.setEnabled(False)
        self.bid_amount.setMinimumHeight(32)
        self.bid_amount.setStyleSheet("""
            QDoubleSpinBox {
                font-size: 16px;
                font-weight: 700;
                color: #10b981;
                background-color: #1f2937;
                border: 2px solid #374151;
                border-radius: 6px;
                padding: 6px 10px;
            }
        """)
        
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(self.bid_amount)
        
        # Quick increments label
        quick_label = QLabel("QUICK INCREMENTS")
        quick_label.setStyleSheet("font-size: 12px; font-weight: 600; color: #9ca3af;")
        
        # Quick increment buttons row
        increment_layout = QHBoxLayout()
        increment_layout.setSpacing(6)
        
        self.increase_1000_btn = QPushButton("+ Rs. 1,000")
        self.increase_1000_btn.clicked.connect(lambda: self.increase_and_place(1000))
        self.increase_1000_btn.setEnabled(False)
        self.increase_1000_btn.setMinimumHeight(32)
        self.increase_1000_btn.setProperty("class", "info")
        
        self.increase_2000_btn = QPushButton("+ Rs. 2,000")
        self.increase_2000_btn.clicked.connect(lambda: self.increase_and_place(2000))
        self.increase_2000_btn.setEnabled(False)
        self.increase_2000_btn.setMinimumHeight(32)
        self.increase_2000_btn.setProperty("class", "info")
        
        self.increase_5000_btn = QPushButton("+ Rs. 5,000")
        self.increase_5000_btn.clicked.connect(lambda: self.increase_and_place(5000))
        self.increase_5000_btn.setEnabled(False)
        self.increase_5000_btn.setMinimumHeight(32)
        self.increase_5000_btn.setProperty("class", "info")
        
        increment_layout.addWidget(self.increase_1000_btn)
        increment_layout.addWidget(self.increase_2000_btn)
        increment_layout.addWidget(self.increase_5000_btn)
        
        # Place bid and pass buttons
        bid_action_layout = QHBoxLayout()
        bid_action_layout.setSpacing(6)
        
        self.place_bid_btn = QPushButton("💰 PLACE BID")
        self.place_bid_btn.clicked.connect(self.place_bid)
        self.place_bid_btn.setEnabled(False)
        self.place_bid_btn.setMinimumHeight(36)
        self.place_bid_btn.setProperty("class", "success")
        
        self.pass_btn = QPushButton("⏸ PASS")
        self.pass_btn.clicked.connect(self.handle_pass)
        self.pass_btn.setEnabled(False)
        self.pass_btn.setMinimumHeight(36)
        self.pass_btn.setProperty("class", "warning")
        
        bid_action_layout.addWidget(self.place_bid_btn, 3)
        bid_action_layout.addWidget(self.pass_btn, 1)
        
        # Pass counter
        self.pass_counter_label = QLabel("Consecutive Passes: 0")
        self.pass_counter_label.setStyleSheet("""
            font-size: 13px; 
            font-weight: 600; 
            color: #f59e0b;
            padding: 6px;
            background-color: rgba(245, 158, 11, 0.1);
            border-radius: 4px;
        """)
        self.pass_counter_label.setAlignment(Qt.AlignCenter)
        
        bid_layout.addLayout(amount_layout)
        bid_layout.addWidget(quick_label)
        bid_layout.addLayout(increment_layout)
        bid_layout.addLayout(bid_action_layout)
        bid_layout.addWidget(self.pass_counter_label)
        
        # === FOOTER INFO ===
        footer_group = QWidget()
        footer_layout = QHBoxLayout(footer_group)
        footer_layout.setContentsMargins(10, 5, 10, 5)
        footer_layout.setSpacing(20)
        
        self.remaining_players_label = QLabel("REMAINING PLAYERS: 0")
        self.remaining_players_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #9ca3af;")
        
        self.auction_time_label = QLabel("AUCTION TIME: 00:00:00")
        self.auction_time_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #9ca3af;")
        
        footer_layout.addWidget(self.remaining_players_label)
        footer_layout.addStretch()
        footer_layout.addWidget(self.auction_time_label)
        
        # Add all sections to container
        layout.addWidget(history_group)
        layout.addWidget(control_group)
        layout.addWidget(player_group)
        layout.addWidget(team_group)
        layout.addWidget(bid_group)
        layout.addWidget(footer_group)
        layout.addStretch()
        
        # Set up scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        return tab
    
    def create_players_tab(self):
        """Create players management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        self.add_player_btn = QPushButton("➕ ADD PLAYER")
        self.add_player_btn.clicked.connect(self.add_player)
        
        self.edit_player_btn = QPushButton("✏️ EDIT PLAYER")
        self.edit_player_btn.clicked.connect(self.edit_player)
        
        self.delete_player_btn = QPushButton("🗑 DELETE PLAYER")
        self.delete_player_btn.clicked.connect(self.delete_player)
        self.delete_player_btn.setProperty("class", "danger")
        
        self.export_players_pdf_btn = QPushButton("📄 GET PDF")
        self.export_players_pdf_btn.clicked.connect(self.export_players_to_pdf)
        self.export_players_pdf_btn.setProperty("class", "success")
        
        btn_layout.addWidget(self.add_player_btn)
        btn_layout.addWidget(self.edit_player_btn)
        btn_layout.addWidget(self.delete_player_btn)
        btn_layout.addWidget(self.export_players_pdf_btn)
        btn_layout.addStretch()
        
        # Players table - Updated with player types
        self.players_table = QTableWidget()
        self.players_table.setColumnCount(11)
        self.players_table.setHorizontalHeaderLabels([
            "ID", "Name", "Base Price (LKR)", "Faculty", "Role", 
            "Batting Style", "Bowling Style", "Status", 
            "Current Bid (LKR)", "Team", "Sold Price (LKR)"
        ])
        self.players_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.players_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.players_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.players_table)
        
        return tab
    
    def create_teams_tab(self):
        """Create teams management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        self.add_team_btn = QPushButton("➕ ADD TEAM")
        self.add_team_btn.clicked.connect(self.add_team)
        
        self.edit_team_btn = QPushButton("✏️ EDIT TEAM")
        self.edit_team_btn.clicked.connect(self.edit_team)
        
        self.delete_team_btn = QPushButton("🗑 DELETE TEAM")
        self.delete_team_btn.clicked.connect(self.delete_team)
        self.delete_team_btn.setProperty("class", "danger")
        
        btn_layout.addWidget(self.add_team_btn)
        btn_layout.addWidget(self.edit_team_btn)
        btn_layout.addWidget(self.delete_team_btn)
        btn_layout.addStretch()
        
        # Teams table
        self.teams_table = QTableWidget()
        self.teams_table.setColumnCount(6)
        self.teams_table.setHorizontalHeaderLabels([
            "ID", "Name", "Budget (LKR)", "Spent (LKR)", "Remaining (LKR)", "Players"
        ])
        self.teams_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.teams_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.teams_table)
        
        return tab
    
    def create_bids_tab(self):
        """Create bids history tab - Only shows winning bids (sold prices)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 REFRESH BID HISTORY")
        refresh_btn.clicked.connect(self.load_bid_history)
        layout.addWidget(refresh_btn)
        
        # Bids table - Only winning bids
        self.bids_table = QTableWidget()
        self.bids_table.setColumnCount(6)
        self.bids_table.setHorizontalHeaderLabels([
            "Player", "Team", "Sold Price (LKR)", "Timestamp", "Status"
        ])
        self.bids_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.bids_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.bids_table)
        
        return tab
    
    def create_summary_tab(self):
        """Create auction summary tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Summary buttons
        btn_layout = QHBoxLayout()
        
        self.refresh_summary_btn = QPushButton("🔄 REFRESH SUMMARY")
        self.refresh_summary_btn.clicked.connect(self.load_summary)
        
        self.export_summary_btn = QPushButton("📄 EXPORT TO PDF")
        self.export_summary_btn.clicked.connect(self.export_summary)
        
        btn_layout.addWidget(self.refresh_summary_btn)
        btn_layout.addWidget(self.export_summary_btn)
        btn_layout.addStretch()
        
        # Summary statistics
        stats_group = QGroupBox("AUCTION STATISTICS")
        stats_layout = QGridLayout(stats_group)
        stats_layout.setSpacing(20)
        
        self.total_players_label = QLabel("Total Players: 0")
        self.total_players_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ff88;")
        
        self.sold_players_label = QLabel("Sold Players: 0")
        self.sold_players_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ff88;")
        
        self.unsold_players_label = QLabel("Unsold Players: 0")
        self.unsold_players_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ff9900;")
        
        self.total_spent_label = QLabel("Total Spent: Rs. 0")
        self.total_spent_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffff00;")

        self.remaining_players_label = QLabel("Remaining Players: 0")
        self.remaining_players_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #9fb2ff;")
        
        stats_layout.addWidget(self.total_players_label, 0, 0)
        stats_layout.addWidget(self.sold_players_label, 0, 1)
        stats_layout.addWidget(self.remaining_players_label, 0, 2)
        stats_layout.addWidget(self.unsold_players_label, 1, 0)
        stats_layout.addWidget(self.total_spent_label, 1, 1)
        
        # Teams summary
        self.teams_summary_table = QTableWidget()
        self.teams_summary_table.setColumnCount(5)
        self.teams_summary_table.setHorizontalHeaderLabels([
            "Team", "Budget", "Spent", "Remaining", "Players"
        ])
        self.teams_summary_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.teams_summary_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.teams_summary_table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d44;
                color: #ffffff;
                gridline-color: #4CAF50;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 8px;
                border: 1px solid #4CAF50;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: #ffffff;
                padding: 8px;
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #388E3C;
            }
        """)
        
        # Players by team
        self.players_by_team_table = QTableWidget()
        self.players_by_team_table.setColumnCount(5)
        self.players_by_team_table.setHorizontalHeaderLabels([
            "Team", "Player", "Faculty", "Role", "Price (LKR)"
        ])
        self.players_by_team_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.players_by_team_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.players_by_team_table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d44;
                color: #ffffff;
                gridline-color: #4CAF50;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 8px;
                border: 1px solid #4CAF50;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: #ffffff;
                padding: 8px;
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #388E3C;
            }
        """)
        
        layout.addLayout(btn_layout)
        layout.addWidget(stats_group)
        layout.addWidget(QLabel("TEAMS SUMMARY:"))
        layout.addWidget(self.teams_summary_table)
        layout.addWidget(QLabel("PLAYERS BY TEAM:"))
        layout.addWidget(self.players_by_team_table)
        
        return tab
    
    def load_data(self):
        """Load data from database"""
        # Load teams for combo box and team buttons
        cursor = db.conn.cursor()
        cursor.execute("SELECT id, name FROM teams ORDER BY name")
        teams = cursor.fetchall()
        
        self.team_combo.clear()
        
        # Clear existing team buttons
        self.team_buttons = {}
        while self.team_buttons_container.count():
            item = self.team_buttons_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Create team buttons - Compact style
        for team in teams:
            self.team_combo.addItem(team['name'], team['id'])
            btn = QPushButton(team['name'])
            btn.setMinimumHeight(36)
            btn.setMinimumWidth(100)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #374151;
                    color: #e5e7eb;
                    font-weight: 600;
                    font-size: 14px;
                    border-radius: 6px;
                    padding: 8px 12px;
                    border: 2px solid #4b5563;
                }
                QPushButton:hover {
                    background-color: #4b5563;
                    border: 2px solid #6b7280;
                }
                QPushButton:pressed {
                    background-color: #1f2937;
                }
            """)
            btn.clicked.connect(lambda checked, team_id=team['id'], team_name=team['name']: self.on_team_button_clicked(team_id, team_name))
            self.team_buttons[team['id']] = btn
            self.team_buttons_container.addWidget(btn)
        
        self.team_buttons_container.addStretch()
        
        # Load players table with all player types - Ordered by ID
        cursor.execute('''
            SELECT p.*, t.name as team_name 
            FROM players p 
            LEFT JOIN teams t ON p.sold_to_team = t.id 
            ORDER BY p.id
        ''')
        players = cursor.fetchall()
        
        self.players_table.setRowCount(len(players))
        for i, player in enumerate(players):
            self.players_table.setItem(i, 0, QTableWidgetItem(str(player['id'])))
            self.players_table.setItem(i, 1, QTableWidgetItem(player['name']))
            self.players_table.setItem(i, 2, QTableWidgetItem(f"Rs. {player['base_price']:,.0f}"))
            self.players_table.setItem(i, 3, QTableWidgetItem(player['faculty'] if player['faculty'] else "-"))
            self.players_table.setItem(i, 4, QTableWidgetItem(player['player_role'] if player['player_role'] else "-"))
            self.players_table.setItem(i, 5, QTableWidgetItem(player['batting_style'] if player['batting_style'] else "-"))
            self.players_table.setItem(i, 6, QTableWidgetItem(player['bowling_style'] if player['bowling_style'] else "-"))
            self.players_table.setItem(i, 7, QTableWidgetItem(player['status']))
            self.players_table.setItem(i, 8, QTableWidgetItem(f"Rs. {player['current_bid']:,.0f}"))
            self.players_table.setItem(i, 9, QTableWidgetItem(player['team_name'] if player['team_name'] else "-"))
            self.players_table.setItem(i, 10, QTableWidgetItem(f"Rs. {player['sold_price']:,.0f}"))
        
        # Load teams table
        cursor.execute('''
            SELECT t.*, COUNT(p.id) as player_count
            FROM teams t
            LEFT JOIN players p ON t.id = p.sold_to_team AND p.status = 'SOLD'
            GROUP BY t.id
            ORDER BY t.name
        ''')
        teams_data = cursor.fetchall()
        
        self.teams_table.setRowCount(len(teams_data))
        for i, team in enumerate(teams_data):
            self.teams_table.setItem(i, 0, QTableWidgetItem(str(team['id'])))
            self.teams_table.setItem(i, 1, QTableWidgetItem(team['name']))
            self.teams_table.setItem(i, 2, QTableWidgetItem(f"Rs. {team['budget']:,.0f}"))
            self.teams_table.setItem(i, 3, QTableWidgetItem(f"Rs. {team['spent']:,.0f}"))
            remaining = team['budget'] - team['spent']
            self.teams_table.setItem(i, 4, QTableWidgetItem(f"Rs. {remaining:,.0f}"))
            self.teams_table.setItem(i, 5, QTableWidgetItem(str(team['player_count'])))
        
        # Load bid history (only winning bids)
        self.load_bid_history()
        
        # Update current player info
        self.update_current_player_info()
        
        # Load summary
        self.load_summary()
    
    def load_bid_history(self):
        """Load only winning bids (sold prices)"""
        bids = db.get_bid_history()
        
        self.bids_table.setRowCount(len(bids))
        for i, bid in enumerate(bids):
            self.bids_table.setItem(i, 0, QTableWidgetItem(bid['player_name']))
            self.bids_table.setItem(i, 1, QTableWidgetItem(bid['team_name']))
            self.bids_table.setItem(i, 2, QTableWidgetItem(f"Rs. {bid['amount']:,.0f}"))
            self.bids_table.setItem(i, 3, QTableWidgetItem(bid['timestamp']))
            self.bids_table.setItem(i, 4, QTableWidgetItem(bid['status']))
    
    def load_summary(self):
        """Load auction summary"""
        summary = db.get_auction_summary()
        
        # Update statistics
        self.total_players_label.setText(f"Total Players: {summary['total_players']}")
        self.sold_players_label.setText(f"Sold Players: {summary['sold_players']}")
        self.unsold_players_label.setText(f"Unsold Players: {summary['unsold_players']}")
        self.total_spent_label.setText(f"Total Spent: Rs. {summary['total_spent']:,.0f}")
        # Show remaining (upcoming) players
        if 'remaining_players' in summary:
            self.remaining_players_label.setText(f"Remaining Players: {summary['remaining_players']}")
        else:
            self.remaining_players_label.setText("Remaining Players: 0")
        
        # Teams summary table
        self.teams_summary_table.setRowCount(len(summary['teams']))
        for i, team in enumerate(summary['teams']):
            remaining = team['budget'] - team['spent']
            self.teams_summary_table.setItem(i, 0, QTableWidgetItem(team['name']))
            self.teams_summary_table.setItem(i, 1, QTableWidgetItem(f"Rs. {team['budget']:,.0f}"))
            self.teams_summary_table.setItem(i, 2, QTableWidgetItem(f"Rs. {team['spent']:,.0f}"))
            self.teams_summary_table.setItem(i, 3, QTableWidgetItem(f"Rs. {remaining:,.0f}"))
            
            # Count players for this team (use team id)
            cursor = db.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM players WHERE sold_to_team = ? AND status = 'SOLD'", (team.get('id'),))
            player_count = cursor.fetchone()[0]
            self.teams_summary_table.setItem(i, 4, QTableWidgetItem(str(player_count)))
        
        # Players by team
        players_by_team = db.get_players_by_team()
        total_players = 0
        rows = []
        
        for team_name, players in players_by_team.items():
            for player in players:
                rows.append({
                    'team': team_name,
                    'player': player['player_name'],
                    'faculty': player['faculty'],
                    'role': player['player_role'],
                    'price': player['sold_price']
                })
                total_players += 1
        
        self.players_by_team_table.setRowCount(total_players)
        for i, row in enumerate(rows):
            self.players_by_team_table.setItem(i, 0, QTableWidgetItem(row['team']))
            self.players_by_team_table.setItem(i, 1, QTableWidgetItem(row['player']))
            self.players_by_team_table.setItem(i, 2, QTableWidgetItem(row['faculty']))
            self.players_by_team_table.setItem(i, 3, QTableWidgetItem(row['role']))
            self.players_by_team_table.setItem(i, 4, QTableWidgetItem(f"Rs. {row['price']:,.0f}"))
    
    def update_current_player_info(self):
        """Update current player information display"""
        cursor = db.conn.cursor()
        cursor.execute("SELECT current_player_id, current_round FROM auction_settings WHERE id = 1")
        result = cursor.fetchone()
        
        if result and result['current_player_id']:
            cursor.execute('''
                SELECT p.*, t.name as team_name
                FROM players p
                LEFT JOIN teams t ON p.sold_to_team = t.id
                WHERE p.id = ?
            ''', (result['current_player_id'],))
            player = cursor.fetchone()
            
            if player:
                self.current_player_label.setText(player['name'])
                
                # Update player role label
                role = player['player_role'] if player['player_role'] else 'Unknown'
                faculty = player['faculty'] if player['faculty'] else 'Unknown'
                self.player_role_label.setText(f"{role} | {faculty}")
                
                self.base_price_label.setText(f"Rs. {player['base_price']:,.0f}")
                self.current_bid_label.setText(f"Rs. {player['current_bid']:,.0f}")
                self.status_label.setText(f"Status: {player['status']}")
                self.round_label.setText(f"Round: {result['current_round']}")
                
                 # Set bid amount to current bid (no auto-increment)
                if player['current_bid'] > 0:
                    self.bid_amount.setValue(player['current_bid'])
                else:
                    self.bid_amount.setValue(player['base_price'])
                
                # Enable/disable buttons based on status
                is_live = player['status'] == 'LIVE'
                self.place_bid_btn.setEnabled(is_live)
                self.increase_1000_btn.setEnabled(is_live)
                self.increase_2000_btn.setEnabled(is_live)
                self.increase_5000_btn.setEnabled(is_live)
                self.pass_btn.setEnabled(is_live)
                self.bid_amount.setEnabled(is_live)
                self.team_combo.setEnabled(is_live)
                
                self.sold_btn.setEnabled(is_live)
                self.unsold_btn.setEnabled(is_live)
        else:
            self.current_player_label.setText("No player selected")
            self.player_role_label.setText("All-Rounder | Sri Lanka")
            self.base_price_label.setText("Rs. 0")
            self.current_bid_label.setText("Rs. 0")
            self.status_label.setText("Status: UPCOMING")
            self.round_label.setText("Round: 1")
            self.pass_btn.setEnabled(False)
    
    def open_display_preview(self):
        """Open display window for preview on laptop screen (resizable)"""
        from display_window import DisplayWindow
        
        # Close existing display window if open
        if self.display_window and self.display_window.isVisible():
            self.display_window.close()
        
        screens = QApplication.screens()
        try:
            # Open on primary screen
            self.display_window = DisplayWindow(mode='preview', screen=screens[0])
            self.display_window.show()
            self.status_bar.showMessage("Display preview opened on laptop screen!")
        except Exception as e:
            self.show_message('warning', "Error", f"Failed to open display: {str(e)}")
    
    def open_display_projector(self):
        """Open display window for projector (full screen, no resize, 1920x1080)"""
        from display_window import DisplayWindow
        
        # Close existing display window if open
        if self.display_window and self.display_window.isVisible():
            self.display_window.close()
        
        screens = QApplication.screens()
        try:
            if len(screens) > 1:
                # Open on second screen (projector)
                self.display_window = DisplayWindow(mode='projector', screen=screens[1])
            else:
                # If only one screen, open in projector mode on that screen
                self.show_message('warning', "Single Screen", "Only one display found. Opening in projector mode on this screen.")
                self.display_window = DisplayWindow(mode='projector', screen=screens[0])
            
            self.display_window.show()
            self.status_bar.showMessage("Display opened on projector!")
        except Exception as e:
            self.show_message('warning', "Error", f"Failed to open projector display: {str(e)}")
    
    def open_display_window(self):
        """Legacy: Open display window on second screen"""
        from display_window import DisplayWindow
        
        if self.display_window and self.display_window.isVisible():
            self.display_window.raise_()
            self.display_window.activateWindow()
            self.status_bar.showMessage("Display window already open!")
            return
        
        screens = QApplication.screens()
        
        if len(screens) > 1:
            self.display_window = DisplayWindow(mode='projector', screen=screens[1])
        else:
            self.display_window = DisplayWindow(mode='preview', screen=screens[0])
        
        self.display_window.show()
        self.status_bar.showMessage("Display window opened!")
    
    def open_teams_summary_window(self):
        """Open a window showing all teams with their logos and purchased players"""
        try:
            from PyQt5.QtCore import Qt
            from PyQt5.QtGui import QPixmap
            import os
            
            # Create dialog window (non-modal)
            dialog = QDialog(self)
            dialog.setWindowTitle("Teams & Players Summary")
            dialog.setWindowFlag(Qt.WindowStaysOnTopHint, False)
            dialog.setModal(False)
            dialog.setMinimumSize(900, 600)
            dialog.resize(1000, 700)
            
            # Main layout
            main_layout = QVBoxLayout(dialog)
            main_layout.setContentsMargins(20, 20, 20, 20)
            main_layout.setSpacing(10)
            
            # Title
            title = QLabel("🏆 TEAMS & PURCHASED PLAYERS")
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("""
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background: #ecf0f1;
                border-radius: 5px;
                margin-bottom: 10px;
            """)
            main_layout.addWidget(title)
            
            # Scroll area for teams
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
            
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)
            scroll_layout.setSpacing(15)
            scroll_layout.setContentsMargins(10, 10, 10, 10)
            
            # Get teams from database
            cursor = db.conn.cursor()
            cursor.execute("SELECT id, name, logo_path, budget FROM teams ORDER BY name")
            teams = cursor.fetchall()
            
            if not teams:
                no_teams_label = QLabel("No teams found in the database.")
                no_teams_label.setAlignment(Qt.AlignCenter)
                no_teams_label.setStyleSheet("font-size: 16px; color: #7f8c8d; padding: 20px;")
                scroll_layout.addWidget(no_teams_label)
            else:
                for team in teams:
                    team_id = team['id']
                    team_name = team['name']
                    logo_path = team['logo_path']
                    budget = team['budget']
                    
                    # Get players for this team
                    cursor.execute('''
                        SELECT name, player_role, sold_price
                        FROM players
                        WHERE sold_to_team = ? AND status = 'SOLD'
                        ORDER BY sold_price DESC
                    ''', (team_id,))
                    players = cursor.fetchall()
                    
                    # Team container
                    team_frame = QFrame()
                    team_frame.setStyleSheet("""
                        QFrame {
                            background: white;
                            border: 2px solid #3498db;
                            border-radius: 8px;
                            padding: 15px;
                        }
                    """)
                    team_layout = QVBoxLayout(team_frame)
                    team_layout.setSpacing(10)
                    
                    # Team header (logo + name + info)
                    header_layout = QHBoxLayout()
                    
                    # Team logo
                    logo_label = QLabel()
                    if logo_path:
                        # Resolve logo path
                        resolved_path = None
                        if os.path.isabs(logo_path) and os.path.exists(logo_path):
                            resolved_path = logo_path
                        else:
                            # Try relative to project root
                            project_root = os.path.dirname(os.path.abspath(__file__))
                            relative_path = os.path.join(project_root, logo_path)
                            if os.path.exists(relative_path):
                                resolved_path = relative_path
                        
                        if resolved_path:
                            pixmap = QPixmap(resolved_path)
                            if not pixmap.isNull():
                                logo_label.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    
                    logo_label.setFixedSize(80, 80)
                    logo_label.setStyleSheet("background: #ecf0f1; border: 2px solid #bdc3c7; border-radius: 5px;")
                    logo_label.setAlignment(Qt.AlignCenter)
                    header_layout.addWidget(logo_label)
                    
                    # Team info
                    info_layout = QVBoxLayout()
                    
                    name_label = QLabel(team_name)
                    name_label.setStyleSheet("""
                        font-size: 20px;
                        font-weight: bold;
                        color: #2c3e50;
                    """)
                    info_layout.addWidget(name_label)
                    
                    # Budget and player count info
                    stats_label = QLabel(f"Budget: Rs. {budget:,} | Players: {len(players)}")
                    stats_label.setStyleSheet("""
                        font-size: 14px;
                        color: #7f8c8d;
                    """)
                    info_layout.addWidget(stats_label)
                    
                    header_layout.addLayout(info_layout)
                    header_layout.addStretch()
                    
                    team_layout.addLayout(header_layout)
                    
                    # Players list
                    if players:
                        players_label = QLabel("Players:")
                        players_label.setStyleSheet("""
                            font-size: 16px;
                            font-weight: bold;
                            color: #34495e;
                            margin-top: 5px;
                        """)
                        team_layout.addWidget(players_label)
                        
                        # Create a grid for players
                        players_grid = QFrame()
                        players_grid.setStyleSheet("""
                            QFrame {
                                background: #f8f9fa;
                                border: 1px solid #dee2e6;
                                border-radius: 5px;
                                padding: 10px;
                            }
                        """)
                        players_grid_layout = QVBoxLayout(players_grid)
                        players_grid_layout.setSpacing(5)
                        
                        for i, player in enumerate(players, 1):
                            player_info = QLabel(f"{i}. {player['name']} - {player['player_role']} (Rs. {player['sold_price']:,})")
                            player_info.setStyleSheet("""
                                font-size: 14px;
                                color: #495057;
                                padding: 5px;
                            """)
                            players_grid_layout.addWidget(player_info)
                        
                        team_layout.addWidget(players_grid)
                    else:
                        no_players_label = QLabel("No players purchased yet")
                        no_players_label.setStyleSheet("""
                            font-size: 14px;
                            color: #95a5a6;
                            font-style: italic;
                            padding: 10px;
                        """)
                        team_layout.addWidget(no_players_label)
                    
                    scroll_layout.addWidget(team_frame)
            
            scroll_layout.addStretch()
            scroll.setWidget(scroll_widget)
            main_layout.addWidget(scroll)
            
            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.close)
            close_btn.setMinimumHeight(25)
            close_btn.setStyleSheet("""
                QPushButton {
                    background: #3498db;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 20px;
                }
                QPushButton:hover {
                    background: #2980b9;
                }
            """)
            main_layout.addWidget(close_btn)
            
            dialog.show()
            
        except Exception as e:
            self.show_message('warning', "Error", f"Failed to open teams summary: {str(e)}")

    def open_teams_window(self):
        """Open the Teams window showing bought players by team"""
        try:
            from teams_window import TeamsWindow
            if hasattr(self, 'teams_window') and self.teams_window and self.teams_window.isVisible():
                self.teams_window.raise_()
                self.teams_window.activateWindow()
                return

            self.teams_window = TeamsWindow(self)
            self.teams_window.show()
            self.status_bar.showMessage("Teams window opened!")
        except Exception as e:
            self.show_message('warning', "Error", f"Failed to open Teams window: {e}")
    
    def start_auction(self):
        """Start the auction"""
        cursor = db.conn.cursor()
        cursor.execute("UPDATE auction_settings SET is_auction_active = 1 WHERE id = 1")
        db.conn.commit()
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.next_player_btn.setEnabled(True)
        self.prev_player_btn.setEnabled(True)
        self.status_bar.showMessage("Auction started!")
        
        self.data_updated.emit()
    
    def stop_auction(self):
        """Stop the auction"""
        cursor = db.conn.cursor()
        cursor.execute("UPDATE auction_settings SET is_auction_active = 0 WHERE id = 1")
        db.conn.commit()
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.next_player_btn.setEnabled(False)
        self.prev_player_btn.setEnabled(False)
        
        self.status_bar.showMessage("Auction stopped!")
        
        self.data_updated.emit()
    
    def end_auction(self):
        """End the auction completely"""
        reply = self.show_message('question', "End Auction", "Are you sure you want to end the auction?\nThis will finalize all sales.", buttons=QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            cursor = db.conn.cursor()
            cursor.execute("UPDATE auction_settings SET is_auction_active = 0 WHERE id = 1")
            db.conn.commit()
            
            self.load_summary()
            self.show_message('info', "Auction Ended", "Auction has been completed!")
            self.status_bar.showMessage("Auction ended!")
    
    def reset_auction_data(self):
        """Reset auction data (but keep player and team details)"""
        reply = self.show_message('question', "Reset Auction Data", "Reset all auction data?\n(Player and Team details will NOT be deleted)\n\nThis will:\n- Reset all player statuses to UPCOMING\n- Clear all bids and sold information\n- Reset auction settings", buttons=QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                cursor = db.conn.cursor()
                
                # Reset all players to UPCOMING status
                # Note: DB schema does not have a 'leading_team' column; avoid updating it
                cursor.execute("""
                    UPDATE players 
                    SET status = 'UPCOMING', 
                        current_bid = 0,
                        sold_to_team = NULL,
                        sold_price = 0
                """)
                
                # Reset auction settings
                cursor.execute("""
                    UPDATE auction_settings 
                    SET current_player_id = NULL,
                        current_round = 1,
                        is_auction_active = 0
                    WHERE id = 1
                """)
                
                # Delete all bids
                cursor.execute("DELETE FROM bids")
                
                # Reset team spent amounts
                cursor.execute("""
                    UPDATE teams 
                    SET spent = 0
                """)
                
                db.conn.commit()
                
                # Refresh UI
                self.load_data()
                self.update_current_player_info()
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.next_player_btn.setEnabled(False)
                self.prev_player_btn.setEnabled(False)
                
                self.show_message('info', "Reset Complete", "Auction data has been reset successfully!")
                self.status_bar.showMessage("Auction data reset!")
                self.data_updated.emit()
                
            except Exception as e:
                self.show_message('critical', "Error", f"Failed to reset auction data: {str(e)}")
    
    def select_previous_player(self):
        """Select the previous player (go back to last player)"""
        cursor = db.conn.cursor()
        
        # Get current player
        cursor.execute("SELECT current_player_id FROM auction_settings WHERE id = 1")
        _current = cursor.fetchone()
        current_id = _current['current_player_id'] if _current else None
        
        # Find previous player (last SOLD or UNSOLD player before current)
        if current_id:
            cursor.execute('''
                SELECT id FROM players 
                WHERE id < ? AND status IN ('SOLD', 'UNSOLD')
                ORDER BY id DESC
                LIMIT 1
            ''', (current_id,))
        else:
            # If no current player, get the last SOLD or UNSOLD player
            cursor.execute('''
                SELECT id FROM players 
                WHERE status IN ('SOLD', 'UNSOLD')
                ORDER BY id DESC
                LIMIT 1
            ''')
        
        prev_player = cursor.fetchone()
        
        if prev_player:
            # Mark current player as UPCOMING if it was LIVE
            if current_id:
                cursor.execute("SELECT status FROM players WHERE id = ?", (current_id,))
                _row = cursor.fetchone()
                if _row and _row['status'] == 'LIVE':
                    cursor.execute("UPDATE players SET status = 'UPCOMING' WHERE id = ?", (current_id,))
            
            # Set previous player as LIVE
            cursor.execute('''
                UPDATE players 
                SET status = 'LIVE'
                WHERE id = ?
            ''', (prev_player['id'],))
            
            # Update auction settings to point to previous player
            cursor.execute('''
                UPDATE auction_settings 
                SET current_player_id = ? 
                WHERE id = 1
            ''', (prev_player['id'],))
            
            db.conn.commit()
            
            self.status_bar.showMessage(f"Previous player selected: {prev_player['id']}")
            self.update_current_player_info()
            self.load_data()
            self.data_updated.emit()
        else:
            self.show_message('info', "No Previous Player", "No previous player available!")
    
    def select_next_player(self):
        """Select the next player for auction"""
        cursor = db.conn.cursor()

        # If a player is currently LIVE, mark them as UNSOLD automatically
        cursor.execute("SELECT current_player_id FROM auction_settings WHERE id = 1")
        _current = cursor.fetchone()
        if _current and _current['current_player_id']:
            cursor.execute("SELECT status FROM players WHERE id = ?", (_current['current_player_id'],))
            _row = cursor.fetchone()
            if _row and _row['status'] == 'LIVE':
                # Mark previous LIVE player as UNSOLD and clear current_player_id
                db.mark_player_unsold(_current['current_player_id'])
                cursor.execute("UPDATE auction_settings SET current_player_id = NULL WHERE id = 1")
                db.conn.commit()
                self.status_bar.showMessage("Previous player marked as UNSOLD")
                self.update_current_player_info()
                self.load_data()
                self.data_updated.emit()

        # Get first upcoming player
        cursor.execute('''
            SELECT id FROM players 
            WHERE status = 'UPCOMING'
            ORDER BY id 
            LIMIT 1
        ''')
        player = cursor.fetchone()
        
        if player:
            # Update current player to LIVE
            cursor.execute('''
                UPDATE players 
                SET status = 'LIVE', 
                    current_bid = base_price 
                WHERE id = ?
            ''', (player['id'],))
            
            # Update auction settings
            cursor.execute('''
                UPDATE auction_settings 
                SET current_player_id = ? 
                WHERE id = 1
            ''', (player['id'],))
            
            db.conn.commit()
            
            self.status_bar.showMessage(f"Next player selected: {player['id']}")
            self.update_current_player_info()
            self.load_data()
            self.data_updated.emit()
        else:
            self.show_message('info', "No Players", "No upcoming players available!")
    
    def rerun_unsold_players(self):
        """Re-auction unsold players"""
        unsold_players = db.get_unsold_players()
        
        if not unsold_players:
            self.show_message('info', "No Unsold Players", "There are no unsold players to re-auction!")
            return
        
        reply = self.show_message('question', "Re-auction Unsold Players", f"Start second round with {len(unsold_players)} unsold players?", buttons=QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            new_round = db.reset_unsold_players_for_rerun()
            self.status_bar.showMessage(f"Second round started! Round {new_round}")
            self.show_message('info', "Second Round Started", f"Round {new_round} started with {len(unsold_players)} players!")
            
            self.load_data()
            self.data_updated.emit()
    
    def place_bid(self, update_ui: bool = True):
        """Place a bid for current player in LKR

        Args:
            update_ui: if True, refresh current player info and reload data after placing.
                       If False, only place the bid without resetting the bid amount spinbox.
        """
        team_id = self.team_combo.currentData()
        amount_lkr = self.bid_amount.value()

        if team_id and amount_lkr > 0:
            if db.place_bid(team_id, amount_lkr):
                # Reset pass counter when new bid is placed
                self.reset_pass_counter()
                self.status_bar.showMessage(f"Bid placed: Rs. {amount_lkr:,.0f}")
                
                # Always update current bid label immediately
                self.current_bid_label.setText(f"Rs. {amount_lkr:,.0f}")
                
                # Set spinbox to next suggested increment
                self.bid_amount.setValue(amount_lkr + 1000)
                
                if update_ui:
                    self.update_current_player_info()
                    self.load_data()
                    self.data_updated.emit()
            else:
                self.show_message('warning', "Error", "Failed to place bid!")
    
    def increase_bid(self, increment):
        """Increase bid amount by specified LKR increment"""
        current = self.bid_amount.value()
        self.bid_amount.setValue(current + increment)

    def increase_and_place(self, increment):
        """Increase the bid amount by increment and place the bid if possible.

        If no team is selected or placing is disabled, only increase the spinbox value.
        """
        # Increase the spinbox value first
        self.increase_bid(increment)

        # If place button is enabled and a team is selected, place the bid immediately
        team_id = self.team_combo.currentData()
        if team_id and self.place_bid_btn.isEnabled():
            # Place bid and update UI with full refresh
            self.place_bid(update_ui=True)
    
    def on_team_button_clicked(self, team_id, team_name):
        """Handle team button click - select team and highlight it"""
        self.leading_team = team_id
        
        # Update combo box to match - find index by data
        for i in range(self.team_combo.count()):
            if self.team_combo.itemData(i) == team_id:
                self.team_combo.setCurrentIndex(i)
                break
        
        # Update button highlighting - Compact design with vibrant selection
        for tid, btn in self.team_buttons.items():
            if tid == team_id:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #10b981;
                        color: #ffffff;
                        font-weight: 700;
                        font-size: 14px;
                        border-radius: 6px;
                        padding: 8px 12px;
                        border: 3px solid #059669;
                        min-height: 36px;
                    }
                    QPushButton:hover {
                        background-color: #059669;
                    }
                    QPushButton:pressed {
                        background-color: #047857;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #374151;
                        color: #e5e7eb;
                        font-weight: 600;
                        font-size: 14px;
                        border-radius: 6px;
                        padding: 8px 12px;
                        border: 2px solid #4b5563;
                        min-height: 36px;
                    }
                    QPushButton:hover {
                        background-color: #4b5563;
                        border: 2px solid #6b7280;
                    }
                    QPushButton:pressed {
                        background-color: #1f2937;
                    }
                """)
        
        self.status_bar.showMessage(f"Leading team selected: {team_name}")
    
    def handle_pass(self):
        """Handle PASS button - increment counter and trigger SOLD on 3 passes"""
        self.pass_count += 1
        self.pass_counter_label.setText(f"Consecutive Passes: {self.pass_count}")
        self.status_bar.showMessage(f"Pass #{self.pass_count}")
        
        if self.pass_count >= 3:
            self.status_bar.showMessage("3 passes reached! Auto-finalizing sale...")
            # Auto trigger mark as sold
            QTimer.singleShot(500, self.mark_as_sold)
    
    def reset_pass_counter(self):
        """Reset pass counter when new bid is placed"""
        self.pass_count = 0
        self.pass_counter_label.setText("Consecutive Passes: 0")
    
    def mark_as_sold(self):
        """Mark current player as sold"""
        cursor = db.conn.cursor()
        
        cursor.execute('''
            SELECT p.id, p.current_bid
            FROM players p
            JOIN auction_settings a ON p.id = a.current_player_id
            WHERE a.id = 1 AND p.status = 'LIVE'
        ''')
        result = cursor.fetchone()
        
        if result and result['current_bid'] > 0:
            player_id = result['id']
            current_bid = result['current_bid']
            
            # Get team with highest bid
            cursor.execute('''
                SELECT team_id FROM bids 
                WHERE player_id = ? AND amount = ?
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (player_id, current_bid))
            bid = cursor.fetchone()
            
            if bid:
                team_id = bid['team_id']
                db.mark_player_sold(player_id, team_id, current_bid)
                
                # Reset pass counter
                self.reset_pass_counter()
                
                
                self.status_bar.showMessage(f"Player sold for Rs. {current_bid:,.0f}")
                self.update_current_player_info()
                self.load_data()
                self.data_updated.emit()
            else:
                # No bid record for the current_bid. Allow selling at base price
                # if no bids were placed by using the selected team from the combo.
                cursor.execute('SELECT base_price FROM players WHERE id = ?', (player_id,))
                row = cursor.fetchone()
                base_price = row['base_price'] if row else 0

                if current_bid == base_price:
                    # Try to get selected team from UI
                    team_id = self.team_combo.currentData()
                    if not team_id:
                        self.show_message('warning', "Error", "No bids found for this player.\nPlease select a team to sell at base price.")
                        return

                    reply = self.show_message('question', "Confirm Sell at Base Price", f"No bids found. Sell player for base price Rs. {current_bid:,.0f} to the selected team?", buttons=QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        db.mark_player_sold(player_id, team_id, current_bid)
                        
                        # Reset pass counter
                        self.reset_pass_counter()
                        
                        self.status_bar.showMessage(f"Player sold for Rs. {current_bid:,.0f}")
                        self.update_current_player_info()
                        self.load_data()
                        self.data_updated.emit()
                    else:
                        return
                else:
                    self.show_message('warning', "Error", "No bids found for this player!")
        else:
            self.show_message('warning', "Error", "No current bid or player not LIVE!")
    
    def mark_as_unsold(self):
        """Mark current player as unsold"""
        cursor = db.conn.cursor()
        
        cursor.execute('''
            SELECT current_player_id FROM auction_settings WHERE id = 1
        ''')
        result = cursor.fetchone()
        
        if result and result['current_player_id']:
            player_id = result['current_player_id']
            db.mark_player_unsold(player_id)
            
            # Reset pass counter
            self.reset_pass_counter()
            
            self.status_bar.showMessage("Player marked as UNSOLD")
            self.update_current_player_info()
            self.load_data()
            self.data_updated.emit()
    
    def add_player(self):
        """Add a new player"""
        dialog = PlayerDialog(self)
        if dialog.exec_():
            self.load_data()
            self.data_updated.emit()
    
    def edit_player(self):
        """Edit selected player"""
        selected = self.players_table.selectedItems()
        if selected:
            player_id = int(self.players_table.item(selected[0].row(), 0).text())
            dialog = PlayerDialog(self, player_id)
            if dialog.exec_():
                self.load_data()
                self.data_updated.emit()
        else:
            self.show_message('warning', "No Selection", "Please select a player to edit!")
    
    def delete_player(self):
        """Delete selected player"""
        selected = self.players_table.selectedItems()
        if selected:
            player_id = int(self.players_table.item(selected[0].row(), 0).text())
            player_name = self.players_table.item(selected[0].row(), 1).text()
            
            reply = self.show_message('question', "Confirm Delete", f"Are you sure you want to delete player: {player_name}?", buttons=QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                cursor = db.conn.cursor()
                cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
                db.conn.commit()
                self.load_data()
                self.data_updated.emit()
        else:
            self.show_message('warning', "No Selection", "Please select a player to delete!")
    
    def add_team(self):
        """Add a new team"""
        dialog = TeamDialog(self)
        if dialog.exec_():
            self.load_data()
            self.data_updated.emit()
    
    def edit_team(self):
        """Edit selected team"""
        selected = self.teams_table.selectedItems()
        if selected:
            team_id = int(self.teams_table.item(selected[0].row(), 0).text())
            dialog = TeamDialog(self, team_id)
            if dialog.exec_():
                self.load_data()
                self.data_updated.emit()
        else:
            self.show_message('warning', "No Selection", "Please select a team to edit!")
    
    def delete_team(self):
        """Delete selected team"""
        selected = self.teams_table.selectedItems()
        if selected:
            team_id = int(self.teams_table.item(selected[0].row(), 0).text())
            team_name = self.teams_table.item(selected[0].row(), 1).text()
            
            reply = self.show_message('question', "Confirm Delete", f"Are you sure you want to delete team: {team_name}?", buttons=QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                cursor = db.conn.cursor()
                cursor.execute("DELETE FROM teams WHERE id = ?", (team_id,))
                db.conn.commit()
                self.load_data()
                self.data_updated.emit()
        else:
            self.show_message('warning', "No Selection", "Please select a team to delete!")
    
    def export_players_to_pdf(self):
        """Export all players list to PDF ordered by ID"""
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib import colors
            from datetime import datetime
            
        except ImportError:
            self.show_message('warning', "Missing Library", 
                            "ReportLab library is not installed.\n\n"
                            "Please install it using:\n"
                            "pip install reportlab")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"players_list_{timestamp}.pdf"
            
            # Create PDF document
            doc = SimpleDocTemplate(filename, pagesize=landscape(A4), topMargin=0.5*inch, bottomMargin=0.5*inch)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#10b981'),
                spaceAfter=6,
                alignment=1
            )
            story.append(Paragraph("TPL AUCTION - PLAYERS LIST", title_style))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Get all players ordered by ID
            cursor = db.conn.cursor()
            cursor.execute('''
                SELECT p.*, t.name as team_name 
                FROM players p 
                LEFT JOIN teams t ON p.sold_to_team = t.id 
                ORDER BY p.id
            ''')
            players = cursor.fetchall()
            
            # Create players table
            table_data = [['#', 'Name', 'Faculty', 'Role', 'Batting', 'Bowling', 
                          'Base Price', 'Status', 'Current Bid', 'Team', 'Sold Price']]
            
            for count, player in enumerate(players, 1):
                table_data.append([
                    str(count),  # Serial number starting from 1
                    player['name'][:22] if player['name'] else '-',
                    player['faculty'][:14] if player['faculty'] else '-',
                    player['player_role'][:11] if player['player_role'] else '-',
                    player['batting_style'][:10] if player['batting_style'] else '-',
                    player['bowling_style'][:10] if player['bowling_style'] else '-',
                    f"{int(player['base_price']):,}",
                    player['status'][:8],
                    f"{int(player['current_bid']):,}",
                    player['team_name'][:12] if player['team_name'] else '-',
                    f"{int(player['sold_price']):,}" if player['sold_price'] else '-'
                ])
            
            # Create table with custom column widths
            col_widths = [0.3*inch, 1.3*inch, 0.9*inch, 0.75*inch, 0.7*inch, 0.7*inch,
                         0.75*inch, 0.6*inch, 0.75*inch, 0.8*inch, 0.75*inch]
            
            players_table = Table(table_data, colWidths=col_widths)
            players_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Center # column
                ('ALIGN', (1, 0), (5, -1), 'LEFT'),    # Left align text columns
                ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),  # Right align price columns
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            story.append(players_table)
            story.append(Spacer(1, 0.2*inch))
            
            # Summary statistics
            total_players = len(players)
            sold_players = sum(1 for p in players if p['status'] == 'SOLD')
            unsold_players = sum(1 for p in players if p['status'] == 'UNSOLD')
            upcoming_players = sum(1 for p in players if p['status'] == 'UPCOMING')
            
            summary_text = f"<b>Summary:</b> Total Players: {total_players} | Sold: {sold_players} | Unsold: {unsold_players} | Upcoming: {upcoming_players}"
            story.append(Paragraph(summary_text, styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            # Get absolute path
            abs_path = os.path.abspath(filename)
            
            self.show_message('info', "Export Successful", f"Players list exported to:\n{abs_path}")
            self.status_bar.showMessage(f"PDF exported: {filename}")
            
        except Exception as e:
            import traceback
            error_log = "export_error.log"
            try:
                with open(error_log, "a", encoding="utf-8") as f:
                    f.write("\n==== Players PDF Export Error ====\n")
                    f.write(f"Timestamp: {datetime.now()}\n")
                    f.write(traceback.format_exc())
                    f.write("\n")
            except:
                pass
            
            self.show_message('warning', "Export Failed", 
                            f"Error exporting PDF:\n{str(e)}\n\n"
                            f"Error details saved to: {os.path.abspath(error_log)}")

    def export_summary(self):
        """Export summary to PDF with team-by-team breakdown"""
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
            from reportlab.lib import colors
            from datetime import datetime
            import os
            
        except ImportError:
            self.show_message('warning', "Missing Library", 
                            "ReportLab library is not installed.\n\n"
                            "Please install it using:\n"
                            "pip install reportlab")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"auction_summary_{timestamp}.pdf"
            
            # Create PDF document
            doc = SimpleDocTemplate(filename, pagesize=landscape(A4), topMargin=0.5*inch, bottomMargin=0.5*inch)
            story = []
            styles = getSampleStyleSheet()
            
            # Helper function to resolve image paths
            def resolve_image_path(path):
                if not path:
                    return None
                if os.path.isabs(path) and os.path.exists(path):
                    return path
                base_dir = os.path.dirname(os.path.abspath(__file__))
                candidate = os.path.abspath(os.path.join(base_dir, path))
                if os.path.exists(candidate):
                    return candidate
                candidate = os.path.abspath(path)
                if os.path.exists(candidate):
                    return candidate
                return None
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#10b981'),
                spaceAfter=6,
                alignment=1
            )
            story.append(Paragraph("TPL AUCTION - UNIVERSITY OF VAVUNIYA", title_style))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Get summary data
            summary = db.get_auction_summary()
            
            # Statistics section
            stats_style = ParagraphStyle(
                'StatHeader',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.HexColor('#ffffff'),
                backColor=colors.HexColor('#10b981'),
                spaceAfter=6
            )
            story.append(Paragraph("AUCTION STATISTICS", stats_style))
            
            stats_data = [
                ['Total Players', str(summary['total_players'])],
                ['Sold Players', str(summary['sold_players'])],
                ['Unsold Players', str(summary['unsold_players'])],
                ['Total Spent (LKR)', f"Rs. {summary['total_spent']:,.0f}"]
            ]
            
            stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Get players by team and team logos
            players_by_team = db.get_players_by_team()
            
            # Get team logos from database
            cursor = db.conn.cursor()
            cursor.execute("SELECT id, name, logo_path FROM teams ORDER BY name")
            teams_with_logos = {team['name']: team['logo_path'] for team in cursor.fetchall()}
            
            # Team-by-team breakdown
            team_header_style = ParagraphStyle(
                'TeamHeader',
                parent=styles['Heading2'],
                fontSize=11,
                textColor=colors.HexColor('#ffffff'),
                backColor=colors.HexColor('#3b82f6'),
                spaceAfter=8
            )
            
            for team_data in summary['teams']:
                team_name = team_data['name']
                team_budget = team_data['budget']
                team_spent = team_data['spent']
                team_remaining = team_budget - team_spent
                
                # Team header with logo
                team_header_text = f"{team_name} | Budget: Rs. {team_budget:,.0f} | Spent: Rs. {team_spent:,.0f} | Remaining: Rs. {team_remaining:,.0f}"
                
                # Try to add team logo next to header
                logo_path = resolve_image_path(teams_with_logos.get(team_name))
                if logo_path:
                    try:
                        # Create a table with logo and header text
                        logo_img = Image(logo_path, width=0.5*inch, height=0.5*inch)
                        header_table = Table([[logo_img, Paragraph(team_header_text, team_header_style)]], 
                                           colWidths=[0.6*inch, 9*inch])
                        header_table.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                        ]))
                        story.append(header_table)
                    except:
                        # If logo fails, just use text header
                        story.append(Paragraph(team_header_text, team_header_style))
                else:
                    story.append(Paragraph(team_header_text, team_header_style))
                
                # Team players table
                team_players = players_by_team.get(team_name, [])
                
                if team_players:
                    table_data = [['#', 'Player Name', 'Faculty', 'Role', 'Sold Price (LKR)']]
                    
                    for idx, player in enumerate(team_players, 1):
                        table_data.append([
                            str(idx),
                            player['player_name'],
                            player['faculty'] if player['faculty'] else '-',
                            player['player_role'] if player['player_role'] else '-',
                            f"Rs. {player['sold_price']:,.0f}"
                        ])
                    
                    team_table = Table(table_data, colWidths=[0.4*inch, 2.2*inch, 1.2*inch, 1.2*inch, 1.5*inch])
                    team_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
                    ]))
                    story.append(team_table)
                else:
                    story.append(Paragraph("No players purchased", styles['Normal']))
                
                story.append(Spacer(1, 0.25*inch))
                
                # Page break for readability (except on last team)
                if team_name != summary['teams'][-1]['name']:
                    story.append(PageBreak())
            
            # Build PDF
            doc.build(story)
            
            # Get absolute path
            abs_path = os.path.abspath(filename)
            
            self.show_message('info', "Export Successful", f"Auction summary exported to:\n{abs_path}")
            self.status_bar.showMessage(f"PDF exported: {filename}")
            
        except Exception as e:
            import traceback
            error_log = "export_error.log"
            try:
                with open(error_log, "a", encoding="utf-8") as f:
                    f.write("\n==== PDF Export Error ====\n")
                    f.write(f"Timestamp: {datetime.now()}\n")
                    f.write(traceback.format_exc())
                    f.write("\n")
            except:
                pass
            
            self.show_message('warning', "Export Failed", 
                            f"Error exporting PDF:\n{str(e)}\n\n"
                            f"Error details saved to: {os.path.abspath(error_log)}")


class PlayerDialog(QDialog):
    """Dialog for adding/editing players with image upload"""
    
    def __init__(self, parent=None, player_id=None):
        super().__init__(parent)
        self.player_id = player_id
        self.setup_ui()
        if player_id:
            self.load_player_data()
    
    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("Add Player" if not self.player_id else "Edit Player")
        self.setModal(True)
        self.setFixedSize(600, 600)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Player name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter player name")
        
        # Base price in LKR
        self.base_price_edit = QDoubleSpinBox()
        self.base_price_edit.setRange(0, 10000000)
        self.base_price_edit.setSingleStep(1000)
        self.base_price_edit.setDecimals(0)
        self.base_price_edit.setPrefix("Rs. ")
        self.base_price_edit.setSuffix(" LKR")
        # Ensure spinbox text is visible on dark background
        self.base_price_edit.setStyleSheet("""
            QDoubleSpinBox {
                color: #ffffff;
                background-color: #22293b;
                border: 1px solid #3f8a57;
                padding: 4px;
            }
            QDoubleSpinBox QLineEdit { color: #ffffff; }
        """)
        
        # Faculty
        self.faculty_combo = QComboBox()
        self.faculty_combo.addItems([
            "Technology", "Applied", "Business Studies", 
             "Other"
        ])
        
        # Player Role
        self.role_combo = QComboBox()
        self.role_combo.addItems([
            "Batsman", "Bowler", "Wicket keeper Batsman",
            "Batting Allrounder", "Bowling Allrounder"
        ])
        
        # Batting Style
        self.batting_combo = QComboBox()
        self.batting_combo.addItems([
            "Right Hand Batsman", "Left Hand Batsman"
        ])
        
        # Bowling Style
        self.bowling_combo = QComboBox()
        self.bowling_combo.addItems([
            "Right arm fast", "Left arm fast", 
            "Right arm spin", "Left arm spin", "Not Applicable"
        ])
        
        # Image upload
        self.image_path_edit = QLineEdit()
        self.image_path_edit.setPlaceholderText("Select player image...")
        
        browse_btn = QPushButton("📁 Browse Image")
        browse_btn.clicked.connect(self.browse_image)
        
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.image_path_edit)
        image_layout.addWidget(browse_btn)
        
        # Image preview
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(200, 200)
        self.image_preview.setStyleSheet("""
            QLabel {
                border: 2px solid #4CAF50;
                border-radius: 10px;
                background-color: #2d2d44;
            }
        """)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setText("No Image\nSelected")
        
        form_layout.addRow("Player Name:", self.name_edit)
        form_layout.addRow("Base Price (LKR):", self.base_price_edit)
        form_layout.addRow("Faculty:", self.faculty_combo)
        form_layout.addRow("Player Role:", self.role_combo)
        form_layout.addRow("Batting Style:", self.batting_combo)
        form_layout.addRow("Bowling Style:", self.bowling_combo)
        form_layout.addRow("Player Image:", image_layout)
        form_layout.addRow("Image Preview:", self.image_preview)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 SAVE")
        save_btn.clicked.connect(self.save_player)
        save_btn.setProperty("class", "success")
        
        cancel_btn = QPushButton("❌ CANCEL")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setProperty("class", "danger")
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def browse_image(self):
        """Browse for player image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Player Image", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.image_path_edit.setText(file_path)
            
            # Show preview
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(190, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_preview.setPixmap(scaled)
            else:
                self.image_preview.setText("Invalid\nImage")
    
    def load_player_data(self):
        """Load existing player data"""
        cursor = db.conn.cursor()
        cursor.execute("SELECT * FROM players WHERE id = ?", (self.player_id,))
        player = cursor.fetchone()
        
        if player:
            self.name_edit.setText(player['name'])
            self.base_price_edit.setValue(player['base_price'])
            
            # Faculty
            if player['faculty']:
                index = self.faculty_combo.findText(player['faculty'])
                if index >= 0:
                    self.faculty_combo.setCurrentIndex(index)
            
            # Player Role
            if player['player_role']:
                index = self.role_combo.findText(player['player_role'])
                if index >= 0:
                    self.role_combo.setCurrentIndex(index)
            
            # Batting Style
            if player['batting_style']:
                index = self.batting_combo.findText(player['batting_style'])
                if index >= 0:
                    self.batting_combo.setCurrentIndex(index)
            
            # Bowling Style
            if player['bowling_style']:
                index = self.bowling_combo.findText(player['bowling_style'])
                if index >= 0:
                    self.bowling_combo.setCurrentIndex(index)
            
            # Image
            if player['image_path']:
                self.image_path_edit.setText(player['image_path'])
                if os.path.exists(player['image_path']):
                    pixmap = QPixmap(player['image_path'])
                    if not pixmap.isNull():
                        scaled = pixmap.scaled(190, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.image_preview.setPixmap(scaled)
    
    def save_player(self):
        """Save player to database with image handling"""
        name = self.name_edit.text().strip()
        base_price_lkr = self.base_price_edit.value()
        faculty = self.faculty_combo.currentText()
        player_role = self.role_combo.currentText()
        batting_style = self.batting_combo.currentText()
        bowling_style = self.bowling_combo.currentText()
        image_path = self.image_path_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Error", "Player name is required!")
            return
        
        # Process image
        processed_image_path = ""
        if image_path and os.path.exists(image_path):
            try:
                # Create players directory
                os.makedirs("images/players", exist_ok=True)
                
                # Generate safe filename
                safe_name = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
                safe_name = ''.join(c for c in safe_name if c.isalnum() or c in ('_', '-', '.'))
                
                # Use player_id if available
                if self.player_id:
                    filename = f"player_{self.player_id}.png"
                else:
                    # Get next player ID
                    cursor = db.conn.cursor()
                    cursor.execute("SELECT MAX(id) FROM players")
                    max_id = cursor.fetchone()[0] or 0
                    filename = f"player_{max_id + 1}.png"
                
                dest_path = os.path.join("images/players", filename)
                
                # Copy image
                shutil.copy2(image_path, dest_path)
                processed_image_path = dest_path
                
            except Exception as e:
                print(f"Image copy error: {e}")
                processed_image_path = image_path  # Use original path as fallback
        
        cursor = db.conn.cursor()
        
        if self.player_id:
            # Update existing player
            cursor.execute('''
                UPDATE players 
                SET name = ?, base_price = ?, faculty = ?, player_role = ?, 
                    batting_style = ?, bowling_style = ?, image_path = ?
                WHERE id = ?
            ''', (name, base_price_lkr, faculty, player_role, 
                  batting_style, bowling_style, processed_image_path, self.player_id))
        else:
            # Insert new player
            cursor.execute('''
                INSERT INTO players (name, base_price, faculty, player_role, 
                                   batting_style, bowling_style, image_path) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, base_price_lkr, faculty, player_role, 
                  batting_style, bowling_style, processed_image_path))
            
            # Get the new player ID and update image filename
            player_id = cursor.lastrowid
            if processed_image_path and player_id:
                try:
                    new_filename = f"player_{player_id}.png"
                    new_path = os.path.join("images/players", new_filename)
                    
                    # Rename the file
                    if os.path.exists(processed_image_path):
                        os.rename(processed_image_path, new_path)
                        
                        # Update database with new path
                        cursor.execute('''
                            UPDATE players SET image_path = ? WHERE id = ?
                        ''', (new_path, player_id))
                except:
                    pass
        
        db.conn.commit()
        self.accept()


class TeamDialog(QDialog):
    """Dialog for adding/editing teams with logo upload"""
    
    def __init__(self, parent=None, team_id=None):
        super().__init__(parent)
        self.team_id = team_id
        self.setup_ui()
        if team_id:
            self.load_team_data()
    
    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("Add Team" if not self.team_id else "Edit Team")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter team name (e.g., Western Bulls)")
        
        self.budget_edit = QDoubleSpinBox()
        self.budget_edit.setRange(0, 100000000)
        self.budget_edit.setSingleStep(10000)
        self.budget_edit.setDecimals(0)
        self.budget_edit.setPrefix("Rs. ")
        self.budget_edit.setSuffix(" LKR")
        self.budget_edit.setValue(1000000)
        # Ensure spinbox text is visible on dark background
        self.budget_edit.setStyleSheet("""
            QDoubleSpinBox {
                color: #ffffff;
                background-color: #22293b;
                border: 1px solid #3366ff;
                padding: 4px;
                font-weight: bold;
            }
            QDoubleSpinBox QLineEdit { color: #ffffff; }
        """)
        
        # Logo upload
        self.logo_path_edit = QLineEdit()
        self.logo_path_edit.setPlaceholderText("Select team logo...")
        
        browse_btn = QPushButton("📁 Browse Logo")
        browse_btn.clicked.connect(self.browse_logo)
        
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.logo_path_edit)
        logo_layout.addWidget(browse_btn)
        
        # Logo preview
        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(150, 150)
        self.logo_preview.setStyleSheet("""
            QLabel {
                border: 2px solid #3366ff;
                border-radius: 10px;
                background-color: #2d2d44;
            }
        """)
        self.logo_preview.setAlignment(Qt.AlignCenter)
        self.logo_preview.setText("No Logo\nSelected")
        
        form_layout.addRow("Team Name:", self.name_edit)
        form_layout.addRow("Budget (LKR):", self.budget_edit)
        form_layout.addRow("Team Logo:", logo_layout)
        form_layout.addRow("Logo Preview:", self.logo_preview)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 SAVE")
        save_btn.clicked.connect(self.save_team)
        save_btn.setProperty("class", "success")
        
        cancel_btn = QPushButton("❌ CANCEL")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setProperty("class", "danger")
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def browse_logo(self):
        """Browse for team logo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Team Logo", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.logo_path_edit.setText(file_path)
            
            # Show preview
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.logo_preview.setPixmap(scaled)
            else:
                self.logo_preview.setText("Invalid\nLogo")
    
    def load_team_data(self):
        """Load existing team data"""
        cursor = db.conn.cursor()
        cursor.execute("SELECT * FROM teams WHERE id = ?", (self.team_id,))
        team = cursor.fetchone()
        
        if team:
            self.name_edit.setText(team['name'])
            self.budget_edit.setValue(team['budget'])
            
            # Logo
            if team['logo_path']:
                self.logo_path_edit.setText(team['logo_path'])
                if os.path.exists(team['logo_path']):
                    pixmap = QPixmap(team['logo_path'])
                    if not pixmap.isNull():
                        scaled = pixmap.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.logo_preview.setPixmap(scaled)
    
    def save_team(self):
        """Save team to database with logo handling"""
        name = self.name_edit.text().strip()
        budget_lkr = self.budget_edit.value()
        logo_path = self.logo_path_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Error", "Team name is required!")
            return
        
        # Process logo
        processed_logo_path = ""
        if logo_path and os.path.exists(logo_path):
            try:
                # Create teams directory
                os.makedirs("images/teams", exist_ok=True)
                
                # Generate safe filename
                safe_name = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
                safe_name = ''.join(c for c in safe_name if c.isalnum() or c in ('_', '-', '.'))
                
                # Use team_id if available
                if self.team_id:
                    filename = f"team_{self.team_id}.png"
                else:
                    # Get next team ID
                    cursor = db.conn.cursor()
                    cursor.execute("SELECT MAX(id) FROM teams")
                    max_id = cursor.fetchone()[0] or 0
                    filename = f"team_{max_id + 1}.png"
                
                dest_path = os.path.join("images/teams", filename)
                
                # Copy logo
                shutil.copy2(logo_path, dest_path)
                processed_logo_path = dest_path
                
            except Exception as e:
                print(f"Logo copy error: {e}")
                processed_logo_path = logo_path  # Use original path as fallback
        
        cursor = db.conn.cursor()
        
        if self.team_id:
            cursor.execute('''
                UPDATE teams 
                SET name = ?, budget = ?, logo_path = ?
                WHERE id = ?
            ''', (name, budget_lkr, processed_logo_path, self.team_id))
        else:
            cursor.execute('''
                INSERT INTO teams (name, budget, logo_path) 
                VALUES (?, ?, ?)
            ''', (name, budget_lkr, processed_logo_path))
            
            # Get the new team ID and update logo filename
            team_id = cursor.lastrowid
            if processed_logo_path and team_id:
                try:
                    new_filename = f"team_{team_id}.png"
                    new_path = os.path.join("images/teams", new_filename)
                    
                    # Rename the file
                    if os.path.exists(processed_logo_path):
                        os.rename(processed_logo_path, new_path)
                        
                        # Update database with new path
                        cursor.execute('''
                            UPDATE teams SET logo_path = ? WHERE id = ?
                        ''', (new_path, team_id))
                except:
                    pass
        
        db.conn.commit()
        self.accept()