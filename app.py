import flask as f
import requests
from time import time
import recomendation_algo as rec_algo

app = f.Flask(__name__)

class Album:
    def __init__(self, json):
        self.master_id = json["master_id"]
        self.cover_image = json["cover_image"]
        self.title = json["title"]

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)
    
@app.route("/searchDiscogs")
def discogs_fetch():
    albums = []

    search_term = f.request.args.get('search_term')

    DISCOGS_API_KEY = "REDACTED_API_KEY"
    DISCOGS_API_SECRET = "REDACTED_API_SECRET"

    url = f"https://api.discogs.com/database/search?q={search_term}&type=master&format=album&per_page=10&key={DISCOGS_API_KEY}&secret={DISCOGS_API_SECRET}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        json_data = response.json()

        data = []
        for masterJSON in json_data["results"]:
            tempAlbum = Album(masterJSON)
            albums.append(tempAlbum.__dict__)

        return f.jsonify({'albums': albums})
    
    except requests.RequestException as error:
        print(f"An error occurred: {error}")
        return None  

@app.route("/computeRec", methods=['POST'])
def computeRecomendation():
    data = f.request.get_json()  # Parse JSON request in post
    user_collection = data['data']  # Extract the array of master_id's

    print("Collection recived from front-end:", user_collection)

    print("Creating user matrix...")
    user_matrix = rec_algo.create_user_matrix(user_collection=user_collection)
    user_matrix = rec_algo.normalise_array(user_matrix)
    print()

    print("Starting to compute recomnedations...")

    start_time = time()
    user_recomendation_results = rec_algo.compute_recomedation(user_matrix=user_matrix, top_n=10)
    end_time = time()

    # Calculate time to compute recomendation
    elapsed_time = end_time - start_time
    print(f"Time to compute recomedation, elapsed time: {elapsed_time:.4f} seconds")
    print(user_recomendation_results)

    return True

@app.route("/")
def index():
    return f.render_template('index.html')