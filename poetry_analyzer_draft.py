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
        elif i + 2 < len(stress_pattern) and stress_pattern[i:i+3] == [1, 0, 0]:
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

def analyze_rhyme_scheme(poem_dict):
    sorted_lines = sorted(poem_dict.items())
    results = {}
    rhyme_labels = {}
    current_rhyme_letter = 'A'
    rhyme_schemes = []
    
    # Step 1: Process lines in chunks of four
    for i in range(0, len(sorted_lines), 4):
        chunk = sorted_lines[i:i+4]
        rhyme_sequence = []
        
        # Step 2: Assign rhyme labels to each line in the chunk
        for line_number, line in chunk:
            last_word = line.split(" ")[-1].lower().strip(".,;!?")
            if last_word in rhyme_labels:
                results[line_number] = rhyme_labels[last_word]
            else:
                results[line_number] = current_rhyme_letter
                rhyme_labels[last_word] = current_rhyme_letter
                current_rhyme_letter = chr(ord(current_rhyme_letter) + 1)
                if current_rhyme_letter > 'Z':
                    current_rhyme_letter = 'A'

            rhyme_sequence.append(results[line_number])

        # Step 3: Match the chunk's rhyme pattern with known schemes
        rhyme_pattern = ''.join(rhyme_sequence)
        possible_schemes = {
            'AABB':  ['AABB', 'CCDD', 'EEFF', 'GGHH'],
            'ABAB': ['ABAB', 'CDCD', 'EFEF', 'GHGH'],
            'ABBA': ['ABBA', 'CDDC', 'EFEG', 'HGHH'],
            'AAAA': ['AAAA', 'BBBB', 'CCCC', 'DDDD'],
            'BABA': ['BABA', 'CDCD', 'EFEF', 'GHGH']
        }

        matched_scheme = None
        for scheme, patterns in possible_schemes.items():
            if any(rhyme_pattern.startswith(pattern) for pattern in patterns):
                matched_scheme = scheme
                break

        # If chunk size is less than 4, just append the current pattern
        if len(chunk) < 4:
            rhyme_schemes.append(rhyme_pattern)
        else:
            rhyme_schemes.append(matched_scheme if matched_scheme else "Unknown")
    
    return results, rhyme_schemes

def analyze_alliteration(poem_dict):
    alliteration_results = {}

    def get_initial_consonant(word):
        # Extract the initial consonant sound
        match = re.match(r'^[^aeiouAEIOU]*', word)
        return match.group().lower() if match else ""

    # Step 1: Process each line in the poem
    for line_number, line in poem_dict.items():
        words = line.split()
        consonants = [get_initial_consonant(word) for word in words if get_initial_consonant(word)]
        
        # Step 2: Count the occurrences of each consonant sound
        consonant_count = Counter(consonants)
        
        # Step 3: Identify alliteration (consonant sounds that appear more than once)
        alliteration = {consonant: count for consonant, count in consonant_count.items() if count > 1}
        
        # Step 4: Store the results
        alliteration_results[line_number] = alliteration
    
    return alliteration_results
def save_rhyme_network(rhyme_results, file_name='rhyme_network.png'):
    G = nx.DiGraph()
    
    # Create a set of unique rhyme schemes
    unique_rhymes = set(rhyme_results.values())
    
    # Add nodes for each unique rhyme scheme
    for rhyme in unique_rhymes:
        G.add_node(rhyme)
    
    # Add edges based on transitions between rhyme schemes
    sorted_lines = sorted(rhyme_results.keys())
    for i in range(len(sorted_lines) - 1):
        current_line = sorted_lines[i]
        next_line = sorted_lines[i + 1]
        current_rhyme = rhyme_results[current_line]
        next_rhyme = rhyme_results[next_line]
        
        if current_rhyme != next_rhyme:
            G.add_edge(current_rhyme, next_rhyme, label=f'{current_rhyme} -> {next_rhyme}')
    
    pos = nx.spring_layout(G)
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000, font_size=10, arrows=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'label'))
    plt.title('Rhyme Network')
    plt.savefig(file_name)
    plt.close()

def save_meter_network(meter_results, file_name='meter_network.png'):
    G = nx.DiGraph()
    
    # Create a set of unique meters
    unique_meters = set(' '.join(data['meter']) for data in meter_results.values())
    
    # Add nodes for each unique meter
    for meter in unique_meters:
        G.add_node(meter)
    
    # Add edges based on transitions between meters
    sorted_lines = sorted(meter_results.keys())
    for i in range(len(sorted_lines) - 1):
        current_line = sorted_lines[i]
        next_line = sorted_lines[i + 1]
        current_meter = ' '.join(meter_results[current_line]['meter'])
        next_meter = ' '.join(meter_results[next_line]['meter'])
        
        if current_meter != next_meter:
            G.add_edge(current_meter, next_meter, label=f'{current_meter} -> {next_meter}')
    
    pos = nx.spring_layout(G)
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_color='lightgreen', edge_color='gray', node_size=2000, font_size=10, arrows=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'label'))
    plt.title('Meter Network')
    plt.savefig(file_name)
    plt.close()

    
    pos = nx.spring_layout(G)
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_color='lightgreen', edge_color='gray', node_size=2000, font_size=10, arrows=True)
    plt.title('Meter Network')
    plt.savefig(file_name)
    plt.close()


def save_alliteration_visualization(alliteration_results, file_name='alliteration.png'):
    alliteration_counts = Counter()
    
    for line_number, alliteration in alliteration_results.items():
        alliteration_counts.update(alliteration)
    
    consonants, counts = zip(*alliteration_counts.items()) if alliteration_counts else ([], [])
    
    plt.figure(figsize=(10, 6))
    plt.bar(consonants, counts, color='salmon')
    plt.xlabel('Consonant')
    plt.ylabel('Count')
    plt.title('Alliteration Frequency')
    plt.savefig(file_name)
    plt.close()


def combine_images(image_files, output_file='combined_output.png'):
    images = [Image.open(img) for img in image_files]
    
    widths, heights = zip(*(i.size for i in images))

    total_width = max(widths)
    total_height = sum(heights)

    new_image = Image.new('RGB', (total_width, total_height))

    y_offset = 0
    for img in images:
        new_image.paste(img, (0, y_offset))
        y_offset += img.height

    new_image.save(output_file)

def features_detected(poem_text):
    poem_dict = poem_to_dict(poem_text)
    print(poem_dict)
    rhyme_results, rhyme_schemes = analyze_rhyme_scheme(poem_dict)
    meter_results = analyze_metre(poem_dict)
    alliteration_results = analyze_alliteration(poem_dict)
    print((rhyme_results, rhyme_schemes))
    # Save individual visualizations
    save_rhyme_network(rhyme_results, 'rhyme_network.png')
    save_meter_network(meter_results, 'meter_network.png')
    save_alliteration_visualization(alliteration_results, 'alliteration.png')
    
    # Combine the saved images into a single image
    combine_images(['rhyme_network.png', 'meter_network.png', 'alliteration.png'], 'combined_output.png')

    return {
        'rhyme_results': rhyme_results,
        'rhyme_schemes': rhyme_schemes,
        'meter_results': meter_results,
        'alliteration_results': alliteration_results
    }

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./script_name.py <path_to_text_file>")
        sys.exit(1)
    file_path = sys.argv[1]
    features_detected(file_path)
