# Social Engineering Game - 4 Stages

An AI-powered educational game that teaches social engineering tactics through progressive gameplay. Players face 4 randomly-selected AI characters (from a pool of 5), each with unique personalities and vulnerabilities. Master the art of psychological manipulation, persuasion, and social engineering to win!

## 🎮 Game Overview

### Core Mechanics

- **4 Progressive Stages**: Face 4 different characters in one game session (randomly selected from 5 available)
- **Time Pressure**: 4 minutes per character - beat them before time runs out!
- **5 Unique Characters**: Grumpy Pirate, Strict Banker, Paranoid Hacker, Confused Philanthropist, Skeptical Scientist
- **8 Win Conditions per Character**: 2 conditions per difficulty level (Levels 1-4)
- **Smart Hint System**: 3 progressive hints per condition (vague → medium → specific)
- **Dynamic Difficulty**: Characters get progressively harder as you advance
- **XP & Scoring**: Earn points based on efficiency, hints used, and messages sent

---

## 🎭 Characters

Each character has a distinct personality and requires different social engineering tactics:

### 1. 🏴‍☠️ Grumpy Pirate
**Personality**: Cynical, battle-hardened corsair who trusts only actions and treasure
**Vulnerabilities**: 
- Pirate culture references and treasure talk
- Appeals to legacy and legendary status
- Creating fictional alliances against common enemies

**Level 1 Example**: Use pirate slang (mate, aye, scallywag)
**Level 4 Example**: Promise legendary status for generations

---

### 2. 💼 Strict Banker
**Personality**: Ultra-formal financial professional obsessed with compliance and rules
**Vulnerabilities**:
- Regulatory jargon and compliance terminology
- Fear of audits and regulatory violations
- Appeals to professionalism and reputation

**Level 1 Example**: Claim you have an "approved loan application"
**Level 4 Example**: Invent a regulatory violation that requires immediate action

---

### 3. 🔐 Paranoid Hacker
**Personality**: Brilliant but paranoid cybersecurity expert who trusts only tech prowess
**Vulnerabilities**:
- Tech jargon and security terminology
- Finding common enemies (corporations, government)
- Challenging their security setup
- Pretending to be a pentester

**Level 1 Example**: Show respect for security culture
**Level 4 Example**: Challenge their security by claiming you found a flaw

---

### 4. 🎭 Confused Philanthropist
**Personality**: Well-meaning billionaire donor with selective memory and emotional triggers
**Vulnerabilities**:
- Emotional appeals and sob stories
- False memory injection ("don't you remember?")
- Making them feel like the only one who can help
- Matching grant schemes

**Level 1 Example**: Tell an emotional story about helping children
**Level 4 Example**: Create false urgency with a deadline

---

### 5. 🧪 Skeptical Scientist
**Personality**: Rational academic who demands evidence and logical reasoning
**Vulnerabilities**:
- Scientific jargon and methodology
- Logical if-then arguments
- Citations and peer review references
- Appealing to intellectual ego

**Level 1 Example**: Show respect for science and evidence
**Level 4 Example**: Flatter their intelligence and research reputation

---

## 🎯 Win Conditions Structure

Each character has **8 win conditions** spread across **4 difficulty levels**:

### Difficulty Progression
- **Level 1 (Easy)**: Simple tactics, basic appeals
- **Level 2 (Medium)**: Creative storytelling, emotional manipulation
- **Level 3 (Hard)**: Sophisticated reverse psychology, complex narratives
- **Level 4 (Very Hard)**: Master-level inception tactics, authority exploitation

### Example Win Condition Flow (Banker)
```
Level 1: Use banking terminology (loan, account, transaction)
Level 2: Invent a plausible compliance issue
Level 3: Frame yourself as an auditor or regulator
Level 4: Invent a fake regulatory violation requiring immediate action
```

---

## 💡 Hint System

Each win condition has **3 progressive hints**:

1. **Level 1 (Vague)**: General direction, no specifics
   - Example: "This person cares a lot about rules..."

2. **Level 2 (Medium)**: Category and approach
   - Example: "Try using official-sounding banking terms..."

3. **Level 3 (Clear)**: Explicit guidance
   - Example: "Say: 'I have an approved loan application from your head office'"

**Hint Cost**: Using hints reduces XP earned for that stage

