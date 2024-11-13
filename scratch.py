import json
import requests
import emailSender

DISCOGS_API_KEY = "REDACTED_API_KEY"
DISCOGS_API_SECRET = "REDACTED_API_SECRET"

class RecommendationMetadata:
    def __init__(self, album_data):
        self.artist = album_data["artist"]
        self.title = album_data["title"]

        # Construct the URLs
        self.appleMusic = f"https://music.apple.com/gb/search?term={self.title} - {self.artist}"
        self.spotify = f"https://open.spotify.com/search/{self.title} - {self.artist}"

def produce_top_recommendation_metadata(rec_results):

    rec_meta_dict = {"distance": [], "dot_product": []}

    # Process distance recommendations
    for rec in rec_results["distance"]:
        top_releases = get_releases(rec["artist"]["id"])[0]
        rec_meta_dict["distance"].append(RecommendationMetadata(top_releases))

    # Process dot_product recommendations
    for rec in rec_results["dot_product"]:
        top_releases = get_releases(rec["artist"]["id"])[0]
        rec_meta_dict["dot_product"].append(RecommendationMetadata(top_releases))

    print(rec_meta_dict)

    return rec_meta_dict

def send_email_workflow(rec_metadata, email):

    # Format the email content using the metadata
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
    emailSender.send_email("bradley5922@icloud.com", rec_email_text)

def produce_email_workflow(rec_results, email):
    """
    Coordinates the process of generating recommendations and sending an email.
    :param rec_results: Recommendation results from distance and dot_product.
    :param email: The recipient email address.
    """
    top_releases_recs = produce_top_recommendation_metadata(rec_results)
    send_email_workflow(top_releases_recs, email)

def get_releases(artist_id):
    """
    Fetches the top album releases for a given artist using the Discogs API.
    :param artist_id: The Discogs artist ID.
    :return: List of top album data based on popularity.
    """
    url = f"https://api.discogs.com/artists/{artist_id}/releases?key={DISCOGS_API_KEY}&secret={DISCOGS_API_SECRET}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        json_data = response.json()

        data = []
        for album in json_data["releases"]:
            title = album["title"]
            artist = album["artist"]
            in_collection = album["stats"]["community"]["in_collection"]

            data.append({
                "title": title,
                "artist": artist,
                "popularity": in_collection
            })

        # Sort albums by popularity (descending)
        top_albums = sorted(data, key=lambda x: x['popularity'], reverse=True)
        return top_albums

    except requests.RequestException as error:
        print(f"An error occurred while fetching releases: {error}")
        return []

rec_results = {'distance': [{'artist': {'id': 3343071, 'name': 'AL-90'}, 'distance': 10.862780491200215, 'dot_product': 330}, {'artist': {'id': 2621684, 'name': 'Carmen Villain'}, 'distance': 11.40175425099138, 'dot_product': 255}, {'artist': {'id': 2854659, 'name': 'Brogan Bentley'}, 'distance': 11.40175425099138, 'dot_product': 255}, {'artist': {'id': 6982172, 'name': 'Clean Slate (4)'}, 'distance': 11.916375287812984, 'dot_product': 220}], 'dot_product': [{'artist': {'id': 1729177, 'name': 'Sienná'}, 'distance': 27.83882181415011, 'dot_product': 400}, {'artist': {'id': 46125, 'name': 'HAN'}, 'distance': 13.228756555322953, 'dot_product': 400}, {'artist': {'id': 699613, 'name': 'Kidkanevil'}, 'distance': 27.83882181415011, 'dot_product': 350}, {'artist': {'id': 1937272, 'name': 'Subminimal'}, 'distance': 19.364916731037084, 'dot_product': 350}]}
produce_email_workflow(rec_results=rec_results, email="bradley5922@icloud.com")
