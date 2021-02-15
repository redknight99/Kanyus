import argparse
import configparser
import json
import logging
import requests
import sys

# Genius API Token / API endpoint setup
config = configparser.ConfigParser()
config.read('settings.ini')
api_token = config["API_KEYS"]["GeniusAPI"]
base_url = "https://api.genius.com/"


def add_to_artist_mapping(artist_id=None, artist_name=None, mapping_data=None,
                          filename=None):
    """
        Utils function: It adds a new artist name / ID to the mapping data and
        saves the data as filename. In the future we'll enable users
        to save the file as whatever filename they want.
    """
    if filename is None:
        logger.debug("No filename was passed to add_to_artist_mapping.")
        logger.debug("We will use the default filename name.")
        filename = "artist_song_id_mapping.json"

    artist_to_save = {"names": [artist_name], "ID": artist_id}
    mapping_data["artists"].append(artist_to_save)
    logger.debug("We have added the artist to the mapping data.")

    with open(filename, 'w') as f:
        json.dump(mapping_data, f)

    logger.debug("Okay it looks like everything went good. Returning True")
    return True


def add_to_songs_mapping(artist_id=None, song_mapping=None, mapping_data=None,
                         filename=None):
    """
        Utils function: It adds newly research songs to the mapping data and
        saves the data as a filename. In the future we'll enable
        users to save the file a whatever filename they want.
    """

    if filename is None:
        logger.debug("No filename was passed to add_to_artist_mapping.")
        logger.debug("Using the default name.")
        filename = "artist_song_id_mapping.json"

    for song in song_mapping:
        if str(artist_id) in mapping_data["songs_to_annotate"].keys():
            need_to_add_song = True
            for old_song in mapping_data["songs_to_annotate"][str(artist_id)]:
                if old_song["song_id"] == song["song_id"]:
                    need_to_add_song = False
            if need_to_add_song is True:
                logger.debug("Addding a new song to mapping!")
                mapping_data["songs_to_annotate"][str(artist_id)].append(song)
        else:
            # The artist ID doesn't exist. Add it and then add the song
            mapping_data["songs_to_annotate"][str(artist_id)] = []
            mapping_data["songs_to_annotate"][str(artist_id)].append(song)

    # Save the JSON file
    with open(filename, 'w') as f:
        json.dump(mapping_data, f)

    logger.debug("Okay it looks like everything went good. Returning True")
    return True


def get_annotation_information(annotation_id=None):
    """
        Wrapper for /annotations/:id Genius API endpoint

        Returns query information or 1 if there was an error.
    """
    if annotation_id is None:
        logger.debug("get_annotation_information was not passed the correct ",
                     "parameters. We're going to use known song annotation ID")
        annotation_id = "3490604"
    search_url = base_url + "annotations/" + str(annotation_id)
    headerz = {"Authorization": "Bearer " + str(api_token)}
    r = requests.get(search_url, headers=headerz)
    if r.status_code == 200:
        logger.debug("The search call was successful!\n")
        answer = r.text
        return answer
    else:
        logger.debug("The call was not successful!")
        logger.debug("The r.status_code is: " + str(r.status_code) + "\n")
        logger.debug("The r.text is: " + str(r.text))
        return 1


def get_song_information(song_id=None):
    """
        Wrapper for /songs/:id Genius API endpoint.

        Returns query information or 1 if there was an error.
    """
    if song_id is None:
        logger.debug("get_song_information was not passed correct parameters.")
        logger.deubg("We are using song ID for a Gorillaz's song as default.")
        song_id = "860"

    search_url = base_url + "songs/" + str(song_id)
    headerz = {"Authorization": "Bearer " + str(api_token)}
    r = requests.get(search_url, headers=headerz)
    if r.status_code == 200:
        logger.debug("The call to artists/:id was successful!\n")
        answer = r.json()
        return answer
    else:
        logger.debug("The call was not successful!")
        logger.debug("The r.status_code is: " + str(r.status_code) + "\n")
        logger.debug("The r.text is: " + str(r.text))
        return 1