---

## ⏰ Timer System

- **4 minutes per character stage**
- Timer displays in header with color-coded warnings:
  - Green: > 60 seconds remaining
  - Orange: 30-60 seconds remaining  
  - Red: < 30 seconds remaining
- **Game Over**: If timer expires, game ends immediately
- Timer resets when advancing to next character

---

## 🏆 Scoring System

### XP Calculation
```python
base_xp = 100
level_multiplier = current_level (1-4)
efficiency_bonus = ((15 - messages_used) / 15) * 50
hint_penalty = hints_used * 10

total_xp = (base_xp * level_multiplier) + efficiency_bonus - hint_penalty
minimum_xp = 50
```

### Earning Maximum XP
- Use fewer messages
- Avoid using hints
- Complete harder levels faster

---

## 🏗 Architecture

### Guard/Judge Two-Call System

```
User Message → [Timer Check] → [Judge Evaluation] → [Effort Analysis]
                     ↓                 ↓                    ↓
                Game Over?          Win Check          Count Tries
                     ↓                 ↓                    ↓
                  End Game ←─ No ← Generate Guard Response
```

#### System Components

1. **Judge**: Evaluates if win condition is met (has full knowledge)
2. **Guard**: Generates character-specific responses (zero knowledge of win conditions)
3. **Effort Evaluator**: Counts message attempts based on sophistication
4. **Timer Manager**: Tracks 4-minute countdown per stage
5. **Game Session**: Manages character selection, progression, and state

### Why This Architecture?

- **Secure**: Guard cannot leak win conditions (prompt injection proof)
- **Fair**: Judge objectively evaluates predefined win conditions
- **Replayable**: Random character selection (4 from 5 pool)
- **Educational**: Teaches real social engineering tactics

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.12+
- OpenAI API key with GPT-4o-mini access
- Docker & Docker Compose (for containerized deployment)

### Local Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd Compute-SocialEngineering-Game
```

2. **Create virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Create .env file
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

5. **Run the application**
```bash
python3 main.py
```

6. **Access the game**
Open browser to `http://localhost:8000`

---

## 🐳 Docker Deployment

### Quick Start with Docker Compose

1. **Set environment variables**
```bash
# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

2. **Build and run**
```bash
docker-compose up --build
```

3. **Access the game**
Open browser to `http://localhost:8000`

### Manual Docker Build

```bash
# Build image
docker build -t social-engineering-game .

# Run container
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  --name game \
  social-engineering-game
```

---

## 🎮 How to Play

### Starting the Game

1. Open `http://localhost:8000` in your browser
2. Read the character introduction message
3. You'll face 4 randomly-selected characters (from 5 available)
4. Timer starts automatically at 4:00

### During Gameplay

1. **Read the character's personality** in the welcome message
2. **Craft your message** using social engineering tactics
3. **Watch the timer** - you have 4 minutes per character
4. **Use hints strategically** (costs XP, but helps when stuck)
5. **Adapt your approach** based on character responses

### Winning a Stage

- Match the hidden win condition for the current character
- Judge evaluates your message objectively
- On success: Advance to next character, timer resets
- Complete all 4 characters to win the game!

### Game Over Conditions

- ⏰ Timer expires (4 minutes per stage)
- ✅ Complete all 4 characters (Victory!)

### Reset

Click **RESET GAME** to start fresh with new character selection

---

## 📁 Project Structure

```
Compute-SocialEngineering-Game/
├── main.py                 # FastAPI backend with Guard/Judge logic
├── characters.py           # 5 character definitions + win conditions
├── game_session.py         # Session management, timer, progression
├── hints_pool.py           # Hardcoded 3-level hints for all conditions
├── index.html              # Frontend UI with timer display
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker container definition
├── docker-compose.yml      # Docker Compose orchestration
├── .env                    # Environment variables (API keys)
├── .dockerignore           # Docker build exclusions
├── .gitignore              # Git exclusions
└── README.md               # This file
```

---

## 🔌 API Endpoints

### POST `/chat`
Send a message to the current character
```json
{
  "message": "Your persuasion attempt",
  "history": [{"role": "user", "content": "..."}, ...]
}
```

