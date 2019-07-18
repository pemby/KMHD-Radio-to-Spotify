from datetime import datetime
from fuzzywuzzy import process
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import CLIENT_ID, CLIENT_SECRET, USER
from time import sleep
import spotipy
import spotipy.util as util


# Simple helper method to encode blank spaces.
def encodeBlankSpaces(input: str):
    return input.replace(" ", "%20")


# Yield successive n-sized
# chunks from l.
def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


# New Playlist ID, Name and creation tracking bool
newPlayListID = ""
newPlayListName = "KHMD " + datetime.today().strftime('%Y-%m-%d')
current_playlist_created = False

# Containers to hold Spotify trackID
spotify_track_ids_buffer = []
list_of_lists_track_ids = [[]]

# Spotify Authentication Token
token = util.prompt_for_user_token(
        username=USER,
        scope="playlist-modify-public",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri="http://localhost:8888/callback/")

# Spotipy object, authenticated
spotify = spotipy.Spotify(auth=token)

# List of all playlist as dictionaries.
playlistList = spotify.current_user_playlists()['items']

# Checking if today's playlist has been created.
# If not, then create todays playlist.
for playlist in playlistList:
    if playlist['name'] == newPlayListName:
        current_playlist_created = True

if not current_playlist_created:
    spotify.user_playlist_create(USER, newPlayListName)
    spotify.user_playlist(USER)

# If we are here we assume today's playlist has been created.
# searching for playlist by name, to the the spotiy playlist ID.
for playlist in playlistList:
    if playlist['name'] == newPlayListName:
        newPlayListID = playlist['id']

# Create variables for scraping KHMD playlists
dataList = []
element = ""
driver = webdriver.Chrome()
driver.get("https://composer.nprstations.org/widgets/iframe/daily.html?station=519298c7e1c876ffebb2149b")

# Call selenium, wait until javascript runs, get rendered source and save it into BS4.
try:
    element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "whatson-content"))
    )
    page_source = element.parent.page_source

finally:
    driver.quit()
soup = BeautifulSoup(page_source, 'html.parser')

# Find all daily playlists (separated by different shows) and store it as a list.
daliyPlayList = soup.find_all('div', 'dailyPlaylist')


# Parsing web data
# Checking for blank strings to avoid runtime exceptions
for playlist in daliyPlayList:
    for songData in playlist:
        try:
            time = songData.contents[0].contents[0]
        except:
            time = ""
            pass
        try:
            title = songData.contents[1].contents[0].contents[0].contents[0].contents[1].contents[0]
        except:
            title = ""
            pass
        try:
            artist = songData.contents[1].contents[0].contents[0].contents[1].contents[1].contents[0]
        except:
            artist = ""
            pass
        try:
            track = songData.contents[1].contents[0].contents[0].contents[2].contents[1].contents[0]
        except:
            track = ""
            pass

        trackNames = []
        if artist:
            search_q = "{}".format(artist)
            spot_search = spotify.search(search_q)
            track_list = spot_search['tracks']['items']
            for track in track_list:
                trackNames.append(track['name'])

            x = process.extract(title, trackNames, limit=1)
            if x:
                best_match = x[0][0]
                for i in track_list:
                    if i['name'] == best_match:
                        spotify_track_ids_buffer.append(i['uri'])

    # Spotify API only allows 100 tracks to be added to a playlist at a time.
    # So here we break apart track id lists that are larger than 100 into sub lists.
    if len(spotify_track_ids_buffer) > 100:
        list_of_lists_track_ids += list(divide_chunks(spotify_track_ids_buffer, 100))

    else:
        list_of_lists_track_ids += list_of_lists_track_ids

# Take all sub lists, delete empty lists.
# note: not sure why some lists are empty here, just going to make it work for now.
final_track_id_lists = [x for x in list_of_lists_track_ids if x != []]

# For each track id list, upload to Spotify playlist.
# Sleeping for 3 seconds between API requests to avoid hammering spotify servers
# Note: I am not sure what the rate limits are and I am assuming 3 seconds is long enough.
for i in final_track_id_lists:
    sleep(3.0)
    print(len(i))
    spotify.user_playlist_add_tracks(USER, newPlayListID, i)
