# KMHD-Radio-to-Spotify
A web-scraper that collects song descriptions from KMHD's webpage (https://www.opb.org/kmhd/playlist/) and parses the artist and song titles 
into Spotify's API and creates a playlist based on resluts. 

# Known limitations and potential TO DO's
Limitation: Must be run at the end of the night 11:50 ish, to get a full result 
TODO: Fix this.

Limitation: If a match is not found for an artist the script does not look further.
TODO: Maybe fix this.

Limitation: If a title track is entered wrong as a playlist description or differntly than how spotify has the song listed. Say & vs and.
I use  python fuzzywuzzy process to pick the most likey track. 

Limitation: IF a artist match if found, the title is searched for. If the title is not found, the title is searched for a random "best match" using python fuzzywuzzy process function.
Justifacation: I thought thhis might as some random variaty for any known artist where a title track could not be found. 
TODO: Add flag to turn off / on option. 

# Known bug
Must be run twice to create playlist.
TODO: fix this. 
