from collections import defaultdict
from .mart import group_personality_mapping, group_keywords, color_mapping, personality_values

def mapping(genres):
    personality_points = defaultdict(int)
    # Iterate through the genres and update the personality points
    for genre_list in genres:
        for genre in genre_list:
            for group, keywords in group_keywords.items():
                if any(keyword in genre.lower() for keyword in keywords):
                    for trait in group_personality_mapping[group]:
                        personality_points[trait] += 1
    # Get the top three personality traits with the highest points
    top_personality_traits = sorted(personality_points, key=personality_points.get, reverse=True)[:3]

    return top_personality_traits

def map_personality_to_color(top_personality_traits):
    
    mapped_traits = [personality_values[trait] for trait in top_personality_traits]
    average_score = sum(mapped_traits) / len(mapped_traits)

    for range, color in color_mapping.items():
        if range[0] <= average_score < range[1]:
            return color

    return None  # Handle case when no color is found within the specified ranges
