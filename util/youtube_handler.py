from youtubesearchpython.__future__ import VideosSearch

import pafy


async def get_first_video_link(arg):
    videos_search = VideosSearch(arg, limit=1)
    videos_result = await videos_search.next()
    return pafy.new(videos_result["result"][0]["link"])
