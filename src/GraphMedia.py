class GraphMedia:
    """base class for graph media"""
    def __init__(self, node={}):
        self.typename = node['__typename']
        self.id = node['id']
        self.shortcode = node['shortcode']
        # dimensions
        self.display_url = node['display_url']
        self.is_video = node['is_video']

        # optional caption
        if 'edge_media_to_caption' in node and node['edge_media_to_caption']['edges']:
            self.caption = node['edge_media_to_caption']['edges'][0]['node']['text']
        
        self.taken_at_timestamp = node['taken_at_timestamp']
        
        # if 'edge_media_to_comment' in node:
        self.comments = {
            "count": node['edge_media_to_comment']['count']
        }

        # not on the paged requests, would have to visit media page
        # if 'edge_liked_by' in node:
        # self.likes = {
        #     "count": node['edge_liked_by']['count']
        # }

        # optional location
        if 'location' in node and node['location']:
            self.location = {
                "id": node['location']['id'],
                "name": node['location']['name'],
                "slug": node['location']['slug']
            }

    def save(self):
        print(self.typename
            , self.display_url
            # , self.is_video
        )






