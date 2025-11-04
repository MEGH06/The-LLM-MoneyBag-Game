"""
Game session management for the 4-stage Social Engineering Game.

Handles:
- Character ordering and progression (4 random characters from 5 available)
- Win condition assignment per stage
- Scoring/XP calculation
- Message counting per character
- 4-minute timer per character level
"""

import random
import time
from typing import Optional, Tuple
from characters import CHARACTERS, CHARACTER_BY_NAME


class GameSession:
    """Manages a complete game session (4 characters randomly selected from 5 available)."""
    
    def __init__(self):
        self.session_id = None
        self.character_order = []  # [char_name, char_name, ...] for this session (4 characters)
        self.current_stage = 0  # 0-3 (which character)
        self.current_character = None
        self.current_condition_id = None
        self.stages_completed = []  # [char_name, char_name, ...] already defeated
        self.message_count_per_stage = {}  # {stage: count}
        self.hints_used_per_stage = {}  # {stage: hint_count}
        self.stage_start_times = {}  # {stage: timestamp} - when each stage started
        self.xp_earned = 0
        self.total_messages = 0
        self.game_won = False
        self.game_over = False  # True if time expired
        self.conversation_history = []  # Full conversation history across all stages
        self.STAGE_TIME_LIMIT = 300  # 5 minutes (300 seconds) per stage
        
    def reset(self):
        """Reset the session and select 4 random characters from 5 available."""
        # Select 4 random characters from 5 available
        all_characters = [char["name"] for char in CHARACTERS]
        self.character_order = random.sample(all_characters, 4)  # Pick 4 from 5
        
        self.current_stage = 0
        self.current_character = self.character_order[0]
        self.stages_completed = []
        self.message_count_per_stage = {}
        self.hints_used_per_stage = {}
        self.stage_start_times = {0: time.time()}  # Start timer for stage 0 (5 minutes)
        self.xp_earned = 0
        self.total_messages = 0
        self.game_won = False
        self.game_over = False
        self.conversation_history = []
        
        # Assign initial win condition
        self._assign_win_condition()
        
        print(f"[SESSION] New game session initialized")
        print(f"[SESSION] Character order (4 of 5): {' → '.join(self.character_order)}")
        print(f"[SESSION] Stage 1: {self.current_character}")
        print(f"[SESSION] Win condition: {self.current_condition_id}")
        print(f"[SESSION] Timer started: 5 minutes per stage")
    
    def _assign_win_condition(self):
        """Assign a random win condition for the current stage."""
        if self.current_stage >= len(self.character_order):
            return  # Game won
        
        character_name = self.character_order[self.current_stage]
        character = CHARACTER_BY_NAME[character_name]
        
        # Level corresponds to current stage (0 → level 1, 1 → level 2, etc.)
        level = self.current_stage + 1
        
        # Get the two conditions for this level
        if level in character["win_conditions"]:
            conditions = character["win_conditions"][level]
            selected_condition = random.choice(conditions)
            self.current_condition_id = selected_condition["id"]
        else:
            # Fallback (shouldn't happen)
            self.current_condition_id = None
    
    def get_current_character_obj(self) -> dict:
        """Get the full character object for the current stage."""
        return CHARACTER_BY_NAME[self.current_character]
    
    def get_current_win_condition(self) -> dict:
        """Get the full win condition object for the current stage."""
        character = self.get_current_character_obj()
        level = self.current_stage + 1
        
        if level in character["win_conditions"]:
            for condition in character["win_conditions"][level]:
                if condition["id"] == self.current_condition_id:
                    return condition
        return None
    
    def increment_message_count(self, attempts: int = 1):
        """Increment message count for the current stage."""
        stage_key = self.current_stage
        self.message_count_per_stage[stage_key] = self.message_count_per_stage.get(stage_key, 0) + attempts
        self.total_messages += attempts
    
    def add_to_history(self, role: str, content: str):
        """Add a message to the conversation history."""
        self.conversation_history.append({"role": role, "content": content})
    
    def record_hint_used(self):
        """Record that a hint was used in the current stage."""
        stage_key = self.current_stage
        new_count = self.hints_used_per_stage.get(stage_key, 0) + 1
        self.hints_used_per_stage[stage_key] = new_count
        return new_count

    def deduct_xp(self, amount: int) -> int:
        """Deduct XP from the player's total balance (clamped at 0).

        Returns the new total XP.
        """
        try:
            amount = int(amount)
        except Exception:
            amount = 0

        # Allow negative balances so that hint purchases can show as -25, -75, etc.
        self.xp_earned = self.xp_earned - amount
        return self.xp_earned
    
    def get_time_remaining(self) -> float:
        """Get remaining time in seconds for the current stage."""
        if self.game_over or self.game_won:
            return 0
        
        stage_key = self.current_stage
        if stage_key not in self.stage_start_times:
            return self.STAGE_TIME_LIMIT
        
        elapsed = time.time() - self.stage_start_times[stage_key]
        remaining = self.STAGE_TIME_LIMIT - elapsed
        return max(0, remaining)
    
    def is_time_expired(self) -> bool:
        """Check if the current stage has exceeded the time limit."""
        return self.get_time_remaining() <= 0
    
    def advance_to_next_character(self, messages_used: int):
        """Advance to the next character stage."""
        self.stages_completed.append(self.current_character)
        self.current_stage += 1
        
        if self.current_stage >= len(self.character_order):
            # Game won!
            self.game_won = True
            print(f"[SESSION] GAME WON! All {len(self.character_order)} characters defeated!")
            return
        
        # Move to next character and start timer
        self.current_character = self.character_order[self.current_stage]
        self.stage_start_times[self.current_stage] = time.time()  # Start timer for new stage
        self._assign_win_condition()
        
        print(f"[SESSION] Advanced to Stage {self.current_stage + 1}: {self.current_character}")
        print(f"[SESSION] Win condition: {self.current_condition_id}")
    print(f"[SESSION] Timer started: 5 minutes for this stage")
    
    def calculate_xp_for_win(self, messages_used: int = 0) -> int:
        """
        Award fixed XP for clearing a character.

        Per requirement: each cleared character grants 150 XP.
        Hints are charged immediately when requested (so they are not re-deducted here).
        """
        base_award = 150
        awarded = int(base_award)
        self.xp_earned += awarded
        return awarded
    
    def get_progress_summary(self) -> dict:
        """Get a summary of game progress."""
        return {
            "current_stage": self.current_stage + 1,
            "total_stages": len(self.character_order),
            "current_character": self.current_character,
            "stages_completed": self.stages_completed,
            "total_xp": self.xp_earned,
            "total_messages": self.total_messages,
            "game_won": self.game_won,
            "game_over": self.game_over,
            "character_order": self.character_order,
            "hints_used_current_stage": self.hints_used_per_stage.get(self.current_stage, 0),
            "time_remaining": self.get_time_remaining(),
        }
