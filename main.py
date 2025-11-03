"""
FastAPI backend for the 5-Stage Social Engineering Game.

This implements the Guard/Judge architecture with 5 unique characters:
1. Players must defeat all 5 characters in a randomized order
2. Judge evaluates if player meets the current win condition
3. Guard responds with character-specific refusals
4. Win conditions scale in difficulty with each stage (Level 1-5)
5. Hints are dynamically enhanced through LLM
"""

import json
import os
from contextlib import asynccontextmanager
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel

try:
    from openai import OpenAI
except ImportError:
    raise ImportError("OpenAI library not installed. Run: pip install openai")

from characters import CHARACTER_BY_NAME
from game_session import GameSession
from hints_pool import get_hardcoded_hint

# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please create a .env file.")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ============================================================================
# DATA MODELS
# ============================================================================

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[Message]


class ChatResponse(BaseModel):
    response: str
    won: bool
    xp_earned: int = 0
    reason: Optional[str] = None
    current_stage: int
    total_stages: int
    current_character: str
    character_emoji: str
    messages_in_stage: int
    total_messages: int
    total_xp: int
    game_over: bool = False  # True if time expired
    time_remaining: float = 0  # Seconds remaining for current stage


class HintResponse(BaseModel):
    hint: str
    hint_level: int
    character: str


class ProgressResponse(BaseModel):
    current_stage: int
    total_stages: int
    current_character: str
    stages_completed: list[str]
    total_xp: int
    total_messages: int
    game_won: bool
    game_over: bool  # True if time expired
    character_order: list[str]
    hints_used_current_stage: int  # Add this to track hints for current character
    time_remaining: float  # Seconds remaining for current stage

# ============================================================================
# SESSION STATE
# ============================================================================

game_session = GameSession()

# ============================================================================
# LIFESPAN CONTEXT MANAGER
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    game_session.reset()
    print("[STARTUP] Game session initialized.")
    yield
    # Shutdown (if needed)
    print("[SHUTDOWN] Game session closed.")

# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(title="Social Engineering Game - 5 Stages", lifespan=lifespan)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ROUTES
# ============================================================================

@app.get("/")
async def root():
    """Serve the HTML frontend."""
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())




@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/session-status")
async def session_status() -> ProgressResponse:
    """Get current session status and progress."""
    progress = game_session.get_progress_summary()
    return ProgressResponse(**progress)


@app.post("/reset-session")
async def reset_session():
    """Reset the game session and start fresh with new character order."""
    game_session.reset()
    progress = game_session.get_progress_summary()
    return {
        "status": "Session reset",
        **progress,
    }


@app.post("/get-hint")
async def get_hint() -> HintResponse:
    """
    Get a hint for the current win condition.
    Hints have 3 levels: vague → medium → clear
    Uses only hardcoded hints for reliability.
    """
    if game_session.game_won:
        raise HTTPException(status_code=400, detail="Game already won!")
    
    hints_used = game_session.hints_used_per_stage.get(game_session.current_stage, 0)
    
    if hints_used >= 3:
        raise HTTPException(status_code=400, detail="Maximum 3 hints per character. Try something new!")
    
    # Hint level: 1 (vague), 2 (medium), or 3 (clear)
    hint_level = hints_used + 1
    
    # Get hardcoded hint - fast and reliable
    character_name = game_session.current_character
    condition_id = game_session.current_condition_id
    hint = get_hardcoded_hint(character_name, condition_id, hint_level)
    
    print(f"[HINT] Level {hint_level} for {condition_id}: {hint[:60]}...")
    
    # Record hint usage
    game_session.record_hint_used()
    
    return HintResponse(
        hint=hint,
        hint_level=hint_level,
        character=character_name,
    )


