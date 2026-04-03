"""
Data models for the auction system with LKR support
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Team:
    id: int
    name: str
    logo_path: str
    budget: float
    spent: float = 0.0
    budget_lkr: float = 0.0  # LKR converted value
    spent_lkr: float = 0.0   # LKR converted value
    
    @property
    def remaining_lkr(self):
        return self.budget_lkr - self.spent_lkr

@dataclass
class Player:
    id: int
    name: str
    base_price: float
    image_path: str
    status: str = "UPCOMING"  # UPCOMING, LIVE, SOLD, UNSOLD
    current_bid: float = 0.0
    sold_to_team: Optional[int] = None
    sold_price: float = 0.0
    base_price_lkr: float = 0.0  # LKR converted value
    current_bid_lkr: float = 0.0 # LKR converted value
    sold_price_lkr: float = 0.0  # LKR converted value

@dataclass
class Bid:
    id: int
    player_id: int
    team_id: int
    amount: float
    timestamp: datetime
    amount_lkr: float = 0.0  # LKR converted value

@dataclass
class AuctionSettings:
    is_auction_active: bool = False
    current_player_id: Optional[int] = None
    countdown_duration: int = 60
    countdown_end: Optional[datetime] = None
    currency: str = "LKR"
    conversion_rate: float = 100.0  # 1 USD = 100 LKR