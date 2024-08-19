#!/usr/bin/env python3
import nltk
from nltk.corpus import cmudict
import re
from collections import Counter
import networkx as nx
import matplotlib.pyplot as plt
import sys
from PIL import Image
# Load the CMU Pronouncing Dictionary
nltk.download('cmudict')
cmu_dict = cmudict.dict()

def poem_to_dict(poem_file_path):
    """
    Converts a multi-line text file containing poem text into a dictionary format.
    Each line is assigned a line number starting from 1, and each line's full text is preserved.
    
    Args:
        poem_file_path (str): Path to the text file containing the poem.
        
    Returns:
        dict: A dictionary where each key is a line number, and each value is the full text of that line.
    """
    with open(poem_file_path, 'r') as file:
        lines = file.read().strip().split('\n')
        
    # Create a dictionary where each line number maps to the full text of that line
    poem_dict = {i+1: line for i, line in enumerate(lines)}
    
    return poem_dict


def syllabify(word):
    """
    Break down a word into its syllables using the CMU Pronouncing Dictionary.
    """
    word = word.lower()
    if word in cmu_dict:
        # Get the pronunciation list (list of phonemes)
        pronunciations = cmu_dict[word][0]
        # Split the pronunciation at '0', '1', '2' which indicate syllable boundaries
        syllables = []
        syllable = []
        for phoneme in pronunciations:
            syllable.append(phoneme)
            if phoneme[-1].isdigit():  # Indicates end of a syllable
                syllables.append(syllable)
                syllable = []
        return syllables
    else:
        return [word]  # If the word is not found, return the word as a single syllable

def get_stress_pattern(word):
    """
    Extract the stress pattern of a word using the CMU Pronouncing Dictionary.
    """
    syllables = syllabify(word)
    stress_pattern = []
    for syllable in syllables:
        for phoneme in syllable:
            if phoneme[-1].isdigit():  # Check if the phoneme has a stress marker
                stress_pattern.append(int(phoneme[-1]))
    return stress_pattern

def process_line_with_stress(line):
    words = line.split()
    stress_patterns = []
    for word in words:
        stress = get_stress_pattern(word)
        if stress:
            stress_patterns.extend(stress)
    return stress_patterns

def identify_meter(stress_pattern):
    meter = []
    i = 0
    while i < len(stress_pattern):
        if i + 1 < len(stress_pattern) and stress_pattern[i:i+2] == [0, 1]:
            meter.append("Iamb")
            i += 2
        elif i + 1 < len(stress_pattern) and stress_pattern[i:i+2] == [1, 0]:
            meter.append("Trochee")
            i += 2
        elif i + 2 < len(stress_pattern) and stress_pattern[i:i+3] == [0, 0, 1]:
            meter.append("Anapest")
            i += 3
        elif i + 2 < len(stress_pattern) and (stress_pattern[i:i+3] == [1, 0, 0] or stress_pattern[i:i+3] == [0,1,1]) :
            meter.append("Dactyl")
            i += 3
        elif i + 1 < len(stress_pattern) and stress_pattern[i:i+2] == [1, 1]:
            meter.append("Spondee")
            i += 2
        elif i + 1 < len(stress_pattern) and stress_pattern[i:i+2] == [0, 0]:
            meter.append("Pyrrhic")
            i += 2
        else:
            i += 1
    return meter

def analyze_metre(poem_dict):
    results = {}
    for line_number, line in poem_dict.items():
        stress_pattern = process_line_with_stress(line)
        meter = identify_meter(stress_pattern)
        results[line_number] = {
            'stress_pattern': stress_pattern,
            'meter': meter
        }
    return results
def state_metre(metre_results):
    fsm = {}
    for line_number, analysis in metre_results.items():
        meter = analysis['meter']
        for element in meter:
            fsm[element]
def save_metre_graph(poem_file_path, filename='metre_graph.png'):
    # Convert the poem text file to a dictionary
    poem_dict = poem_to_dict(poem_file_path)

    # Analyze the poem to get stress patterns and meters
    analysis_results = analyze_metre(poem_dict)
    print(analysis_results)
    # Initialize a directed graph
    G = nx.DiGraph()

    # Track all transitions across the entire poem
    for line_number, analysis in analysis_results.items():
        meter = analysis['meter']

        # Create directed edges based on transitions between meters in each line
        for i in range(len(meter) - 1):
            if G.has_edge(meter[i], meter[i + 1]):
                # If the edge already exists, increase the weight
                G[meter[i]][meter[i + 1]]['weight'] += 1
            else:
                # If the edge doesn't exist, create it with weight 1
                G.add_edge(meter[i], meter[i + 1], weight=1)

    # Draw the directed graph
    pos = nx.spring_layout(G)  # Positioning the nodes
    nx.draw(G, pos, with_labels=True, node_color='lightblue', font_weight='bold', font_size=10, arrows=True)

    # Draw edge labels to show the number of transitions between meters
    edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    # Save the graph as an image file
    plt.savefig(filename)
def sequence_metre_diagram(poem_file_path,sequence_filename='sequence_diagram.png'):
    poem_dict = poem_to_dict(poem_file_path)
    analysis_results = analyze_metre(poem_dict)
    plt.figure(figsize=(12, len(poem_dict) * 0.5))
    for line_number, analysis in analysis_results.items():
        meter = analysis['meter']
        plt.plot(range(len(meter)), meter, marker='o', label=f'Line {line_number}')

    plt.xlabel('Position in Line')
    plt.ylabel('Meter')
    plt.title('Meter Sequence Diagram')
    plt.legend()
    plt.xticks(range(len(meter)), rotation=45)
    plt.savefig(sequence_filename)
    plt.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./script_name.py <path_to_text_file>")
        sys.exit(1)
    file_path = sys.argv[1]
    save_metre_graph(file_path)
    sequence_metre_diagram(file_path)
