import random
import time
import sys

def typewriter(text, delay=0.05):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()  # New line at the end

# Welcome message
typewriter("🕵️  SPY CODENAME GENERATOR 🕵️")
typewriter("=" * 40)

# Ask for user's name
print()  # Blank line
sys.stdout.write("Enter your name, agent: ")
sys.stdout.flush()
name = input()

# Lists of adjectives and animals
adjectives = ["Stealthy", "Swift", "Silent", "Cunning", "Phantom", "Shadow"]
animals = ["Falcon", "Eagle", "Dolphin", "Shark", "Albatross", "Seahawk"]

# Randomly select adjective and animal
random_adjective = random.choice(adjectives)
random_animal = random.choice(animals)

# Generate codename
codename = f"{random_adjective} {random_animal}"

# Generate lucky number (1-99)
lucky_number = random.randint(1, 99)

# Display results with typewriter effect
print()
typewriter("=" * 40)
typewriter(f"Agent {name}:")
typewriter(f"🎭 Codename: {codename}")
typewriter(f"🍀 Lucky Number: {lucky_number}")
typewriter("=" * 40)
print()
typewriter("Good luck on your mission! 🚁")