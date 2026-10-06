import pandas as pd
from collections import Counter, defaultdict
from wellbeing_vs_playtime import create_gaming_logs, import_data

def keywords_vs_gender(meta, intake, daily, biweekly, xbox, steam, nintendo, **kwargs):
    
    game_metadata, user_info, _, xbox, steam, nintendo  = import_data(meta, intake, daily, biweekly, xbox, steam, nintendo)
    game_keywords = game_metadata[["original_name", "keywords"]].set_index("original_name").to_dict(orient="dict")

    gaming_logs = create_gaming_logs(xbox, steam, nintendo)
    per_pid = pd.DataFrame(gaming_logs.groupby(["pid", "title_id"], as_index=False).duration.sum())
    per_pid = per_pid[per_pid.duration > 1000] # at least 1000 minutes spent on the game
    per_pid["gender"] = per_pid.pid.apply(lambda pid: user_info[pid]["gender"])
    per_pid["keywords"] = per_pid.title_id.apply(lambda title: game_keywords["keywords"].get(title, 0))
    per_pid = per_pid[per_pid.keywords.notna() == True] # discard any NA values in keywords
    per_pid = per_pid[per_pid.gender.isin(["Man", "Woman", "Non-binary"]) == True].reset_index(drop=True) # only keep top 3 answered values

    gender_keyword = defaultdict(dict)
    keyword_exp = ["male protagonist", "female protagonist", "magic", "cooking", "pvp", "cozy"] # highest tag-word count after award tags

    for keyword in keyword_exp:
        gender_keyword[keyword].update(per_pid.apply(lambda row: row["gender"] if keyword in row["keywords"] else 0, axis=1).value_counts().to_dict())

    gender_keyword_wo_0 = pd.DataFrame(gender_keyword).reset_index().rename(columns={"index" : "gender"})
    gender_keyword_wo_0 = gender_keyword_wo_0[gender_keyword_wo_0.gender != 0]

    return gender_keyword_wo_0
    
