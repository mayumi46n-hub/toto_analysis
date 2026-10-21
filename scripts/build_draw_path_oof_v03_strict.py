import pandas as pd,numpy as np,glob,os
from sklearn.linear_model import LogisticRegression

OUT="data/evaluation/draw_path_oof_2020_2025_v03_strict.csv"

PREDICTION_FILES = ["data/evaluation/footystats_walkforward_2019_2024_predictions_20260830_v1.csv", "data/evaluation/footystats_2025_oos_predictions_20260830_v1.csv"]

A=[]
for f in PREDICTION_FILES:
    x=pd.read_csv(f)
    k=["jleague_match_id","match_date","home_team_name","away_team_name",
       "target_toto","core4_p_home","core4_p_draw","core4_p_away",
       "market_p_home","market_p_away"]
    if not all(c in x for c in k): continue
    x=x[k].copy()
    x["year"]=pd.to_datetime(x.match_date).dt.year
    x["match_date"]=pd.to_datetime(x.match_date).dt.date
    A.append(x)
p=pd.concat(A,ignore_index=True)

B=[]
for f in glob.glob("data/footystats/csv/20*/J[123]/*-matches-*.csv"):
    x=pd.read_csv(f)
    k=["date_GMT","home_team_name","away_team_name","odds_ft_over25"]
    if not all(c in x for c in k): continue
    x=x[k].copy()
    x["match_date"]=pd.to_datetime(
        x.date_GMT.str.split(" - ").str[0],errors="coerce").dt.date
    B.append(x)
m=pd.concat(B,ignore_index=True)

key=["match_date","home_team_name","away_team_name"]
d=p.merge(m,on=key)
d["ou_over25_odds"]=pd.to_numeric(
    d.odds_ft_over25,errors="coerce").replace(0,np.nan)
d=d[d.ou_over25_odds.notna()].copy()

P=d[["core4_p_home","core4_p_away"]].to_numpy()
fav=np.where(P[:,0]>=P[:,1],1,2)
d["favorite"]=fav
d["favorite_confidence"]=P.max(1)
d["market_opposition"]=np.where(
    fav==1,d.market_p_away>d.market_p_home,
    d.market_p_home>d.market_p_away).astype(int)

actual=d.target_toto.map({0:1,1:0,2:2}).to_numpy()
d["actual"]=actual
d["actual_draw"]=(actual==0).astype(int)
d["favorite_fail"]=(actual!=fav).astype(int)

eps=1e-5
logit=lambda x:np.log(np.clip(x,eps,1-eps)/(1-np.clip(x,eps,1-eps)))

def temporal_blocks(tr):
    dates=np.array(sorted(tr.match_date.unique()))
    blocks=np.array_split(dates,4)
    assert all(len(b)>0 for b in blocks)
    return blocks

def fit_predict_ab(train,valid):
    ma=LogisticRegression(max_iter=1000).fit(train[["favorite_confidence","market_opposition"]],train["favorite_fail"])
    tb=train[train.favorite_fail==1].copy()
    tb["ouc"]=tb["ou_over25_odds"]-2.0
    tb["ou_mopp_int"]=tb["ouc"]*tb["market_opposition"]
    va=valid.copy()
    va["ouc"]=va["ou_over25_odds"]-2.0
    va["ou_mopp_int"]=va["ouc"]*va["market_opposition"]
    bx=["ouc","market_opposition","ou_mopp_int"]
    mb=LogisticRegression(C=1e6,max_iter=1000).fit(tb[bx],tb["actual_draw"])
    va["pf"]=ma.predict_proba(va[["favorite_confidence","market_opposition"]])[:,1]
    va["pb"]=mb.predict_proba(va[bx])[:,1]
    va["path"]=va.pf*va.pb
    return va

def make_inner_oof(tr):
    blocks=temporal_blocks(tr)
    parts=[]
    for i in range(1,4):
        valid=tr[tr.match_date.isin(blocks[i])].copy()
        train=tr[tr.match_date<blocks[i][0]].copy()
        assert train.match_date.max()<valid.match_date.min()
        parts.append(fit_predict_ab(train,valid))
    z=pd.concat(parts,ignore_index=True)
    assert not z[["pf","pb","path"]].isna().any().any()
    return z

O=[]
for y in range(2020,2026):
    tr=d[d.year<y].copy()
    te=d[d.year==y].copy()

    inner=make_inner_oof(tr)
    inner["lc"]=logit(inner.core4_p_draw)
    inner["lp"]=logit(inner.path)

    mc=LogisticRegression(max_iter=1000).fit(inner[["lc"]],inner.actual_draw)
    mp=LogisticRegression(max_iter=1000).fit(inner[["lc","lp"]],inner.actual_draw)

    te=fit_predict_ab(tr,te)
    te["p_favorite_fail"]=te["pf"]
    te["p_draw_given_fail"]=te["pb"]
    te["draw_path"]=te["path"]
    te["path_residual"]=te.draw_path-te.core4_p_draw
    te["lc"]=logit(te.core4_p_draw)
    te["lp"]=logit(te.draw_path)

    te["p_draw_corecal"]=mc.predict_proba(te[["lc"]])[:,1]
    te["p_draw_pathcal"]=mp.predict_proba(te[["lc","lp"]])[:,1]
    te["path_meta_coef"]=mp.coef_[0,1]
    te["oof_test_year"]=y
    O.append(te)

o=pd.concat(O,ignore_index=True)

keep=["jleague_match_id","match_date","year","home_team_name","away_team_name",
      "actual","actual_draw","favorite","favorite_fail",
      "favorite_confidence","market_opposition","ou_over25_odds",
      "core4_p_draw","p_favorite_fail","p_draw_given_fail",
      "draw_path","path_residual","p_draw_corecal","p_draw_pathcal",
      "path_meta_coef","oof_test_year"]

os.makedirs(os.path.dirname(OUT),exist_ok=True)
o[keep].to_csv(OUT,index=False)

print("OUT",OUT)
print("ROWS",len(o),"YEARS",o.year.value_counts().sort_index().to_dict())
print("NULL",int(o[keep].isna().sum().sum()))
print("OOF_YEAR_OK",bool((o.year==o.oof_test_year).all()))
print("PATH_COEF_POS",o.groupby("year").path_meta_coef.first().gt(0).sum(),"/6")
print("STEP 16aw: PASS")