def get_the_next_page_of_artist_songs(next_page, artist_id):
    """
        Worker function for get_artist_songs_genius( )

        Function recursively calls the artists/:id/songs Genius API endpoint.

        It returns song results for each call and raises an Exception
        if there's an issue.
    """
    search_url = base_url + "artists/" + str(artist_id) + "/songs?page=" + \
                            str(next_page)
    headerz = {"Authorization": "Bearer " + str(api_token)}
    r = requests.get(search_url, headers=headerz)
    if r.status_code == 200:
        yes_msg = "Recursive call to get more of artist's songs was success!\n"
        logger.debug(yes_msg)
        results = r.json()
        song_ids = []
        if "next_page" in results["response"]:
            if results["response"]["next_page"] is not None:
                # Recursive hell to collect all the songs.
                next_page = results["response"]["next_page"]
                songs_to_add = get_the_next_page_of_artist_songs(next_page,
                                                                 artist_id)
                song_ids = results["response"]["songs"]
                song_ids = song_ids + songs_to_add
                return song_ids
            else:
                song_ids = results["response"]["songs"]
                return song_ids
    else:
        logger.debug("The call was not successful!")
        logger.debug("The r.status_code is: " + str(r.status_code) + "\n")
        logger.debug("The r.text is: " + str(r.text))
        raise Exception("Exception in get_the_next_page_of_artist_songs()")


def get_artist_songs_genius(artist_id=None):
    """
        Wrapper for the /artists/:id/songs Genius API endpoint

        Returns songs for a given artist ID or 1 if an error occurred.
    """
    if artist_id is None:
        logger.debug("get_artist_song_genius was not passed correct params.")
        logger.debug("We are going to use the artist ID of the Gorillaz. 860.")
        artist_id = "860"
    search_url = base_url + "artists/" + str(artist_id) + "/songs"
    headerz = {"Authorization": "Bearer " + str(api_token)}
    r = requests.get(search_url, headers=headerz)
    if r.status_code == 200:
        logger.debug("The call to artists/id/songs was successful!\n")
        results = r.json()
        song_ids = []
        if "next_page" in results["response"]:
            logger.debug("Recursively trying to get all of artist's songs.\n")
            # Start the recursion to get all the songs
            next_page = results["response"]["next_page"]
            songs_to_add = get_the_next_page_of_artist_songs(next_page,
                                                             artist_id)
            # set song_ids to our initial results + the recursion results.
            song_ids = results["response"]["songs"] + songs_to_add
            return song_ids
    else:
        logger.debug("The call was not successful!")
        logger.debug("The r.status_code is: " + str(r.status_code) + "\n")
        logger.debug("The r.text is: " + str(r.text))
        return 1


def get_artist_data_genius(artist_id=None):
    """
        Wrapper for the /artists/:id Genius API endpoint.

        Returns search query result or 1 if an error occurred.
    """
    logger.debug("get_artist_data_genius() started!\n")
    if artist_id is None:
        artist_id = "860"
    search_url = base_url + "artists/" + str(artist_id)
    headerz = {"Authorization": "Bearer " + str(api_token)}
    r = requests.get(search_url, headers=headerz)
    if r.status_code == 200:
        logger.debug("The search call was successful!\n")
        logger.debug("Returning now!\n")
        answer = r.text
        return answer
    else:
        logger.debug("The call was not successful!")
        logger.debug("The r.status_code is: " + str(r.status_code) + "\n")
        logger.debug("The r.text is: " + str(r.text))
        return 1


def get_list_of_low_popularity_artist_songs(list_of_songs_data=None,
                                            artist_id=None):
    """Takes a list of Genius API song objects and returns a list of
       low popularity song objects.
    """
    if list_of_songs_data is None or artist_id is None:
        logger.debug("get_list_of_low_popularity_artist_songs was not passed",
                     " the proper parameters.")
        logger.debug("Returning 1.")
        return 1
    answer = []
    low_pop_count = [0]
    for song_data in list_of_songs_data:
        if song_data["annotation_count"] in low_pop_count:
            # Check to prevent including songs where the aritst was a producer.
            if song_data["primary_artist"]["id"] == artist_id:
                relevant_info = {}
                relevant_info["song_name"] = song_data["title"]
                relevant_info["song_id"] = song_data["id"]
                relevant_info["song_note_amt"] = song_data["annotation_count"]
                relevant_info["song_url"] = song_data["url"]
                answer.append(relevant_info)
    return answer


