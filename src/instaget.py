import argparse
import requests
from pathlib import Path
import json
import re
from datetime import datetime
from User import User

parser = argparse.ArgumentParser(
    description='Save an Instagram story.',
    epilog="",
    usage='%(prog)s <username>')
parser.add_argument("username", help="The name of an Instagram story")
# parser.add_argument('-a','--all', help="print all replacements", action="store_true")
# parser.add_argument('-c','--continue', help="new GraphQL query after given end_cursor", action='store_true')
parser.add_argument('-v','--version', action='version', version='%(prog)s 1.0-pre-release')
# limit??
# starter page???
# parser.add_argument('--dry-run')
# parser.add_argument('message', help="the message to be encoded")
args = parser.parse_args()

username = args.username
profileDir = Path('profiles') / username

dev = True

# prevSharedData = 
lastRunSharedData = sharedData = lastRun = profile = {}

jsonDir = profileDir / 'json'
mediaDir = profileDir / 'media'
sharedDataJson = jsonDir / '_sharedData.json'
nextPageJson = jsonDir / 'nextPage.json'

# create the profile directory if it doesn't exist
if profileDir.exists():
    print('loading sharedData from last run:'
        , datetime.fromtimestamp(sharedDataJson.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'))
    lastRunSharedData = json.loads(sharedDataJson.read_text())
else:
    print('creating new profile directory')
    jsonDir.mkdir(mode=0o777, parents=True)
    mediaDir.mkdir(mode=0o777, parents=True)
    nextPageJson.touch()
    sharedDataJson.touch()

if lastRunSharedData:
    lastRun = User(lastRunSharedData["entry_data"]["ProfilePage"][0]["graphql"]["user"])
    sharedData = lastRunSharedData
else:
    lastRunSharedData = {'user': {'edge_owner_to_timeline_media': {'count': 0}}}
    lastRun = User(lastRunSharedData['user'])
    # if you can't load the profile, request it from the server
    url = 'https://www.instagram.com/' + username
    r = requests.get(url)
    print(r.request.method, r.request.url, r.status_code)
    sharedData = json.loads(re.findall('window._sharedData = {.*};', r.text)[0][21:-1])

# update lastRun sharedData
sharedDataJson.write_text(json.dumps(sharedData, indent=2))

# by this point you should have enough info to load the profile object and compare to lastRun object
profile = User(sharedData["entry_data"]["ProfilePage"][0]["graphql"]["user"])

print(lastRun.posts)

if profile.posts['count'] > lastRun.posts['count']:
    print('queueing up', profile.posts['count'] - lastRun.posts['count'], 'new posts')

    # save related_profiles
    # only do this once for now until you need to use it
    relatedJson = profileDir / 'json' / 'related.json'
    if not relatedJson.exists():
        relatedJson.write_text(json.dumps(profile.related_profiles, indent=2))

    # get posts until you reach a post you already have
    profile.savePage()

    if profile.hasNextPage():
        nextPageJson = profileDir / 'json' / 'nextPage.json'
        nextPageJson.write_text(json.dumps(profile.getNextPage(), indent=2))
        profile.savePage()

    # eventually do this...
    # while profile.hasNextPage():
        # profile.savePage()

    print('saved'
        , profile.posts['saved']
        , 'posts with'
        , profile.posts['images']
        , 'images and'
        , profile.posts['videos']
        , 'videos.'
    )

else:
    print("Everything up to date!")


