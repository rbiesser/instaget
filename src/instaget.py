import argparse
import requests
from pathlib import Path
import json
import re
from datetime import datetime
from User import User

global args


parser = argparse.ArgumentParser(
    description='',
    epilog="Save an Instagram story.",
    usage='%(prog)s <username>')
parser.add_argument("username", help="An Instagram username")
parser.add_argument('-i','--images', help="Get only images", action="store_true", dest="getImages")
parser.add_argument('-V','--videos', help="Get only videos", action="store_true", dest="getVideos")
parser.add_argument('-b','--both', help="Get all images and videos, same as -iV", action="store_true", dest="getBoth")
parser.add_argument('--limit', help="Get the newest n posts", type=int, dest="limit")
parser.add_argument('--dry-run', help="Skip downloading is the default", action="store_true", dest="dryRun")
parser.add_argument('-v','--version', action='version', version='%(prog)s 1.0-pre-release')

args = parser.parse_args()

# getImages = args.getImages
# getVideos = args.getVideos
if args.getBoth:
    args.getImages = args.getVideos = True
if args.dryRun:
    args.getImages = args.getVideos = False
# limit = args.limit


# print(args)
# exit()

username = args.username
profileDir = Path('profiles') / username

dev = True

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
    jsonDir.mkdir(mode=0o644, parents=True)
    mediaDir.mkdir(mode=0o644, parents=True)
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

# print(lastRun.posts)

if profile.posts['count'] >= lastRun.posts['count']:
    # pluralize output
    # https://stackoverflow.com/a/60864346
    def sp(num):
        if num == 1:
            return 0
        else:
            return 1

    s = ["","s"]

    newPosts = profile.posts['count'] - lastRun.posts['count']
    print('queueing up', newPosts, f'new post{s[sp(newPosts)]}')

    # save related_profiles
    # only do this once for now until you need to use it
    relatedJson = profileDir / 'json' / 'related.json'
    if not relatedJson.exists():
        relatedJson.write_text(json.dumps(profile.related_profiles, indent=2))

    # get posts until you reach a post you already have
    profile.savePage(args)

    while profile.hasNextPage():
        if profile.posts['saved'] == args.limit:
            break
        nextPageJson = profileDir / 'json' / 'nextPage.json'
        nextPageJson.write_text(json.dumps(profile.getNextPage(), indent=2))
        profile.savePage(args)

    # eventually do this...
    # while profile.hasNextPage():
        # profile.savePage()

    print('saved'
        , profile.posts['pages']
        , f'page{s[sp(profile.posts["pages"])]} containing'
        , profile.posts['saved']
        , f'post{s[sp(profile.posts["saved"])]} with'
        , profile.posts['images']
        , f'image{s[sp(profile.posts["images"])]} and'
        , profile.posts['videos']
        , f'video{s[sp(profile.posts["videos"])]} totalling'
        , profile.posts['bytes']
        , f'byte{s[sp(profile.posts["bytes"])]}.'
    )

else:
    print("Everything up to date!")