def get_artist_id(artist_name=None):
    """
        This function tries to determine an artist's ID on
        Genius.com using the /search endpoint.

        It returns a numerical ID for that artist or a 1 if an error occurred.
    """
    if artist_name is None:
        logger.debug("get_artist_id was not passed the proper parameters.\n")
        logger.debug("Returning 1 now")
        return 1
    result = search_genius(artist_name)
    if result == 1:
        logger.debug("An error when trying to get the search response.\n")
        logger.debug("Returning now!")
        return 1
    else:
        response = result["response"]
        if len(response["hits"]) == 0:
            logger.debug("Search result contained no results.")
            logger.debug("Returning 1")
            return 1
        else:
            hits = response["hits"]
            for hit in hits:
                if "result" in hit.keys():
                    if "primary_artist" in hit["result"].keys():
                        if "id" in hit["result"]["primary_artist"]:
                            name = hit["result"]["primary_artist"]["name"]
                            logger.debug("The primary artist for this hit is: "
                                         + str(name) + "\n")
                            if name == artist_name:
                                return hit["result"]["primary_artist"]["id"]
                    else:
                        logger.debug("We could not find any primary",
                                     " information in the hit['result']",
                                     " We are continuing onward!")
                else:
                    logger.debug("Error: We couldn't find any result key",
                                 " in the song's information. This is odd.",
                                 " We are continuing onward!")
            logger.debug("We do not appear to have found the artist ID ")
            logger.debug(" with the user's search query!")
            logger.debug("Returning 1")
            return 1


def read_artist_song_mapping_file(filename=None):
    """
       Utils function that reads default Genius ID mappings file.
    """
    default_mapping_filename = "artist_song_id_mapping.json"
    if filename is None:
        logger.debug("No filename passed to read_artist_song_mapping_file().")
        logger.debug("We are going to use the default filename.")
        filename = default_mapping_filename
    try:
        with open(filename) as f:
            data = json.load(f)
            logger.debug("We've opened the file and loaded it into memory.")
    except Exception as e:
        logger.debug("Error occurred when attempting to open the json file.")
        logger.debug("The error that occurred is: " + str(e))
        data = 1
    return data


def save_artist_song_mapping_file(new_mapping_data=None, filename=None):
    """
        Utils function: Overwrites mapping data. It's used for prune-ing
        and maintenance.
    """

    if filename is None:
        logger.debug("No filename was passed to add_to_artist_mapping.")
        logger.debug("Using the default name.")
        filename = "artist_song_id_mapping.json"

    # Save the JSON file
    with open(filename, 'w') as f:
        json.dump(mapping_data, f)

    logger.debug("Okay it looks like everything went good. Returning 0!")
    return 0


def search_mapping_for_artist_id(given_artist_name=None, mapping_data=None):
    """
        Utils function that searches for artist ID is in our mapping data.

        It returns a 1 if the artist ID was not found.
    """
    if given_artist_name is None or mapping_data is None:
        logger.debug("search_mapping_for_artist_id",
                     " was not passed the proper parameters.")
        return 1

    answer_id = 1
    artist_mappings = mapping_data["artists"]

    for artist in artist_mappings:
        if given_artist_name in artist["names"]:
            logger.debug("We found a match. The artist ID appears to be: " +
                         str(artist["ID"]))
            answer_id = artist["ID"]

    return answer_id


def search_genius(query=None):
    """
        Wrapper for the /search Genius API endpoint.

        Returns search query result or 1 if an error occurred.
    """
    logger.debug("search_genius() started!\n")
    if query is None:
        logger.debug("search_genius() was not passed the proper parameters.")
        logger.debug("Using Gorillaz now to search for the Gorillaz band id.")
        query = "Gorillaz"
    search_url = base_url + "search?q=" + str(query)
    headerz = {"Authorization": "Bearer " + str(api_token)}
    r = requests.get(search_url, headers=headerz)
    if r.status_code == 200:
        logger.debug("The /search call was successful!\n")
        answer = r.json()
    else:
        logger.debug("The call to /search was not successful!")
        logger.debug("The r.status_code is: " + str(r.status_code) + "\n")
        logger.debug("The r.text is: " + str(r.text))
        answer = 1
    return answer


