"""
Database setup with player types and image support
"""
import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path="database/auction.db"):
        """Initialize database connection and create tables"""
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        self.seed_data()
        
        # Currency settings - Only LKR
        self.currency = "LKR"

        # ── Runtime shared state (used by both windows) ──────────────────────
        self.countdown_enabled = True     # Show/hide the timer on the display
        self.countdown_limit = 60         # Total seconds per player
        self.countdown_remaining = 60     # Seconds remaining (decremented by admin)
        self.countdown_running = False    # Is the timer actively counting?
        self.show_confetti = False        # Trigger confetti celebration overlay
        self.last_bid_value = 0           # Last confirmed bid value (for flash detection)
    
    def create_tables(self):
        """Create all necessary tables with player types and images"""
        cursor = self.conn.cursor()
        
        # Teams table with logo support
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                logo_path TEXT,
                budget REAL DEFAULT 1000000.0, -- LKR amount
                spent REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Players table with player types and image
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                base_price REAL NOT NULL, -- In LKR
                image_path TEXT,
                faculty TEXT,
                player_role TEXT,
                batting_style TEXT,
                bowling_style TEXT,
                status TEXT DEFAULT 'UPCOMING',
                current_bid REAL DEFAULT 0.0,
                sold_to_team INTEGER,
                sold_price REAL DEFAULT 0.0,
                auction_round INTEGER DEFAULT 1,
                FOREIGN KEY (sold_to_team) REFERENCES teams(id)
            )
        ''')
        
        # Bids table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                team_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                round_number INTEGER DEFAULT 1,
                is_winning_bid INTEGER DEFAULT 0,
                FOREIGN KEY (player_id) REFERENCES players(id),
                FOREIGN KEY (team_id) REFERENCES teams(id)
            )
        ''')
        
        # Auction settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auction_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                is_auction_active INTEGER DEFAULT 0,
                current_player_id INTEGER,
                countdown_duration INTEGER DEFAULT 60,
                countdown_end TIMESTAMP,
                current_round INTEGER DEFAULT 1,
                FOREIGN KEY (current_player_id) REFERENCES players(id)
            )
        ''')

        # Safe schema migrations for older databases
        migrations = [
            "ALTER TABLE auction_settings ADD COLUMN auction_name TEXT DEFAULT 'TPL AUCTION 2026'",
            "ALTER TABLE auction_settings ADD COLUMN org_name TEXT DEFAULT 'UNIVERSITY OF VAVUNIYA'",
            "ALTER TABLE auction_settings ADD COLUMN bid_increment_1 INTEGER DEFAULT 1000",
            "ALTER TABLE auction_settings ADD COLUMN bid_increment_2 INTEGER DEFAULT 2000",
            "ALTER TABLE auction_settings ADD COLUMN bid_increment_3 INTEGER DEFAULT 5000",
            "ALTER TABLE auction_settings ADD COLUMN projector_view_mode TEXT DEFAULT 'player'",
            "ALTER TABLE teams ADD COLUMN max_players INTEGER DEFAULT 11"
        ]
        
        for sql in migrations:
            try:
                cursor.execute(sql)
            except sqlite3.OperationalError:
                pass
        
        self.conn.commit()
    
    def seed_data(self):
        """Insert sample data for testing"""
        cursor = self.conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM teams")
        if cursor.fetchone()[0] == 0:
            # Insert sample teams with LKR budget
            sample_teams = [
                ('Science Faculty', 'images/teams/science.png', 1000000.0),
                ('Engineering Faculty', 'images/teams/engineering.png', 1000000.0),
                ('Management Faculty', 'images/teams/management.png', 1000000.0),
                ('Arts Faculty', 'images/teams/arts.png', 1000000.0),
                ('Medicine Faculty', 'images/teams/medicine.png', 1000000.0),
                ('Law Faculty', 'images/teams/law.png', 1000000.0),
            ]
            cursor.executemany(
                "INSERT INTO teams (name, logo_path, budget) VALUES (?, ?, ?)",
                sample_teams
            )
        
        # Check if players exist
        cursor.execute("SELECT COUNT(*) FROM players")
        if cursor.fetchone()[0] == 0:
            # Insert sample players with LKR prices and types
            sample_players = [
                ('John Silva', 50000.0, 'images/players/player1.png', 'Science', 'Batsman', 'Right Hand Batsman', 'Right arm spin'),
                ('David Perera', 45000.0, 'images/players/player2.png', 'Engineering', 'Bowler', 'Left Hand Batsman', 'Left arm fast'),
                ('Kamal Fernando', 60000.0, 'images/players/player3.png', 'Management', 'Wicket keeper Batsman', 'Right Hand Batsman', 'Right arm fast'),
            ]
            cursor.executemany(
                "INSERT INTO players (name, base_price, image_path, faculty, player_role, batting_style, bowling_style) VALUES (?, ?, ?, ?, ?, ?, ?)",
                sample_players
            )
        
        # Check if auction settings exist
        cursor.execute("SELECT COUNT(*) FROM auction_settings")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO auction_settings (id, current_round) VALUES (1, 1)"
            )
        
        self.conn.commit()
    
    def get_current_auction_data(self):
        """Get all data needed for display window"""
        cursor = self.conn.cursor()
        
        # Get auction settings
        cursor.execute("SELECT * FROM auction_settings WHERE id = 1")
        settings_row = cursor.fetchone()
        settings = {}
        if settings_row:
            settings = dict(settings_row)
        
        current_player = None
        if settings.get('current_player_id'):
            cursor.execute('''
                SELECT p.*, t.name as team_name, t.logo_path as team_logo
                FROM players p
                LEFT JOIN teams t ON p.sold_to_team = t.id
                WHERE p.id = ?
            ''', (settings['current_player_id'],))
            player_row = cursor.fetchone()
            if player_row:
                current_player = dict(player_row)
                
                # Get the current highest bidder (leading team) if player is not sold
                if current_player['status'] != 'SOLD' and current_player['current_bid'] > current_player['base_price']:
                    cursor.execute('''
                        SELECT t.name as leading_team
                        FROM bids b
                        JOIN teams t ON b.team_id = t.id
                        WHERE b.player_id = ? AND b.amount = ?
                        ORDER BY b.timestamp DESC
                        LIMIT 1
                    ''', (current_player['id'], current_player['current_bid']))
                    leading_bid = cursor.fetchone()
                    if leading_bid:
                        current_player['leading_team'] = leading_bid['leading_team']
                    else:
                        current_player['leading_team'] = "-"
                else:
                    current_player['leading_team'] = "-"
        
        # Get all teams
        cursor.execute("SELECT * FROM teams ORDER BY name")
        teams = []
        for row in cursor.fetchall():
            teams.append(dict(row))
        
        # Count remaining players
        cursor.execute("SELECT COUNT(*) as count FROM players WHERE status = 'UPCOMING'")
        remaining_result = cursor.fetchone()
        remaining_players = remaining_result['count'] if remaining_result else 0
        
        return {
            'settings': settings,
            'current_player': current_player,
            'teams': teams,
            'currency': self.currency,
            'remaining_players': remaining_players,
            'auction_name': settings.get('auction_name', 'TPL AUCTION 2026'),
            'org_name': settings.get('org_name', 'UNIVERSITY OF VAVUNIYA')
        }

    def get_auction_branding(self):
        """Return auction settings (branding and bid increments)."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT auction_name, org_name, bid_increment_1, bid_increment_2, bid_increment_3, projector_view_mode FROM auction_settings WHERE id = 1"
        )
        row = cursor.fetchone()
        if not row:
            return {
                'auction_name': 'TPL AUCTION 2026',
                'org_name': 'UNIVERSITY OF VAVUNIYA',
                'bid_increment_1': 1000,
                'bid_increment_2': 2000,
                'bid_increment_3': 5000,
                'projector_view_mode': 'player'
            }
        return {
            'auction_name': row['auction_name'] or 'TPL AUCTION 2026',
            'org_name': row['org_name'] or 'UNIVERSITY OF VAVUNIYA',
            'bid_increment_1': row['bid_increment_1'] if row['bid_increment_1'] is not None else 1000,
            'bid_increment_2': row['bid_increment_2'] if row['bid_increment_2'] is not None else 2000,
            'bid_increment_3': row['bid_increment_3'] if row['bid_increment_3'] is not None else 5000,
            'projector_view_mode': row['projector_view_mode'] or 'player'
        }

    def set_auction_branding(self, auction_name, org_name, inc1=1000, inc2=2000, inc3=5000):
        """Persist auction settings for admin/display windows."""
        safe_auction = (auction_name or '').strip() or 'TPL AUCTION 2026'
        safe_org = (org_name or '').strip() or 'UNIVERSITY OF VAVUNIYA'
        cursor = self.conn.cursor()
        cursor.execute(
            '''
            UPDATE auction_settings
            SET auction_name = ?, org_name = ?, bid_increment_1 = ?, bid_increment_2 = ?, bid_increment_3 = ?
            WHERE id = 1
            ''',
            (safe_auction, safe_org, inc1, inc2, inc3)
        )
        self.conn.commit()
        
    def set_projector_view_mode(self, mode):
        """Set the projector view mode ('player' or 'summary')."""
        if mode not in ['player', 'summary']:
            mode = 'player'
        cursor = self.conn.cursor()
        cursor.execute("UPDATE auction_settings SET projector_view_mode = ? WHERE id = 1", (mode,))
        self.conn.commit()

    def get_team_roster_summary(self):
        """Return per-team roster progress and sold players."""
        cursor = self.conn.cursor()
        cursor.execute(
            '''
            SELECT
                t.id,
                t.name,
                t.logo_path,
                t.budget,
                t.spent,
                COALESCE(t.max_players, 11) AS max_players,
                COUNT(p.id) AS sold_count
            FROM teams t
            LEFT JOIN players p ON p.sold_to_team = t.id AND p.status = 'SOLD'
            GROUP BY t.id
            ORDER BY t.name
            '''
        )

        teams = []
        for row in cursor.fetchall():
            team = dict(row)
            team['remaining_slots'] = max(0, team['max_players'] - team['sold_count'])
            cursor.execute(
                '''
                SELECT name, player_role, sold_price
                FROM players
                WHERE sold_to_team = ? AND status = 'SOLD'
                ORDER BY sold_price DESC, name
                ''',
                (team['id'],)
            )
            team['sold_players'] = [dict(p) for p in cursor.fetchall()]
            teams.append(team)
        return teams
    
    def get_unsold_players(self):
        """Get all unsold players for re-auction"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM players 
            WHERE status = 'UNSOLD' 
            ORDER BY id
        ''')
        players = []
        for row in cursor.fetchall():
            players.append(dict(row))
        return players
    
    def reset_unsold_players_for_rerun(self):
        """Reset unsold players for second round auction"""
        cursor = self.conn.cursor()
        
        # Update auction round
        cursor.execute('''
            UPDATE auction_settings 
            SET current_round = current_round + 1 
            WHERE id = 1
        ''')
        
        # Get current round
        cursor.execute("SELECT current_round FROM auction_settings WHERE id = 1")
        current_round = cursor.fetchone()['current_round']
        
        # Reset unsold players for new round
        cursor.execute('''
            UPDATE players 
            SET status = 'UPCOMING', 
                current_bid = base_price,
                auction_round = ?
            WHERE status = 'UNSOLD'
        ''', (current_round,))
        
        self.conn.commit()
        return current_round
    
    def get_players_by_team(self):
        """Get all players sorted by team"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                t.name as team_name,
                p.name as player_name,
                p.faculty,
                p.player_role,
                p.sold_price,
                p.status
            FROM players p
            LEFT JOIN teams t ON p.sold_to_team = t.id
            WHERE p.status = 'SOLD'
            ORDER BY t.name, p.sold_price DESC
        ''')
        
        teams_dict = {}
        for row in cursor.fetchall():
            team_name = row['team_name'] or 'Unsold'
            if team_name not in teams_dict:
                teams_dict[team_name] = []
            teams_dict[team_name].append(dict(row))
        
        return teams_dict
    
    def get_auction_summary(self):
        """Get auction summary statistics"""
        cursor = self.conn.cursor()
        
        # Total players
        cursor.execute("SELECT COUNT(*) as total FROM players")
        total = cursor.fetchone()['total']
        
        # Sold players
        cursor.execute("SELECT COUNT(*) as sold FROM players WHERE status = 'SOLD'")
        sold = cursor.fetchone()['sold']
        
        # Unsold players
        cursor.execute("SELECT COUNT(*) as unsold FROM players WHERE status = 'UNSOLD'")
        unsold = cursor.fetchone()['unsold']
        
        # Total amount spent
        cursor.execute("SELECT SUM(sold_price) as total_spent FROM players WHERE status = 'SOLD'")
        total_spent = cursor.fetchone()['total_spent'] or 0
        
        # Team budgets remaining
        cursor.execute("SELECT id, name, budget, spent, (budget - spent) as remaining FROM teams ORDER BY name")
        teams = []
        for row in cursor.fetchall():
            teams.append(dict(row))

        # Count remaining (upcoming) players
        cursor.execute("SELECT COUNT(*) as remaining FROM players WHERE status = 'UPCOMING'")
        remaining_row = cursor.fetchone()
        remaining_players = remaining_row['remaining'] if remaining_row else 0
        
        return {
            'total_players': total,
            'sold_players': sold,
            'unsold_players': unsold,
            'total_spent': total_spent,
            'teams': teams,
            'remaining_players': remaining_players
        }
    
    def place_bid(self, team_id, amount):
        """Place a bid for current player"""
        cursor = self.conn.cursor()
        
        # Get current player and round
        cursor.execute("SELECT current_player_id, current_round FROM auction_settings WHERE id = 1")
        result = cursor.fetchone()
        if not result or not result['current_player_id']:
            return False
        
        player_id = result['current_player_id']
        current_round = result['current_round']
        
        # Insert bid with round number
        cursor.execute(
            "INSERT INTO bids (player_id, team_id, amount, round_number) VALUES (?, ?, ?, ?)",
            (player_id, team_id, amount, current_round)
        )
        
        # Update player's current bid
        cursor.execute(
            "UPDATE players SET current_bid = ? WHERE id = ?",
            (amount, player_id)
        )
        
        self.conn.commit()
        return True
    
    def mark_player_sold(self, player_id, team_id, sold_price):
        """Mark a player as sold to a team"""
        cursor = self.conn.cursor()
        
        # Mark all previous bids for this player as non-winning
        cursor.execute('''
            UPDATE bids SET is_winning_bid = 0 
            WHERE player_id = ?
        ''', (player_id,))
        
        # Mark the highest bid for this player in current round as winning
        cursor.execute('''
            UPDATE bids SET is_winning_bid = 1 
            WHERE player_id = ? AND amount = ? AND team_id = ?
        ''', (player_id, sold_price, team_id))
        
        cursor.execute('''
            UPDATE players 
            SET status = 'SOLD', 
                sold_to_team = ?, 
                sold_price = ?,
                current_bid = ?
            WHERE id = ?
        ''', (team_id, sold_price, sold_price, player_id))
        
        # Update team's spent amount
        cursor.execute('''
            UPDATE teams 
            SET spent = spent + ? 
            WHERE id = ?
        ''', (sold_price, team_id))
        
        self.conn.commit()
    
    def mark_player_unsold(self, player_id):
        """Mark a player as unsold.
        
        If the player was previously SOLD, the team's spent budget is
        corrected by subtracting the previously paid sold_price.
        """
        cursor = self.conn.cursor()

        # Check current state – if SOLD we must refund the team's budget
        cursor.execute(
            "SELECT status, sold_to_team, sold_price FROM players WHERE id = ?",
            (player_id,)
        )
        row = cursor.fetchone()
        if row and row['status'] == 'SOLD' and row['sold_to_team'] and row['sold_price']:
            # Deduct the previously paid price from the team's spent column
            cursor.execute(
                "UPDATE teams SET spent = MAX(0, spent - ?) WHERE id = ?",
                (row['sold_price'], row['sold_to_team'])
            )
            # Clear the winning-bid flag so bid history stays clean
            cursor.execute(
                "UPDATE bids SET is_winning_bid = 0 WHERE player_id = ?",
                (player_id,)
            )

        cursor.execute('''
            UPDATE players 
            SET status = 'UNSOLD', 
                current_bid = base_price,
                sold_to_team = NULL,
                sold_price = 0
            WHERE id = ?
        ''', (player_id,))

        self.conn.commit()

        # Clear the celebration flag on the shared state
        self.show_confetti = False
    
    def get_bid_history(self):
        """Get only winning bids (sold prices) for history"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                b.id,
                p.name as player_name,
                t.name as team_name,
                b.amount,
                b.timestamp,
                p.status
            FROM bids b
            JOIN players p ON b.player_id = p.id
            JOIN teams t ON b.team_id = t.id
            WHERE b.is_winning_bid = 1 OR p.status = 'SOLD'
            ORDER BY b.timestamp DESC
            LIMIT 50
        ''')
        
        bids = []
        for row in cursor.fetchall():
            bids.append(dict(row))
        return bids
    
    def close(self):
        """Close database connection"""
        self.conn.close()

# Global database instance
db = Database()