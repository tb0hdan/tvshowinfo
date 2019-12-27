#!/usr/bin/env python3

# std
import argparse
import json
import re
import sys
import urllib3

# from std
from http import HTTPStatus
from urllib.parse import quote

# 3rd party
import requests

# from 3rd party


# global changes
urllib3.disable_warnings()

class GenericShowImage(object):
    '''
    Generic TV Show image container clas
    '''
    def __getattr__(self, attr):
        if attr in ["small", "medium", "large", "original"]:
            return getattr(self, "_%s_image" % attr, None)
        raise AttributeError

    @property
    def first_available(self):
        result = None
        for img in [self.small, self.medium, self.large, self.original]:
            result = img
            if result:
                break
        return result


class GenericShowNetworkCountry(object):
    def __getattr__(self, attr):
        if attr in ["name", "code", "timezone"]:
            return getattr(self, "_%s" % attr, None)
        raise AttributeError


class GenericShowNetwork(object):
    def __getattr__(self, attr):
        if attr in ["id", "name", "country"]:
            return getattr(self, "_%s" % attr, None)
        raise AttributeError


class GenericTVShow(object):
    '''
    Generic TV Show container class
    '''
    def __getattr__(self, attr):
        if attr == "description":
            return getattr(self, "summary", None)
        if attr in ["score", "show", "show_type"]:
            return getattr(self, "_%s" % attr, None)
        if attr in ["id", "url", "name", "language", "genres", "status",
                    "runtime", "premiered", "officialSite",
                    "schedule", "rating", "weight", "network",
                    "webChannel", "externals", "image", "summary",
                    "updated", "links"]:
            return getattr(self, "_show_%s" % attr, None)
        raise AttributeError


class EpisodateImage(GenericShowImage):
    def __init__(self, show_json=None):
        super(EpisodateImage, self).__init__()
        self.show_json = show_json if show_json else {}
        self.parse()

    def parse(self):
        if not self.show_json:
            return
        self._small_image = self.show_json.get('image_thumbnail_path')
        self._medium_image = self.show_json.get('image_path')


class TVMazeImage(GenericShowImage):
    def __init__(self, show_json=None):
        super(TVMazeImage, self).__init__()
        self.show_json = show_json if show_json else {}
        self.parse()

    def parse(self):
        if not self.show_json:
            return
        self._small_image = self.show_json.get('small')
        self._medium_image = self.show_json.get('medium')
        self._large_image = self.show_json.get('large')
        self._original_image = self.show_json.get('original')
        return


class TVMazeNetworkCountry(GenericShowNetworkCountry):
    def __init__(self, show_json=None):
        super(TVMazeNetworkCountry, self).__init__()
        self.show_json = show_json if show_json else {}
        self.parse()

    def parse(self):
        if not self.show_json:
            return
        self._name = self.show_json.get('name')
        self._code = self.show_json.get('code')
        self._timezone = self.show_json.get('timezone')


class TVMazeNetwork(GenericShowNetwork):
    def __init__(self, show_json=None):
        super(TVMazeNetwork, self).__init__()
        self.show_json = show_json if show_json else {}
        self.parse()

    def parse(self):
        if not self.show_json:
            return
        self._id = self.show_json.get('id')
        self._name = self.show_json.get('name')
        self._country = TVMazeNetworkCountry(self.show_json.get('country'))
        return


class TVMazeShow(GenericTVShow):
    def __init__(self, show_json=None):
        super(TVMazeShow, self).__init__()
        self.show_json = show_json if show_json else {}
        self.parse()

    def parse(self):
        if not self.show_json:
            return
        self._score = self.show_json.get('score')
        self._show = self.show_json.get('show', {})
        self._show_id = self._show.get('id')
        self._show_url = self._show.get('url')
        self._show_name = self._show.get('name')
        self._show_type = self._show.get('type')
        self._show_language = self._show.get('language')
        self._show_genres = self._show.get('genres', [])
        self._show_status = self._show.get('status')
        self._show_runtime = self._show.get('runtime')
        self._show_premiered = self._show.get('premiered')
        self._show_officialSite = self._show.get('officialSite')
        self._show_schedule = self._show.get('schedule')
        self._show_rating = self._show.get('rating')
        self._show_weight = self._show.get('weight')
        self._show_network = TVMazeNetwork(self._show.get('network'))
        self._show_webChannel = self._show.get('webChannel')
        self._show_externals = self._show.get('externals')
        self._show_image = TVMazeImage(self._show.get('image'))
        self._show_summary = re.sub('<[^<]+?>', '', self._show.get('summary'))
        self._show_updated = self._show.get('updated')
        self._show_links = self._show.get('_links')
        return


