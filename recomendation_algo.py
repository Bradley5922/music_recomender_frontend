import math
import styles
import json
import requests
import time

# Example Data
user_matrix = [0] * len(styles.list)

# Load in matrix
print("Loading in artist matrix...")
with open('output_matrix.json') as f:
    data = json.load(f)
    f.close()
print("Large artist matrix loaded in! Total Artists:", len(data))
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
    indexes_of_highest = [[i,x] for i, x in sorted(enumerate(matrix), key=lambda x: x[1], reverse=True)]
    # print(indexes_of_highest)
    indexes_of_highest = list(filter(lambda arr: arr[1] != 0, indexes_of_highest))
    # print(indexes_of_highest)
    top_sub_genres = list(map(lambda arr: [arr[1], styles.list[arr[0]]], indexes_of_highest))

    return top_sub_genres

def create_user_matrix(user_collection):
    for album_master_id in user_collection:
        
        fetched_discogs_data = discogs_fetch(album_id=album_master_id)
        
        if fetched_discogs_data == None:
            continue
        # print(fetched_discogs_data)
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

    for artist in data:
        artist_matrix = data[artist]["matrix"]
        # print(artist_matrix)
        artist_matrix = normalise_array(artist_matrix)

        # Compute Euclidean distance
        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(user_matrix, artist_matrix)))
        
        # Compute dot product
        # dot_product = sum(a * b for a, b in zip(user_matrix, artist_matrix))
        
        # Collect both metrics
        results.append({'artist': {"id": data[artist]["id"], "name": artist}, 'distance': distance})

    # Sort separately for Euclidean distance and dot product
    top_by_distance = sorted(results, key=lambda x: x['distance'])[:top_n]
    # top_by_dot_product = sorted(results, key=lambda x: x['dot_product'], reverse=True)[:top_n]

    # Print the top artists by Euclidean distance
    # print(f"\nTop {top_n} artists by Euclidean distance:")
    # for item in top_by_distance:
    #     print(f"Artist: {item['artist']}, Distance: {item['distance']:.2f}")

    # Print the top artists by dot product
    # print(f"\nTop {top_n} artists by Dot Product:")
    # for item in top_by_dot_product:
    #     print(f"Artist: {item['artist']}, Dot Product: {item['dot_product']:.2f}")

    return top_by_distance

# Only run if called directly
# if __name__ == '__main__':
#     BRADLEY_user_discogs_ids = [3167631,3455408,3091320,2889037,2605046,2849290,179186,21680,3085476,2982971,7941]
#     ALLISON_user_discogs_ids = [2545954, 2192617, 2640143, 1777815, 1664705, 2136718, 3038081, 2685212, 2154187, 1849689, 116449, 3003113]
#     LYNSEY_user_discogs_ids = [79018, 669, 74165, 4095, 52860, 102749, 52009, 39316, 48240, 18993, 25922]
#     # ALFI_user_discogs_ids = [7661, 377085, 57521, 124542, 122261]
#     DAVE_user_discogs_ids = [1749910, 17008, 842235, 11001, 1827078,1233928, 1820087,1034752,2013673,4264,231219]

#     user_collection = BRADLEY_user_discogs_ids

#     print("Creating user matrix...")
#     user_matrix = create_user_matrix(user_collection=user_collection)
#     user_matrix = normalise_array(user_matrix)
#     print()

#     print("Starting to compute recomnedations...")

#     start_time = time.time()
#     compute_recomedation(user_matrix=user_matrix, top_n=10)
#     end_time = time.time()

#     # Calculate time to compute recomendation
#     elapsed_time = end_time - start_time
#     print(f"Time to compute recomedation, elapsed time: {elapsed_time:.4f} seconds")
#     print("Exiting...")