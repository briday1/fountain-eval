import re
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.colors as mcolors
import numpy as np

WORDS_PER_MINUTE = 150  # Words spoken per minute

# Adjusted regex patterns to handle characters with numbers and special characters
character_re = re.compile(r"^[A-Z#0-9 ]+(?: \(CONT'D\))?\s*$")
dialogue_re = re.compile(r"^[^\n]+\n")
parenthetical_re = re.compile(r"^\([^\)]+\)\n$")
stage_direction_re = re.compile(r"^\.[^\n]+\n$")  # To capture stage directions like .Blackout

def count_words(text):
    """Helper function to count words in dialogue text."""
    return len(text.split())

def clean_line(line):
    """Remove any parentheticals or CONT'D from character names or dialogue."""
    return re.sub(r"\(.*?\)", "", line).replace(" (CONT'D)", "").strip()

def extract_script_title(file_path):
    """Extracts the title of the script from the Fountain file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("Title:"):
                return line.replace("Title:", "").strip()
    return "Untitled Script"

def extract_character_data(file_path):
    """Extracts character activity, word count, and line count from a Fountain file."""
    character_data = {}
    current_time = 0  # Start the timeline at 0 minutes
    current_character = None
    capturing_dialogue = False  # Flag to handle multiline dialogue

    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Process each line to extract characters and dialogue
    for i, line in enumerate(lines):
        cleaned_line = clean_line(line)  # Clean the line from parentheticals and CONT'D

        # Check if this is a character name
        if character_re.match(cleaned_line):
            current_character = cleaned_line.strip()

            if current_character not in character_data:
                character_data[current_character] = {
                    'positions': [],
                    'word_count': 0,
                    'line_count': 0
                }
            capturing_dialogue = True  # Start capturing dialogue after character name

        # Skip parentheticals and stage directions
        elif parenthetical_re.match(cleaned_line) or stage_direction_re.match(cleaned_line):
            continue

        # Handle dialogue
        elif capturing_dialogue and cleaned_line:
            if current_character:
                dialogue_text = cleaned_line.strip()
                word_count = count_words(dialogue_text)

                # Calculate the duration of this speaking turn based on word count
                duration = word_count / WORDS_PER_MINUTE * 60  # Duration in seconds
                end_time = current_time + duration

                # Append this speaking turn to the character's activity
                character_data[current_character]['positions'].append((current_time, end_time))
                character_data[current_character]['word_count'] += word_count
                character_data[current_character]['line_count'] += 1

                # Update current time for the next speaking turn
                current_time = end_time

        # If we reach an empty line, stop capturing dialogue for this character
        if cleaned_line == "":
            capturing_dialogue = False

    # Calculate total duration as the maximum end_time across all characters
    total_seconds = max(end_time for character in character_data.values() for _, end_time in character['positions'])

    return character_data, total_seconds

def format_duration(total_seconds):
    """Converts total duration in seconds to 'x min y sec' format."""
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    return f"{minutes} min {seconds} sec"

def plot_character_activity(character_data, total_seconds, script_title):
    """Plots character activity across the script timeline with stylistic rectangles and unique colors."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Generate a unique color for each character
    colors = list(mcolors.TABLEAU_COLORS.values())  # Get a predefined color palette
    color_map = {character: colors[i % len(colors)] for i, character in enumerate(character_data)}

    # Adjust the height and vertical position to remove gaps
    num_characters = len(character_data)
    height_per_row = 1 / num_characters  # Height of each row, so there's no gap

    # Plot each character's dialogue turn as a rectangle
    for i, (character, data) in enumerate(character_data.items()):
        y_position = i * height_per_row
        for start_time, end_time in data['positions']:
            # Transparent rectangles with no borders, filling the y-axis completely
            ax.add_patch(Rectangle(
                (start_time / 60, y_position),          # Start point
                (end_time - start_time) / 60,           # Width (duration in minutes)
                height_per_row,                         # Height per row
                color=color_map[character],             # Fill color
                alpha=0.5,                              # Transparency
                edgecolor=None,                         # No edge color
                linewidth=0                             # No border
            ))

        # Move character labels inside the plot boundary, but closer to 0 on the x-axis
        ax.text(0.05, y_position + height_per_row / 2, character, va='center', ha='left', fontsize=10, color='black', weight='bold')

    # Formatting the plot
    ax.set_ylim(0, 1)  # Set y-limits from 0 to 1 to fill the space
    ax.set_xlim(0, total_seconds / 60)  # Set xlim to the actual total duration in minutes
    ax.set_yticks([])  # Remove y-axis labels (we'll label the characters manually)

    # Add vertical dotted lines at every one-minute interval
    for minute in range(1, int(np.ceil(total_seconds / 60)) + 1):
        ax.axvline(x=minute, color='gray', linestyle='dotted', lw=1)

    # Invert the y-axis to match the CLI output style
    ax.invert_yaxis()

    # Title of the plot is the script title
    ax.set_title(script_title, fontsize=14, weight='bold')

    # Add a single label at the far right indicating total duration
    duration_label = format_duration(total_seconds)
    ax.set_xticks([total_seconds / 60])  # Set a single xtick at the end
    ax.set_xticklabels([f"Duration: {duration_label}"], fontsize=10, ha='right')

    plt.tight_layout()
    plt.show()