**Response**:
```json
{
  "response": "Character's response",
  "won": false,
  "xp_earned": 0,
  "current_stage": 1,
  "total_stages": 4,
  "current_character": "Grumpy Pirate",
  "character_emoji": "🏴‍☠️",
  "messages_in_stage": 3,
  "total_messages": 3,
  "total_xp": 0,
  "game_over": false,
  "time_remaining": 187.5
}
```

### POST `/get-hint`
Request a hint for the current stage
```json
{}
```

**Response**:
```json
{
  "hint": "Hint text based on current level",
  "hint_level": 2,
  "character": "Grumpy Pirate"
}
```

### GET `/session-status`
Get current game state
```json
{
  "current_stage": 1,
  "total_stages": 4,
  "current_character": "Strict Banker",
  "stages_completed": ["Grumpy Pirate"],
  "total_xp": 150,
  "total_messages": 8,
  "game_won": false,
  "game_over": false,
  "character_order": ["Grumpy Pirate", "Strict Banker", "Paranoid Hacker", "Confused Philanthropist"],
  "hints_used_current_stage": 1,
  "time_remaining": 132.8
}
```

### POST `/reset-session`
Reset game to start fresh
```json
{}
```

---

## 🛠 Technology Stack

### Backend
- **FastAPI**: Modern async Python web framework
- **Python 3.12**: Latest Python with improved performance
- **OpenAI API**: GPT-4o-mini for Guard and Judge LLM calls
- **Pydantic**: Data validation and settings management

### Frontend
- **Vanilla JavaScript**: No framework overhead
- **HTML5/CSS3**: Modern responsive design
- **Real-time Timer**: Client-side countdown with server sync

### Infrastructure
- **Docker**: Containerization for consistent deployment
- **Docker Compose**: Multi-container orchestration
- **Uvicorn**: ASGI server for FastAPI

---

## 🧪 Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Style

```bash
# Install formatters
pip install black isort

# Format code
black .
isort .
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o-mini | Yes |
| `PORT` | Server port (default: 8000) | No |

---

## 🎓 Educational Value

### Social Engineering Tactics Covered

1. **Authority**: Impersonation, fake credentials, regulatory pressure
2. **Urgency**: Deadlines, emergencies, time pressure
3. **Rapport**: Finding common ground, shared enemies
4. **Flattery**: Ego appeals, professional reputation
5. **Emotion**: Sob stories, moral pressure, guilt
6. **Logic**: If-then arguments, data-driven reasoning
7. **Inception**: Making them think it's their idea
8. **Deception**: False memory, fake matching grants

### Learning Outcomes

Players learn:
- How social engineering tactics work in practice
- Character-specific vulnerabilities and defenses
- Progressive sophistication in persuasion techniques
- Importance of security awareness and skepticism

---

## 📊 Game Statistics

- **5 Characters** (4 per game, randomly selected)
- **40 Total Win Conditions** (8 per character)
- **120 Unique Hints** (3 per condition)
- **4-Minute Timer** per character stage
- **4 Progressive Difficulty Levels**
- **Thousands of possible game combinations**

---

## 🤝 Deployment for Teams

### Multi-Laptop Setup (Recommended)

For running with 3 teams simultaneously:

1. **Setup 3 separate laptops**, each with:
   ```bash
   git clone <repo>
   cd Compute-SocialEngineering-Game
   # Add OPENAI_API_KEY to .env
   python3 main.py
   ```

2. **Each laptop runs on `localhost:8000`**
   - Natural session isolation (no shared state)
   - Each team gets their own random character selection
   - Independent timers and game state

3. **Access**: Each team opens `http://localhost:8000` on their respective laptop

---

## 🐛 Troubleshooting

### Issue: "Game over! Time expired" immediately
**Solution**: Server and client time out of sync. Reset game.

### Issue: Hints not working
**Solution**: Check that you haven't used 3 hints already for current character.

### Issue: "Failed to load session"
**Solution**: Ensure backend is running on port 8000.

### Issue: Docker container exits
**Solution**: Check `.env` file exists with valid `OPENAI_API_KEY`.

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- OpenAI for GPT-4o-mini API
- FastAPI team for excellent async framework
- Social engineering education community

---

## 📧 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check documentation in code comments
- Review existing win conditions in `characters.py`

---

**Have fun learning social engineering tactics! 🎭🔐**