class EpisodateShow(GenericTVShow):
    def __init__(self, show_json=None):
        super(EpisodateShow, self).__init__()
        self.show_json = show_json if show_json else {}
        self.parse()

    def parse(self):
        if not self.show_json:
            return
        tv_show = self.show_json.get('tvShow', {})
        if not tv_show:
            return
        self._show_id = tv_show.get('id')
        self._show_url = tv_show.get('url')
        self._show_name = tv_show.get('name')
        self._show_summary = re.sub('<[^<]+?>', '', tv_show.get('description'))
        self._show_status = tv_show.get('status')
        self._show_genres = tv_show.get('genres', [])
        self._show_runtime = tv_show.get('runtime')
        self._show_image = EpisodateImage(tv_show)


class TVMazeClient(object):
    SEARCH_BASE = "https://api.tvmaze.com/search/shows?q="

    def __init__(self):
        pass

    def get_matching_shows(self, show):
        result = []
        r = requests.get(self.SEARCH_BASE + quote(show))
        if r.status_code == HTTPStatus.OK:
            for show_json in r.json():
                result.append(TVMazeShow(show_json))
        return result

    def get_top_matching_show(self, show):
        result = sorted(self.get_matching_shows(show), key=lambda item: item.score, reverse=True)
        if result:
            return result[0]


class EpisodateClient(object):
    SEARCH_BASE = "https://www.episodate.com/api/search?page=1&q="
    DETAIL_BASE = "https://www.episodate.com/api/show-details?q="

    def __init__(self):
        pass

    def get_show_info(self, show):
        result = {}
        r = requests.get(self.DETAIL_BASE + quote(show), verify=False)
        if r.status_code == HTTPStatus.OK:
            result = r.json()
        return result

    def get_matching_shows(self, show):
        result = []
        r = requests.get(self.SEARCH_BASE + quote(show), verify=False)
        if r.status_code == HTTPStatus.OK:
            for show_json in r.json().get('tv_shows'):
                permalink = show_json.get('permalink', '')
                if not permalink:
                    continue
                show_info = self.get_show_info(permalink)
                if not show_info:
                    continue
                result.append(EpisodateShow(show_info))
        return result


    def get_top_matching_show(self, show):
        '''
        Episodate returns already sorted array
        :param show:
        :return:
        '''
        result = self.get_matching_shows(show)
        if result:
            return result[0]


class SlackNotification(object):
    WEBHOOK_URL = None
    SOURCES = [EpisodateClient, TVMazeClient]
    def __init__(self):
        pass

    def set_webhook_url(self, url):
        self.WEBHOOK_URL = url

    def send_tv_show_message(self, show_name):
        match = re.match('(.+)\s+(S\d+E\d+)', show_name)
        if match is not None and len(match.groups()) >= 2:
            title = match.group(1)
            episode = match.group(2)
        else:
            title = show_name
            episode = ''
        # TODO: Merge show info
        show = None
        for source in self.SOURCES:
            client = source()
            show = client.get_top_matching_show(title)
            if show:
                break
        # TV Show found, go with formatted message with attachment
        if show:
            title_text = '{0!s} - {1!s} (original title: {2!s})'.format(show.name, episode, show_name)
            payload = {'username': 'TVShowInfo', 'icon_emoji': ':tv:',
                 'attachments': [
                     {'fallback': title_text,
                      'color': '#36a64f',
                      'pretext': title_text,
                      'text': show.description,
                      'image_url': show.image.first_available
                      }
                 ]}
        # show not found, send minimal payload as is
        else:
            payload = {'username': 'TVShowInfo', 'icon_emoji': ':tv:', 'text': show_name}
        for real_url in self.WEBHOOK_URL.split(","):
            reply = requests.post(real_url, json.dumps(payload))
            print (reply.status_code == HTTPStatus.OK, reply.text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="TVShowInfo", description='Display TV Show info (and do some other stuff)')
    parser.add_argument("-w", "--webhook", dest="slack", help="Slack incoming webhook. Use comma to provide more than one")
    parser.add_argument("-s", "--show", dest="show", help="TV Show name to process")
    args = sys.argv[1:] if len(sys.argv) > 1 else ['-h']
    parsed = parser.parse_args(args)
    if parsed.slack is not None and parsed.show is not None:
        slack = SlackNotification()
        slack.set_webhook_url(parsed.slack)
        slack.send_tv_show_message(parsed.show)
