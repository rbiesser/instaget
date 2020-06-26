# sharedData

Instagram is a React ui with a GraphQL backend.

## `https://www.instagram.com/<username>`

- Every user has a story of posts (images and videos) where links to the first 12 posts appear in the index within the `window._sharedData` object. 

## https://www.instagram.com/data/shared_data/

- You can see how the server views your client by requesting this url.
- These seem to be settings for how the app should render.
- Of those listed, these are probably the most interesting:

```json
    "country_code": "US",
    "language_code": "en",
    "locale": "en_US",
    "entry_data": {},
    "hostname": "www.instagram.com",
    "is_whitelisted_crawl_bot": false,
    ...
    "device_id": "",
    "encryption": {
        "key_id": "211",
        "public_key": "cef843614f6a5f2d51c2b09221a8de0f374476504d246bad5aa87a5fb8e13805",
        "version": "10"
    },
    "is_dev": false,
    "rollout_hash": "197d0b77dbdb",
    "bundle_variant": "metro",
    "frontend_env": "prod"
```

- These are the same values that exist in the `window._sharedData` object except that the `entry_data` key is empty.
- Not sure why else an extra request is made to this url at the moment.

## window._sharedData
- Initialize the application
- Within `entry_data` there is a `user` object:

```python
entry_data["ProfilePage"][0]["graphql"]["user"]
```
- Every entry maps to some element in the user interface and even a little extra that is used in the background.
- One of the first tasks is figuring out how to tell if there is new content.
- Is it safe to assume that we can just check the number of posts and compare to a previous amount? But what happens if a user deletes a post?
- Otherwise would need to check the full list looking for missing posts. This creates a logic error, but no need to overload the server.
- Here's some interesting keys:

```json
"user": {
    // let's you know how popular this user is
    "edge_followed_by": {
        "count": 1104598
    },
    // every user has a unique id
    "id": "",
    // the username matches the url requested to get here
    "username": "",
    // contains the posts info
    "edge_owner_to_timeline_media": {
        // the number of posts
        "count": 430,
        "page_info": {
            "has_next_page": true,
            // contains a hash to the next page, more later
            "end_cursor": ""
        },
        // an array of the first 12 posts
        "edges": [
            {
                  "node": {},
            },
        ]
    },
    // useful for discovering new profiles
    "edge_related_profiles": {
        "edges": [
            {
                "node": {},
            },
        ]
    }
}
```

- Just look for others, it might be there.
- The idea of edges is a common graphql term.


