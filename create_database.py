"""
Script to create and populate the auction database
"""
import sqlite3
import os
from datetime import datetime

def create_database():
    """Create SQLite database with all tables and sample data"""
    
    # Create database directory if it doesn't exist
    os.makedirs("database", exist_ok=True)
    os.makedirs("images/players", exist_ok=True)
    os.makedirs("images/teams", exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect('database/auction.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("Creating database tables...")
    
    # Drop tables if they exist
    cursor.execute("DROP TABLE IF EXISTS bids")
    cursor.execute("DROP TABLE IF EXISTS players")
    cursor.execute("DROP TABLE IF EXISTS teams")
    cursor.execute("DROP TABLE IF EXISTS auction_settings")
    
    # Create Teams table with logo support
    cursor.execute('''
        CREATE TABLE teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            logo_path TEXT,
            budget REAL DEFAULT 1000000.0,
            spent REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Players table with player types and image
    cursor.execute('''
        CREATE TABLE players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            base_price REAL NOT NULL,
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
    
    # Create Bids table with winning bid flag
    cursor.execute('''
        CREATE TABLE bids (
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
    
    # Create Auction Settings table
    cursor.execute('''
        CREATE TABLE auction_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            is_auction_active INTEGER DEFAULT 0,
            current_player_id INTEGER,
            countdown_duration INTEGER DEFAULT 60,
            countdown_end TIMESTAMP,
            current_round INTEGER DEFAULT 1,
            FOREIGN KEY (current_player_id) REFERENCES players(id)
        )
    ''')
    
    print("Inserting sample data...")
    
    # Insert sample teams (Faculties)
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
    
    # Insert sample players with player types and images
    sample_players = [
        # Format: (name, base_price, image_path, faculty, player_role, batting_style, bowling_style)
        ('John Silva', 50000.0, 'images/players/player1.png', 'Science', 'Batsman', 'Right Hand Batsman', 'Right arm spin'),
        ('David Perera', 45000.0, 'images/players/player2.png', 'Engineering', 'Bowler', 'Left Hand Batsman', 'Left arm fast'),
        ('Kamal Fernando', 60000.0, 'images/players/player3.png', 'Management', 'Wicket keeper Batsman', 'Right Hand Batsman', 'Right arm fast'),
    ]
    
    cursor.executemany(
        "INSERT INTO players (name, base_price, image_path, faculty, player_role, batting_style, bowling_style) VALUES (?, ?, ?, ?, ?, ?, ?)",
        sample_players
    )
    
    # Insert auction settings
    cursor.execute(
        "INSERT INTO auction_settings (id, current_round) VALUES (1, 1)"
    )
    
    # Commit changes
    conn.commit()
    
    # Verify data
    print("\n✅ Database created successfully!")
    print("\n📊 Sample Data Summary:")
    
    cursor.execute("SELECT COUNT(*) FROM teams")
    print(f"  Teams: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM players")
    print(f"  Players: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT current_round FROM auction_settings WHERE id = 1")
    print(f"  Current Round: {cursor.fetchone()[0]}")
    
    print("\n👤 Sample Players (Base Price in LKR):")
    cursor.execute("SELECT id, name, base_price, faculty, player_role FROM players LIMIT 3")
    for row in cursor.fetchall():
        print(f"  {row['id']}: {row['name']} (Rs. {row['base_price']:,.0f})")
        print(f"     Faculty: {row['faculty']}, Role: {row['player_role']}")
    
    print("\n🏆 Sample Teams (Budget in LKR):")
    cursor.execute("SELECT id, name, budget FROM teams LIMIT 3")
    for row in cursor.fetchall():
        print(f"  {row['id']}: {row['name']} (Rs. {row['budget']:,.0f})")
    
    # Close connection
    conn.close()
    
    print(f"\n💾 Database file created at: database/auction.db")
    print("📁 Image directories created: images/players/, images/teams/")
    print("\n🎯 Ready to run! Execute: python main.py")
    print("\n📸 Tip: Add player images (PNG/JPG) to images/players/ folder")
    print("🏆 Tip: Add team logos to images/teams/ folder")
    print("💰 Currency: LKR (Sri Lankan Rupees) only")

def main():
    """Main function"""
    print("Cricket Player Auction System - Database Setup")
    print("="*50)
    print("Features: Player images, Team logos, LKR currency")
    print("Bid History: Shows only winning bids (sold prices)")
    
    response = input("\nDo you want to create the database? (y/n): ")
    if response.lower() == 'y':
        create_database()
        print("\n✅ Setup complete! You can now run the application.")
        print("\nTo run: python main.py")
        print("\n📸 Remember to add actual images to the images folders!")
    else:
        print("Database creation cancelled.")

if __name__ == "__main__":
    main()