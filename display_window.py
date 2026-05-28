import os
from typing import cast, Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QFrame,
    QVBoxLayout, QHBoxLayout, QSizePolicy, QBoxLayout, QScrollArea,
    QStackedWidget, QProgressBar, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve, QPoint, QVariantAnimation
from PyQt5.QtGui import QPixmap, QFont, QKeyEvent, QPainter, QPen, QColor, QFontDatabase
import urllib.request
import ssl
import tempfile

from database import db


STYLE = """
#root {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #060c1f,
        stop:1 #0f2b63
    );
    font-family: "Montserrat", "Segoe UI", sans-serif;
}

QLabel { color: white; }

/* HEADER */
#header-title {
    /* size now controlled in code */
    font-weight: 900;
    color: #ffcc33;
}

#header-subtitle {
    /* size now controlled in code */
    font-weight: 700;
    color: #b8c7ff;
}

/* PLAYER */
#player-name {
    /* size now controlled in code */
    font-weight: 900;
}

#faculty {
    /* size now controlled in code */
    font-weight: 800;
    color: #ffcc33;
}

/* PLAYER CARD */
#player-card {
    background-color: rgba(0,0,0,0.35);
    border-radius: 26px;
    border: 2px solid rgba(255,204,51,0.6);
}

/* INFO CARD */
.card {
    background-color: rgba(255,255,255,0.07);
    border-radius: 24px;
}

.card-title {
    /* size now controlled in code */
    font-weight: 700;
    color: #9fb2ff;
}

.card-value {
    /* size now controlled in code */
    font-weight: 900;
}

/* CURRENT BID */
#bid {
    /* size now controlled in code */
    font-weight: 900;
    color: #00ffae;
}

/* PLAYER TYPE */
.type-value {
    /* size now controlled in code */
    font-weight: 900;
}

/* FOOTER */
#footer {
    color: #9fb2ff;
    /* size now controlled in code */
}
"""


class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setScaledContents(False)
        self.original = None

    def setImage(self, pix: QPixmap):
        if pix is None or pix.isNull():
            self.clearImage()
            return
        self.original = pix
        self.updateImage()

    def clearImage(self):
        self.original = None
        self.setPixmap(QPixmap())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateImage()

    def updateImage(self):
        if self.original:
            scaled_pix = self.original.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled_pix)


class CircularTimer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 60
        self.maximum = 60
        self.setMinimumSize(80, 80)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setVisible(False)
    
    def setValue(self, val, limit=60):
        self.value = val
        self.maximum = limit
        self.update()
        
    def paintEvent(self, event):
        if self.maximum <= 0: return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect().adjusted(5, 5, -5, -5)
        
        # Background circle
        p.setPen(QPen(QColor(50, 50, 50, 150), 6))
        p.drawEllipse(rect)
        
        # Arc
        if self.value <= 10:
            color = QColor(255, 68, 68)
        else:
            color = QColor(0, 255, 174)
            
        p.setPen(QPen(color, 6))
        
        span_angle = int((self.value / self.maximum) * 360 * 16)
        p.drawArc(rect, 90 * 16, span_angle)
        
        # Text
        p.setPen(color)
        font = self.font()
        font.setPixelSize(int(rect.height() * 0.4))
        font.setBold(True)
        p.setFont(font)
        p.drawText(rect, Qt.AlignCenter, str(self.value))


class LiveBadge(QLabel):
    def __init__(self, parent=None):
        super().__init__("● LIVE", parent)
        self.setObjectName("live-badge")
        self.setStyleSheet("""
            QLabel#live-badge {
                background-color: #ff003c;
                color: white;
                font-weight: 900;
                padding: 4px 12px;
                border-radius: 6px;
                font-size: 16px;
            }
        """)
        self.setVisible(False)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._toggle)
        self._visible = True
        
    def start_blink(self):
        self.setVisible(True)
        self._timer.start(800)
        
    def stop_blink(self):
        self._timer.stop()
        self.setVisible(False)
        
    def _toggle(self):
        self._visible = not self._visible
        self.setStyleSheet(f"""
            QLabel#live-badge {{
                background-color: {'#ff003c' if self._visible else '#880020'};
                color: {'white' if self._visible else '#dddddd'};
                font-weight: 900;
                padding: 4px 12px;
                border-radius: 6px;
                font-size: 16px;
            }}
        """)


