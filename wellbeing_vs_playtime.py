# import numpy as np IN CASE NP.LOG IS NEEDED
import pandas as pd
from datetime import date, timedelta
from scipy.signal import savgol_filter

def playtime_2weeks(row, gaming_logs):
    return gaming_logs[(gaming_logs.pid == row.pid) & (row.date - timedelta(days=14) < gaming_logs.session_start) & (gaming_logs.session_start < row.date)].duration.sum()/14

def create_gaming_logs(xbox, steam, nintendo):
    gaming_logs = pd.concat([
        xbox[["pid", "title_id", "session_start", "session_end", ".had_overlap", "duration", "platform"]], 
        steam[["pid", "title_id", "session_start", "session_end", "duration", "playtime_forever", "platform"]],
        nintendo[["pid",	"title_id",	"session_start",	"session_end",	"duration", "platform"]]
    ], ignore_index=True)

    return gaming_logs

def create_users_with_data(survey_biweekly, gaming_logs):
    survey_biweekly["wellbeing_index"] = (((survey_biweekly.life_sat * 4)/10) + 
        40 - (survey_biweekly.promis_1 + survey_biweekly.promis_2 + survey_biweekly.promis_3 + survey_biweekly.promis_4 + 
        survey_biweekly.promis_5 + survey_biweekly.promis_6 + survey_biweekly.promis_7 + survey_biweekly.promis_8) + 
        survey_biweekly.wemwbs_1 + survey_biweekly.wemwbs_2 + survey_biweekly.wemwbs_3 + survey_biweekly.wemwbs_4 +  
        survey_biweekly.wemwbs_5 + survey_biweekly.wemwbs_6 + survey_biweekly.wemwbs_7 - 7)/16 * 10/4
    
    survey_biweekly["playtime_2weeks"] = survey_biweekly.apply(playtime_2weeks, args=(gaming_logs,), axis=1)

    total_playtime_ever_per_pid = gaming_logs.groupby(by="pid").duration.sum().to_dict()
    survey_biweekly["total_playtime_ever"] = survey_biweekly.pid.apply(lambda pid: total_playtime_ever_per_pid.get(pid, 0))
   
    users_with_2weeks_data = survey_biweekly[survey_biweekly.total_playtime_ever > 0]
    
    return users_with_2weeks_data


def import_data(meta, intake, daily, biweekly, xbox, steam, nintendo, **kwargs):
    survey_biweekly = biweekly.copy()
    steam = steam.copy()
    xbox = xbox.copy()
    nintendo = nintendo.copy()
    game_metadata = meta.copy()
    user_info = intake.set_index("pid").to_dict("index")

    steam.rename(columns=
    {
    "approximate_session_start" : "session_start",
    "approximate_session_end" : "session_end",
    "minutes" : "duration"
    }, inplace=True)

    for df in [steam, xbox, nintendo]:
        df.session_start = pd.to_datetime(df.session_start, format="ISO8601")

    survey_biweekly.date = pd.to_datetime(survey_biweekly.date, format="ISO8601")

    xbox["platform"] = xbox.apply(lambda _: 'xbox', axis=1)
    steam["platform"] = steam.apply(lambda _: 'steam', axis=1)
    nintendo["platform"] = nintendo.apply(lambda _: 'nintendo', axis=1)

    return game_metadata, user_info, survey_biweekly, xbox, steam, nintendo 

    # === GRAPH 1 ====
def wellbeing_vs_playtime(meta, intake, daily, biweekly, xbox, steam, nintendo, **kwargs):
    __, _, survey_biweekly, xbox, steam, nintendo = import_data(meta, intake, daily, biweekly, xbox, steam, nintendo)
    gaming_logs = create_gaming_logs(xbox, steam, nintendo)
    users_with_2weeks_data = create_users_with_data(survey_biweekly, gaming_logs)
    users_with_2weeks_data = users_with_2weeks_data[["wellbeing_index", "playtime_2weeks"]]
    
    return users_with_2weeks_data

    # === GRAPH 2 ====
def playtime_spike(meta, intake, daily, biweekly, xbox, steam, nintendo, **kwargs):
    __, _, survey_biweekly, xbox, steam, nintendo = import_data(meta, intake, daily, biweekly, xbox, steam, nintendo)
    gaming_logs = create_gaming_logs(xbox, steam, nintendo)
    per_day_2025 = gaming_logs[(gaming_logs.session_start.dt.date > date(2024, 1, 1)) & (gaming_logs.session_start.dt.date < date(2025, 9, 30))]
    users_with_2weeks_data = create_users_with_data(survey_biweekly, gaming_logs)


    log_and_survey = {}
    for pid in per_day_2025.pid.unique():
        log_and_survey[pid] = True if pid in users_with_2weeks_data.pid.to_list() else False

    per_day_2025["survey"] = per_day_2025.pid.apply(lambda pid: log_and_survey[pid])
    per_day_2025 = per_day_2025[per_day_2025.survey == True]
    per_day_2025 = per_day_2025.groupby(per_day_2025.session_start.dt.date, as_index=False).duration.sum()
    per_day_2025.rename(columns={"duration" : "avg_duration",
                                "session_start" : "date"}, inplace=True)
    
    per_day_2025_smooth = per_day_2025.copy()
    per_day_2025_smooth["avg_duration_smooth"] = savgol_filter(per_day_2025_smooth.avg_duration, 100, 4)
    per_day_2025_smooth.drop(columns=["avg_duration"], inplace=True)

    biweekly_wellbeing = users_with_2weeks_data[["pid", "date", "wellbeing_index"]].reset_index(drop=True)
    biweekly_wellbeing.date = biweekly_wellbeing.date.dt.date
    biweekly_wellbeing = biweekly_wellbeing.groupby("date", as_index=False).wellbeing_index.mean()
    biweekly_wellbeing = biweekly_wellbeing[biweekly_wellbeing.wellbeing_index.notna() == True]

    biweekly_wellbeing_smooth = biweekly_wellbeing.copy()
    biweekly_wellbeing_smooth["wellbeing_index_smooth"] = savgol_filter(biweekly_wellbeing_smooth.wellbeing_index, 100, 6)
    biweekly_wellbeing_smooth.drop(columns=["wellbeing_index"], inplace=True)

    return per_day_2025, per_day_2025_smooth, biweekly_wellbeing, biweekly_wellbeing_smooth

    
