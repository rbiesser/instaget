import json
import requests
from pathlib import Path

class GraphMedia:
    """base class for graph media"""
    def __init__(self, node={}):
        if '__typename' in node:
            self.typename = node['__typename']

        if 'id' in node:
            self.id = node['id']

        if 'shortcode' in node:
            self.shortcode = node['shortcode']
        
        # dimensions

        if 'display_url' in node:
            self.display_url = node['display_url']

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

    def _save(self, url, skip=True):
        size = 0
        
        if skip == True:
            rcvdBytes = 'skipped'
        else:
            # get the file
            rcvdBytes = size

        print(self.typename
            , self.shortcode
            , url
            , rcvdBytes
        )

        return size

    def saveGraphImage(self, args):
        # print(self.typename)
        return self._save(self.display_url, args.getImages)

    def saveGraphVideo(self, args):
        # print(self.typename)
        return self._save(self.video_url, args.getVideos)

    # these are probably not needed, but need to find 
    # where to put the download code.

    def saveGraphSidecar(self, args):
        # print(self.typename)
        # not needed since first child is duplicate of sidecar
        return self._save(self.display_url, True)
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






