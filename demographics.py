import pandas as pd
from bokeh.plotting import figure
from bokeh.layouts import gridplot
import datetime


def parse_time(s):
    return int(s[0:4]), int(s[5:7]), int(s[8:10]), int(s[11:13]), int(s[14:16])


def get_play_distribution_in_one_platform(player_distribution, data, pid_list, time_adjust):# an empty dict, and a dataframe of one platform's data

    adjust = {}
    for _ in range(len(pid_list)):
        adjust[pid_list[_]] = time_adjust[_]
 
    if 'approximate_session_start' in data.columns:
        start_col, end_col = 'approximate_session_start', 'approximate_session_end'
    else:
        start_col, end_col = 'session_start', 'session_end'

    minutes_col = 'minutes' if 'minutes' in data.columns else None

    pids = data['pid'].tolist()
    starts = data[start_col].tolist()
    ends = data[end_col].tolist()
    mins = data[minutes_col].tolist() if minutes_col is not None else None

    for i in range(len(pids)):
        pid = pids[i]
        y, m, d, h, mi = parse_time(str(starts[i]))
        wd = datetime.date(y, m, d).weekday()

        if mins is not None:
            remaining = float(mins[i])
        else:
            y2, m2, d2, h2, mi2 = parse_time(str(ends[i]))
            remaining = (h2 - h) * 60 + (mi2 - mi)
            if d2 != d:                                 
                remaining += 24 * 60
        h = h + adjust[pid]
        if h < 0:
            h += 24
            wd = (wd - 1) % 7
        elif h >= 24:
            h -= 24
            wd = (wd + 1) % 7

        while remaining > 0:
            chunk = min(60 - mi, remaining)
            week = 1 if wd >= 5 else 0                    
            player_distribution[pid][week][h] += chunk #n(pid)x2x24
            remaining -= chunk
            mi = 0
            h += 1
            if h == 24:
                h = 0
                wd = (wd + 1) % 7
    print(f'dealing:{len(pids)}')
    return player_distribution

def get_distribution_from_geography(all_player, feature, feature_lists, pid_list):
    if feature not in feature_lists:
        print(f"Feature '{feature}' is not supported.")
        return None, None
    this_feature = feature_lists[feature]
    count = {}
    #get top3 feature
    for _ in range(len(pid_list)):
        v = this_feature[_]
        if v is None or str(v) == 'nan':
            continue
        count[v] = count.get(v, 0) + 1
    top3 = sorted(count, key=count.get, reverse=True)[:3]
    result = {c: [[0] * 24, [0] * 24] for c in top3} #3x2x24
    n_player = {c: 0 for c in top3} #the number of players for each feature
    for _ in range(len(pid_list)):
        v = this_feature[_]
        if v not in result:
            continue
        pid = pid_list[_]
        n_player[v] += 1
        for i in range(2):
            for j in range(24):
                result[v][i][j] += all_player[pid][i][j]
    return result, n_player

