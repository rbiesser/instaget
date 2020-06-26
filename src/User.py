import json
import requests
from GraphMedia import GraphMedia

class User(object):
    """A User ProfilePage"""
    def __init__(self, node={}):
        self.biography = node['biography']
        self.external_url = node['external_url']
        self.followers = node['edge_followed_by']['count']
        self.following = node['edge_follow']['count']
        self.full_name = node['full_name']
        self.id = node['id']
        self.is_business_account = node['is_business_account']
        self.business_category_name = node['business_category_name']
        self.profile_pic_url_hd = node['profile_pic_url_hd']
        self.username = node['username']

        self.current_page = {
            "has_next_page": node['edge_owner_to_timeline_media']['page_info']['has_next_page'],
            "end_cursor": node['edge_owner_to_timeline_media']['page_info']['end_cursor']
        }

        self.posts = {
            "count": node['edge_owner_to_timeline_media']['count'],
            "edges": [],
            "images": 0,
            "videos": 0
        }

        for media in node['edge_owner_to_timeline_media']['edges']:
            self.posts['edges'].append(GraphMedia(media["node"]))

        self.related_profiles = []
        # for profile in node['edge_related_profiles']['edges']:
        #     self.related_profiles.append({
        #         "id": profile['node']['id'],
        #         "full_name": profile['node']['full_name'],
        #         "profile_pic_url": profile['node']['profile_pic_url'],
        #         "username": profile['node']['username']
        #     })

    @property
    def username(self):
        """str:"""
        print("getter property")
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

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

        next_page = json.loads(r.text)
        next_page_media = next_page['data']['user']['edge_owner_to_timeline_media']

        self.current_page['has_next_page'] = next_page_media['page_info']['has_next_page']
        self.current_page['end_cursor'] = next_page_media['page_info']['end_cursor']

        # empty list
        self.posts['edges'] = []
        for media in next_page_media['edges']:
            self.posts['edges'].append(GraphMedia(media["node"]))

        return next_page

    def savePage(self):
        for post in self.posts['edges']:
            post.save()
        # self.getNextPage()
    

    def toJson(self):
        """dump json"""
        # remove underscore from private variables
        # https://stackoverflow.com/a/31813187
        object_dict = lambda o: {key.lstrip('_'): value for key, value in o.__dict__.items()}
        return json.dumps(self, default=object_dict, allow_nan=False, sort_keys=True, indent=4)

    def __repr__(self):
        return self.toJson()
