# FountainEval

`fountain_eval` is a Python tool designed to analyze Fountain screenplay files, providing a breakdown of character activity, word counts, and line counts, along with visualizing character dialogue over the duration of the script. This tool is ideal for screenwriters, editors, or anyone looking to get a detailed analysis of their screenplay's structure.

## Features

- **Character Word/Line Count**: Analyze the number of words and lines spoken by each character.
- **Character Activity Plot**: Visualize when each character speaks throughout the screenplay using a timeline.
- **Command Line Interface (CLI)**: Run the tool directly from the command line, providing the path to a `.fountain` file.
- **Fountain Script Formatting**: Automatically handles and parses the Fountain format, respecting proper screenplay formatting.

## Installation

To install `fountain_eval`, clone the repository and install it using `pip`:

```bash
git clone https://github.com/briday1/fountain_eval.git
cd fountain_eval
pip install .
```

Alternatively, you can install directly from GitHub via:

```bash
pip install git+https://github.com/briday1/fountain_eval.git
```

Dependencies
fountain_eval uses the following Python libraries:

- `matplotlib` for visualizing character activity
- `pandas` for processing and displaying character data
- `screenplain` for parsing Fountain files

## Usage

Once installed, you can run `fountain_eval` from the command line by passing a
`.fountain` file as an argument.

```bash
fountain_eval /path/to/your_script.fountain
```

## Example Ouput (CLI)

Processing file: Syzyjury.fountain
Total duration: 160.80 seconds

Character Activity Timeline (Duration: 2 min 40 sec)
PROSECUTION ATTORNEY: █   ████                                  █       
JUROR #85      :  ██                                               
DEFENSE ATTORNEY:    █    █                     ██                  
JUDGE          :          █████          █               █  ███   █
JUROR #86      :               ██████████ █████  ████████ █    ███ 
BAILIFF        :                                                   
              Character Word Count    Line Count
0  PROSECUTION ATTORNEY         48             5
1             JUROR #85         17             1
2      DEFENSE ATTORNEY         43             4
3                 JUDGE         86             9
4             JUROR #86        208            11
5               BAILIFF          0             0
6        Total Duration          -  2 min 40 sec

## Example Output (GUI)

![GUI_OUTPUT)(figs/example.png)
