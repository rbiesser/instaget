# GraphMedia
Three basic types of media:

## GraphImage
- An image will have a display_url linking to the image.

## GraphVideo
- A video with have is_video set to true and a video_url linking to the video.
- The display_url links to the preview image for the video.
- Therefore a video will have at least an image and a video.

## GraphSidecar
- Can be any combination of the other two types.
- Does not contain any additional attributes without making request to the shortcode page.
- Does have the caption and display_url
- For the GraphSidecar, taken_at_timestamp, caption and location, etc. come from the GraphSidecar and not repeated for each edge_sidecar_to_children.
- It looks like the only thing you don't get without making shortcode requests is tagged users and commenters.



## check

- [ ] Page 2 might contain different properties than the first page and would need to make shortcode request for every post.
