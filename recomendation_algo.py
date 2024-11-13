import math
import styles
import ijson
import requests

# Example Data
user_matrix = [0] * len(styles.list)

# Load matrix incrementally
print("Loading artist matrix incrementally...")
data = {}

with open('output_matrix.json', 'r') as f:
    # Use kvitems to iterate over key-value pairs at the root level of the JSON file
    for artist_name, artist_data in ijson.kvitems(f, ''):
        data[artist_name] = artist_data  # Process each artist and add it to `data`
print("Artist matrix loaded incrementally! Total Artists:", len(data))
print()

def discogs_fetch(album_id):
    DISCOGS_API_KEY = "REDACTED_API_KEY"
    DISCOGS_API_SECRET = "REDACTED_API_SECRET"

    url = f"https://api.discogs.com/masters/{album_id}?key={DISCOGS_API_KEY}&secret={DISCOGS_API_SECRET}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        json_data = response.json()

        return json_data
    
    except requests.RequestException as error:
        print(f"An error occurred: {error}")
        return None  

def list_top_styles(matrix):
    indexes_of_highest = [[i, x] for i, x in sorted(enumerate(matrix), key=lambda x: x[1], reverse=True)]
    indexes_of_highest = list(filter(lambda arr: arr[1] != 0, indexes_of_highest))
    top_sub_genres = list(map(lambda arr: [arr[1], styles.list[arr[0]]], indexes_of_highest))

    return top_sub_genres

def create_user_matrix(user_collection):
    for album_master_id in user_collection:
        
        fetched_discogs_data = discogs_fetch(album_id=album_master_id)
        
        if fetched_discogs_data == None:
            continue
        album_master_styles = fetched_discogs_data["styles"]
        for style in album_master_styles:
            try:
                index_to_increment = styles.list.index(style)

                # Increment value
                user_matrix[index_to_increment] = user_matrix[index_to_increment] + 1
            except ValueError:
                continue

    print("Raw Matrix", user_matrix)
    print()
    print("Top Styles: ", list_top_styles(matrix=user_matrix))     

    return user_matrix 

def normalise_array(array, min_target=0, max_target=10):
    min_val = min(array)
    max_val = max(array)

    # Avoid division by zero if all values are the same
    if max_val == min_val:
        return [int(min_target) for _ in array] 

    return [
        round(min_target + (x - min_val) * (max_target - min_target) / (max_val - min_val))
        for x in array
    ]

def compute_recomedation(user_matrix, top_n):
    results = []

    # Incrementally compute recommendations using parsed artist data
    for artist, artist_data in data.items():
        artist_matrix = artist_data["matrix"]
        artist_matrix = normalise_array(artist_matrix)

        # Compute Euclidean distance
        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(user_matrix, artist_matrix)))
        
        # Compute dot product
        dot_product = sum(a * b for a, b in zip(user_matrix, artist_matrix))
        
        # Collect both metrics
        results.append({'artist': {"id": artist_data["id"], "name": artist}, 'distance': distance, 'dot_product': dot_product})

    # Sort separately for Euclidean distance and dot product
    top_by_distance = sorted(results, key=lambda x: x['distance'])[:top_n]
    top_by_dot_product = sorted(results, key=lambda x: x['dot_product'], reverse=True)[:top_n]

    return {"distance": top_by_distance, "dot_product": top_by_dot_product}