def pretty_print(given_artist_name, mapping_data):
    """
        Utils function: This function takes a given name and tries to
        get all the songs we have for annotation.
    """
    artist_id = search_mapping_for_artist_id(given_artist_name,
                                             mapping_data)
    if artist_id == 1:
        logger.debug("We were unable to find the artist ID in our mapping.")
        logger.debug("Returning Now!")
        return 1
    else:
        logger.debug("We were able to find the artist ID in our mapping.")
        try:
            songs_list = mapping_data["songs_to_annotate"][str(artist_id)]
        except Exception as e:
            logger.debug("We encountered an error: " + str(e))
            logger.debug("I think the artist doesn't have songs in mapping.")
            logger.debug("Returning now!")
            return 1
        for song in songs_list:
            logger.info("\nAvailable Song Details: " + str(song))
        logger.debug("The amount of songs we've printed is: " +
                     str(len(songs_list)) + "\n")
        logger.debug("Okay! Returning Now!")
        return 0


def prune_artist_songs(given_artist_name, mapping_data):
    artist_name_to_id = search_mapping_for_artist_id(given_artist_name,
                                                     mapping_data)
    if artist_name_to_id == 1:
        logger.debug("We were unable to find the artist ID in our mapping.")
        logger.debug("Returning Now!")
        return 1
    else:
        logger.debug("We were able to find the artist ID in our mapping.")
        songs_list = mapping_data["songs_to_annotate"][str(artist_name_to_id)]
        """
            The approach we want to take for this is, check each song in our
            mapping for the artist via the API. If the song now has

        """
        new_songs = []
        for song in songs_list:
            logger.debug("Getting information for song: " +
                         str(song["song_name"]))
            update_check = get_song_information(song["song_id"])
            if update_check["response"]["song"]["annotation_count"] == 0:
                new_songs.append(song)
        mapping_data["songs_to_annotate"][str(artist_name_to_id)] = new_songs
        save_result = save_artist_song_mapping_file(mapping_data)
        if save_result == 0:
            logger.debug("Okay! Looks like we successfuly pruned.")
            logger.debug("Returning Now!")
            return 0
        else:
            logger.debug("Yikes, it looks like we encountered an issue.")
            logger.debug("Returning Now!")
            return 1


