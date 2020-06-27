import json
import requests
from pathlib import Path

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
            self.owner = {
                "id": node['owner']['id'],
                "username": node['owner']['username']
            }

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

    def _save(self, url, mediaDir, get=True):
        filename = mediaDir / Path(url).name.split('?')[0]
        
        if get == True:
            if filename.exists():
                print('STOP', filename.name, filename.stat().st_size)
                # return filename
                return False
            else:
                # get the file
                r = requests.get(url)
                print(r.request.method, r.request.url, r.status_code)

                open(filename, 'wb').write(r.content)
                print('SAVE', filename.name, filename.stat().st_size)

                return filename
        
        else:
            print('SKIP', filename.name, filename.stat().st_size)
            return True


    def saveGraphImage(self, args, mediaDir):
        # print(self.typename)
        # print(args)
        print(self)
        filename = self._save(self.display_url, mediaDir, args.getImages)
        if filename and filename.exists():
            # update exif info
            # initialize variables
            owner = caption = application = date_time_original = ''
            ts = 0

            # owner should be the same as the current profile, but we'll get it off the node since it is there
            application = 'Instagram'
            owner = self.owner['username']
            if hasattr(self, 'caption'):
                caption = self.caption.encode('utf-8')
            # else:
            #     logging.info('caption not available')
            if hasattr(self, 'taken_at_timestamp'):
                ts = self.taken_at_timestamp
                date_time_original = datetime.utcfromtimestamp(self.taken_at_timestamp).strftime('%Y-%m-%d %H:%M:%S')
            else:
                # I think I fixed this part
                print('self.taken_at_timestamp')
                exit()
                # node = shortcode_media_query(node['shortcode'])
                # date_time_original = datetime.utcfromtimestamp(node['taken_at_timestamp']).strftime('%Y-%m-%d %H:%M:%S')

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

            os.utime(filename, (ts,ts))

        return filename

    def saveGraphVideo(self, args, mediaDir):
        # print(self.typename)
        return self._save(self.video_url, mediaDir, args.getVideos)

    # these are probably not needed, but need to find 
    # where to put the download code.

    def saveGraphSidecar(self, args, mediaDir):
        # print(self.typename)
        # not needed since first child is duplicate of sidecar
        return self._save(self.display_url, mediaDir, False)
        # print(self.sidecar)
        # exit()


    def toJson(self):
        """dump json"""
        # remove underscore from private variables
        # https://stackoverflow.com/a/31813187
        object_dict = lambda o: {key.lstrip('_'): value for key, value in o.__dict__.items()}
        return json.dumps(self, default=object_dict, allow_nan=False, sort_keys=True, indent=4)

    def __repr__(self):
        return self.toJson()






