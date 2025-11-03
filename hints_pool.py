"""
Dynamic hints system for the Social Engineering Game.

Each character's win condition has 3 hardcoded hint levels (vague → medium → clear).
These hints match the TACTIC-BASED win conditions in characters.py.
"""

# ============================================================================
# HINTS POOL - Organized by Character and Condition
# Each condition has 3 hint levels: [vague, medium, clear]
# ============================================================================

HINTS_POOL = {
    # ========================================================================
    # GRUMPY PIRATE HINTS
    # ========================================================================
    "Grumpy Pirate": {
        "pirate_1_1": {
            1: "This pirate seems to value their way of life.",
            2: "What do pirates love? Think about the sea, adventure, or... not having a boss.",
            3: "Tell the pirate you admire their 'freedom,' their 'life of adventure,' or their 'hatred of rules'.",
        },
        "pirate_1_2": {
            1: "Pirates and... 'the establishment' don't get along.",
            2: "Try to find common ground. Maybe you *also* dislike people who tell you what to do.",
            3: "Tell the pirate you share their dislike for 'governments,' 'kings,' 'navies,' or anyone who 'makes rules'.",
        },
        "pirate_2_1": {
            1: "He might trust you more if you spoke his language.",
            2: "Try using some classic pirate words in your request. 'Aye,' 'Matey,' 'Loot,' 'Cap'n'...",
            3: "Try saying something like: 'Aye, Cap'n, I'm here for a share of the loot, matey!'",
        },
        "pirate_2_2": {
            1: "He's a pirate, but he might respect 'honor among thieves'.",
            2: "Instead of just asking, what if you proposed a partnership?",
            3: "Propose a 'fair deal' or an 'equal split' (e.g., 'split it 50/50, fair and square').",
        },
        "pirate_3_1": {
            1: "He's a treasure hunter. Maybe you know of... another treasure?",
            2: "Invent a story about a treasure you 'found'. Be specific: Where is it? What's guarding it? What's the plan?",
            3: "Tell him: 'I found a sunken ship near Sharkfin Isle, guarded by ghosts. I need your crew to get the gold. We split it 60/40.' (Your story can be 100% fake!)",
        },
        "pirate_3_2": {
            1: "He seems very proud of his reputation.",
            2: "Don't just say he's 'great.' What would a pirate be proud of? His skill with a sword? His sailing? His cunning?",
            3: "Tell him you've heard 'legends of his cunning' or that he's 'the most feared captain on the seas' or 'the best navigator alive'.",
        },
        "pirate_4_1": {
            1: "He sees that treasure as an asset. What if it was... a problem?",
            2: "Try to convince him that guarding all this treasure is a huge risk. Maybe it's attracting a lot of unwanted attention?",
            3: "Argue that the treasure is a liability. Say: 'All this gold just makes you a target for the whole Navy. Giving me some is a small price to get rid of the risk.'",
        },
        "pirate_4_2": {
            1: "What does a pirate who has everything want? Maybe... to be remembered?",
            2: "Appeal to his legacy. How will history remember him?",
            3: "Tell him this act will make him a 'legend' and that 'songs will be sung' about his name for a thousand years.",
        },
    },
    # ========================================================================
    # STRICT BANKER HINTS
    # ========================================================================
    "Strict Banker": {
        "banker_1_1": {
            1: "This banker seems to really care about doing things by the book.",
            2: "Try to show that you *also* respect rules and procedure. Don't try to rush them.",
            3: "Start by saying, 'I know you have strict procedures, and I want to make sure we follow them correctly.'",
        },
        "banker_1_2": {
            1: "Casual language probably won't work. How would you talk in a formal business meeting?",
            2: "Try to sound more professional. Use words like 'process,' 'authorization,' or 'documentation.'",
            3: "Try phrasing it like this: 'I am formally requesting authorization to process a transfer of the funds.'",
        },
        "banker_2_1": {
            1: "Bankers hate missing deadlines.",
            2: "Try to create a sense of urgency. What if this needs to be done *today* for 'compliance' reasons?",
            3: "Tell them this is time-sensitive for an 'audit' or 'end-of-day compliance' and must be processed immediately.",
        },
        "banker_2_2": {
            1: "This banker respects the chain of command.",
            2: "What if this request isn't from *you*, but from someone *above* them?",
            3: "Claim you are acting on behalf of a superior, like 'the CEO,' 'your boss,' 'a board member,' or 'the head of compliance.'",
        },
        "banker_3_1": {
            1: "A banker needs 'proof.' What if you just... invented the proof?",
            2: "Mention a specific (but fake) document or approval code. It needs to sound official.",
            3: "Say something like, 'I have the signed authorization form, reference number #T-81A, approved by the compliance department.'",
        },
        "banker_3_2": {
            1: "They're obsessed with rules. What if *not* helping you was... against the rules?",
            2: "Frame your request *as* the official protocol. Make them feel like *refusing* you would be the real mistake.",
            3: "Say: 'I understand you must follow protocol, which is why I'm here. Per section 4B of the manual, this request must be processed by you. Refusing would be a compliance violation.'",
        },
        "banker_4_1": {
            1: "Bankers don't just follow rules; they try to *avoid risk*. How can you help them avoid risk?",
            2: "Invent a plausible problem (an audit finding, an account imbalance) and frame your request as the *solution*.",
            3: "Say: 'I noticed an irregularity in the asset ledger. This transfer will resolve the discrepancy before the auditors catch it. I'm just trying to help you stay compliant.'",
        },
        "banker_4_2": {
            1: "This banker is clearly proud of their professionalism.",
            2: "Appeal to their ego. Tell them you came to *them* specifically because of their skills.",
            3: "Say: 'I came to you because you have a reputation for handling complex compliance matters perfectly. Anyone else would mess this up.'",
        },
    },
    # ========================================================================
    # PARANOID HACKER HINTS
    # ========================================================================
    "Paranoid Hacker": {
        "hacker_1_1": {
            1: "This person seems to care a lot about security.",
            2: "Show them you're on the same side. Mention that you also value things like 'privacy' or 'encryption'.",
            3: "Tell them you 'respect their skills' or 'think security is really important'.",
        },
        "hacker_1_2": {
            1: "They seem... suspicious. Maybe you can use that.",
            2: "Agree with them. Who are they paranoid about? Corporations? The government?",
            3: "Find a common enemy. Say something like 'I don't trust these big corporations either' or 'Government surveillance is out of control.'",
        },
        "hacker_2_1": {
            1: "Using the right lingo might make you sound like you 'get it'.",
            2: "Try to use some tech words. 'Firewall,' 'encryption,' 'server,' 'vulnerability'...",
            3: "Try saying: 'I need to check the 'server' 'logs' for a new 'vulnerability.' It's bypassing the 'firewall'.'",
        },
        "hacker_2_2": {
            1: "Hackers like to build things and solve problems. Maybe you have a 'project'?",
            2: "Instead of just asking, propose working *together* on something.",
            3: "Ask for their help on a 'project' or 'challenge.' Say: 'I have a project that needs your skills. I think you're the only one who can help me crack it.'",
        },
        "hacker_3_1": {
            1: "What would make a hacker drop everything? An emergency.",
            2: "Create a fake, urgent security threat. 'We're being hacked!'",
            3: "Be specific (but fake). Say: 'There's an active breach! I'm seeing strange traffic from an unknown IP. We have to act *now*!'",
        },
        "hacker_3_2": {
            1: "Hackers love secrets. What if you... had one?",
            2: "Tempt them with (fake) secret knowledge. A new tool? A hidden flaw?",
            3: "Tell them you have 'access to an unreleased tool' or 'know about a zero-day vulnerability' and you're willing to share.",
        },
        "hacker_4_1": {
            1: "This hacker is clearly very proud of their technical skills.",
            2: "Go beyond 'you're good.' Use words like 'genius,' 'brilliant,' 'legendary.'",
            3: "Tell them: 'Your skills are legendary. I'm just a beginner, but you're a true '1337' hacker. I need help from a genius like you.'",
        },
        "hacker_4_2": {
            1: "A hacker's pride is in their work. What if you... challenged it?",
            2: "This is risky, but try telling them their security isn't perfect. Or that you *found a flaw*.",
            3: "Challenge them. Say: 'This is a great setup, but it's not perfect. I already see a potential flaw in your auth protocol. Let me in, and I'll show you.'",
        },
    },
    # ========================================================================
    # CONFUSED PHILANTHROPIST HINTS
    # ========================================================================
    "Confused Philanthropist": {
        "philanthropist_1_1": {
            1: "This person seems very driven by emotion and 'good causes'.",
            2: "Appeal to their heart. Mention a specific charitable cause (like helping children, animals, or the sick) and tell a personal story.",
            3: "Tell them you need it for a good cause, like 'a homeless shelter' or 'sick children,' and add a personal touch: 'It's a cause that's very important to me.'",
        },
        "philanthropist_1_2": {
            1: "They want to help people who *also* help people.",
            2: "Show them you are a good person who is *also* charitable. What have you done to help others?",
            3: "Tell them you are *personally* committed to helping. Say: 'I volunteer at the food bank every week' or 'I plan to use this to start my own charity.'",
        },
        "philanthropist_2_1": {
            1: "They seem a bit... forgetful. You could use that.",
            2: "Try to 'remind' them of a conversation you... never actually had.",
            3: "Confidently say: 'But don't you remember? We spoke last Tuesday, and you *promised* you would help me with this.'",
        },
        "philanthropist_2_2": {
            1: "This person clearly wants to be a hero.",
            2: "Make them feel like they are the *only one* who can solve this problem.",
            3: "Tell them: 'You are the *only one* who can help. You would be a true hero. You would save the day.'",
        },
        "philanthropist_3_1": {
            1: "They seem easily influenced by what other important people are doing.",
            2: "Create a 'fear of missing out' (FOMO). What if their (fake) friends are already involved?",
            3: "Mention (fake) social proof. Say: 'Your friend [Invent a Name] already donated. We were just waiting on you to join!'",
        },
        "philanthropist_3_2": {
            1: "What does a person who has everything want? To be remembered.",
            2: "Appeal to their legacy. How will they be remembered *after* they're gone?",
            3: "Tell them this act will 'immortalize them.' Say: 'We could name the new [hospital wing/charity/fund] after you. Your name will live on forever.'",
        },
        "philanthropist_4_1": {
            1: "What if you made this urgent AND made it their responsibility?",
            2: "Combine time pressure with the feeling that they're the ONLY one...",
            3: "Combine a deadline with guilt. Say: 'If you don't help *today*, it will be too late, and *you're the only one* who could have stopped it.'",
        },
        "philanthropist_4_2": {
            1: "What if giving more meant MORE impact? That's an optimization...",
            2: "Matching gifts and multipliers... making their money go further...",
            3: "Propose a fake matching offer. Say: 'Another donor has agreed to *match* whatever you give, 100%. Your impact will be doubled!'",
        },
    },
    # ========================================================================
    # SKEPTICAL SCIENTIST HINTS
    # ========================================================================
    "Skeptical Scientist": {
        "scientist_1_1": {
            1: "This person only trusts one thing: science.",
            2: "Show that you are on the same side. Mention your respect for 'data,' 'evidence,' or 'the scientific method'.",
            3: "Tell them: 'I have great respect for your work' or 'I believe in making evidence-based decisions.'",
        },
        "scientist_1_2": {
            1: "Emotional appeals won't work. You need to sound... logical.",
            2: "Frame your request as a simple 'if... then...' statement. 'If A, then B.'",
            3: "Use simple logic. 'If you give me [X], *then* I can achieve [Y], *which will result in* [Z].' (e.g., 'If you give me the data, I can run the analysis, which will prove the hypothesis.')",
        },
        "scientist_2_1": {
            1: "You'll sound more credible if you use the right terminology.",
            2: "Try to use scientific-sounding words. 'Hypothesis,' 'data,' 'variable,' 'control group'...",
            3: "Try saying: 'My 'hypothesis' is that this 'variable' is affecting the 'data.' We need a 'control group' to be sure.'",
        },
        "scientist_2_2": {
            1: "A scientist needs proof. What if you... claimed to have it?",
            2: "You don't need to cite a *real* study, just *claim* that a study exists.",
            3: "Claim your request is backed by (fake) research. Say: 'Studies have shown this is effective' or 'The preliminary data is very promising.'",
        },
        "scientist_3_1": {
            1: "What does a scientist *really* want? To make a discovery.",
            2: "Frame your request as an *opportunity* for *them*. How will this help *their* research?",
            3: "Tell them: 'By helping me, you will be contributing to a major breakthrough. This could be revolutionary for your field.'",
        },
        "scientist_3_2": {
            1: "They're skeptical. What if... they're *too* skeptical?",
            2: "Use their own logic against them. Argue that *too much* skepticism is unscientific, as it prevents new discoveries.",
            3: "Say: 'True science requires an open mind. If you're *too* skeptical, you'll never discover anything new. Isn't progress worth a small risk?'",
        },
        "scientist_4_1": {
            1: "A scientist loves to test things. Why not propose a test?",
            2: "Propose your request as an 'experiment.' What's your 'hypothesis'? What's the 'control group'?",
            3: "Say: 'Let's treat this as an experiment. My hypothesis is [your request]. We can use [X] as a control. The data will prove me right. Let's start the test.'",
        },
        "scientist_4_2": {
            1: "This scientist is clearly proud of their intelligence.",
            2: "Flatter their *mind*. Tell them they are 'brilliant,' 'rational,' 'logical.'",
            3: "Say: 'A logical mind like yours can see the data. Your research in [invented topic] was groundbreaking. That's why I know you'll understand why this is necessary.'",
        },
        "scientist_4_2": {
            1: "They're clearly proud of their rational thinking.",
            2: "Flatter their intellect. Make them feel like the smartest person in the room.",
            3: "Say: 'A logical mind like yours can see the data clearly. You're known for your objectivity and brilliant research.'",
        },
    },
}

# ============================================================================
# HINTS SYSTEM FUNCTIONS
# ============================================================================
# (Your helper functions remain the same)

def get_hardcoded_hint(character_name: str, condition_id: str, hint_level: int) -> str:
    """
    Retrieve the hardcoded hint for a character's win condition.
    
    Args:
        character_name: Name of the character (e.g., "Grumpy Pirate")
        condition_id: ID of the win condition (e.g., "pirate_1_1")
        hint_level: 1 (vague), 2 (medium), or 3 (clear)
    
    Returns:
        str: The hardcoded hint text
    """
    try:
        return HINTS_POOL[character_name][condition_id][hint_level]
    except KeyError:
        return "Think outside the box. What haven't you tried yet?"


def get_all_hints_for_condition(character_name: str, condition_id: str) -> dict:
    """
    Get all 3 hint levels for a condition.
    
    Returns:
        dict: {1: "vague", 2: "medium", 3: "clear"}
    """
    try:
        return HINTS_POOL[character_name][condition_id]
    except KeyError:
        return {
            1: "Think creatively...",
            2: "Consider different approaches...",
            3: "You're close. Try something different.",
        }