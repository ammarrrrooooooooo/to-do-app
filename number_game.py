import random
import time

def print_with_delay(text, delay=0.03):
    """Print text with a typewriter effect"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def get_difficulty():
    """Get the difficulty level from the user"""
    print_with_delay("\nChoose difficulty level:")
    print_with_delay("1. Easy (1-50)")
    print_with_delay("2. Medium (1-100)")
    print_with_delay("3. Hard (1-200)")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-3): "))
            if choice in [1, 2, 3]:
                return {1: 50, 2: 100, 3: 200}[choice]
            print("Please enter 1, 2, or 3.")
        except ValueError:
            print("Invalid input! Please enter a number.")

def play_game():
    """Main game function"""
    print_with_delay("🎮 Welcome to the Number Guessing Game! 🎮")
    
    # Get the range based on difficulty
    max_number = get_difficulty()
    secret_number = random.randint(1, max_number)
    attempts = 0
    max_attempts = 10
    
    print_with_delay(f"\nI'm thinking of a number between 1 and {max_number}.")
    print_with_delay(f"You have {max_attempts} attempts to guess it!")

    while attempts < max_attempts:
        try:
            guess = int(input("\nEnter your guess: "))
            attempts += 1
            
            if guess < 1 or guess > max_number:
                print_with_delay(f"Please enter a number between 1 and {max_number}!")
                continue
                
            if guess == secret_number:
                print_with_delay("\n🎉 Congratulations! You've won! 🎉")
                print_with_delay(f"You guessed it in {attempts} attempts!")
                score = calculate_score(attempts, max_attempts, max_number)
                print_with_delay(f"Your score: {score} points!")
                return
            
            # Provide hints
            if guess < secret_number:
                print_with_delay("Too low! Try a higher number.")
            else:
                print_with_delay("Too high! Try a lower number.")
                
            print_with_delay(f"Attempts remaining: {max_attempts - attempts}")
            
        except ValueError:
            print_with_delay("Please enter a valid number!")
            
    print_with_delay(f"\n😔 Game Over! The number was {secret_number}.")

def calculate_score(attempts, max_attempts, max_number):
    """Calculate the player's score based on attempts and difficulty"""
    base_score = 1000
    difficulty_multiplier = max_number / 50  # Higher difficulty = higher potential score
    attempt_factor = (max_attempts - attempts + 1) / max_attempts
    return int(base_score * attempt_factor * difficulty_multiplier)

if __name__ == "__main__":
    while True:
        play_game()
        play_again = input("\nWould you like to play again? (yes/no): ").lower()
        if play_again != 'yes':
            print_with_delay("\nThanks for playing! Goodbye! 👋")
            break 