# Kanyus

<img src="kanyus.jpeg" width="250" height="250" />
<p>
  <a href="https://www.python.org/" target="_blank">
    <img alt="MadeWith" src="https://img.shields.io/badge/Made%20with-Python-1f425f.svg">
  </a>
  <a href="" target="_blank">
    <img alt="MadeWith" src="https://img.shields.io/badge/version-v0.57-blue">
  </a>
  <a href="" target="_blank">
    <img alt="MadeWith" src="https://img.shields.io/badge/PRs-Yes%20Please-brightgreen.svg?style=flat-square">
  </a>
</p>

## Why
Because sometimes in order to show the world that you are a musical genius, you need to automate! Kanyus is designed to help you scale up your efforts to reach <a href="https://genius.com/albums/Genius/Genius-users-hall-of-fame">Genius.com Hall of Fame</a> by helping you find unannotated songs from your favorite artists. 

## How
Using the <a href="https://docs.genius.com/">Genius.com API</a>, a little bit of Python, and some meta-API magic.

## Installation
* From the project's directory run the command: `pip install -r requirements.txt` . 
* You're also going to need your own <a href="https://genius.com/api-clients">Genius.com API "Client Access Token"</a>.
* You're going to need to add your API "Client Access Token" in the settings.ini file.

## Usage Example
`python main.py -h`

```
  -h, --help            show this help message and exit
  -a ARTIST, --artist ARTIST Name of the aritst who's songs we want to get.
  -d, --debug           This flag will set logging to Debug mode.
  -p ARTIST_TO_PRUNE, --prune ARTIST_TO_PRUNE Name of the artist who's songs we want to prune
  -l LIST_SONGS_BY, --listsongsby LIST_SONGS_BY Name of Artist we want to get songs for.
  -m MAPPING_FILE, --mapping MAPPING_FILE Name of custom mapping file you want to use.
  -v, --verbose         Flag will set logging to Debug mode like -d.
```
----------------------------------------------------------------
`python main.py --artist "The Beatles" --debug`

```
   Command finds "The Beatles" 's Genius.com Artist ID and stores information
   about any unannotated songs of theirs locally in artist_song_id_mapping.json
```
-----------------------------------------------------------------
`python main.py --listsongsby "The Beatles" --debug`

```
    Command lists information about unannotated songs by "The Beatles" from
    artist_song_id_mapping.json
```
-----------------------------------------------------------------
## Known Issues
* Genius.com has a builtin rate limiter that blocks you from posting if you post too frequently. Only a human Moderator / Editor can remove the rate limit blocker which can take time / effort contacting the Moderators to remove.
