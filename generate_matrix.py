import json
import styles
import genres

print("Total styles: ", len(styles.list))
print("Total top level genres: ", len(genres.list))

print("Starting Matrix Generation (loading in file)...")

with open('masters.json') as f:
    data = json.load(f)
    f.close()

artists = {}

def gen_dict(artists):
    elements_cycled_through = 0
    not_in_condensed_list = 0 
    in_condensed_list = 0

    for master in data:
        # Increment to keep track of progress
        elements_cycled_through += 1

        if (elements_cycled_through % 100000) == 0:
            # Allows me to check progress of program
            print("Percent of elements iterated though:", int(((elements_cycled_through / len(data)) * 100)),"%")

        # Init matrix
        matrix = [0] * len(styles.list)

        main_artist = master["artists"][0]
        main_artist_name = main_artist["name"]
        master_styles = master["styles"]
        master_genres = master["genres"]

        # If already in list, we need to append to their matrix
        if main_artist_name in artists:
            matrix = artists[main_artist_name]["matrix"]
        # print(matrix)

        for style in master_styles:
            try:
                index_to_increment = styles.list.index(style)
                in_condensed_list += 1

                # Increment value
                matrix[index_to_increment] = matrix[index_to_increment] + 1
            except ValueError:
                not_in_condensed_list += 1
                # print("masters style not in condensed list")
        
        artists[main_artist_name] = {"id": main_artist["id"], "matrix": matrix}

    print()
    print("DONE!")
    print("Artists: ", len(artists))
    print("Instances of style NOT being in list: ", not_in_condensed_list)
    print("Instances of style BEING in list: ", in_condensed_list)  
    print()

    return artists

def list_top_styles(matrix):
    indexes_of_highest = [[i,x] for i, x in sorted(enumerate(matrix), key=lambda x: x[1], reverse=True)]
    # print(indexes_of_highest)
    indexes_of_highest = list(filter(lambda arr: arr[1] != 0, indexes_of_highest))
    # print(indexes_of_highest)
    top_sub_genres = list(map(lambda arr: [arr[1], styles.list[arr[0]]], indexes_of_highest))

    return top_sub_genres

def search_dict(artists):
    while True:
        search_term = input("Search Artist Dictionary: ")
        
        if search_term == "exit":
            print("Exiting search...")
            break

        try: 
            results = artists[search_term]

            print("Entry:", results)
            print()

            print("Top Styles:", list_top_styles(matrix=results["matrix"]))
            print()
        except KeyError:
            print("Artist Not Found")

def output_to_file(artists):
    print("\nOutputting to file...")

    # def format_array(array, chunk_size=40):
    #     # Break the array into chunks
    #     chunks = [array[i:i + chunk_size] for i in range(0, len(array), chunk_size)]
    #     # Format each chunk as a JSON array, separated by commas
    #     return '[\n' + ',\n'.join('    ' + json.dumps(chunk) for chunk in chunks) + '\n]'

    with open('output_matrix.json', 'w+', encoding='utf-8') as f:
        f.write('{\n')
        # Iterate through each artist and their values
        for i, (artist, values) in enumerate(artists.items()):

            # Remove backslashes and escape quotes in artist names
            safe_artist = artist.replace('\\', '').replace('"', '\\"')
            
            safe_id = values.get("id")
            if safe_id == "" or safe_id is None:
                safe_id = 0   

            # Format the artist name and values, using format_array for the arrays
            f.write(f'    "{safe_artist}": {{"id": {safe_id}, "matrix": {values["matrix"]}}}')
            # Add a comma if it's not the last item
            if i < len(artists) - 1:
                f.write(',\n')
            else:
                f.write('\n')
        f.write('}\n')
    
    print("Saved to file, exiting...")

if __name__ == '__main__':
    artists = gen_dict(artists=artists)        
    search_dict(artists=artists)
    output_to_file(artists=artists)
