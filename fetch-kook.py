from datetime import datetime
import requests
import json
import time


def build_params(offset, per_page): 
    return {
        'offset': offset,
        'perPage': per_page,
        'c': c
    }

def fetch_once(offset, per_page):
    params = build_params(offset, per_page)
    response = requests.get('https://www.kookapp.cn/api/v2/guilds/users-v2/8011297845074571', params=params, cookies=cookies, headers=headers)
    return response.json()

def fetch_at_first(per_page): 
    response_json = fetch_once(offset=0, per_page=per_page)
    return (response_json, response_json['user_count'])

def fetch_all_users():
    response_json, user_count = fetch_at_first(per_page=per_page_const)
    users = response_json['data']
    seconds = 0

    run_times = int(user_count / per_page_const) + 1
    offset = 0

    now = datetime.now()
    now_time_stamp = time.time()

    for x in range(1, run_times):
        offset = x + 1 * per_page_const
        response_json = fetch_once(offset, per_page=per_page_const)
        time.sleep(1)
        seconds += 1
        print('wait for %d seconds' % seconds)
        users.extend(response_json['data'])

    return  {
        'users': users,
        'date': str(now),
        'timestamp': int(now_time_stamp)
    }


def main():
    users = fetch_all_users()
    with open('users_response.json', 'w') as f:
        json.dump(users, f, ensure_ascii=False)
   

if __name__ == '__main__':
    main()

