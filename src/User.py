import json
import requests
from GraphMedia import GraphMedia

class User(object):
    """A User ProfilePage"""
    def __init__(self, node={}):
        if 'biography' in node:
            self.biography = node['biography']
        
        if 'external_url' in node:
            self.external_url = node['external_url']
        
        if 'edge_followed_by' in node:
            self.followers = node['edge_followed_by']['count']

        if 'edge_follow' in node:
            self.following = node['edge_follow']['count']

        if 'full_name' in node:
            self.full_name = node['full_name']

        if 'id' in node:
            self.id = node['id']

        if 'is_business_account' in node:
            self.is_business_account = node['is_business_account']

        if 'business_category_name' in node:
            self.business_category_name = node['business_category_name']

        if 'profile_pic_url_hd' in node:
            self.profile_pic_url_hd = node['profile_pic_url_hd']

        if 'username' in node:
            self.username = node['username']

        if 'edge_owner_to_timeline_media' in node:
            if 'page_info' in node['edge_owner_to_timeline_media']:
                self.current_page = {
                    "has_next_page": node['edge_owner_to_timeline_media']['page_info']['has_next_page'],
                    "end_cursor": node['edge_owner_to_timeline_media']['page_info']['end_cursor']
                }

            self.posts = {
                "count": node['edge_owner_to_timeline_media']['count'],
                "edges": [],
                "images": 0,
                "videos": 0,
                "saved": 0,
                "pages": 1,
                "bytes": 0
            }

            if 'edges' in node['edge_owner_to_timeline_media']:
                for media in node['edge_owner_to_timeline_media']['edges']:
                    self.posts['edges'].append(GraphMedia(media["node"]))

        if 'edge_related_profiles' in node:
            self.related_profiles = []
            for profile in node['edge_related_profiles']['edges']:
                self.related_profiles.append({
                    "id": profile['node']['id'],
                    "full_name": profile['node']['full_name'],
                    "profile_pic_url": profile['node']['profile_pic_url'],
                    "username": profile['node']['username']
                })

    # @property
    # def username(self):
    #     """str:"""
    #     print("getter property")
    #     return self._username

    # @username.setter
    # def username(self, value):
    #     self._username = value

    def hasNextPage(self):
        return self.current_page['has_next_page']

    def getNextPage(self):
        print(self.current_page['end_cursor'])
        # keep object with full list of posts or delete and populate with each page?

        query_hash = '9dcf6e1a98bc7f6e92953d5a61027b98'
        variables = {
            # 'shortcode': node['shortcode']
            'id': self.id,
            'first': 12,
            'after': self.current_page['end_cursor']
        }

        r = requests.get('https://www.instagram.com/graphql/query/',
            params={
                'query_hash': query_hash,
                'variables': json.dumps(variables)
            }
        )

        print(r.request.method, r.request.url, r.status_code)
        next_page = json.loads(r.text)
        next_page_media = next_page['data']['user']['edge_owner_to_timeline_media']

        self.current_page['has_next_page'] = next_page_media['page_info']['has_next_page']
        self.current_page['end_cursor'] = next_page_media['page_info']['end_cursor']

        # empty list
        self.posts['edges'] = []
        for media in next_page_media['edges']:
            self.posts['edges'].append(GraphMedia(media["node"]))

        self.posts['pages'] += 1

        return next_page

    def savePage(self, args):
        for post in self.posts['edges']:
            if self.posts['saved'] == args.limit:
                return

            # post._save()
            if post.typename == 'GraphImage':
                rcvdBytes = post.saveGraphImage(args)
                self.posts['bytes'] += rcvdBytes
                self.posts['images'] += 1
            elif post.typename == 'GraphVideo':
                # videos have both a display_url and video_url
                # saveGraphVideo needs to specifically tell save to use video_url
                rcvdBytes = post.saveGraphImage(args)
                self.posts['bytes'] += rcvdBytes
                self.posts['images'] += 1

                rcvdBytes = post.saveGraphVideo(args)
                self.posts['bytes'] += rcvdBytes
                self.posts['videos'] += 1
                # exit()
            elif post.typename == 'GraphSidecar':
                # a sidecar can contain multiple images or videos 
                # the sidecar display_url matches the first child
                post.saveGraphSidecar(args)
                # print(post.location, post.taken_at_timestamp)
                for child in post.sidecar['edges']:
                    # share the sidecar attributes with the children
                    if hasattr(post, 'shortcode'):
                        child.shortcode = post.shortcode
                    if hasattr(post, 'location'):
                        child.location = post.location
                    if hasattr(post, 'taken_at_timestamp'):
                        child.taken_at_timestamp = post.taken_at_timestamp
                    
                    if child.typename == 'GraphImage':
                        rcvdBytes = child.saveGraphImage(args)
                        self.posts['bytes'] += rcvdBytes
                        self.posts['images'] += 1
                    elif child.typename == 'GraphVideo':
                        # videos have a display_url and video_url
                        rcvdBytes = child.saveGraphImage(args)
                        self.posts['bytes'] += rcvdBytes
                        self.posts['images'] += 1
                        
                        rcvdBytes = child.saveGraphVideo(args)
                        self.posts['bytes'] += rcvdBytes
                        self.posts['videos'] += 1
                        # exit()
                    else:
                        print('new typename in a sidecar', child.typename)
                        exit()

            else:
                print('new typename', post.typename)
                exit()

            self.posts['saved'] += 1
    

    def toJson(self):
        """dump json"""
        # remove underscore from private variables
        # https://stackoverflow.com/a/31813187
        object_dict = lambda o: {key.lstrip('_'): value for key, value in o.__dict__.items()}
        return json.dumps(self, default=object_dict, allow_nan=False, sort_keys=True, indent=4)

    def __repr__(self):
        return self.toJson()
