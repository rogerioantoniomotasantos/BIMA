# WallDimensions.py

def calculate_wall_dimensions(distances_df):
    """
    Given a DataFrame of distances, this function determines the wall's
    thickness, height, and length.
    """
    sorted_distances = distances_df.sort_values(by='Distance')

    # Assuming the smallest distance represents the thickness
    thickness = sorted_distances.iloc[0]['Distance']
    # The largest distance could be the length
    length = sorted_distances.iloc[-1]['Distance']
    # The middle value could be the height
    height = sorted_distances.iloc[len(sorted_distances) // 2]['Distance']

    return thickness, height, length

def format_dimensions(thickness, height, length):
    """
    Format and display wall dimensions.
    """
    return f"Wall Dimensions:\nThickness: {thickness} meters\nHeight: {height} meters\nLength: {length} meters"