def erase_artist_from_mapping(given_artist_name, mapping_data):
    """
        Utils Function: Used to remove a given_artist_name from
        our mapping.
    """
    artist_name_to_id = search_mapping_for_artist_id(given_artist_name,
                                                     mapping_data)
    if artist_name_to_id == 1:
        logger.debug("We were unable to find the artist ID in our mapping.")
        logger.debug("Returning Now!")
        return 1
    else:
        logger.debug("We were able to find the artist ID in our mapping.")
        mapping_data["songs_to_annotate"].pop(str(artist_name_to_id), None)
        save_result = save_artist_song_mapping_file(mapping_data)
        if save_result != 1:
            logger.debug("Okay! We saved the new file. Returning Now!")
            return 0
        else:
            logger.debug("Yikes, looks like we had an issue with saving.")
            return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger('main_thread_logger')

    # Begin Command Line Arguments Code Block
    parser = argparse.ArgumentParser(description="Commandline parser for  ")
    parser.add_argument("-a", "--artist", required=False, type=str,
                        dest="artist",
                        help="Name of the aritst who's songs we want to get.")
    parser.add_argument("-d", "--debug", required=False, dest="debug_switch",
                        action="store_true",
                        help="This flag will set logging to Debug mode.")
    parser.add_argument("-e", "--erasefrommapping", required=False, type=str,
                        dest="artist_entry_to_erase",
                        help="Artist name who's entry we want to remove")
    parser.add_argument("-l", "--listsongsby", required=False, type=str,
                        dest="list_songs_by",
                        help="Name of Artist we want to get songs for.")
    parser.add_argument("-m", "--mapping", required=False, type=str,
                        dest="mapping_file",
                        help="Name of custom mapping file you want to use.")
    parser.add_argument("-p", "--prune", required=False, type=str,
                        dest="artist_to_prune",
                        help="Name of the artist who's songs we want to prune")
    parser.add_argument("-v", "--verbose", required=False,
                        dest="verbose_switch",
                        action="store_true",
                        help="Flag will set logging to Debug mode like -d.")
    # End Command Line Arguments Code Block

    results = parser.parse_args()

    if results.debug_switch is True or results.verbose_switch is True:
        logger.setLevel(logging.DEBUG)
        logger.debug("User has requested debugging mode!")

    logger.debug("Attemping to read artist / song mapping.")
    mapping_data = read_artist_song_mapping_file()
    if mapping_data != 1:
        logger.debug("We successfully openned retrieved the mapping data!")
    else:
        logger.debug("Error occured in read_artist_song_mapping_file()")
        logger.debug("We're gonna crash the program here.")
        logger.debug("Exiting Now.")
        sys.exit()

    if results.artist_to_prune is not None:
        logger.debug("The user wants to prune a specific artist's songs of ")
        logger.debug("stale / annotated songs.")
        prune_result = prune_artist_songs(results.artist_to_prune,
                                          mapping_data)
        if prune_result != 1:
            logger.debug("\n Okay it looks like we were successful.")
            logger.debug("Ending now!")
        else:
            logger.debug("\n Okay it looks like we weren't successful.")
            logger.debug("Ending now!")
        sys.exit()

    if results.list_songs_by is not None:
        logger.debug("\nWe want to get all songs from mapping by artist: \n")
        logger.debug(str(results.list_songs_by))
        pretty_result = pretty_print(results.list_songs_by,
                                     mapping_data)
        if pretty_result != 1:
            logger.debug("\n It looks like were successful at getting songs.")
            logger.debug("Ending now!")
        else:
            logger.debug("\nWe were unsuccessful at getting songs.\n")
            logger.debug("Ending now!")
        sys.exit()

    if results.artist_entry_to_erase is not None:
        logger.debug("Okay it looks like the user wants to erase an artist.")
        erase_artist = results.artist_entry_to_erase
        logger.debug("They want to erase: " + str(erase_artist))
        erase_result = erase_artist_from_mapping(erase_artist, mapping_data)
        if erase_result != 1:
            logger.debug("Okay, it looks like we erased them. Ending now!")
            sys.exit()
        else:
            logger.debug("It looks like there was an issue when erasing.")
            logger.debug("Ending Now!")
            sys.exit()

    # Standard get all songs for artist from Genius.com run --artist .
    logger.debug("The user wants to look up artist: " + str(results.artist))
    if mapping_data != 1:
        logger.debug("Attempting to see if we already know the artist ID.")
        search_data_result = search_mapping_for_artist_id(results.artist,
                                                          mapping_data)
    else:
        logger.debug("Error occured trying to read mapping file.")
        logger.debug("Continuing Onward!")

    if search_data_result == 1:
        logger.debug("We were unable to find the artist's ID in our mapping.")
        logger.debug("Automagically looking up the artist ID now.\n")
        artist_id = get_artist_id(results.artist)
        logger.debug("The artist_id we found is: " + str(artist_id))
        if artist_id == 1:
            logger.debug("We were unable to find the artist ID for: " +
                         str(results.artist))
            logger.debug("Please check spelling of the artist's name.\n")
            logger.debug("EXITING PROGRAM NOW!")
            sys.exit()
        else:
            logger.debug("We found the artist ID by searching for it.")
            if mapping_data != 1:
                logger.debug("We are adding it to the mapping")
                add_result = add_to_artist_mapping(artist_id, results.artist,
                                                   mapping_data)
                if add_result != 1 and add_result is True:
                    logger.debug("We successfully added researched ID to our ")
                    logger.debug("mapping and have saved the file.")
    else:
        logger.debug("We were able to find the artist ID in our mapping.")
        logger.debug("We are setting artist id to " + str(search_data_result))
        artist_id = search_data_result

    artist_songs = get_artist_songs_genius(artist_id)
    songs_to_annotate = get_list_of_low_popularity_artist_songs(artist_songs,
                                                                artist_id)

    logger.debug("Attemping to read artist / song mapping.")
    mapping_data = read_artist_song_mapping_file()
    if mapping_data != 1:
        logger.debug("We successfully retrieved the mapping data!")
    else:
        logger.debug("Error occured in read_artist_song_mapping_file()")
        logger.debug("ERROR: WE CANNOT SAVE SONGS TO MAPPING!")
        logger.debug("EXITING NOW!")
        sys.exit()

    add_songs_to_mapping_result = add_to_songs_mapping(artist_id,
                                                       songs_to_annotate,
                                                       mapping_data)
    if add_songs_to_mapping_result is True:
        logger.debug("We successfully added the songs to our mapping.")
    else:
        logger.debug("We were unable to add the songs to our mapping.")
