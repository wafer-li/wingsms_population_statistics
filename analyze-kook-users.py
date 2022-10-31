from distutils.command.install_egg_info import to_filename
from itertools import groupby
from tokenize import group
import json
import re

regex = r'(.*)-(.*?)-(.*)'

level_cap = 120


# user classes

noob = '新手'

warrior = '战士'
# warrior_sword = ['剑客', '勇士', '英雄']
warrior_sword = ['剑客']
# warrior_spear = ['枪战士', '龙骑士', '黑骑士']
warrior_spear = ['枪战士']
# warrior_dark = ['准骑士', '骑士', '圣骑士']
warrior_dark = ['准骑士']

warrior_group = [warrior, *warrior_sword, *warrior_spear, *warrior_dark]

magician = '魔法师'
# magician_priest = ['牧师', '祭司', '主教']
magician_priest = ['牧师']
magician_ice = ['法师(冰,雷)']
magician_fire = ['法师(火,毒)']
magician_group = [magician, *magician_priest, *magician_ice, *magician_fire]

bowman = '弓箭手'
# bowman_bow = ['猎人', '射手', '神射手']
bowman_bow = ['猎人']
# bowman_cross_bow = ['弩弓手', '游侠', '箭神']
bowman_cross_bow = ['弩弓手']
bowman_group = [bowman, *bowman_bow, *bowman_cross_bow]

thief = '飞侠'
# thief_dart= ['刺客', '无影人', '隐士']
thief_dart= ['刺客']
# thief_knife = ['侠客', '独行客', '侠盗']
thief_knife = ['侠客']
thief_group = [thief, *thief_dart, *thief_knife]

pirate = '海盗'
# pirate_fist = ['拳手', '斗士', '冲锋队长']
pirate_fist = ['拳手']
# pirate_gun = ['火枪手', '大副', '船长']
pirate_gun = ['火枪手']
pirate_group = [pirate, *pirate_fist, *pirate_gun]

class_groups = [warrior_group, magician_group, bowman_group, thief_group, pirate_group]
base_class_groups = [noob, warrior, magician, bowman, thief, pirate]

# user class end



class user_info:
    user_name = ''
    user_class = ''
    user_level = 0

    def __init__(self, user_name, user_class, user_level):
        self.user_name = user_name
        self.user_class = user_class
        self.user_level = user_level


def obtain_valuable_user_infos(users): 
    nicknames = map(lambda user: user['nickname'], users)
    filtered_nicknames = filter(lambda nickname: re.fullmatch(regex, nickname) != None, nicknames)
    user_infos = map(lambda nickname: nickname_to_user_info(nickname), filtered_nicknames)
    valid_user_infos = filter(lambda user_info: is_user_info_valid(user_info), user_infos)
    return list(valid_user_infos)

def nickname_to_user_info(nickname):
    groups = re.fullmatch(regex, nickname).groups()

    level_text = groups[2]
    print('nickname: %s, level_text: %s' % (nickname, level_text))

    level_match = re.match(r'\d+', level_text)

    level = 0

    if level_match is not None:
        level = int(level_match.group())

    user_class = groups[1]

    if find_valid_user_class(user_class) == '':
        user_class = ''

    return user_info(groups[0], user_class, level)

def find_valid_user_class(user_class):
    if user_class == noob:
        return noob

    for group in class_groups:
        if user_class in group:
            return user_class
    
    return ''


def is_user_info_valid(user_info):
    level = user_info.user_level
    class_name = user_info.user_class

    return level > 0 and level <= level_cap and class_name != ''


def analyze_user_infos(user_infos):
    real_user_info = sorted(user_infos, key=lambda user_info: user_info.user_class)

    total_count = len(real_user_info)

    dict_by_user_class = groupby(real_user_info, lambda user_info: user_info.user_class)

    class_infos = list(map(lambda item: analyze_user_class_raw(item[0], item[1]), dict_by_user_class))

    non_base_classes_infos = list(filter(lambda class_info: is_class_above_first(class_info), class_infos))

    return {
        'total_count': total_count,
        'most_user_class': find_most_user_class(class_infos),
        'most_user_non_base_class': find_most_user_non_base_class(non_base_classes_infos),
        'non_base_classes_sorted_by_count': sorted(non_base_classes_infos, key=lambda class_info: class_info['total_count'], reverse=True),
        'non_base_classes_sorted_by_average_level': sorted(non_base_classes_infos, key=lambda class_info: class_info['average_level'], reverse=True),
        'class_info_groups': group_class_infos(class_infos)
    }


def analyze_user_class_raw(class_name, user_infos_of_class):
    # class name
    # total count
    # user max level of this class
    # average level of this class
    print('class_name: %s' % class_name)

    user_infos_of_class_real = list(user_infos_of_class)
    max_level_user = max(user_infos_of_class_real, key=lambda user_info: user_info.user_level)
    total_count = len(user_infos_of_class_real)
    total_level = sum(map(lambda user_info: user_info.user_level, user_infos_of_class_real))

    return {
        'class_name': class_name,
        'total_count': total_count,
        'total_level': total_level,
        'max_level': max_level_user.user_level,
        'max_level_user': max_level_user.user_name,
        'average_level': sum(map(lambda user_info: user_info.user_level, user_infos_of_class_real)) / total_count
    }

def find_most_user_class(class_infos):
    return max(class_infos, key=lambda class_info: class_info['total_count']).get('class_name')


def find_most_user_non_base_class(non_base_classes_infos):
    most_non_base_class_info =  max(non_base_classes_infos, key=lambda class_info: class_info['total_count'])
    return most_non_base_class_info.get('class_name', '')

def is_class_above_first(class_info):
    class_name = class_info['class_name']
    print(class_name)
    return class_name not in base_class_groups

def group_class_infos(class_infos):
    sorted_class_infos = sorted(class_infos, key=lambda class_info: find_user_class_group(class_info['class_name']))
    class_groups = groupby(sorted_class_infos, lambda class_info: find_user_class_group(class_info['class_name']))
    return list(map(lambda item: build_class_groups(item[0], list(item[1])), class_groups))

def find_user_class_group(user_class):
    if user_class == noob:
        return noob

    for group in class_groups:
        if user_class in group:
            return group[0]
    
    return ''

def build_class_groups(class_group_name, class_infos_of_groups):
    max_level_class_info = max(class_infos_of_groups, key=lambda class_info: class_info['max_level'])
    total_count = sum(map(lambda class_info: class_info['total_count'], class_infos_of_groups))
    total_level = sum(map(lambda class_info: class_info['total_level'], class_infos_of_groups))

    return {
        'class_group': class_group_name,
        'total_count': total_count,
        'max_level': max_level_class_info['max_level'],
        'max_level_user': max_level_class_info['max_level_user'],
        'average_level': total_level / total_count,
        'classes': class_infos_of_groups
    }



def main():
    with open('users_response.json', 'r') as src:
        json_dict = json.loads(src.read())
        users = json_dict['users']
        valuable_user_infos = obtain_valuable_user_infos(users)
        analyze_result = analyze_user_infos(valuable_user_infos)
    
        result = {
            'analyze_result': analyze_result,
            'date': json_dict['date'],
            'timestamp': json_dict['timestamp'],
        }
    
        with open('result.json', 'w') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
 

if __name__ == '__main__':
    main()


