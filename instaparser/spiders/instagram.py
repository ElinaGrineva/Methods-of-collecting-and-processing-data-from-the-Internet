import scrapy
import re
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy
from instaparser.items import InstaparserItem
import insta_settings

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com']
    insta_login = insta_settings.insta_login
    insta_pass = insta_settings.insta_pass
    insta_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    users_parse = ['ai_machine_learning', 'rbc_ru']
    posts_hash = '8c2a529969ee035a5063f2fc8602a0fd'
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    friendships_url = 'https://i.instagram.com/api/v1/friendships/'



    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(self.insta_login_link,
                                 method='POST',
                                 callback=self.user_login,
                                 formdata={'username': self.insta_login,
                                           'enc_password': self.insta_pass},
                                 headers={'X-CSRFToken': csrf})

    def user_login(self, response: HtmlResponse):
        j_body = response.json()
        if j_body['authenticated']:
            yield response.follow(f'/{self.user_parse}',
                                  callback=self.user_data_parse,
                                  cb_kwargs={'username': self.user_parse})

    def user_follow_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {
            'count': 12,
            'search_surface': 'follow_list_page'
        }
        url_followers = f'{self.friendships_url}{user_id}/followers/?{urlencode(variables)}'
        yield response.follow(url_followers,
                              callback=self.followers_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'variables': deepcopy(variables)},
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'}
                              )

        url_following = f'{self.friendships_url}{user_id}/following/?{urlencode(variables)}'
        yield response.follow(url_following,
                              callback=self.following_parse,
                              cb_kwargs={'username': deepcopy(username),
                                         'user_id': deepcopy(user_id),
                                         'variables': deepcopy(variables)},
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'}
                              )

    def following_parse(self, response: HtmlResponse, username, user_id, variables):
        if response.status == 200:
            j_data = response.json()
            if j_data.get('big_list'):
                variables['max_id'] = j_data.get('next_max_id')
                url_following = f'{self.friendships_url}{user_id}/following/?{urlencode(variables)}'
                yield response.follow(url_following,
                                      callback=self.following_parse,
                                      cb_kwargs={'username': username,
                                                 'user_id': user_id,
                                                 'variables': deepcopy(variables)},
                                      headers={'User-Agent': 'Instagram 155.0.0.37.107'}
                                      )

            users = j_data.get('users')
            for user in users:
                item = InstaparserItem(user_id=user.get('pk'),
                                       username=user.get('username'),
                                       full_name=user.get('full_name'),
                                       profile_pic_url=user.get('profile_pic_url'),
                                       follower_id=user_id,
                                       follower_name=username,
                                       following_to_id=None,
                                       following_to_name=None
                                       )
                yield item

    def followers_parse(self, response: HtmlResponse, username, user_id, variables):
        if response.status == 200:
            j_data = response.json()
            if j_data.get('big_list'):
                variables['max_id'] = j_data.get('next_max_id')
                url_followers = f'{self.friendships_url}{user_id}/followers/?{urlencode(variables)}'
                yield response.follow(url_followers,
                                      callback=self.followers_parse,
                                      cb_kwargs={'username': username,
                                                 'user_id': user_id,
                                                 'variables': deepcopy(variables)},
                                      headers={'User-Agent': 'Instagram 155.0.0.37.107'}
                                      )

            users = j_data.get('users')
            for user in users:
                item = InstaparserItem(user_id=user.get('pk'),
                                       username=user.get('username'),
                                       full_name=user.get('full_name'),
                                       profile_pic_url=user.get('profile_pic_url'),
                                       follower_id=None,
                                       follower_name=None,
                                       following_to_id=user_id,
                                       following_to_name=username
                                       )
                yield item


    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')


    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')