def demographics(steam, xbox, nintendo, intake, **kwargs):
    xbox = xbox[(xbox['session_start'] >= '2024-11-30') & (xbox['session_start'] < '2025-10-07')]
    nintendo = nintendo[(nintendo['session_start'] >= '2024-11-30') & (nintendo['session_start'] < '2025-10-07')]

    pid_list = []
    time_adjust = []
    country_list = []
    zone_list = []
    gender_list = []
    age_list = []
    marital_status_list = []
    employment_list = []
    care_children_list = []
    for row in steam.itertuples():
        pid_list.append(row.pid) if row.pid not in pid_list else None
    for row in xbox.itertuples():
        pid_list.append(row.pid) if row.pid not in pid_list else None
    for row in nintendo.itertuples():
        pid_list.append(row.pid) if row.pid not in pid_list else None
    for _ in range(len(pid_list)):
        country = intake.loc[intake['pid'] == pid_list[_], 'country'].iloc[0]
        country_list.append(country)
        zone = intake.loc[intake['pid'] == pid_list[_], 'local_timezone'].iloc[0]
        zone_list.append(zone)
        gender = intake.loc[intake['pid'] == pid_list[_], 'gender'].iloc[0]
        gender_list.append(gender)
        age = intake.loc[intake['pid'] == pid_list[_], 'age'].iloc[0]
        age_list.append(age)
        marital_status = intake.loc[intake['pid'] == pid_list[_], 'marital_status'].iloc[0]
        marital_status_list.append(marital_status)
        employment = intake.loc[intake['pid'] == pid_list[_], 'employment'].iloc[0]
        employment_list.append(employment)
        care_children = intake.loc[intake['pid'] == pid_list[_], 'care_children'].iloc[0]
        care_children_list.append(care_children)

    hours = list(range(24))
    dashes = ['solid', 'dashed', 'dotted']
    greys = ['black', 'dimgray', 'darkgray']
    Y_MAX = 10

    time_adjust = []
    for _ in range(len(pid_list)):
        if country_list[_] == 'UK':
            time_adjust.append(0)
        elif str(zone_list[_])[0:3] == 'GMT':
                time_adjust.append(int(str(zone_list[_])[3:6]))
        elif country_list[_] == 'US':
                time_adjust.append(int(-6))
        else:
                time_adjust.append(pd.NA)


    platform_distribution = {} # 3x2x24
    all_player = {pid: [[0] * 24, [0] * 24] for pid in pid_list} #the average time in this hour for all players pid x 2 x 24
    for name, data in [('steam', steam), ('xbox', xbox), ('nintendo', nintendo)]:
        one = {pid: [[0] * 24, [0] * 24] for pid in pid_list}#prepara for the empty dict 
        one = get_play_distribution_in_one_platform(one, data, pid_list, time_adjust ) #'pid' x 2 x 24
        #the period of each player
        col = 'approximate_session_start' if 'approximate_session_start' in data.columns else 'session_start'
        first = data.groupby('pid')[col].min()
        last = data.groupby('pid')[col].max()
        days = {}
        for pid in first.index:#the key
            y1, m1, d1, h1, mi1 = parse_time(first[pid])
            y2, m2, d2, h2, mi2 = parse_time(last[pid])
            days[pid] = (datetime.date(y2, m2, d2) - datetime.date(y1, m1, d1)).days + 1

        total = [[0] * 24, [0] * 24]
        for pid in one:
            if pid not in days:
                continue
            for i in range(2):
                for j in range(24):
                    v = one[pid][i][j] / days[pid] 
                    total[i][j] += v
                    all_player[pid][i][j] += v
        platform_distribution[name] = total

    age_group_list = []
    for a in age_list:
        if str(a) == 'nan':
            age_group_list.append(None)
        elif int(a) <= 24:
            age_group_list.append('18-24')
        elif int(a) <= 29:
            age_group_list.append('25-29')
        else:
            age_group_list.append('30+')

    feature_lists = {
        'country': country_list,
        'gender': gender_list,
        'age': age_group_list,
        'marital_status': marital_status_list,
        'employment': employment_list,
        'care_children': care_children_list,
    }
    geo_distribution = {}   
    geo_count = {}          
    for feature in feature_lists:
        geo_distribution[feature], geo_count[feature] = get_distribution_from_geography(all_player, feature, feature_lists, pid_list)

    platform_24 = {}
    for platform_name in platform_distribution:
        platform_24[platform_name] = []
        for j in range(24):
            platform_24[platform_name].append(platform_distribution[platform_name][0][j] + platform_distribution[platform_name][1][j])

    geo_24={}
    for feature_name in geo_distribution:
        geo_24[feature_name]={}
        for c in geo_distribution[feature_name]:
            geo_24[feature_name][c] = []
            for j in range(24):
                geo_24[feature_name][c].append(geo_distribution[feature_name][c][0][j] + geo_distribution[feature_name][c][1][j])

    all_player = {pid: [[0] * 24, [0] * 24] for pid in pid_list} #the average time in this hour for all players pid x 2 x 24
    for name, data in [('steam', steam), ('xbox', xbox), ('nintendo', nintendo)]:
        one = {pid: [[0] * 24, [0] * 24] for pid in pid_list}#prepara for the empty dict 
        one = get_play_distribution_in_one_platform(one, data, pid_list, time_adjust) #'pid' x 2 x 24
        #the period of each player
        col = 'approximate_session_start' if 'approximate_session_start' in data.columns else 'session_start'
        first = data.groupby('pid')[col].min()
        last = data.groupby('pid')[col].max()
        days = {}
        for pid in first.index:#the key
            y1, m1, d1, h1, mi1 = parse_time(first[pid])
            y2, m2, d2, h2, mi2 = parse_time(last[pid])
            days[pid] = (datetime.date(y2, m2, d2) - datetime.date(y1, m1, d1)).days + 1

        total = [[0] * 24, [0] * 24]
        for pid in one:
            if pid not in days:
                continue
            for i in range(2):
                for j in range(24):
                    v = one[pid][i][j] / days[pid] 
                    total[i][j] += v
                    all_player[pid][i][j] += v
        platform_distribution[name] = total

    no_kid = [0] * 24
    no_kid_n = 0
    for _ in range(len(pid_list)):
        if str(care_children_list[_]) == 'nan':
            no_kid_n += 1
            for j in range(24):
                no_kid[j] += all_player[pid_list[_]][0][j] + all_player[pid_list[_]][1][j]
    geo_24['care_children']['No children'] = no_kid
    geo_count['care_children']['No children'] = no_kid_n

    platform_n = {'steam': steam['pid'].nunique(), 'xbox': xbox['pid'].nunique(), 'nintendo': nintendo['pid'].nunique()}

    panels = {}
    p = figure(title='Platform', x_axis_label='Hour (local)', y_axis_label='Minutes per player per day',
            y_range=(0, Y_MAX),
            tooltips=[('hour', '$x{0}'), ('minutes', '$y{0.0}')])
    k = 0
    for name in platform_24:
        y = []
        for j in range(24):
            y.append(platform_24[name][j] / platform_n[name])
        p.line(hours, y, legend_label=f'{name} (n={platform_n[name]})',
            line_dash=dashes[k], color=greys[k], line_width=2)
        k += 1
    p.legend.location = 'top_left'
    p.legend.click_policy = 'hide'
    p.legend.label_text_font_size = '8pt'
    panels['platform'] = p

    for feature in ['care_children', 'gender', 'employment']:
        p = figure(title=feature, x_axis_label='Hour (local)', y_axis_label='Minutes per player per day',
                y_range=(0, Y_MAX),
                tooltips=[('hour', '$x{0}'), ('minutes', '$y{0.0}')])
        k = 0
        for c in geo_24[feature]:
            n = geo_count[feature][c]
            y = []
            for j in range(24):
                y.append(geo_24[feature][c][j] / n)
            p.line(hours, y, legend_label=f'{c} (n={n})',
                line_dash=dashes[k], color=greys[k], line_width=2)
            k += 1
        p.legend.location = 'top_left'
        p.legend.click_policy = 'hide'
        p.legend.label_text_font_size = '8pt'
        panels[feature] = p

    plots = [panels['platform'], panels['gender'], panels['employment'], panels['care_children']]
    grid = gridplot(plots, ncols=2, width=600, height=400)

    return grid