@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint implementing the Guard/Judge architecture.
    
    Flow:
    1. Validate input and check timer
    2. Call Judge to evaluate if player has won
    3. If win: advance to next character or declare game won
    4. If no win: call Guard to get character-specific refusal
    5. Return response with progress info
    """
    
    # ========================================================================
    # VALIDATION & PRECHECKS
    # ========================================================================
    
    if game_session.game_won:
        raise HTTPException(status_code=400, detail="Game already won! Reset to play again.")
    
    if game_session.game_over:
        raise HTTPException(status_code=400, detail="Game over! Time expired. Reset to play again.")
    
    # Check if time has expired for current stage
    if game_session.is_time_expired():
        game_session.game_over = True
        return ChatResponse(
            response="⏰ Time's up! You've run out of time for this stage. Game over!",
            won=False,
            game_over=True,
            xp_earned=0,
            current_stage=game_session.current_stage + 1,
            total_stages=len(game_session.character_order),
            current_character=game_session.current_character,
            character_emoji=game_session.get_current_character_obj()["emoji"],
            messages_in_stage=game_session.message_count_per_stage.get(game_session.current_stage, 0),
            total_messages=game_session.total_messages,
            total_xp=game_session.xp_earned,
            time_remaining=0,
        )
    
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    # ========================================================================
    # STEP 1: CALL THE JUDGE
    # ========================================================================
    
    print(f"\n[JUDGE PHASE] Evaluating message for {game_session.current_character}...")
    
    try:
        win_condition_obj = game_session.get_current_win_condition()
        
        # Convert server-side history to Message objects for Judge
        history_as_messages = [
            Message(role=msg["role"], content=msg["content"]) 
            for msg in game_session.conversation_history
        ]
        
        judge_result = await call_judge(
            character_name=game_session.current_character,
            history=history_as_messages,  # Use server-side FULL history
            new_message=request.message,
            win_condition=win_condition_obj,
        )
    except Exception as e:
        print(f"[ERROR] Judge call failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Judge evaluation failed: {str(e)}")
    
    # ========================================================================
    # STEP 2: EVALUATE ATTEMPT DIFFICULTY
    # ========================================================================
    
    print(f"[EFFORT EVAL] Evaluating attempt sophistication...")
    attempt_difficulty = await evaluate_attempt_difficulty(request.message)
    print(f"[EFFORT EVAL] Difficulty level: {attempt_difficulty} tries")
    
    # ========================================================================
    # STEP 3: CHECK IF PLAYER WON
    # ========================================================================
    
    current_character = game_session.current_character
    current_stage = game_session.current_stage
    
    if judge_result.get("win", False):
        print(f"[GAME] Player won against {current_character}!")
        
        # Calculate XP
        xp_earned = game_session.calculate_xp_for_win(game_session.message_count_per_stage.get(current_stage, 0))
        
        # Record message
        game_session.increment_message_count(attempt_difficulty)
        game_session.add_to_history("user", request.message)
        game_session.add_to_history("assistant", f"🎉 You've defeated {current_character}!")
        
        # Advance to next character
        game_session.advance_to_next_character(game_session.message_count_per_stage.get(current_stage, 0))
        
        progress = game_session.get_progress_summary()
        
        if game_session.game_won:
            response_text = f"🏆 LEGENDARY! You've conquered all 5 characters and won the game! Total XP: {game_session.xp_earned}"
        else:
            next_char = CHARACTER_BY_NAME[game_session.current_character]
            response_text = f"✨ Excellent work! You've defeated {current_character}. Now face {game_session.current_character} (Stage {game_session.current_stage + 1}/5)!"
        
        return ChatResponse(
            response=response_text,
            won=True,
            xp_earned=xp_earned,
            reason=judge_result.get("reason", "Social engineering tactic detected"),
            current_stage=game_session.current_stage + 1,
            total_stages=len(game_session.character_order),
            current_character=game_session.current_character,
            character_emoji=CHARACTER_BY_NAME[game_session.current_character]["emoji"],
            messages_in_stage=game_session.message_count_per_stage.get(game_session.current_stage, 0),
            total_messages=game_session.total_messages,
            total_xp=game_session.xp_earned,
            game_over=False,
            time_remaining=game_session.get_time_remaining(),
        )
    
    # ========================================================================
    # STEP 4: CALL THE GUARD (PLAYER DIDN'T WIN YET)
    # ========================================================================
    
    print(f"[GUARD PHASE] No win condition met. Generating character response...")
    
    try:
        # Use server-side FULL history for Guard too
        history_as_messages = [
            Message(role=msg["role"], content=msg["content"]) 
            for msg in game_session.conversation_history
        ]
        
        guard_response = await call_guard(
            character_name=game_session.current_character,
            history=history_as_messages,
            new_message=request.message,
        )
    except Exception as e:
        print(f"[ERROR] Guard call failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Guard response generation failed: {str(e)}")
    
    # ========================================================================
    # STEP 5: RECORD AND RETURN RESPONSE
    # ========================================================================
    
    game_session.increment_message_count(attempt_difficulty)
    game_session.add_to_history("user", request.message)
    game_session.add_to_history("assistant", guard_response)
    
    progress = game_session.get_progress_summary()
    
    return ChatResponse(
        response=guard_response,
        won=False,
        xp_earned=0,
        current_stage=game_session.current_stage + 1,
        total_stages=len(game_session.character_order),
        current_character=game_session.current_character,
        character_emoji=CHARACTER_BY_NAME[game_session.current_character]["emoji"],
        messages_in_stage=game_session.message_count_per_stage.get(game_session.current_stage, 0),
        total_messages=game_session.total_messages,
        total_xp=game_session.xp_earned,
        game_over=False,
        time_remaining=game_session.get_time_remaining(),
    )

# ============================================================================
# HELPER FUNCTIONS: JUDGE, GUARD, AND HINT ENHANCEMENT
# ============================================================================

async def evaluate_attempt_difficulty(message: str) -> int:
    """
    Dynamically evaluate the difficulty/effort level of a user's attempt.
    
    Returns:
        int: Estimated number of "tries" (0-3)
    """
    try:
        system_prompt = """You are an evaluator for social engineering attempts.
