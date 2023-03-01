r"""
               _          __                                                                      
  ___   _ __  | | _   _  / _|  __ _  _ __   ___         ___   ___  _ __   __ _  _ __    ___  _ __ 
 / _ \ | '_ \ | || | | || |_  / _` || '_ \ / __| _____ / __| / __|| '__| / _` || '_ \  / _ \| '__|
| (_) || | | || || |_| ||  _|| (_| || | | |\__ \|_____|\__ \| (__ | |   | (_| || |_) ||  __/| |   
 \___/ |_| |_||_| \__, ||_|   \__,_||_| |_||___/       |___/ \___||_|    \__,_|| .__/  \___||_|   
                  |___/                                                        |_|                
"""

import httpx


from ..constants import (
    timelineEP, timelineNextEP,
    timelinePinnedEP,
    archivedEP, archivedNextEP, of_posts_list_name
)
from ..utils import auth


def scrape_pinned_posts(headers, model_id) -> list:
    with httpx.Client(http2=True, headers=headers) as c:
        url = timelinePinnedEP.format(model_id)

        auth.add_cookies(c)
        c.headers.update(auth.create_sign(url, headers))

        r = c.get(url, timeout=None)
        if not r.is_error:
            return r.json()['list']
        r.raise_for_status()


def scrape_timeline_posts(headers, model_id, timestamp=0) -> list:
    ep = timelineNextEP if timestamp else timelineEP
    url = ep.format(model_id, timestamp)

    with httpx.Client(http2=True, headers=headers) as c:
        auth.add_cookies(c)
        c.headers.update(auth.create_sign(url, headers))

        r = c.get(url, timeout=None)
        if not r.is_error:
            posts = r.json()['list']
            hasMore = r.json()['hasMore']
            if not posts:
                return posts
            while hasMore:
                posts_data = scrape_archived_posts2(headers,model_id,posts[-1]['postedAtPrecise'])
                posts += posts_data.get('posts')
                hasMore = posts_data.get('hasMore')
            return posts
        r.raise_for_status()

# REWRITE OF ABOVE FUNCTION



def scrape_archived_posts2(headers, model_id, timestamp=0) -> dict:
    ep = timelineNextEP if timestamp else timelineEP
    url = ep.format(model_id, timestamp)

    with httpx.Client(http2=True, headers=headers) as c:
        auth.add_cookies(c)
        c.headers.update(auth.create_sign(url, headers))

        r = c.get(url, timeout=None)
        if not r.is_error:
            posts = r.json()['list']
            post_data = {'hasMore':r.json()['hasMore'],'posts':posts}
            return post_data



def parse_posts(posts: list):
    media = [post['media'] for post in posts if post.get('media')]
    urls = [
        (i['info']['source']['source'], i['createdAt'], i['id'], i['type']) for m in media for i in m if i['canView']]
    return urls
