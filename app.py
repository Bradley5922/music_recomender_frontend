import flask as f
import requests
from time import time
import emailSender
import recomendation_algo as rec_algo

DISCOGS_API_KEY = "REDACTED_API_KEY"
DISCOGS_API_SECRET = "REDACTED_API_SECRET"

app = f.Flask(__name__)

class DiscogsAlbumData:
    def __init__(self, album_data):
        self.master_id = album_data["master_id"]
        self.cover_image = album_data["cover_image"]
        self.title = album_data["title"]

    def __str__(self):
        return f"{self.__class__}: {self.__dict__}"

@app.route("/searchDiscogs")
def fetch_discogs_albums():
    albums = []
    search_term = f.request.args.get('search_term')

    print(f"Searching Discogs for albums with term: {search_term}")

    url = f"https://api.discogs.com/database/search?q={search_term}&type=master&format=album&per_page=10&key={DISCOGS_API_KEY}&secret={DISCOGS_API_SECRET}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        json_data = response.json()

        print(f"Discogs API response: {json_data['pagination']['items']} albums found.")

        for masterJSON in json_data["results"]:
            temp_album = DiscogsAlbumData(masterJSON)
            albums.append(temp_album.__dict__)

        return f.jsonify({'albums': albums})

    except requests.RequestException as error:
        print(f"An error occurred while fetching albums: {error}")
        return None

@app.route("/computeRec", methods=['POST'])
def generate_recommendation_results():
    data = f.request.get_json()
    user_collection = data['data']
    email = data['email']

    print(f"Collection received from front-end: {user_collection}")

    print("Creating user matrix...")
    user_matrix = rec_algo.create_user_matrix(user_collection=user_collection)
    user_matrix = rec_algo.normalise_array(user_matrix)
    print(f"User matrix created: {user_matrix}")

    print("Computing recommendations...")

    start_time = time()
    user_recommendation_results = rec_algo.compute_recomedation(user_matrix=user_matrix, top_n=4)
    end_time = time()

    elapsed_time = end_time - start_time
    print(f"Recommendation computation completed in {elapsed_time:.4f} seconds")

    send_recommendation_email(produce_top_recommendation_metadata(user_recommendation_results), email)

    return "Processed!"

class ReleaseMetadata:
    def __init__(self, album_data):
        self.artist = album_data["artist"]
        self.title = album_data["title"]
        self.apple_music_url = f"https://music.apple.com/gb/search?term={self.title} - {self.artist}"
        self.spotify_url = f"https://open.spotify.com/search/{self.title} - {self.artist}"

def produce_top_recommendation_metadata(rec_results):
    rec_meta_dict = {"distance": [], "dot_product": []}

    print(f"Processing recommendations based on 'distance' and 'dot_product'.")

    # Process distance recommendations
    for rec in rec_results["distance"]:
        print(f"Fetching releases for artist ID: {rec['artist']['id']}")
        top_releases = fetch_artist_releases(rec["artist"]["id"])[0]
        rec_meta_dict["distance"].append(ReleaseMetadata(top_releases))

    # Process dot_product recommendations
    for rec in rec_results["dot_product"]:
        print(f"Fetching releases for artist ID: {rec['artist']['id']}")
        top_releases = fetch_artist_releases(rec["artist"]["id"])[0]
        rec_meta_dict["dot_product"].append(ReleaseMetadata(top_releases))

    print(f"Recommendation metadata generated: {rec_meta_dict}")
    return rec_meta_dict

def send_recommendation_email(rec_metadata, email):
    print(f"Sending recommendation email to {email}...")

    rec_email_text = f"""
    <p style="font-weight: bold;">Measure A:</p>
    <ul>
        <li>{rec_metadata['distance'][0].title} by {rec_metadata['distance'][0].artist}</li>
        <li>{rec_metadata['distance'][1].title} by {rec_metadata['distance'][1].artist}</li>
        <li>{rec_metadata['distance'][2].title} by {rec_metadata['distance'][2].artist}</li>
        <li>{rec_metadata['distance'][3].title} by {rec_metadata['distance'][3].artist}</li>
    </ul>

    <p style="font-weight: bold;">Measure B:</p>
    <ul>
        <li>{rec_metadata['dot_product'][0].title} by {rec_metadata['dot_product'][0].artist}</li>
        <li>{rec_metadata['dot_product'][1].title} by {rec_metadata['dot_product'][1].artist}</li>
        <li>{rec_metadata['dot_product'][2].title} by {rec_metadata['dot_product'][2].artist}</li>
        <li>{rec_metadata['dot_product'][3].title} by {rec_metadata['dot_product'][3].artist}</li>
    </ul>
    """

    try:
        emailSender.send_email(email, rec_email_text)
    except Exception as e:
        print(f"Error sending email: {e}")


def fetch_artist_releases(artist_id):
    url = f"https://api.discogs.com/artists/{artist_id}/releases?key={DISCOGS_API_KEY}&secret={DISCOGS_API_SECRET}"

    try:
        print(f"Fetching releases for artist ID {artist_id}...")
        response = requests.get(url)
        response.raise_for_status()
        json_data = response.json()

        data = []
        for album in json_data["releases"]:
            data.append({
                "title": album["title"],
                "artist": album["artist"],
                "popularity": album["stats"]["community"]["in_collection"]
            })

        top_albums = sorted(data, key=lambda x: x['popularity'], reverse=True)
        return top_albums

    except requests.RequestException as error:
        print(f"An error occurred while fetching releases for artist {artist_id}: {error}")
        return []

@app.route("/")
def index():
    return f.render_template('index.html')

# if __name__ == '__main__':
#       app.run(host='0.0.0.0', port=5050)
