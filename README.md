# TPL Cricket Auction System 🏏

A fully-featured, dual-screen desktop application built for the **Technology Premier League (TPL)** cricket tournament at the **University of Vavuniya**. This software facilitates live player auctions with real-time projector displays, bidding controls, and budget management.

## Features

*   **Dual-Screen Architecture:**
    *   **Admin Panel:** A comprehensive control center for managing the auction, bidding, players, and teams.
    *   **Projector Display:** A clean, high-visibility live screen intended for the audience/bidders, showing the current player, live bids, leading team, and auction status.
*   **Real-time Bidding Engine:** Live bid updates, dynamic team assignment, and a customizable countdown timer (with visual and audio cues).
*   **Player & Team Management:**
    *   Add/Edit players with images, roles, base prices, and university faculties.
    *   Manage teams with custom logos, budgets, and roster size limits.
*   **Live Dashboard & Statistics:** Track team spending, remaining budget, roster slots, and view the history of winning bids.
*   **Customizable Auction Settings:** Easily change the Auction Name and Organization Name directly from the admin panel (updates live on the projector).
*   **Persistent Storage:** Uses SQLite to ensure auction data (bids, budgets, sold/unsold status) is safely stored and recoverable.
*   **Dark Mode UI:** A premium, modern dark-themed interface built with PyQt5.

## Installation

1.  **Prerequisites:** Ensure you have Python 3.8+ installed on your system.
2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Thiwanka-work/cricket_auction_system.git
    cd cricket_auction_system
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Main requirement is `PyQt5`)*

## How to Run

Launch the application by running the main Python file:

```bash
python main.py
```

## Admin Controls Guide

The Admin Panel is divided into several tabs for easy navigation:

### 1. 🎯 AUCTION (Main Dashboard)
This is the live control center during the auction.
*   **Current Player:** Displays the active player's details, base price, and current bid.
*   **Action Controls:** `NEXT PLAYER`, `PREV PLAYER`, `SOLD` (assigns player to leading team and deducts budget), and `UNSOLD`.
*   **Fast Team Selection:** Click a team's button to quickly assign the current leading bid to them.
*   **Bid Management:** Use the quick increment buttons (+1000, +2000, +5000) or enter a custom amount to update the current bid. Includes a `PASS` button for tracking consecutive passes.
*   **System Utilities (Bottom):**
    *   **Projector View:** Switch the live screen between the `BID VIEW` (current player) and `SUMMARY VIEW` (team rosters and budgets).
    *   **Display Window:** Open a `PREVIEW` on your admin monitor or launch the full-screen `PROJECTOR WINDOW`.
    *   **Auction State:** `START` or `STOP` the auction. Use `RERUN UNSOLD` to bring unsold players back into the pool.
    *   **Countdown:** Enable, set duration, and control (Start/Pause/Reset) the bidding timer.

### 2. 👤 PLAYERS
Manage the player pool.
*   Click `ADD PLAYER` to input details and upload a photo.
*   The table shows the real-time status of all players (Upcoming, Sold, Unsold).
*   **Refund/Unsold Action:** For sold players, a small red "Unsold" button appears in the action column. Clicking this will revert the player to unsold status and instantly refund the team's budget.

### 3. 🛡️ TEAMS
Manage the participating teams.
*   Click `ADD TEAM` to set the team name, total budget, maximum roster size (`max_players`), and upload a team logo.

### 4. 📜 BIDS
A read-only log showing the final sold history (winning bids only).

### 5. 📊 SUMMARY
A high-level overview comparing all teams' total budgets, spent amounts, and remaining funds.

### 6. 👥 TEAM ROSTERS
A detailed breakdown of each team.
*   Shows a progress bar of filled roster slots (e.g., 7/11 players).
*   Lists all the specific players acquired by each team.

## Project Structure

*   `main.py`: Entry point for the application.
*   `admin_window.py`: Core logic and UI for the Administrator control panel.
*   `display_window.py`: Logic and UI for the public-facing projector screen.
*   `database.py`: SQLite database operations and schema definitions.
*   `styles.py`: Centralized CSS/styling definitions for the PyQt5 widgets.
*   `images/`: Directory storing uploaded player and team photos.
*   `fonts/`: Directory for custom fonts.

## License
Created for the University of Vavuniya. All rights reserved.