def display_character_counts(character_data, total_seconds):
    """Displays a table of character word and line counts, and script total duration."""
    char_stats = {
        'Character': [],
        'Word Count': [],
        'Line Count': []
    }

    for character, data in character_data.items():
        char_stats['Character'].append(character)
        char_stats['Word Count'].append(data['word_count'])
        char_stats['Line Count'].append(data['line_count'])

    df = pd.DataFrame(char_stats)

    # Create a new row for the total duration
    total_duration_row = pd.DataFrame([{
        'Character': 'Total Duration',
        'Word Count': '-',
        'Line Count': format_duration(total_seconds)
    }])

    # Use pd.concat instead of deprecated append
    df = pd.concat([df, total_duration_row], ignore_index=True)

    print(df)

def display_cli_timeline(character_data, total_seconds):
    """Displays a CLI timeline of character activity using bars."""
    print(f"\nCharacter Activity Timeline (Duration: {format_duration(total_seconds)})")
    max_length = 50  # Max length for each bar in the CLI
    for character, data in character_data.items():
        bar = [' '] * max_length
        for start_time, end_time in data['positions']:
            start_idx = int(start_time / total_seconds * max_length)
            end_idx = int(end_time / total_seconds * max_length)
            for i in range(start_idx, end_idx):
                bar[i] = '█'
        print(f"{character.ljust(15)}: {''.join(bar)}")

def analyze_fountain_file(file_path, show_plot=False, show_cli=False, verbose=False):
    """Main function to analyze a Fountain file and display either a plot, CLI timeline, or both."""
    # Extract the script title
    script_title = extract_script_title(file_path)

    # Analyze the character data
    character_data, total_seconds = extract_character_data(file_path)

    if verbose:
        print(f"Processing file: {file_path}")
        print(f"Total duration: {total_seconds:.2f} seconds")

    if show_plot:
        plot_character_activity(character_data, total_seconds, script_title)

    if show_cli:
        display_cli_timeline(character_data, total_seconds)

    display_character_counts(character_data, total_seconds)

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Analyze character activity and word/line counts in Fountain files.")
    parser.add_argument("file", help="Path to the Fountain file to analyze.")
    parser.add_argument("--gui_timeline", action="store_true", help="Show a GUI plot of character activity.")
    parser.add_argument("--cli_timeline", action="store_true", help="Show a CLI timeline of character activity.")
    parser.add_argument("--verbose", action="store_true", help="Display additional details during execution.")

    args = parser.parse_args()
    analyze_fountain_file(args.file, show_plot=args.gui_timeline, show_cli=args.cli_timeline, verbose=args.verbose)

if __name__ == '__main__':
    main()
