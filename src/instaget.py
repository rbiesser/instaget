import argparse
import requests
from pathlib import Path
import json
import re
from datetime import datetime
from User import User

parser = argparse.ArgumentParser(
    description='',
    epilog="Save an Instagram story.",
    usage='%(prog)s <username>')
parser.add_argument("username", help="An Instagram username")
parser.add_argument('-i','--images', help="Get only images", action="store_true", dest="getImages")
parser.add_argument('-V','--videos', help="Get only videos", action="store_true", dest="getVideos")
parser.add_argument('-b','--both', help="Get all images and videos, same as -iV", action="store_true", dest="getBoth")
parser.add_argument('-f','--fetch', help="Fetch latest profile", action="store_true", dest="fetch")
parser.add_argument('-r','--resume', help="Resume a previous session", action="store_true", dest="resume")
parser.add_argument('--limit', help="Get the newest n posts", type=int, dest="limit")
parser.add_argument('--dry-run', help="Skip downloading is the default", action="store_true", dest="dryRun")
parser.add_argument('-v','--version', action='version', version='%(prog)s 1.0-pre-release')

args = parser.parse_args()

# dry-run is the default and will take precedence
if args.dryRun:
    args.getImages = args.getVideos = args.getBoth = False
elif args.getBoth:
    args.getImages = args.getVideos = True
elif args.getImages:
    if args.getVideos:
        args.getBoth = True
else:
    if args.getVideos == False:
        args.dryRun = True

username = args.username

# might want to change download location, but use the Path library here
profileDir = Path('profiles') / username

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
    jsonDir.mkdir(parents=True, exist_ok=True)
    mediaDir.mkdir(parents=True, exist_ok=True)
    nextPageJson.touch()
    sharedDataJson.touch()
    args.fetch = True

if lastRunSharedData:
    lastRun = User(lastRunSharedData["entry_data"]["ProfilePage"][0]["graphql"]["user"])
    sharedData = lastRunSharedData
else:
    # empty lastRun object
    lastRunSharedData = {'user': {'edge_owner_to_timeline_media': {'count': 0}}}
    lastRun = User(lastRunSharedData['user'])

if args.fetch:
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

# simple check to see if the count has increased
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

    try:
        # get posts until you reach a post you already have
        # if the file exists, no new request is made, but metadata will be updated.
        # runing with --resume will make a request for each new page.
        profile.savePage(args, mediaDir)

        while profile.hasNextPage():
            nextPageJson = profileDir / 'json' / 'nextPage.json'
            nextPageJson.write_text(json.dumps(profile.getNextPage(), indent=2))
            profile.savePage(args, mediaDir)
   
    except KeyboardInterrupt:
        # exit gracefully
        print('\nexiting')
        pass
    except Exception as e:
        print(e)

    finally:

        # https://stackoverflow.com/a/1094933
        def sizeof_fmt(num, suffix='B'):
            for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
                if num < 1024.0:
                    return "%3.1f%s%s" % (num, unit, suffix)
                num /= 1024.0
            return "%.1f%s%s" % (num, 'Yi', suffix)

        print('would have saved' if (args.dryRun) else 'saved'
            , f'{profile.posts["pages"]} page{s[sp(profile.posts["pages"])]}'
            , f'containing {profile.posts["saved"]} post{s[sp(profile.posts["saved"])]}'
            , f'with {profile.posts["images"]} image{s[sp(profile.posts["images"])]}'
            , f'and {profile.posts["videos"]} video{s[sp(profile.posts["videos"])]}'
            , f'totalling {sizeof_fmt(profile.posts["bytes"])}.' if args.dryRun == False else ''
            , '\nrun again with the -b flag to get all images and videos or --help for more options.' if args.dryRun else ''
        )

else:
    print("Everything up to date!")