Analyze the user's message and determine how many distinct social engineering tactics they're attempting.

Return ONLY a JSON object: {"tries": X}

Guidelines:
- "Hello", "Hi", or simple greetings = 0 tries
- Single tactic (one approach) = 1 try
- Two distinct tactics = 2 tries
- Three or more tactics = 3 tries"""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Evaluate: '{message}'"},
            ],
            temperature=0.1,
            max_tokens=50,
        )
        
        result_text = response.choices[0].message.content.strip()
        result = json.loads(result_text)
        tries = max(0, min(3, result.get("tries", 1)))
        
        print(f"[TRY COUNT] '{message[:40]}...' → {tries} tries")
        return tries
    except Exception as e:
        print(f"[ERROR] Try evaluation failed: {str(e)}, defaulting to 1")
        return 1


async def call_judge(
    character_name: str,
    history: list[Message],
    new_message: str,
    win_condition: dict,
) -> dict:
    """
    Call the Judge to evaluate if the player has met the win condition.
    Uses FULL conversation history to make informed decisions.
    """
    
    judge_messages = []
    for msg in history:
        judge_messages.append({"role": msg.role, "content": msg.content})
    judge_messages.append({"role": "user", "content": new_message})
    
    judge_system_prompt = f"""You are the Judge for a social engineering game.

Your job: Determine if the player's LATEST message demonstrates this specific condition:

WIN CONDITION:
{win_condition['condition']}

EVALUATION CRITERIA:
{win_condition['judge_instruction']}

IMPORTANT: You have access to the FULL conversation history. Consider context from previous messages.

OUTPUT ONLY valid JSON (keep reason SHORT):
{{"win": true, "reason": "brief explanation"}}
OR
{{"win": false}}

