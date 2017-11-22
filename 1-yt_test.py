#!/usr/bin/python

from apiclient.discovery import build
from apiclient.errors import HttpError
#from oauth2client.tools import argparser
from bs4 import BeautifulSoup
import requests
import re
import os #should use import subprocess but not ever gonna face outward (webward?)


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyAfjfdpun0DUAC3Z-0gS3wML09tEFcbTAg" 
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


# FXN TO TAKE IN 92Q PLAYLIST URL AND RETURN LIST OF SEARCH TERMS FOR SONGS
def song_search(url):
  html = requests.get(url)
  soup = BeautifulSoup(html.text, 'html5lib')
  artists = soup.find_all("label", class_ = "music-artist")
  songs = soup.find_all("a", class_ = "playlist-music")
  if(len(artists) != len(songs)): exit(1)
  play_list = []
  for x in range(len(artists)):
    temp = []
    #print re.sub('<[^<]+?>', '', str(artists[x])).strip()
    temp.append(re.sub('<[^<]+?>', '', str(artists[x])).strip())
    #print re.sub('<[^<]+?>', '', str(songs[x])).strip(), '\n\n'
    temp.append(re.sub('<[^<]+?>', '', str(songs[x])).strip())
    play_list.append(temp)
  return play_list


# CLASS FOR Namespace OBJECT
class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

  
# FXN TO TURN SEARCH TERM INTO URL
def url_return(search_string):
  print 'Finding song url...'
  track_info = []
  args = Namespace(auth_host_name='localhost', auth_host_port=[8080, 8090], logging_level='ERROR', max_results=1, noauth_local_webserver=False, q=search_string)
  try:
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)
    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(
      q=args.q,
      part="id,snippet",
      maxResults=args.max_results
    ).execute()
    # Add each result to the appropriate list, and then display the lists of
    # matching video names and urls.
    for search_result in search_response.get("items", []):
      if search_result["id"]["kind"] == "youtube#video":
        temp =[]
        temp.append("%s (%s)" % (search_result["snippet"]["title"], search_result["id"]["videoId"]))
        temp.append("%s%s" % ("https://www.youtube.com/watch?v=", search_result["id"]["videoId"]))
        track_info.append(temp)
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
  return track_info


def download_songs(play_list):
  cnt = 1
  for each in play_list:
    if each:
      #print 'Downloading ', each[0]
      cnt += 1
      string = 'youtube-dl --output ~/Music/folder/\'%(title)s.%(ext)s\' --extract-audio --audio-format mp3 ' + each[0][1]
      os.system(string)

# MAIN---
if __name__ == "__main__":
  hot_play_list = song_search("http://www.quuit.com/quu/playlist/152")
  hot_info = []

  for each in hot_play_list:
    temp = each[0] + ' ' + each[1]
    hot_info.append(url_return(temp))

  for each in hot_info: #debug
    if each:
      print each[0][0] , ' ', each[0][1]

  download_songs(hot_info)
  

# features to add:
# 1. import time module so program can run permanently in background
# and download the playlist every x minutes
# 2. tying into #1, put each new batch of files into new folder named 
# after the current date/time 
# # 3. make a single track consisting of the first 30 secs of each
# song
