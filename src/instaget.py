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

prevSharedData = sharedData = lastRun = profile = {}

# using number of posts to determine if there are any new posts
prevCountOfPosts = 0

if profileDir.exists():
    print('profile exists')
    prevSharedDataJson = profileDir / 'json' / '_sharedData.json'

    if prevSharedDataJson.exists():
        print('loading sharedData from last run:'
            , datetime.fromtimestamp(prevSharedDataJson.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'))
        prevSharedData = json.loads(prevSharedDataJson.read_text())
        
        lastRun = User(prevSharedData["entry_data"]["ProfilePage"][0]["graphql"]["user"])
    else:
        # create the file before writing to it
        prevSharedData.touch()
        lastRun = {"posts": {"count": 0}}

else:
    print('creating new profile directory')
    profileDir.mkdir()
    jsonDir = profileDir / 'json'
    mediaDir = profileDir / 'media'
    jsonDir.mkdir()
    mediaDir.mkdir()
    nextPageJson = jsonDir / 'nextPage.json'
    nextPageJson.touch()

# do something if requests does not return
# dry run isn't the right word for this, but need a way to not make requests while debugging
dev = True
if dev == False:
    url = 'https://www.instagram.com/' + username
    r = requests.get(url)
    sharedData = json.loads(re.findall('window._sharedData = {.*};', r.text)[0][21:-1])
else:
    sharedData = prevSharedData

# save new lastRun data
sharedDataJson = profileDir / 'json' / '_sharedData.json'
sharedDataJson.write_text(json.dumps(sharedData, indent=2))

profile = User(sharedData["entry_data"]["ProfilePage"][0]["graphql"]["user"])

if dev or profile.posts['count'] > lastRun.posts['count']:
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

else:
    print("Everything up to date!")


