import re
import pandas as pd
import matplotlib.pyplot as plt

MINUTES_PER_PAGE = 1
LINES_PER_PAGE = 55  # Approximate number of lines per page

# Updated regex pattern for character detection
character_re = re.compile(r"^[A-Z#0-9 ]+\n$")
dialogue_re = re.compile(r"^[^\n]+\n")

def count_words(text):
    """Helper function to count words in dialogue text."""
    return len(text.split())

def extract_character_data(file_path):
    """Extracts character activity, word count, and line count from a Fountain file."""
    character_data = {}
    scene_position = 0

    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Estimate total minutes based on the number of pages
    total_pages = len(lines) / LINES_PER_PAGE
    total_minutes = total_pages * MINUTES_PER_PAGE

    current_character = None

    # Process each line to extract characters and dialogue
    for line in lines:
        if character_re.match(line):
            # Character name identified
            current_character = line.strip()

            if current_character not in character_data:
                character_data[current_character] = {
                    'positions': [],
                    'word_count': 0,
                    'line_count': 0
                }

        elif current_character and dialogue_re.match(line):
            # Dialogue text for the current character
            dialogue_text = line.strip()
            word_count = count_words(dialogue_text)
            line_count = dialogue_text.count('\n') + 1

            character_data[current_character]['word_count'] += word_count
            character_data[current_character]['line_count'] += line_count

            # Estimate time based on scene position relative to total pages
            estimated_time = (scene_position / len(lines)) * total_minutes
            character_data[current_character]['positions'].append(estimated_time)

        scene_position += 1

    return character_data, total_minutes

def plot_character_activity(character_data, total_minutes):
    """Plots character activity across the script timeline."""
    plt.figure(figsize=(10, 6))
    
    for character, data in character_data.items():
        plt.plot(data['positions'], [character] * len(data['positions']), 'o', label=character)

    plt.xlabel("Time (minutes)")
    plt.ylabel("Character")
    plt.title("Character Activity vs Time")
    plt.xlim(0, total_minutes)
    plt.legend(loc="upper left")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def display_character_counts(character_data):
    """Displays a table of character word and line counts."""
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
    print(df)

def analyze_fountain_file(file_path, show_plot=True, verbose=False):
    """Main function to analyze a Fountain file and display both a plot and a table."""
    character_data, total_minutes = extract_character_data(file_path)

    if verbose:
        print(f"Processing file: {file_path}")
        print(f"Total estimated time: {total_minutes:.2f} minutes")

    if show_plot:
        plot_character_activity(character_data, total_minutes)

    display_character_counts(character_data)

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Analyze character activity and word/line counts in Fountain files.")
    parser.add_argument("file", help="Path to the Fountain file to analyze.")
    parser.add_argument("--no-plot", action="store_true", help="Do not show the plot of character activity.")
    parser.add_argument("--verbose", action="store_true", help="Display additional details during execution.")

    args = parser.parse_args()
    analyze_fountain_file(args.file, show_plot=not args.no_plot, verbose=args.verbose)

if __name__ == '__main__':
    main()

