import re
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.colors as mcolors
import numpy as np

character_re = re.compile(r"^[A-Z#0-9 ]+(?: \(CONT'D\))?\s*$")
dialogue_re = re.compile(r"^[^\n]+\n")
parenthetical_re = re.compile(r"^\([^\)]+\)\n?$")
stage_direction_re = re.compile(r"^\.[^\n]+\n?$")  # Stage directions like .Blackout

def count_words(text):
    return len(text.split())

def clean_line(line):
    return re.sub(r"\(.*?\)", "", line).replace(" (CONT'D)", "").strip()

def extract_script_title(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("Title:"):
                return line.replace("Title:", "").strip()
    return "Untitled Script"

def extract_character_data(file_path, wpm):
    character_data = {}
    current_time = 0
    current_character = None
    capturing_dialogue = False

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        raw_line = line
        stripped_line = line.strip()

        if character_re.match(raw_line):
            current_character = clean_line(raw_line)
            if current_character not in character_data:
                character_data[current_character] = {
                    'positions': [],
                    'word_count': 0,
                    'line_count': 0
                }
            capturing_dialogue = True

        elif parenthetical_re.match(raw_line):
            continue  # Parentheticals allowed between character and dialogue

        elif stage_direction_re.match(raw_line):
            capturing_dialogue = False
            continue

        elif capturing_dialogue and stripped_line:
            if current_character:
                dialogue_text = clean_line(stripped_line)
                word_count = count_words(dialogue_text)
                duration = word_count / wpm * 60
                end_time = current_time + duration

                character_data[current_character]['positions'].append((current_time, end_time))
                character_data[current_character]['word_count'] += word_count
                character_data[current_character]['line_count'] += 1

                current_time = end_time

        if stripped_line == "":
            capturing_dialogue = False

    total_seconds = max(
        end_time for character in character_data.values() for _, end_time in character['positions']
    ) if character_data else 0

    return character_data, total_seconds

def format_duration(total_seconds):
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    return f"{minutes} min {seconds} sec"

def plot_character_activity(character_data, total_seconds, script_title):
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = list(mcolors.TABLEAU_COLORS.values())
    color_map = {character: colors[i % len(colors)] for i, character in enumerate(character_data)}

    num_characters = len(character_data)
    height_per_row = 1 / num_characters if num_characters else 1

    for i, (character, data) in enumerate(character_data.items()):
        y_position = i * height_per_row
        for start_time, end_time in data['positions']:
            ax.add_patch(Rectangle(
                (start_time / 60, y_position),
                (end_time - start_time) / 60,
                height_per_row,
                color=color_map[character],
                alpha=0.5,
                edgecolor=None,
                linewidth=0
            ))
        ax.text(0.05, y_position + height_per_row / 2, character, va='center', ha='left', fontsize=10, color='black', weight='bold')

    ax.set_ylim(0, 1)
    ax.set_xlim(0, total_seconds / 60)
    ax.set_yticks([])

    for minute in range(1, int(np.ceil(total_seconds / 60)) + 1):
        ax.axvline(x=minute, color='gray', linestyle='dotted', lw=1)

    ax.invert_yaxis()
    ax.set_title(script_title, fontsize=14, weight='bold')

    duration_label = format_duration(total_seconds)
    ax.set_xticks([total_seconds / 60])
    ax.set_xticklabels([f"Duration: {duration_label}"], fontsize=10, ha='right')

    plt.tight_layout()
    plt.show()

def display_character_counts(character_data, total_seconds):
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

    total_duration_row = pd.DataFrame([{
        'Character': 'Total Duration',
        'Word Count': '-',
        'Line Count': format_duration(total_seconds)
    }])

    df = pd.concat([df, total_duration_row], ignore_index=True)
    print(df)

def display_cli_timeline(character_data, total_seconds):
    print(f"\nCharacter Activity Timeline (Duration: {format_duration(total_seconds)})")
    max_length = 50  # Width of timeline bar in characters

    for character in sorted(character_data):
        bar = [' '] * max_length
        data = character_data[character]

        for start_time, end_time in data['positions']:
            start_idx = int(start_time / total_seconds * max_length)
            end_idx = int(end_time / total_seconds * max_length)
            for i in range(start_idx, min(end_idx, max_length)):
                bar[i] = '█'

        print(f"{character.ljust(15)}: {''.join(bar)}")



def analyze_fountain_file(file_path, wpm=150, show_plot=False, show_cli=False):
    script_title = extract_script_title(file_path)
    character_data, total_seconds = extract_character_data(file_path, wpm)

    if show_plot:
        plot_character_activity(character_data, total_seconds, script_title)

    if show_cli:
        display_cli_timeline(character_data, total_seconds)

    display_character_counts(character_data, total_seconds)

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Analyze character activity and word/line counts in Fountain files.")
    parser.add_argument("file", help="Path to the Fountain file to analyze.")
    parser.add_argument("--wpm", type=float, default=150, help="Words per minute used for timing dialogue (default: 150).")
    parser.add_argument("--gui_timeline", action="store_true", help="Show a GUI plot of character activity.")
    parser.add_argument("--cli_timeline", action="store_true", help="Show a CLI timeline of character activity.")

    args = parser.parse_args()
    analyze_fountain_file(args.file, wpm=args.wpm, show_plot=args.gui_timeline, show_cli=args.cli_timeline)

if __name__ == '__main__':
    main()