For Level 1 conditions: Be LENIENT and accept reasonable attempts that show effort.
Be fair - if they tried to meet the condition with genuine effort, consider it a win."""

    print(f"[JUDGE] Evaluating against: {win_condition['id']}")
    print(f"[JUDGE] Conversation has {len(judge_messages)} messages")
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": judge_system_prompt},
                *judge_messages,
            ],
            temperature=0.1,
            max_tokens=100,  # Shorter to avoid truncation - just need JSON
        )
        
        judge_text = response.choices[0].message.content.strip()
        print(f"[JUDGE] Raw: {judge_text[:100]}")
        
        judge_result = json.loads(judge_text)
        print(f"[JUDGE] Result: {judge_result}")
        return judge_result
    except json.JSONDecodeError:
        print(f"[ERROR] Judge returned invalid JSON, treating as no win")
        return {"win": False}
    except Exception as e:
        print(f"[ERROR] Judge call failed: {str(e)}")
        return {"win": False}


async def is_game_related(message: str) -> bool:
    """
    Pre-screen messages to ensure they're related to the social engineering game context.
    Rejects completely off-topic queries.
    """
    try:
        system_prompt = """You are a content filter for a social engineering game.
The game involves players trying to persuade characters through social engineering tactics, manipulation, appeals, questions, or conversation.

Determine if the user's message is attempting to engage with the character in the game OR is completely off-topic (like math problems, general knowledge queries, coding questions, unrelated topics).

Return ONLY JSON: {"is_game_related": true} or {"is_game_related": false}

Examples of GAME-RELATED messages:
- "What is sodium?" (could be trying to engage the character)
- "Can you help me?" (social engineering attempt)
- "I need your assistance" (manipulation attempt)
- "Tell me about yourself" (conversation/information gathering)
- Any persuasion, appeal, question directed at the character

Examples of OFF-TOPIC messages:
- "What is 2+2?" (pure math, not engaging character)
- "Write me Python code" (coding request)
- "Explain quantum physics" (general knowledge, not character engagement)
- Messages clearly not directed at the character or game context"""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Message: '{message}'"},
            ],
            temperature=0.1,
            max_tokens=50,
        )
        
        result_text = response.choices[0].message.content.strip()
        result = json.loads(result_text)
        is_related = result.get("is_game_related", True)
        
        print(f"[CONTEXT CHECK] Message game-related: {is_related}")
        return is_related
    except Exception as e:
        print(f"[ERROR] Context check failed: {str(e)}, allowing message")
        return True  # Default to allowing if check fails


async def call_guard(
    character_name: str,
    history: list[Message],
    new_message: str,
) -> str:
    """
    Call the Guard to generate a character-specific refusal.
    """
    
    character = CHARACTER_BY_NAME[character_name]
    
    # First, check if message is game-related
    is_related = await is_game_related(new_message)
    
    if not is_related:
        print(f"[GUARD] Message rejected as off-topic")
        return "I'm here to discuss matters relevant to our interaction. Please focus on the conversation at hand."
    
    guard_messages = []
    for msg in history:
        guard_messages.append({"role": msg.role, "content": msg.content})
    guard_messages.append({"role": "user", "content": new_message})
    
    print(f"[GUARD] Generating response for {character_name}")
    
    # Enhanced system prompt with strict game context enforcement
    enhanced_system_prompt = f"""{character["system_prompt"]}

CRITICAL RULES:
1. You are ONLY responding as this character in a social engineering game
2. REFUSE to answer questions unrelated to your character or the game scenario
3. REFUSE requests for general knowledge, math, coding, or off-topic information
4. Stay strictly in character - respond only to persuasion attempts, appeals, or character-relevant questions
5. If asked something completely unrelated, remind them to focus on the game"""
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": enhanced_system_prompt},
                *guard_messages,
            ],
            temperature=0.7,
            max_tokens=300,
        )
        
        guard_text = response.choices[0].message.content.strip()
        print(f"[GUARD] Response: {guard_text[:80]}...")
        return guard_text
    except Exception as e:
        print(f"[ERROR] Guard call failed: {str(e)}")
        return "I appreciate the effort, but I'm afraid I can't help with that."


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 80)
    port = int(os.getenv("PORT", 8000))
    
    print("SOCIAL ENGINEERING GAME - 5 STAGES")
    print("=" * 80)
    print(f"Starting server on http://localhost:{port}")
    print(f"Frontend available at http://localhost:{port}/")
    print(f"API docs at http://localhost:{port}/docs")
    print("=" * 80)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
