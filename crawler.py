import json
import requests
import sqlite3

from pyquery import PyQuery
from random import randint
from slackclient import SlackClient

from config import FILESTACK_APIKEY, SLACK_CLIENT_ID, SLACK_CLIENT_SECRET, SLACK_OAUTH_TOKEN, SLACK_BOT_OAUTH_TOKEN

reddit_thread = 'aww'
reddit_url = 'https://www.reddit.com/r/{}'.format(reddit_thread)
filestackapi = 'https://www.filestackapi.com/api/store/S3?key={}'.format(FILESTACK_APIKEY)

post_info = {}


def query_database(database_name, query, forLoop=None, printQuery=None, returnResult=None):
    conn = None

    try:
        conn = sqlite3.connect(database_name)

        if returnResult:
            result = conn.execute(query)
            result = result.fetchall()
        else:
            conn.execute(query)

        if printQuery:
            print(query)

        conn.commit()

    except sqlite3.Error as er:
        print('DATABASE ERROR: {}'.format(er))

    finally:
        if conn:
            conn.close()

        try:
            return result
        except:
            pass


def create_table(database_name, table_name, query):
    query_database(database_name,
                   ('CREATE TABLE IF NOT EXISTS {} ({})'.format(table_name,
                                                                query)))


def fetch_table(database_name, table_name):
    return query_database(database_name,
                          'SELECT * FROM {}'.format(table_name),
                          returnResult=True)


def drop_table(database_name, table_name):
    query_database(database_name,
                   'DROP TABLE {}'.format(table_name))


def store_to_database(database_name, table_name, column_names, values):
    query_database(database_name,
                   'INSERT INTO {} {} values ({})'.format(table_name,
                                                          column_names,
                                                          values),
                   printQuery=False)  # Set to True to print each query


def fetch_last_id_from_table(database_name, table_name):
    id_obj = query_database(database_name,
                            'SELECT max(id) FROM {}'.format(table_name),
                            returnResult=True)

    for attr in id_obj:
        return attr[0]


def check_database_for_unposted(database_name, table_name):
    return query_database(database_name,
                          'SELECT * FROM {} WHERE has_been_picked = 0'.format(table_name),
                          returnResult=True)


def check_if_randomInt_is_unposted(database_name, table_name, random_int):
    return query_database(database_name,
                          'SELECT * FROM {} WHERE id = {} AND has_been_picked = 0'.format(table_name,
                                                                                          random_int),
                          returnResult=True)


def reset_has_been_picked(database_name, table_name):
    query_database(database_name,
                   'UPDATE {} SET has_been_picked = 0'.format(table_name))


def set_all_has_been_picked(database_name, table_name):
    query_database(database_name,
                   'UPDATE {} SET has_been_picked = 1'.format(table_name))


def set_has_been_picked(database_name, table_name, random_int):
    query_database(database_name,
                   'UPDATE {} SET has_been_picked = 1 WHERE id = {}'.format(table_name,
                                                                            random_int))


def get_and_upload_post_info():
    response = requests.get(reddit_url, headers={'User-agent': 'Not a bot :)'})

    print(response.status_code)

    jQuery = PyQuery(response.content)

    children = jQuery('#siteTable').children()

    last_id = fetch_last_id_from_table('awwbot.db', 'awwPostsInfo')

    try:
        index = last_id + 1
    except:
        index = 1

    for child in children:
        try:
            cssSelector = '#{} > div.entry.unvoted > p.title > a'.format(child.items()[1][1])
            post_info[index] = {'handle': child.items()[1][1],
                                'url': child.items()[10][1],
                                'post_title': child.cssselect(cssSelector)[0].text_content()}
            upload_post_url(index)
            sanitize_post_title(post_info, index)
            index += 1
            # print(post_info)  # Prints as it stores
        except:
            pass


def upload_post_url(index):
    response = requests.post(filestackapi, data={'url': post_info[index]['url']})
    data = json.loads(response.text)
    cdnURL = data['url']
    handle = cdnURL.split('https://cdn.filestackcontent.com/')[1]

    post_info[index].update({'handle': handle, 'url': data['url']})


def sanitize_post_title(post_dict, index):
    for k, v in post_dict.items():
        if '"' in v['post_title']:
            post_title = v['post_title'].replace('"', '')
            post_info[index].update({'post_title': post_title})


def build_values_list_and_store(database_name, table_name, column_names, post_dict):
    for k, v in post_dict.items():
        store_to_database(
            database_name,
            table_name,
            column_names,
            ("'{}', '{}', \"{}\", 'None', 0").format(v['handle'], v['url'], v['post_title']))


def fetch_random_post_from_database(database_name, table_name, columns):
    last_id = fetch_last_id_from_table(database_name, table_name)

    random_int = randint(1, last_id)

    if check_if_randomInt_is_unposted(database_name, table_name, random_int):
        post = query_database(database_name,
                              'SELECT {} FROM {} WHERE id = {}'.format(columns,
                                                                       table_name,
                                                                       random_int),
                              returnResult=True)
        set_has_been_picked(database_name, table_name, random_int)
    elif check_database_for_unposted(database_name, table_name):
        return fetch_random_post_from_database(database_name, table_name, columns)
    else:
        post = query_database(database_name,
                              'SELECT {} FROM {} WHERE id = {}'.format(columns,
                                                                       table_name,
                                                                       random_int),
                              returnResult=True)
    try:
        if post:
            return [post[0][0], post[0][1]]
    except:
        pass


def post_message_to_slack(post_title, post_url):
    sc = SlackClient(SLACK_OAUTH_TOKEN)
    print(sc.api_call("chat.postMessage", channel="#aww", text='{}: {}'.format(post_title, post_url)))


# drop_table('awwbot.db', 'awwPostsInfo')
# create_table('awwbot.db', 'awwPostsInfo', ('''id INTEGER PRIMARY KEY AUTOINCREMENT,
#                                                   handle TEXT NOT NULL,
#                                                   url TEXT NOT NULL,
#                                                   post_title TEXT,
#                                                   tags TEXT,
#                                                   has_been_picked INTEGER NOT NULL'''))
#
# get_and_upload_post_info()
#
# awwcrawler_column_names = ('handle', 'url', 'post_title', 'tags', 'has_been_picked')
# build_values_list_and_store('awwbot.db', 'awwPostsInfo', awwcrawler_column_names, post_info)

# check_database_for_unposted('awwbot.db', 'awwPostsInfo')
# reset_has_been_picked('awwbot.db', 'awwPostsInfo')
# set_all_has_been_picked('awwbot.db', 'awwPostsInfo')

# print(fetch_last_id_from_table('awwbot.db', 'awwPostsInfo'))
# print(fetch_table('awwbot.db', 'awwPostsInfo'))
print(fetch_random_post_from_database('awwbot.db', 'awwPostsInfo', 'url, post_title'))

# random_post = fetch_random_post_from_database('awwbot.db', 'awwPostsInfo', 'url, post_title')
# post_message_to_slack(random_post[1], random_post[0])
