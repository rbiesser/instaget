import json
import requests
from pathlib import Path
import os
from datetime import datetime
from PIL import Image
import piexif

class GraphMedia:
    """base class for graph media"""
    def __init__(self, node={}):
        if '__typename' in node:
            self.typename = node['__typename']

        if 'id' in node:
            self.id = node['id']

        if 'shortcode' in node:
            self.shortcode = node['shortcode']
        
        # dimensions, only useful for ui, get from file

        if 'display_url' in node:
            self.display_url = node['display_url']

        if 'owner' in node:
            # self.owner = {
            #     "id": node['owner']['id'],
            #     "username": node['owner']['username']
            # }
            self.owner = node['owner']

        if 'is_video' in node:
            self.is_video = node['is_video']

        if 'video_url' in node:
            self.video_url = node['video_url']

        if 'video_view_count' in node:
            self.video_view_count = node['video_view_count']

        if 'edge_sidecar_to_children' in node and node['edge_sidecar_to_children']['edges']:
            self.sidecar = {
                "edges": []
            }
            for media in node['edge_sidecar_to_children']['edges']:
                self.sidecar['edges'].append(GraphMedia(media["node"]))

        if 'edge_media_to_caption' in node and node['edge_media_to_caption']['edges']:
            self.caption = node['edge_media_to_caption']['edges'][0]['node']['text']
        
        if 'taken_at_timestamp' in node:
            self.taken_at_timestamp = node['taken_at_timestamp']
        
        if 'edge_media_to_comment' in node:
            self.comments = {
                "count": node['edge_media_to_comment']['count']
            }

        # not on the paged requests, would have to visit media page
        if 'edge_liked_by' in node:
            self.likes = {
                "count": node['edge_liked_by']['count']
            }

        if 'location' in node and node['location']:
            self.location = {
                "id": node['location']['id'],
                "name": node['location']['name'],
                "slug": node['location']['slug']
            }

    def _save(self, url, mediaDir, args, saveFile=True):
        filename = mediaDir / Path(url).name.split('?')[0]

        # print(self)
        
        if saveFile:
            if filename.exists():
                if args.resume:
                    print('SKIP', self.typename, filename.name, filename.stat().st_size)
                    return filename
                else:
                    print('STOP', self.typename, filename.name, filename.stat().st_size)
                    # stop after finding the first post that has already been retrieved
                    raise Exception('no new posts')
            else:
                # get the file
                r = requests.get(url)
                print(r.request.method, r.request.url, r.status_code)

                open(filename, 'wb').write(r.content)
                print('SAVE', self.typename, filename.name, filename.stat().st_size)
                
                return filename
        
        else:
            print('SKIP', self.typename, filename.name, '-')
            return filename


    def saveGraphImage(self, args, mediaDir):
        filename = self._save(self.display_url, mediaDir, args, args.getImages)
        if filename.exists():
            # initialize variables
            owner = caption = application = date_time_original = ''
            ts = datetime.now().timestamp()

            # owner should be the same as the current profile, but 
            # get it off the node since it is there
            application = 'Instagram'
            print(filename)
            owner = self.owner['username']

            if hasattr(self, 'caption'):
                caption = self.caption.encode('utf-8')

            if hasattr(self, 'taken_at_timestamp'):
                ts = self.taken_at_timestamp
                date_time_original = datetime.utcfromtimestamp(self.taken_at_timestamp).strftime('%Y-%m-%d %H:%M:%S')
            
            # update exif info
            img = Image.open(filename)
            zeroth_ifd = {
                piexif.ImageIFD.Artist: owner,
                piexif.ImageIFD.ImageDescription: caption,
                piexif.ImageIFD.Software: application
            }
            exif_ifd = {
                # piexif.ExifIFD.UserComment: b"comment",
                piexif.ExifIFD.DateTimeOriginal: date_time_original,
            }

            exif_dict = {"0th": zeroth_ifd, "Exif": exif_ifd}
            exif_bytes = piexif.dump(exif_dict)
            img.save(filename, exif=exif_bytes)

            # change create, modified timestamp
            os.utime(filename, (ts,ts))

        return filename

    def saveGraphVideo(self, args, mediaDir):
        filename = self._save(self.video_url, mediaDir, args, args.getVideos)
        if filename.exists():
            ts = datetime.now().timestamp()
            if hasattr(self, 'taken_at_timestamp'):
                ts = self.taken_at_timestamp

            # change create, modified timestamp
            os.utime(filename, (ts,ts))

        return filename
        
    def saveGraphSidecar(self, args, mediaDir):
        # not needed to save since first child is duplicate of sidecar
        return self._save(self.display_url, mediaDir, args, False)

    def toJson(self):
        """dump json"""
        # remove underscore from private variables
        # https://stackoverflow.com/a/31813187
        object_dict = lambda o: {key.lstrip('_'): value for key, value in o.__dict__.items()}
        return json.dumps(self, default=object_dict, allow_nan=False, sort_keys=True, indent=4)

    def __repr__(self):
        return self.toJson()






