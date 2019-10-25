import requests
import json
from base64 import b64decode, b64encode
from bs4 import BeautifulSoup
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import SocketServer

STEAMID64 = 76561198092188114
baseUrl = "https://potato.tf"
progressUrl = "https://potato.tf/breakdown/"
serverListUrl = "https://potato.tf/servers"

class Mission:
    def __init__(self, missionName, mapName=None):
        self.missionName = missionName
        self.mapName = mapName

def cache(url):
    with open("cache/cache.json", "r") as cacheR:
        currCache = json.load(cacheR)
    if url in currCache.keys():
        return b64decode(currCache[url])
    else:
        currCache[url] = b64encode(fetch(url))
        with open("cache/cache.json", "w") as cacheW:
            json.dump(currCache, cacheW)


def fetchProgress(steamId64=STEAMID64):
    r = requests.get(progressUrl + str(steamId64))
    soup = BeautifulSoup(r.text, "html.parser")
    # Select element containing completed missions
    scores = soup.find_all("article", class_="media box has-background-grey-darker")
    results = []
    for score in scores:
        missionName = score.find("strong", class_="has-text-grey-lighter").text.strip(" ")
        mapName = score.find("img", class_="is-slightly-rounded")["alt"]
        missionObj = Mission(missionName=missionName, mapName=mapName)
        results.append(missionObj)
    print("%s missions completed out of 81"%len(results))
    return results

# Fetch a given url's contents, assumes it's a valid link
def fetch(url):
    acceptable = False
    while not acceptable:
        try:
            r = requests.get(url)
            acceptable = True if r.status_code == 200 else False
        except (requests.ConnectTimeout, requests.ConnectionError):
            print("fetch() had a connection error, retrying...")
    return r.content

def filteredServerList():
    serverList = fetch(serverListUrl)
    completedMissions = [x.missionName for x in fetchProgress()]
    soup = BeautifulSoup(serverList, "html.parser")
    servers = soup.find_all("div", class_="columns is-vcentered has-background-grey-dark")
    if len(servers) == 0:
        print("ERROR: No servers found in server list")
    print("%s servers found"%len(servers))

    removedMissions = []
    for server in servers:
        missionName = server.find("h1", class_="has-text-light subtitle is-size-7-tablet is-size-7-mobile is-marginless").text
        # mapName = server.find("h1", class_="has-text-light subtitle is-size-7-desktop is-size-7-tablet is-size-7-mobile").text
        if missionName in completedMissions:
            removedMissions.append(missionName)
            server.decompose()

    print("Decomposed %s missions from server list:" % len(removedMissions))
    print(removedMissions)
    return soup

class Handler(SocketServer.ThreadingMixIn, BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        if self.path == "/":
            self.wfile.write(filteredServerList())
        else:
            self.wfile.write(cache(baseUrl + self.path))

def startServer():
    httpd = HTTPServer(("", 1336), Handler)
    print("Potato proxy started at localhost:1336")
    httpd.serve_forever()

startServer()
