import json
import requests
import math
import time

start = time.time()

url = "https://yts.mx/api/v2/list_movies.json?sort_by=year&limit=50&with_rt_ratings=true"
details_url = "https://yts.mx/api/v2/movie_details.json?with_cast=true"

genres = ["Comedy", "Sci-Fi", "Horror", "Romance", "Action", "Thriller", "Drama", "Mystery", "Crime", "Animation", "Adventure", "Fantasy", "Comedy-Romance", "Action-Comedy", "Superhero"]

db = {}
db["db"] = {};
genres_db = {}
added_ids = []

start_req = requests.get(url)
start_json = start_req.json()

movie_count = start_json["data"]["movie_count"]
page_count = math.ceil(movie_count/50)
print("Found " + str(page_count) + " pages")

for a in range(0, len(genres)):
    genres_db[genres[a]] = {}

for i in range(301, page_count+1):
    req_url = url + "&page=" + str(i)
    print("Requesting: " + str(req_url))
    req = requests.get(req_url, verify=False)
    results_json = req.json()      
    for j in range(0, len(results_json["data"]["movies"])):
        movie_id = results_json["data"]["movies"][j]["imdb_code"]
        yts_id = results_json["data"]["movies"][j]["id"]
        if movie_id not in added_ids:            
            if "torrents" in results_json["data"]["movies"][j]:
                # generate magnet link
                current_high = 0
                largest_index = 0
                for h in range(0, len(results_json["data"]["movies"][j]["torrents"])):
                    if results_json["data"]["movies"][j]["torrents"][h]["seeds"] > current_high and results_json["data"]["movies"][j]["torrents"][h]["quality"] != "2160p" :        
                        current_high = results_json["data"]["movies"][j]["torrents"][h]["seeds"]
                        largest_index = h
                movie_hash = results_json["data"]["movies"][j]["torrents"][largest_index]["hash"]    
                magnet_link = "magnet:?xt=urn:btih:" + str(movie_hash) + "&dn=" + str(movie_id) + "&tr=udp://open.demonii.com:1337/announce&tr=udp://tracker.openbittorrent.com:80&tr=udp://tracker.coppersurfer.tk:6969&tr=udp://glotorrents.pw:6969/announce&tr=udp://tracker.opentrackr.org:1337/announce&tr=udp://torrent.gresille.org:80/announce&tr=udp://p4p.arenabg.com:1337&tr=udp://tracker.leechers-paradise.org:6969"
                
                db["db"][movie_id] = results_json["data"]["movies"][j]
                db["db"][movie_id]["magnet"] = magnet_link    
                
                # retrieve cast information
                req_details_url = details_url + "&movie_id=" + str(yts_id)                 
                req_details = requests.get(req_details_url, verify=False)
                details_json = req_details.json() 
                if "cast" in details_json["data"]["movie"]:                    
                    db["db"][movie_id]["cast"] = details_json["data"]["movie"]["cast"]
                else:
                    db["db"][movie_id]["cast"] = []
                                
                added_ids.append(movie_id)         

db["version"] = "1.0.2";
db_json = json.dumps(db)
print("Loaded " + str(len(db["db"])) + " entries in db.json")
print("Added ids: " + str(len(added_ids)) + " in db.json")
with open('db_301_.json', 'w') as f:
    f.write(db_json)

stop = time.time()
print('[Time]: ', str(stop - start))