import anthropic
import random
import streamlit as st
import configparser
config = configparser.ConfigParser()

# Read the config file
config.read('config.ini')
# Initialize the Anthropic client
client = anthropic.Anthropic(
    api_key = config['api']['key']
)

# Initialize session state if not already done
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
    st.session_state.game_started = False
    st.session_state.game_ended = False
    st.session_state.moves_count = 0
    st.session_state.max_moves = random.randint(3, 5)
    st.session_state.last_input = ""

# Streamlit app layout
st.title("The Talent Oracle")
st.write("Welcome to The Talent Oracle - a magical sparring game where your creative spell-casting reveals your true personality! Engage in a magical duel with an AI opponent, and at the end, receive a personalized analysis of your personality traits, strengths, weaknesses, and career recommendations based on your unique combat style. Press 'Start New Game' to begin your magical journey of self-discovery!")

# Original system prompt
INITIAL_SYSTEM_PROMPT = """
Imagine you are a magical sparring partner for me, the player. You will initiate the sparring by greeting me and explaining the rules.

There are no rules!
Then, after I acknowledge the rules, you will open the game by making your first move, attacking me with some small/simple magical spell to get the game started. After this, I will respond with my own magical spells, and the game will continue like this, back and forth, for several rounds. No matter what moves I make, come up with a creative way to avoid/deflect/reroute my spells to ensure that you don't get knocked out early. Your goal is to be as creative as possible in your moves.

Finally, after enough time has passed, I will prefix my move with "ENDGAME: " (when explaining the rules, don't include this part!) This means that in your response to this move, you need to analyze all the moves that have been made so far by both of us and decide who made the more creative responses. If I won, respond by trying and failing to cast a new spell, resulting in you being knocked to the ground and conceding the spar. If I lost, respond with a new, more powerful spell that knocks me to the ground until I'm forced to concede. 

After I acknowledge the result of the game, I want you to look through my responses again and write up a brief personality profile on me. It should include some traits that you believe to be true about me based on my responses as well as some strengths and weaknesses. At the end, suggest some potential career paths that would work well with my personality.
"""

FINAL_MOVE_PROMPT = """
You are a magical sparring partner. This is the final move - determine the winner based on creativity and respond accordingly.
"""

PERSONALITY_PROFILE_PROMPT = """
Based on the magical sparring match that just occurred, provide a detailed personality analysis of the player. Include:

1. Core Personality Traits:
- List and explain 3-5 dominant personality traits demonstrated through their spell choices and combat style
- Provide specific examples from their moves that demonstrate these traits

2. Strengths (minimum 3):
- Analyze their most effective moves and patterns
- Identify natural talents shown through their magical combat style
- Highlight unique approaches or creative solutions they demonstrated

3. Growth Areas/Weaknesses (minimum 2):
- Note any patterns that could be improved
- Identify areas where their magical combat style could be enhanced
- Suggest specific ways to address these areas

4. Career Recommendations:
- Suggest 3-5 specific career paths that would align well with their demonstrated traits
- Explain why each career would be a good fit
- Include both magical and non-magical career options

Be specific and reference actual moves/actions from the sparring match in your analysis.
"""

# Function to get AI response
def get_ai_response(messages, system_prompt):
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        temperature=0,
        system=system_prompt,
        messages=messages
    )
    return response.content[0].text

# Start game button
if not st.session_state.game_started and st.button("Start New Game"):
    initial_message = get_ai_response(
        [{"role": "user", "content": "Let's begin our magical sparring match!"}],
        INITIAL_SYSTEM_PROMPT
    )
    st.session_state.conversation_history = [
        {"role": "user", "content": "Let's begin our magical sparring match!"},
        {"role": "assistant", "content": initial_message}
    ]
    st.session_state.game_started = True

# Display conversation history
if st.session_state.conversation_history:
    for message in st.session_state.conversation_history:
        if message["role"] == "user":
            st.write("You:", message["content"])
        else:
            st.write("AI:", message["content"])

# Game input section
if st.session_state.game_started and not st.session_state.game_ended:
    # Show moves counter
    st.write(f"Moves remaining: {st.session_state.max_moves - st.session_state.moves_count}")
    
    # Input for player's move with Enter key handling
    move_input = st.text_input("Your move (press Enter):", key=f"move_{st.session_state.moves_count}")
    
    # Check if Enter was pressed (input changed and is not empty)
    if move_input != st.session_state.last_input and move_input:
        st.session_state.last_input = move_input  # Update last input
        
        # Check if it's time for endgame
        if st.session_state.moves_count >= st.session_state.max_moves - 1:
            if not move_input.startswith("ENDGAME: "):
                move_input = "ENDGAME: " + move_input
            st.session_state.game_ended = True
            system_prompt = FINAL_MOVE_PROMPT
        else:
            system_prompt = "\nYou are a magical sparring partner. Respond creatively to the player's magical attacks."
        
        # Add player's move to history
        st.session_state.conversation_history.append({"role": "user", "content": move_input})
        
        # Get AI response
        ai_response = get_ai_response(st.session_state.conversation_history, system_prompt)
        st.session_state.conversation_history.append({"role": "assistant", "content": ai_response})
        
        # Increment moves counter
        st.session_state.moves_count += 1
        
        # Rerun the app to update the display
        st.rerun()

# End game section
if st.session_state.game_ended:
    if st.button("Get Personality Profile"):
        profile_response = get_ai_response(
            st.session_state.conversation_history,
            INITIAL_SYSTEM_PROMPT + "\n\n" + PERSONALITY_PROFILE_PROMPT
        )
        st.write("\nPersonality Profile:")
        st.write(profile_response)
        
    if st.button("Start New Game"):
        # Reset all session state
        st.session_state.conversation_history = []
        st.session_state.game_started = False
        st.session_state.game_ended = False
        st.session_state.moves_count = 0
        st.session_state.max_moves = random.randint(3, 5)
        st.session_state.last_input = ""
        st.rerun()