class SoldBadge(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sold-badge")
        self.setStyleSheet("""
            QFrame#sold-badge {
                background-color: rgba(200, 0, 0, 0.85);
                border: 6px solid #ffcc00;
                border-radius: 35px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(0)

        self.sold_label = QLabel("SOLD")
        self.sold_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sold_label)

        # Size will be controlled dynamically


class TeamSummaryView(QWidget):
    """Full-screen team progress summary for projector display."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            #summary-root {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #020b18,
                    stop:0.5 #061a35,
                    stop:1 #0a0a25
                );
            }
            QLabel { color: white; }
            .ts-title {
                font-size: 22px;
                font-weight: 900;
                color: #38bdf8;
                letter-spacing: 1px;
            }
            .ts-budget {
                font-size: 18px;
                font-weight: 700;
                color: #10b981;
            }
            .ts-spent {
                font-size: 16px;
                font-weight: 600;
                color: #ef4444;
            }
            .ts-players {
                font-size: 16px;
                font-weight: 700;
                color: #f59e0b;
            }
            QProgressBar {
                border: 2px solid #1e3a5f;
                border-radius: 8px;
                background: #0f2040;
                text-align: center;
                color: white;
                font-weight: 700;
                font-size: 14px;
                min-height: 22px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10b981, stop:1 #3b82f6
                );
                border-radius: 6px;
            }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        root = QWidget()
        root.setObjectName("summary-root")
        self.root = root
        outer.addWidget(root)

        self._main_layout = QVBoxLayout(root)
        self._main_layout.setContentsMargins(40, 30, 40, 30)
        self._main_layout.setSpacing(20)

        # ── Header ──────────────────────────────────────────────────────────
        self.sum_title = QLabel("TEAM SUMMARY")
        self.sum_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sum_title.setStyleSheet("""
            font-size: 48px;
            font-weight: 900;
            color: #ffcc33;
            letter-spacing: 4px;
        """)
        self._main_layout.addWidget(self.sum_title)

        # ── Scroll area for team cards ───────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        self._main_layout.addWidget(scroll, 1)

        self._cards_container = QWidget()
        self._cards_container.setStyleSheet("background: transparent;")
        self._grid = QGridLayout(self._cards_container)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setHorizontalSpacing(20)
        self._grid.setVerticalSpacing(20)
        scroll.setWidget(self._cards_container)

        self._card_widgets = []

    def refresh(self, teams_data):
        """Rebuild team cards from fresh data."""
        # Clear old cards
        for w in self._card_widgets:
            self._grid.removeWidget(w)
            w.deleteLater()
        self._card_widgets.clear()

        cols = 3 if len(teams_data) > 4 else (2 if len(teams_data) > 1 else 1)

        for idx, team in enumerate(teams_data):
            card = self._build_card(team)
            row, col = divmod(idx, cols)
            self._grid.addWidget(card, row, col)
            self._card_widgets.append(card)

    def _build_card(self, team):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(14,30,60,0.95),
                    stop:1 rgba(8,18,42,0.95)
                );
                border: 2px solid #1e3a5f;
                border-radius: 22px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)

        # Top row: logo + name + budget
        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        # Logo
        logo_label = QLabel()
        logo_label.setFixedSize(100, 100)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("""
            QLabel {
                background: #0f2040;
                border: 3px solid #3b82f6;
                border-radius: 14px;
            }
        """)
        logo_path = team.get('logo_path', '')
        if logo_path and os.path.exists(logo_path):
            pix = QPixmap(logo_path)
            if not pix.isNull():
                logo_label.setPixmap(pix.scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        if logo_label.pixmap() is None or logo_label.pixmap().isNull():
            logo_label.setText("🏆")
            logo_label.setStyleSheet(logo_label.styleSheet() + "font-size: 36px;")

        top_row.addWidget(logo_label)

        # Name + budget
        info_col = QVBoxLayout()
        info_col.setSpacing(6)

        name_lbl = QLabel(team['name'].upper())
        name_lbl.setStyleSheet("""
            font-size: 28px;
            font-weight: 900;
            color: #38bdf8;
            letter-spacing: 1px;
        """)
        name_lbl.setWordWrap(True)

        remaining_budget = team['budget'] - team['spent']
        budget_lbl = QLabel(f"💰 Remaining: Rs. {remaining_budget:,.0f}")
        budget_lbl.setStyleSheet("font-size: 18px; font-weight: 700; color: #10b981;")

        spent_lbl = QLabel(f"💸 Spent: Rs. {team['spent']:,.0f}")
        spent_lbl.setStyleSheet("font-size: 16px; font-weight: 600; color: #ef4444;")

        info_col.addWidget(name_lbl)
        info_col.addWidget(budget_lbl)
        info_col.addWidget(spent_lbl)
        info_col.addStretch()

        top_row.addLayout(info_col, 1)
        layout.addLayout(top_row)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #1e3a5f; border: 1px solid #1e3a5f;")
        layout.addWidget(sep)

        # Progress bar
        max_p = team.get('max_players', 11)
        sold = team.get('sold_count', 0)
        remaining_slots = max(0, max_p - sold)

        prog_label = QLabel(f"🏏 PLAYERS:  {sold} / {max_p}  |  {remaining_slots} slots left")
        prog_label.setStyleSheet("font-size: 16px; font-weight: 700; color: #f59e0b;")
        layout.addWidget(prog_label)

        progress = QProgressBar()
        progress.setMaximum(max_p)
        progress.setValue(sold)
        progress.setFormat(f"{sold}/{max_p} Players")
        progress.setMinimumHeight(24)
        layout.addWidget(progress)

        # Sold players list (up to 5)
        sold_players = team.get('sold_players', [])
        if sold_players:
            players_lbl = QLabel("Bought Players:")
            players_lbl.setStyleSheet("font-size: 13px; color: #9ca3af; font-weight: 600;")
            layout.addWidget(players_lbl)

            for sp in sold_players[:5]:
                row_w = QHBoxLayout()
                p_name = QLabel(f"  ✔ {sp['name']}")
                p_name.setStyleSheet("font-size: 14px; color: #e2e8f0; font-weight: 600;")
                p_price = QLabel(f"Rs. {sp['sold_price']:,.0f}")
                p_price.setStyleSheet("font-size: 14px; color: #10b981; font-weight: 700;")
                p_price.setAlignment(Qt.AlignmentFlag.AlignRight)
                row_w.addWidget(p_name)
                row_w.addStretch()
                row_w.addWidget(p_price)
                layout.addLayout(row_w)

            if len(sold_players) > 5:
                more_lbl = QLabel(f"  + {len(sold_players) - 5} more...")
                more_lbl.setStyleSheet("font-size: 13px; color: #6b7280; font-style: italic;")
                layout.addWidget(more_lbl)
        else:
            empty_lbl = QLabel("No players bought yet")
            empty_lbl.setStyleSheet("font-size: 14px; color: #4b5563; font-style: italic;")
            layout.addWidget(empty_lbl)

        layout.addStretch()
        return card


class DisplayWindow(QMainWindow):
    def __init__(self, mode="preview", screen=None):
        super().__init__()
        self.mode = mode
        self.display_screen = screen
        self.setWindowTitle("TPL Auction – Display")
        self.setStyleSheet(STYLE)

        self._ui_ready = False
        self._previous_player_status: Optional[str] = None
        self._animation_overlay: Optional[QLabel] = None
        self._drop_animation: Optional[QPropertyAnimation] = None
        self._bid_flash_anim: Optional[QVariantAnimation] = None
        self._last_known_bid = 0

        self._download_and_register_font()
        self.build_ui()
        self.start_timer()

        if self.mode == "projector":
            self.setup_projector_mode()
        else:
            self.setup_preview_mode()

        self.scale_factor = 1.0
        self.updateScaling()

    # ---------- RESIZE / SCALING ----------

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if getattr(self, "_ui_ready", False):
            QTimer.singleShot(50, self.updateAfterResize)

    def updateAfterResize(self):
        """Update UI after resize is complete."""
        self.updateScaling()
        # Force update of images
        if hasattr(self, 'player_image') and self.player_image:
            self.player_image.updateImage()

    def updateScaling(self):
        if not getattr(self, "_ui_ready", False):
            return

        # Base reference resolution
        base_w, base_h = 1920, 1080
        w = max(1, self.width())
        h = max(1, self.height())

        # Calculate scale factors
        scale_w = w / base_w
        scale_h = h / base_h
        
        # Use the smaller ratio to ensure everything fits
        self.scale_factor = min(scale_w, scale_h)
        
        # Clamp scale factor for very small/large screens
        self.scale_factor = max(0.4, min(self.scale_factor, 2.0))
        
        # Apply all responsive adjustments
        self.applyDynamicFonts()
        self.applyDynamicSizes()
        self.applyResponsiveMargins()

    def applyDynamicSizes(self):
        """Resize images and widgets based on scale factor."""
        try:
            s = self.scale_factor
            
            # Player image
            if hasattr(self, 'player_image') and self.player_image:
                player_w = int(520 * s)
                player_h = int(640 * s)
                self.player_image.setMinimumSize(
                    QSize(max(220, player_w), max(280, player_h))
                )
                self.player_image.setMaximumSize(
                    QSize(int(1000 * s), int(1200 * s))
                )
                self._position_sold_badge()
            
            # Team logo in leading team card
            if hasattr(self, 'team_logo') and self.team_logo:
                logo_size = int(100 * s)  # Increased size
                logo_size = max(60, min(logo_size, 160))  # Clamp
                self.team_logo.setFixedSize(logo_size, logo_size)
            
            # Sold badge
            if hasattr(self, 'sold_badge') and self.sold_badge:
                badge_size = int(280 * s)
                badge_size = max(180, min(badge_size, 400))
                self.sold_badge.setFixedSize(badge_size, int(badge_size * 0.5))
                
                # Update font size for sold badge
                if hasattr(self.sold_badge, 'sold_label'):
                    font = self.sold_badge.sold_label.font()
                    font_size = int(52 * s)
                    font_size = max(36, min(font_size, 72))
                    font.setPixelSize(font_size)
                    font.setWeight(QFont.Weight.Black)
                    self.sold_badge.sold_label.setFont(font)
                    self.sold_badge.sold_label.setStyleSheet(f"""
                        QLabel {{
                            font-size: {font_size}px;
                            font-weight: 900;
                            color: white;
                            text-transform: uppercase;
                            letter-spacing: {int(5 * s)}px;
                        }}
                    """)
            
            # Sold badge positioning
            if hasattr(self, 'sold_badge') and self.sold_badge and self.sold_badge.isVisible():
                self._position_sold_badge()
                
        except Exception as e:
            print(f"Dynamic sizing error: {e}")

    def applyResponsiveMargins(self):
        """Adjust margins based on window size."""
        try:
            main_widget = self.centralWidget()
            if not main_widget:
                return
                
            main_layout = main_widget.layout()
            if main_layout:
                # Calculate margins based on window size
                base_margin = int(20 * self.scale_factor)
                base_margin = max(10, min(base_margin, 40))
                
                base_spacing = int(15 * self.scale_factor)
                base_spacing = max(8, min(base_spacing, 25))
                
                main_layout.setContentsMargins(
                    base_margin, base_margin, base_margin, base_margin
                )
                main_layout.setSpacing(base_spacing)
                
            # Update team badges spacing
            if hasattr(self, 'team_badges_layout'):
                badge_spacing = int(12 * self.scale_factor)
                badge_spacing = max(6, min(badge_spacing, 20))
                self.team_badges_layout.setSpacing(badge_spacing)
                
        except Exception as e:
            print(f"Margin adjustment error: {e}")

    def _resolve_image_path(self, path: Optional[str]) -> Optional[str]:
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

    # ---------- MODES ----------

    def setup_projector_mode(self):
        try:
            flags = cast(
                Qt.WindowFlags,
                Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
            )
            self.setWindowFlags(flags)

            if self.display_screen:
                screen_geom = self.display_screen.geometry()
                self.move(screen_geom.x(), screen_geom.y())
                self.setGeometry(screen_geom)
            else:
                self.setGeometry(0, 0, 1920, 1080)

            self.showFullScreen()
        except Exception as e:
            print(f"Projector mode setup error: {e}")

    def setup_preview_mode(self):
        try:
            flags = cast(Qt.WindowFlags, Qt.WindowType.Widget | Qt.WindowType.Window)
            self.setWindowFlags(flags)
            self.setGeometry(100, 100, 1280, 720)
            self.setMinimumSize(800, 600)

            if self.display_screen:
                screen_geom = self.display_screen.geometry()
                x = screen_geom.x() + (screen_geom.width() - 1280) // 2
                y = screen_geom.y() + (screen_geom.height() - 720) // 2
                self.move(x, y)

            self.showMaximized()
        except Exception as e:
            print(f"Preview mode setup error: {e}")

    # ---------- FONTS ----------
    def _download_and_register_font(self):
        try:
            # Bypass SSL verification for font downloads
            original_context = getattr(ssl, '_create_default_https_context', None)
            ssl._create_default_https_context = ssl._create_unverified_context
            
            font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
            os.makedirs(font_dir, exist_ok=True)
            
            fonts = [
                ("Montserrat-Regular.ttf", "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Regular.ttf"),
                ("Montserrat-Bold.ttf", "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Bold.ttf"),
                ("Montserrat-Black.ttf", "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Black.ttf")
            ]
            
            for fname, url in fonts:
                fpath = os.path.join(font_dir, fname)
                if not os.path.exists(fpath):
                    print(f"Downloading {fname}...")
                    urllib.request.urlretrieve(url, fpath)
                QFontDatabase.addApplicationFont(fpath)
                
            # Restore original SSL context
            if original_context:
                ssl._create_default_https_context = original_context
        except Exception as e:
            print(f"Failed to download/register font: {e}")

    # ---------- UI BUILD ----------


    def build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        main = QVBoxLayout(root)
        main.setContentsMargins(20, 15, 20, 15)
        main.setSpacing(15)

        # QStackedWidget: page 0 = player bidding, page 1 = team summary
        self.main_stack = QStackedWidget()

        # ── PAGE 0: Player Bidding View ────────────────────────────────────
        self._player_page = QWidget()
        player_main = QVBoxLayout(self._player_page)
        player_main.setContentsMargins(0, 0, 0, 0)
        player_main.setSpacing(15)

        # Alias for convenience – all remaining build code writes to player_main
        main_alias = player_main

        # HEADER
        header = QHBoxLayout()
        header.setSpacing(20)

        left_h = QVBoxLayout()
        self.header_title = QLabel("TPL AUCTION 2026")
        self.header_title.setObjectName("header-title")

        self.header_subtitle = QLabel("UNIVERSITY OF VAVUNIYA")
        self.header_subtitle.setObjectName("header-subtitle")

        left_h.addWidget(self.header_title)
        left_h.addWidget(self.header_subtitle)

        header.addLayout(left_h)
        header.addStretch()

        self.team_badges_scroll = QScrollArea()
        self.team_badges_scroll.setWidgetResizable(True)
        self.team_badges_scroll.setFrameShape(QFrame.NoFrame)
        self.team_badges_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.team_badges_scroll.setStyleSheet("background: transparent; border: none;")

        self.team_badges_widget = QWidget()
        self.team_badges_layout = QHBoxLayout(self.team_badges_widget)
        self.team_badges_layout.setContentsMargins(0, 0, 0, 0)
        self.team_badges_layout.setSpacing(12)
        self.team_badges_layout.setAlignment(Qt.AlignLeft)
        
        self.team_badges_scroll.setWidget(self.team_badges_widget)
        header.addWidget(self.team_badges_scroll, stretch=1)

        # CENTER

        center = QHBoxLayout()
        center.setSpacing(20)
        center.setContentsMargins(0, 0, 0, 0)

        # PLAYER CARD (LEFT) - GIVE MORE SPACE
        player_card = QFrame()
        player_card.setObjectName("player-card")
        player_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        pc = QVBoxLayout(player_card)
        pc.setContentsMargins(20, 20, 20, 20)
        pc.setSpacing(10)

        self.player_image = ImageLabel()

        self.sold_badge = SoldBadge(player_card)
        self.sold_badge.setVisible(False)
        self.sold_badge.raise_()

        self.player_name = QLabel("PLAYER")
        self.player_name.setObjectName("player-name")
        self.player_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.player_name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.player_name.setWordWrap(True)

        self.faculty = QLabel("")
        self.faculty.setObjectName("faculty")
        self.faculty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.faculty.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.faculty.setWordWrap(True)
        
        self.live_badge = LiveBadge()

        # Add widgets directly without complex stretches
        top_pc = QHBoxLayout()
        top_pc.addStretch()
        top_pc.addWidget(self.live_badge)
        pc.addLayout(top_pc)
        
        pc.addWidget(self.player_image, alignment=Qt.AlignmentFlag.AlignCenter)
        pc.addWidget(self.player_name)
        pc.addWidget(self.faculty)
        pc.addStretch(0)

        self._animation_overlay = QLabel(self)

        self._animation_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._animation_overlay.setScaledContents(False)
        self._animation_overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._animation_overlay.hide()
        self._animation_overlay.raise_()

        # RIGHT PANEL
        right = QVBoxLayout()
        right.setSpacing(15)

        # BASE PRICE CARD
        base = self.info_card("BASE PRICE", "Rs. 0")
        self.base_value = base.value
        base.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        # LEADING TEAM CARD - LEFT ALIGNED WITH LOGO
        team = self.info_card("LEADING TEAM", "-")
        self.team_title = team.title
        self.team_value = team.value

        # Remove existing layout and rebuild with horizontal layout
        old_layout = team.layout()
        if old_layout is not None:
            for i in reversed(range(old_layout.count())):
                item = old_layout.takeAt(i)
                if item:
                    w = item.widget()
                    if w:
                        w.setParent(None)

        hteam = QHBoxLayout()
        if not isinstance(old_layout, QBoxLayout):
            old_layout = QVBoxLayout(team)
        old_layout.addLayout(hteam)
        hteam.setContentsMargins(15, 15, 15, 15)
        hteam.setSpacing(15)

        left_col = QVBoxLayout()
        left_col.setSpacing(5)
        align_left = cast(
            Qt.Alignment,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.team_title.setAlignment(align_left)
        self.team_value.setAlignment(align_left)
        self.team_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.team_value.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        left_col.addWidget(self.team_title)
        left_col.addWidget(self.team_value)

        self.team_logo = QLabel()
        self.team_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.team_logo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.team_logo.setScaledContents(True)

        hteam.addLayout(left_col, 3)  # 75% for text
        hteam.addWidget(self.team_logo, 1)  # 25% for logo

        team.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.team_title.setWordWrap(True)
        self.team_value.setWordWrap(True)

        # CURRENT HIGHEST BID CARD - LABEL LEFT, VALUE CENTERED
        self.bid_card = QFrame()
        self.bid_card.setProperty("class", "card")
        self.bid_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        bc = QVBoxLayout(self.bid_card)
        bc.setContentsMargins(20, 20, 20, 20)
        bc.setSpacing(10)

        # Title label - LEFT ALIGNED at top
        bid_header = QHBoxLayout()
        bt = QLabel("CURRENT HIGHEST BID")
        bt.setObjectName("header-subtitle")
        bt.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        bt.setWordWrap(True)
        bt.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        self.circular_timer = CircularTimer()
        
        bid_header.addWidget(bt)
        bid_header.addWidget(self.circular_timer)
        bc.addLayout(bid_header)

        # Bid value - CENTERED in the remaining space
        self.bid = QLabel("Rs. 0")
        self.bid.setObjectName("bid")
        self.bid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bid.setWordWrap(True)
        self.bid.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.bid.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        
        # Add stretch to push bid value to center
        bc.addStretch(1)
        bc.addWidget(self.bid, 0, Qt.AlignmentFlag.AlignCenter)
        bc.addStretch(1)

        # PLAYER TYPE CARDS
        types = QHBoxLayout()
        types.setSpacing(15)
        self.role = self.type_card("ROLE")
        self.bat = self.type_card("BATTING")
        self.bowl = self.type_card("BOWLING")

        for card in (self.role, self.bat, self.bowl):
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            types.addWidget(card)

        # Add all to right panel
        right.addWidget(base, 1)  # 15% of space
        right.addWidget(team, 1)  # 15% of space
        right.addWidget(self.bid_card, 3)  # 45% of space (largest)
        right.addLayout(types, 1)  # 15% of space

        # Add player card and right panel to center
        center.addWidget(player_card, 40)  # Player card gets 40% of width
        center.addLayout(right, 60)  # Right panel gets 60% of width

        # FOOTER
        footer = QHBoxLayout()
        self.footer = QLabel("AUCTION ACTIVE")
        self.footer.setObjectName("footer")
        footer.addWidget(self.footer)
        footer.addStretch()

        # Assemble player_page layout
        player_main.addLayout(header, 1)
        player_main.addLayout(center, 8)
        player_main.addLayout(footer, 1)

        # ── PAGE 1: Team Summary View ───────────────────────────────────────
        self._summary_view = TeamSummaryView()

        # Wire pages into stacked widget
        self.main_stack.addWidget(self._player_page)   # index 0
        self.main_stack.addWidget(self._summary_view)  # index 1
        self.main_stack.setCurrentIndex(0)

        # Assemble root main layout
        main.addWidget(self.main_stack)

        self._ui_ready = True

    def info_card(self, title_text, value_text):
        f = QFrame()
        f.setProperty("class", "card")
        l = QVBoxLayout(f)
        l.setContentsMargins(20, 20, 20, 20)
        l.setSpacing(5)

        title = QLabel(title_text)
        title.setProperty("class", "card-title")
        title.setWordWrap(True)
        title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        value = QLabel(value_text)
        value.setProperty("class", "card-value")
        value.setWordWrap(True)
        value.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        l.addWidget(title)
        l.addWidget(value)
        l.addStretch(0)

        f.title = title
        f.value = value
        return f

    def type_card(self, title_text):
        f = QFrame()
        f.setProperty("class", "card")
        l = QVBoxLayout(f)
        l.setContentsMargins(15, 15, 15, 15)
        l.setSpacing(5)

        t = QLabel(title_text)
        t.setProperty("class", "card-title")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t.setWordWrap(True)
        t.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        v = QLabel("-")
        v.setProperty("class", "type-value")
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.setWordWrap(True)
        v.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        f.value = v
        l.addWidget(t)
        l.addWidget(v)
        l.addStretch(0)
        return f

    # ---------- TIMER ----------

    def start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)

    # ---------- SOLD ANIMATION ----------

    def trigger_sold_animation(self):
        if not hasattr(self, 'sold_badge') or not self.sold_badge:
            return
        
        if not hasattr(self, 'player_image') or not self.player_image:
            return

        if self._drop_animation and self._drop_animation.state() == QPropertyAnimation.State.Running:
            self._drop_animation.stop()

        # Calculate final position (center of player image)
        img_rect = self.player_image.geometry()
        badge_width = self.sold_badge.width()
        badge_height = self.sold_badge.height()
        
        end_x = img_rect.x() + (img_rect.width() - badge_width) // 2
        end_y = img_rect.y() + (img_rect.height() - badge_height) // 2
        
        # Start position (above the window)
        start_x = end_x
        start_y = -badge_height - 50
        
        # Show and position badge for animation
        self.sold_badge.move(start_x, start_y)
        self.sold_badge.setVisible(True)
        self.sold_badge.raise_()
        
        # Create and start animation
        self._drop_animation = QPropertyAnimation(self.sold_badge, b"pos")
        self._drop_animation.setDuration(800)
        self._drop_animation.setStartValue(QPoint(start_x, start_y))
        self._drop_animation.setEndValue(QPoint(end_x, end_y))
        self._drop_animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        self._drop_animation.start()

    def _on_animation_finished(self):
        pass  # Badge stays visible after animation

    def _trigger_bid_flash(self):
        """Flashes the bid card cyan when a new bid is placed."""
        if not hasattr(self, 'bid_card'): return
        
        if self._bid_flash_anim and self._bid_flash_anim.state() == QPropertyAnimation.State.Running:
            self._bid_flash_anim.stop()
            
        self._bid_flash_anim = QVariantAnimation(self)
        self._bid_flash_anim.setDuration(500)
        self._bid_flash_anim.setStartValue(QColor(0, 255, 174, 150))
        self._bid_flash_anim.setEndValue(QColor(255, 255, 255, 18)) # original rgba(255,255,255,0.07) is roughly 18 alpha
        self._bid_flash_anim.valueChanged.connect(self._on_bid_flash_update)
        self._bid_flash_anim.start()
        
    def _on_bid_flash_update(self, color):
        self.bid_card.setStyleSheet(f"""
            QFrame.card {{
                background-color: rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha() / 255.0:.2f});
                border-radius: 24px;
            }}
        """)

    def _trigger_confetti(self):
        """Overlay confetti celebration on the whole screen."""
        if not self._animation_overlay: return
        
        self._animation_overlay.setGeometry(self.rect())
        
        # Create a simple confetti-like generated pixmap or a celebratory text overlay
        pix = QPixmap(self.size())
        pix.fill(Qt.transparent)
        
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        
        # Dark overlay
        p.fillRect(pix.rect(), QColor(0, 0, 0, 160))
        
        # Get team logo if available
        data = db.get_current_auction_data()
        p_data = data.get("current_player", {})
        team_logo_path = self._resolve_image_path(p_data.get("team_logo"))
        
        rect = pix.rect()
        center_y = rect.height() // 2
        
        if team_logo_path:
            logo_pix = QPixmap(team_logo_path)
            if not logo_pix.isNull():
                l_size = min(rect.width(), rect.height()) // 3
                logo_pix = logo_pix.scaled(l_size, l_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                p.drawPixmap((rect.width() - logo_pix.width()) // 2, center_y - logo_pix.height() // 2 - 50, logo_pix)
                
        p.setPen(QColor("#ffcc00"))
        font = self.font()
        font.setPixelSize(80)
        font.setBold(True)
        p.setFont(font)
        p.drawText(rect.adjusted(0, 50, 0, 50), Qt.AlignCenter, f"SOLD TO {p_data.get('team_name', 'TEAM').upper()}!")
        
        p.end()
        
        self._animation_overlay.setPixmap(pix)
        self._animation_overlay.show()
        self._animation_overlay.raise_()

    def _position_sold_badge(self):
        if not hasattr(self, "sold_badge") or not hasattr(self, "player_image"):
            return
        if not self.sold_badge or not self.player_image:
            return
        if not self.sold_badge.isVisible():
            return

        img_rect = self.player_image.geometry()
        badge_width = self.sold_badge.width()
        badge_height = self.sold_badge.height()

        center_x = img_rect.x() + (img_rect.width() - badge_width) // 2
        center_y = img_rect.y() + (img_rect.height() - badge_height) // 2
        self.sold_badge.move(center_x, center_y)

    # ---------- FONTS ----------

    def applyDynamicFonts(self):
        """Apply responsive font sizes based on window dimensions."""
        try:
            # Get window dimensions
            window_width = max(1, self.width())
            window_height = max(1, self.height())
            
            # Calculate scale based on both dimensions
            width_ratio = window_width / 1920  # Base reference width
            height_ratio = window_height / 1080  # Base reference height
            
            # Use the smaller ratio to ensure everything fits
            font_scale = min(width_ratio, height_ratio)
            font_scale = max(0.5, min(font_scale, 2.0))  # Clamp between 0.5-2.0
            
            # Header fonts
            if hasattr(self, 'header_title'):
                font = self.header_title.font()
                font_size = int(45 * font_scale)  # Reduced from 52
                font_size = max(26, min(font_size, 65))  # Reduced from 28-72
                font.setPixelSize(font_size)
                font.setWeight(QFont.Weight.Black)
                self.header_title.setFont(font)
            
            if hasattr(self, 'header_subtitle'):
                font = self.header_subtitle.font()
                font_size = int(28 * font_scale)
                font_size = max(18, min(font_size, 40))
                font.setPixelSize(font_size)
                font.setWeight(QFont.Weight.Bold)
                self.header_subtitle.setFont(font)
            
            # Player name
            if hasattr(self, 'player_name'):
                font = self.player_name.font()
                font_size = int(48 * font_scale)  # Reduced from 56
                font_size = max(28, min(font_size, 70))  # Reduced from 32-80
                font.setPixelSize(font_size)
                font.setWeight(QFont.Weight.Black)
                self.player_name.setFont(font)
            
            # Faculty
            if hasattr(self, 'faculty'):
                font = self.faculty.font()
                font_size = int(26 * font_scale)
                font_size = max(18, min(font_size, 36))
                font.setPixelSize(font_size)
                font.setWeight(QFont.Weight.ExtraBold)
                self.faculty.setFont(font)
            
            # Current bid - SCALED TO CONTAINER
            if hasattr(self, 'bid'):
                font = self.bid.font()
                if hasattr(self, 'bid_card'):
                    # Use 40% of bid card height for font size (reduced from 50%)
                    bid_height = max(1, self.bid_card.height())
                    font_size = int(bid_height * 0.4)
                else:
                    font_size = int(75 * font_scale)  # Reduced from 94
                
                font_size = max(35, min(font_size, 150))  # Reduced max from 180 to 150
                font.setPixelSize(font_size)
                font.setWeight(QFont.Weight.Black)
                self.bid.setFont(font)
                
                # Scale the "CURRENT HIGHEST BID" label
                for child in self.bid_card.findChildren(QLabel):
                    if child != self.bid and "CURRENT" in child.text().upper():
                        f = child.font()
                        label_size = int(20 * font_scale)  # Reduced from 24
                        label_size = max(14, min(label_size, 30))  # Reduced from 16-36
                        f.setPixelSize(label_size)
                        f.setWeight(QFont.Weight.Bold)
                        child.setFont(f)
            
            # Base price value - SMALLER THAN CURRENT BID
            if hasattr(self, 'base_value'):
                font = self.base_value.font()
                font_size = int(32 * font_scale)  # Increased from 28
                font_size = max(20, min(font_size, 45))  # Increased max from 40 to 45
                font.setPixelSize(font_size)
                font.setWeight(QFont.Weight.Black)
                self.base_value.setFont(font)
            
            # Team name value
            if hasattr(self, 'team_value'):
                font = self.team_value.font()
                font_size = int(32 * font_scale)
                font_size = max(20, min(font_size, 45))
                font.setPixelSize(font_size)
                font.setWeight(QFont.Weight.Black)
                self.team_value.setFont(font)
            
            # Team title
            if hasattr(self, 'team_title'):
                font = self.team_title.font()
                font_size = int(20 * font_scale)
                font_size = max(16, min(font_size, 28))
                font.setPixelSize(font_size)
                font.setWeight(QFont.Weight.ExtraBold)
                self.team_title.setFont(font)
            
            # Card titles / values (roles etc.) - Increased font sizes
            card_title_size = int(26 * font_scale)  # Increased from 22
            card_value_size = int(36 * font_scale)  # Increased from 28
            
            for card in [getattr(self, "role", None),
                         getattr(self, "bat", None),
                         getattr(self, "bowl", None)]:
                if not card:
                    continue
                for child in card.findChildren(QLabel):
                    text = child.text().upper()
                    f = child.font()
                    if text in ("ROLE", "BATTING", "BOWLING"):
                        f.setPixelSize(card_title_size)
                        f.setWeight(QFont.Weight.Bold)
                    else:
                        f.setPixelSize(card_value_size)
                        f.setWeight(QFont.Weight.Black)
                    child.setFont(f)
            
            # Footer
            if hasattr(self, "footer"):
                font = self.footer.font()
                font_size = int(18 * font_scale)
                font_size = max(12, min(font_size, 24))
                font.setPixelSize(font_size)
                font.setWeight(QFont.Weight.Normal)
                self.footer.setFont(font)
                
        except Exception as e:
            print(f"Font scaling error: {e}")

    # ---------- DATA UPDATE ----------

    def update_display(self):
        try:
            data = db.get_current_auction_data()

            # ── Check projector view mode ────────────────────────────────────
            settings = data.get('settings', {})
            view_mode = settings.get('projector_view_mode', 'player')

            if view_mode == 'summary':
                # Switch to summary page and refresh team cards
                if hasattr(self, 'main_stack') and self.main_stack.currentIndex() != 1:
                    self.main_stack.setCurrentIndex(1)
                if hasattr(self, '_summary_view'):
                    teams_data = db.get_team_roster_summary()
                    self._summary_view.sum_title.setText(
                        f"{data.get('auction_name', 'TPL AUCTION 2026')} – TEAM SUMMARY"
                    )
                    self._summary_view.refresh(teams_data)
                return
            else:
                # Switch back to player bidding page
                if hasattr(self, 'main_stack') and self.main_stack.currentIndex() != 0:
                    self.main_stack.setCurrentIndex(0)

            # ── Normal player bidding update ─────────────────────────────────
            self.header_title.setText(str(data.get("auction_name", "TPL AUCTION 2026")).upper())
            self.header_subtitle.setText(str(data.get("org_name", "UNIVERSITY OF VAVUNIYA")).upper())
            p = data.get("current_player")
            leading_team_name = None

            if p:
                try:
                    if p.get("status") == "SOLD":
                        leading_team_name = p.get("team_name")
                    else:
                        leading_team_name = p.get("leading_team")
                except Exception:
                    leading_team_name = None
            else:
                leading_team_name = None

            teams = data.get("teams", [])
            if (not leading_team_name or leading_team_name == "-") and p:
                leading_team_name = p.get("team_name") or leading_team_name

            self.update_team_badges(teams, leading_team_name)

            if not p:
                self.player_name.setText(" READY ")
                self.faculty.setText("")
                self.base_value.setText("Rs. 0")
                self.bid.setText("Rs. 0")
                self.sold_badge.setVisible(False)
                self.team_title.setText("LEADING TEAM")
                self.team_value.setText("-")
                self.role.value.setText("-")
                self.bat.value.setText("-")
                self.bowl.value.setText("-")
                self.player_image.clearImage()
                self.footer.setText(
                    f"AUCTION ACTIVE | REMAINING PLAYERS: {data.get('remaining_players', 0)}"
                )
                self._previous_player_status = None
                return

            current_status = p.get("status")
            player_id = p.get("id")
            status_key = f"{player_id}_{current_status}" if player_id else current_status

            self.player_name.setText(str(p.get("name", "")).upper())
            self.faculty.setText(str(p.get("faculty", "")).upper())

            self.base_value.setText(f"Rs. {int(p.get('base_price', 0)):,}")
            
            # Display bid value without currency prefix
            bid_value = int(p.get('current_bid', 0))
            self.bid.setText(f"{bid_value:,}")
            
            # Bid Flash
            if bid_value > self._last_known_bid and self._last_known_bid != 0 and current_status == "LIVE":
                self._trigger_bid_flash()
            self._last_known_bid = bid_value
            
            # Circular Timer
            if db.countdown_enabled and current_status == "LIVE":
                self.circular_timer.setVisible(True)
                self.circular_timer.setValue(db.countdown_remaining, db.countdown_limit)
            else:
                self.circular_timer.setVisible(False)
                
            # Live Badge
            if current_status == "LIVE":
                if not self.live_badge.isVisible():
                    self.live_badge.start_blink()
            else:
                self.live_badge.stop_blink()

            if p.get("status") == "SOLD":
                # Badge visibility and position handled by animation
                if not self.sold_badge.isVisible():
                    self.sold_badge.setVisible(True)
                    self.sold_badge.raise_()

                self.team_title.setText("SOLD SUCCESSFULLY TO")
                self.team_value.setText(p.get("team_name", "-").upper())
                align_left = cast(
                    Qt.Alignment,
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                )
                self.team_title.setAlignment(align_left)
                self.team_value.setAlignment(align_left)

                team_logo = self._resolve_image_path(p.get("team_logo"))
                if team_logo:
                    pix = QPixmap(team_logo)
                    # Scale to fit logo area while maintaining aspect ratio
                    pix = pix.scaled(self.team_logo.size(), 
                                    Qt.AspectRatioMode.KeepAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation)
                    self.team_logo.setPixmap(pix)
                else:
                    self.team_logo.setPixmap(QPixmap())
            else:
                self.sold_badge.setVisible(False)
                self.team_title.setText("LEADING TEAM")
                leading_team = p.get("leading_team", "-")
                self.team_value.setText(leading_team.upper())

                logo_shown = False
                for t in teams:
                    if t.get("name") and t.get("name").upper() == leading_team.upper():
                        logo_path = self._resolve_image_path(
                            t.get("logo_path") or t.get("team_logo")
                        )
                        if logo_path:
                            pix = QPixmap(logo_path)
                            pix = pix.scaled(self.team_logo.size(),
                                           Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation)
                            self.team_logo.setPixmap(pix)
                            logo_shown = True
                            break
                if not logo_shown:
                    self.team_logo.setPixmap(QPixmap())

            self.role.value.setText(p.get("player_role", "-").upper())
            self.bat.value.setText(p.get("batting_style", "-").upper())
            self.bowl.value.setText(p.get("bowling_style", "-").upper())

            img = self._resolve_image_path(p.get("image_path"))
            player_pixmap = None
            if img:
                player_pixmap = QPixmap(img)
                self.player_image.setImage(player_pixmap)

            if current_status == "SOLD" and self._previous_player_status != status_key:
                QTimer.singleShot(100, self.trigger_sold_animation)
                
            if getattr(db, 'show_confetti', False) and not getattr(self, "_confetti_active", False):
                self._confetti_active = True
                QTimer.singleShot(100, self._trigger_confetti)
            elif not getattr(db, 'show_confetti', False):
                self._confetti_active = False
                if self._animation_overlay and self._animation_overlay.isVisible():
                    self._animation_overlay.hide()

            self._previous_player_status = status_key

            self.footer.setText(
                f"AUCTION ACTIVE | REMAINING PLAYERS: {data.get('remaining_players', 0)}"
            )
        except Exception as e:
            print("Display error:", e)

    # ---------- KEYS ----------

    def keyPressEvent(self, event: Optional[QKeyEvent]):
        if not event:
            return
        if event.key() == Qt.Key.Key_F11:
            self.showNormal() if self.isFullScreen() else self.showFullScreen()
        elif event.key() == Qt.Key.Key_Escape:
            self.showNormal()

    # ---------- TEAM BADGES ----------

    def update_team_badges(self, teams, leading_team=None):
        self.current_leading_team = leading_team

        while self.team_badges_layout.count():
            item = self.team_badges_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        for team in teams:
            try:
                name = team.get("name", "TEAM")
                budget = float(team.get("budget") or 0)
                spent = float(team.get("spent") or 0)
                remaining = budget - spent

                badge = QFrame()
                badge.setObjectName("team-badge")
                
                # Default style
                base_style = """
                    QFrame#team-badge {
                        background-color: rgba(255,255,255,0.04);
                        border: 1px solid rgba(255,255,255,0.1);
                        border-radius: 18px;
                        padding: 8px 12px;
                    }
                """
                
                # Highlight leading team
                if leading_team and name.upper() == str(leading_team).upper():
                    badge.setStyleSheet(base_style + """
                        QFrame#team-badge {
                            border: 2px solid #00ffae;
                            background-color: rgba(0,255,174,0.05);
                        }
                    """)
                else:
                    badge.setStyleSheet(base_style)

                h = QHBoxLayout(badge)
                h.setContentsMargins(6, 6, 6, 6)
                h.setSpacing(10)

                # Team logo - RESPONSIVE
                logo_lbl = QLabel()
                logo_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                logo_lbl.setScaledContents(True)  # Important for responsive scaling
                logo_lbl.setStyleSheet(
                    "border-radius:8px; background: rgba(255,255,255,0.03);"
                )
                logo_path = self._resolve_image_path(
                    team.get("logo_path") or team.get("team_logo")
                )
                if logo_path:
                    pix = QPixmap(logo_path)
                    logo_lbl.setPixmap(pix)

                # Text column
                col = QVBoxLayout()
                col.setSpacing(2)
                
                # Team name - RESPONSIVE FONT
                title = QLabel(name.upper())
                title_font = QFont()
                title_font.setWeight(QFont.Weight.Bold)
                title_font.setPixelSize(int(16 * self.scale_factor))
                title.setFont(title_font)
                title.setStyleSheet("color: #b8c7ff;")
                title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                
                # Budget amount - RESPONSIVE FONT
                amt = QLabel(f"Rs. {int(remaining):,}")
                amt_font = QFont()
                amt_font.setWeight(QFont.Weight.Black)
                amt_font.setPixelSize(int(22 * self.scale_factor))
                amt.setFont(amt_font)
                amt.setStyleSheet("color: #ffcc33;")
                amt.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

                col.addWidget(title)
                col.addWidget(amt)

                # Set fixed but responsive sizes for logo
                logo_size = int(70 * self.scale_factor)
                logo_size = max(50, min(logo_size, 100))
                logo_lbl.setFixedSize(logo_size, logo_size)
                
                # Update logo scaling
                if logo_path:
                    pix = QPixmap(logo_path)
                    pix = pix.scaled(logo_size, logo_size,
                                   Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
                    logo_lbl.setPixmap(pix)

                badge.logo = logo_lbl
                h.addWidget(logo_lbl)
                h.addLayout(col)

                self.team_badges_layout.addWidget(badge)
            except Exception as e:
                print("badge error:", e)