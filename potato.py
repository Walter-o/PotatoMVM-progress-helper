import requests
from bs4 import BeautifulSoup
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

STEAMID64 = 0
baseUrl = "https://potato.tf"
progressUrl = "https://potato.tf/breakdown/"
serverListUrl = "https://potato.tf/servers"

def fetchProgress(steamId64=STEAMID64):
    r = requests.get(progressUrl + str(steamId64))
    soup = BeautifulSoup(r.text, "html.parser")
    scores = soup.find_all("article", class_="media box has-background-grey-darker")
    results = {}
    for score in scores:
        mapName = score.find("img", class_="is-slightly-rounded")["alt"]
        missionName = score.find("strong", class_="has-text-grey-lighter").text
        results[missionName] = mapName
    return results

def fetch(url):
    r = requests.get(url)
    return r.content

def filteredServerList():
    serverList = fetch(serverListUrl)
    progress = fetchProgress()
    soup = BeautifulSoup(serverList, "html.parser")
    servers = soup.find_all("div", class_="columns is-vcentered has-background-grey-dark is-paddingless")
    for server in servers:
        """ mapName = server.find("h1", class_="has-text-light subtitle is-size-7-desktop is-size-7-tablet is-size-7-mobile").text """
        missionName = server.find("h1", class_="has-text-light subtitle is-size-7-tablet is-size-7-mobile is-marginless").text
        if missionName in progress.keys():
            print("decomposing: %s"%missionName)
            server.decompose()
    return soup

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        if self.path == "/":
            self.wfile.write(filteredServerList())
        else:
            self.wfile.write(fetch(baseUrl + self.path))

def startServer():
    httpd = HTTPServer(("", 1336), Handler)
    print("Potato proxy started")
    httpd.serve_forever()

startServer()