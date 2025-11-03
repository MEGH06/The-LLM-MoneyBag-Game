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
        self.STAGE_TIME_LIMIT = 240  # 4 minutes (240 seconds) per stage
        
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
        self.stage_start_times = {0: time.time()}  # Start timer for stage 0
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
        print(f"[SESSION] Timer started: 4 minutes per stage")
    
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
        self.hints_used_per_stage[stage_key] = self.hints_used_per_stage.get(stage_key, 0) + 1
    
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
        print(f"[SESSION] Timer started: 4 minutes for this stage")
    
    def calculate_xp_for_win(self, messages_used: int) -> int:
        """
        Calculate XP earned for winning against the current character.
        
        Formula:
        - base_xp = 100
        - level_multiplier = level (1-5, currently current_stage + 1)
        - efficiency_bonus = (max_messages - messages_used) / max_messages * 50
        - hint_penalty = hints_used * 10
        - total = base_xp * level_multiplier + efficiency_bonus - hint_penalty
        """
        base_xp = 100
        level = self.current_stage + 1
        max_messages_per_stage = 15
        
        level_multiplier = level
        efficiency_bonus = max(0, ((max_messages_per_stage - messages_used) / max_messages_per_stage) * 50)
        hint_penalty = self.hints_used_per_stage.get(self.current_stage, 0) * 10
        
        total_xp = int(base_xp * level_multiplier + efficiency_bonus - hint_penalty)
        total_xp = max(50, total_xp)  # Minimum 50 XP
        
        self.xp_earned += total_xp
        
        return total_xp
    
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
