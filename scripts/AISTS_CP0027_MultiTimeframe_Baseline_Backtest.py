#!/usr/bin/env python3
"""
AISTS CP-0027: Gap-aware, deterministic baseline backtest on CP-0026 candidate datasets.
Google Colab, single-cell execution. No downloads, no API keys, no orders, no strategy optimization.

Data source:
  MyDrive/AISTS/market_data/binance_spot/BTCUSDT/derived/research_candidate_v1/BTCUSDT/intervals/

Fixed strategies (long-only Spot, no leverage or shorting):
  - EMA trend regime 12/26
  - RSI(14) mean-reversion: enter <=30, exit >=55
  - Donchian breakout: close > prior 20-bar high to enter, close < prior 10-bar low to exit
Benchmarks:
  - Buy and hold
  - Cash/no trade

Execution policy:
  - Decisions use completed candle data only.
  - Signals execute at next bar's OPEN only when it is the expected contiguous next interval.
  - If the next candle is missing, the pending order is skipped (not fabricated).
  - Indicators reset at gaps; existing spot exposure is carried through gaps and marked at the next observed prices.
  - If a position remains open at a split's last row, it is liquidated at the last CLOSE including modeled slippage and fee.
  - Gaps are reported, not interpolated.
Costs:
  - Assumed taker fee: 10 bps per side, not verified against the user's account.
  - Slippage sensitivity: 0 / 5 / 10 bps per side, reported OOS. 5 bps is the default across all periods.
Evaluation periods:
  - Train/research: before 2023-01-01
  - Validation: 2023-01-01 to before 2025-01-01
  - Out-of-sample (OOS): 2025-01-01 to 2026-10-01 UTC
Parameters are fixed ex ante; no parameter search or selection on OOS is performed.
"""
from __future__ import annotations

import csv, gc, gzip, hashlib, json, os, zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

SYMBOL = "BTCUSDT"
INTERVALS = ["5m", "15m", "30m", "1h", "4h", "1d", "1mo"]
ROOT = Path("/content/drive/MyDrive/AISTS/market_data/binance_spot/BTCUSDT")
CANDIDATE_DIR = ROOT / "derived" / "research_candidate_v1" / SYMBOL / "intervals"
REPORT_DIR = ROOT / "reports"
RESULT_DIR = ROOT / "derived" / "research_candidate_v1" / SYMBOL / "backtest_cp0027"
INITIAL_CAPITAL = 10_000.0
FEE_BPS_PER_SIDE = 10.0  # Assumption for research; not user's verified tier/rate.
DEFAULT_SLIPPAGE_BPS = 5.0
OOS_SLIPPAGE_SCENARIOS = [0.0, 5.0, 10.0]
TRAIN_END = pd.Timestamp("2023-01-01T00:00:00Z")
OOS_START = pd.Timestamp("2025-01-01T00:00:00Z")
OOS_END = pd.Timestamp("2026-10-01T00:00:00Z")
STEP_MS = {"5m":300_000, "15m":900_000, "30m":1_800_000, "1h":3_600_000, "4h":14_400_000, "1d":86_400_000}
CSV_COLUMNS = [
    "open_time_ms","open","high","low","close","volume",
    "source_type","source_archive","source_sha256","close_time_ms","close_time_normalized",
    "aggregation_bar_count","partial_calendar_month"
]
STRATEGIES = ["EMA_12_26", "RSI14_30_55", "DONCHIAN20_10"]
PERIODS = ["TRAIN", "VALIDATION", "OOS"]

def now_utc():
    return datetime.now(timezone.utc).isoformat()

def get_root():
    try:
        import google.colab  # noqa: F401
        from google.colab import drive
        if not Path("/content/drive/MyDrive").exists():
            from google.colab import drive as colab_drive
            colab_drive.mount("/content/drive")
        if not Path("/content/drive/MyDrive").exists():
            raise RuntimeError("Google Drive is not mounted at /content/drive/MyDrive")
        return ROOT
    except ImportError:
        fallback=Path(os.environ.get("AISTS_DATA_ROOT","/content/AISTS/market_data/binance_spot/BTCUSDT"))
        print("Colab not detected; using local fallback:",fallback)
        return fallback

def sha256_file(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def write_dict_csv(path, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:
        path.write_text("status,no_rows\nPASS,0\n",encoding="utf-8")
        return
    columns=[]
    seen=set()
    for row in rows:
        for k in row:
            if k not in seen:
                seen.add(k); columns.append(k)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=columns,extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)

def load_candidate(root, interval, manifest):
    expected=manifest["results"][interval]
    path=root / "derived" / "research_candidate_v1" / SYMBOL / "intervals" / f"{SYMBOL}-{interval}-research-candidate.csv.gz"
    if not path.exists():
        raise FileNotFoundError(f"Candidate data missing: {path}. Run CP-0026 first.")
    actual_sha=sha256_file(path)
    if actual_sha.lower()!=str(expected["sha256"]).lower():
        raise RuntimeError(f"Candidate SHA256 mismatch for {interval}: {actual_sha} != {expected['sha256']}")
    usecols=[c for c in CSV_COLUMNS if c in pd.read_csv(path,compression="gzip",nrows=0).columns]
    df=pd.read_csv(path,compression="gzip",usecols=usecols,low_memory=False)
    if len(df)!=int(expected["candidate_rows"]):
        raise RuntimeError(f"Candidate row-count mismatch for {interval}: {len(df)} != {expected['candidate_rows']}")
    df["open_time_ms"]=pd.to_numeric(df["open_time_ms"],errors="raise").astype("int64")
    for col in ("open","high","low","close","volume"):
        df[col]=pd.to_numeric(df[col],errors="raise").astype("float64")
    # Check file order BEFORE any sort, so malformed ordering cannot be hidden by normalization.
    if df["open_time_ms"].duplicated().any():
        raise RuntimeError(f"Candidate has duplicate open times for {interval}")
    if not df["open_time_ms"].is_monotonic_increasing:
        raise RuntimeError(f"Candidate open times not strictly increasing for {interval}")
    df=df.reset_index(drop=True)
    if "close_time_ms" in df.columns:
        df["close_time_ms"]=pd.to_numeric(df["close_time_ms"],errors="raise").astype("int64")
        opens_ms=df["open_time_ms"].to_numpy(dtype=np.int64)
        closes_ms=df["close_time_ms"].to_numpy(dtype=np.int64)
        if interval in STEP_MS:
            expected_closes=opens_ms+STEP_MS[interval]-1
        else:
            open_dt=pd.to_datetime(opens_ms,unit="ms",utc=True)
            next_month=(open_dt+pd.offsets.MonthBegin(1))
            expected_closes=(next_month.astype("int64")//1_000_000)-1
        if not np.array_equal(closes_ms,expected_closes):
            wrong=int(np.sum(closes_ms!=expected_closes))
            raise RuntimeError(f"Candidate close_time validation failed for {interval}: {wrong} rows do not match the declared interval boundary")
    # Monthly first bar (Aug 2017) is partial because BTCUSDT data starts mid-month.
    partial_excluded=0
    if interval=="1mo" and "partial_calendar_month" in df.columns:
        part=df["partial_calendar_month"].astype(str).str.lower().isin(["true","1","yes"])
        partial_excluded=int(part.sum())
        df=df.loc[~part].copy().reset_index(drop=True)
    if len(df)<40 and interval=="1mo":
        print("WARNING: monthly sample is small; statistical confidence will be limited.")
    return df, {"interval":interval,"file":str(path),"sha256":actual_sha,
                "rows_in_manifest":int(expected["candidate_rows"]),
                "rows_used":len(df),"partial_month_rows_excluded":partial_excluded,
                "first_open_time_utc":pd.to_datetime(df["open_time_ms"].iloc[0],unit="ms",utc=True).isoformat(),
                "last_open_time_utc":pd.to_datetime(df["open_time_ms"].iloc[-1],unit="ms",utc=True).isoformat(),
                "source_types":{str(k):int(v) for k,v in df["source_type"].value_counts(dropna=False).to_dict().items()} if "source_type" in df.columns else {}}

def add_features(df, interval):
    """Indicators are computed only within consecutive-candle segments."""
    out=df.copy()
    step=STEP_MS.get(interval)
    if step is None: # Calendar month interval
        # Monthly candles are calendar-aligned; use calendar-open boundary, not fixed milliseconds.
        opens=pd.to_datetime(out["open_time_ms"],unit="ms",utc=True)
        out["contiguous"]=opens.dt.to_period("M").astype(str).shift(1).eq(opens.dt.to_period("M").astype(str)) if False else True
        # 1mo is derived with one row per calendar month; segment on actual calendar succession.
        dates=opens.dt.year*12+opens.dt.month
        diffs=dates.diff()
        contig=diffs.eq(1)
    else:
        times=out["open_time_ms"].to_numpy(dtype=np.int64)
        contig=np.zeros(len(out),dtype=bool)
        if len(out)>1:
            contig[1:]=np.diff(times)==step
    out["contiguous"]=np.asarray(contig,dtype=bool)
    breaks=~out["contiguous"].to_numpy(dtype=bool)
    if len(breaks): breaks[0]=True
    out["segment_id"]=np.cumsum(breaks).astype(np.int32)
    g=out.groupby("segment_id",sort=False)
    out["ema_fast"]=g["close"].transform(lambda s:s.ewm(span=12,adjust=False,min_periods=12).mean())
    out["ema_slow"]=g["close"].transform(lambda s:s.ewm(span=26,adjust=False,min_periods=26).mean())
    diff=g["close"].diff()
    gain=diff.clip(lower=0)
    loss=(-diff).clip(lower=0)
    avg_gain=gain.groupby(out["segment_id"],sort=False).transform(lambda s:s.ewm(alpha=1/14,adjust=False,min_periods=14).mean())
    avg_loss=loss.groupby(out["segment_id"],sort=False).transform(lambda s:s.ewm(alpha=1/14,adjust=False,min_periods=14).mean())
    rs=avg_gain/avg_loss.replace(0,np.nan)
    out["rsi14"]=100-(100/(1+rs))
    out.loc[(avg_loss==0)&(avg_gain>0),"rsi14"]=100.0
    out.loc[(avg_gain==0)&(avg_loss>0),"rsi14"]=0.0
    out.loc[(avg_gain==0)&(avg_loss==0),"rsi14"]=50.0
    out["prior_high20"]=g["high"].transform(lambda s:s.shift(1).rolling(20,min_periods=20).max())
    out["prior_low10"]=g["low"].transform(lambda s:s.shift(1).rolling(10,min_periods=10).min())
    return out

def metrics_from_equity(equity, start_ms, end_ms):
    if len(equity)==0:
        return {"initial_equity":INITIAL_CAPITAL,"final_equity":INITIAL_CAPITAL,"total_return_pct":0.0,
                "cagr_pct":None,"max_drawdown_pct":0.0,"equity_points":0}
    # Include the initial account value so entry fees/slippage count toward drawdown from the start.
    curve=np.concatenate(([float(INITIAL_CAPITAL)], np.asarray(equity,dtype=np.float64)))
    peaks=np.maximum.accumulate(curve)
    dd=np.where(peaks>0,curve/peaks-1,0.0)
    final=float(curve[-1])
    duration_years=max((end_ms-start_ms)/1000.0/(365.2425*24*3600),0.0)
    cagr=((final/INITIAL_CAPITAL)**(1/duration_years)-1)*100 if duration_years>0 and final>0 else None
    return {
        "initial_equity":INITIAL_CAPITAL,"final_equity":final,
        "total_return_pct":(final/INITIAL_CAPITAL-1)*100,
        "cagr_pct":cagr,"max_drawdown_pct":float(np.min(dd))*100,
        "equity_points":len(curve)
    }

def simulate_strategy(df, interval, start_idx, end_idx, strategy, fee_bps, slippage_bps, trade_log=False):
    """
    Causal spot backtest for one time window. Indicators already calculated without looking forward.
    Signals are created at close i and filled at open i+1 only if timestamps are contiguous.
    """
    if end_idx-start_idx < 2:
        return {"status":"INSUFFICIENT_BARS","trade_log":[]}
    step=STEP_MS.get(interval)
    t=df["open_time_ms"].to_numpy(dtype=np.int64)
    op=df["open"].to_numpy(dtype=np.float64)
    hi=df["high"].to_numpy(dtype=np.float64)
    lo=df["low"].to_numpy(dtype=np.float64)
    cl=df["close"].to_numpy(dtype=np.float64)
    emaf=df["ema_fast"].to_numpy(dtype=np.float64)
    emas=df["ema_slow"].to_numpy(dtype=np.float64)
    rsi=df["rsi14"].to_numpy(dtype=np.float64)
    ph=df["prior_high20"].to_numpy(dtype=np.float64)
    pl=df["prior_low10"].to_numpy(dtype=np.float64)
    contiguous=df["contiguous"].to_numpy(dtype=bool)
    fee_rate=fee_bps/10000.0
    slip_rate=slippage_bps/10000.0
    cash=float(INITIAL_CAPITAL); qty=0.0
    pending=None
    entry_cost=None; entry_time=None; entry_price=None
    fees_paid=0.0; slippage_paid=0.0; total_buys=0; total_sells=0; closed_pnls=[]
    trades=[]
    equity=[]
    interval_days=[]
    for i in range(start_idx,end_idx):
        # Execute the prior completed candle's signal at this candle's open only if contiguous.
        if i>start_idx and contiguous[i] and pending is not None:
            target=pending
            if target==1 and qty<=0 and cash>1e-9:
                ref=op[i]; fill=ref*(1+slip_rate)
                qty=cash/(fill*(1+fee_rate))
                notion=qty*fill; fee=notion*fee_rate
                fees_paid+=fee; slippage_paid+=max(0.0,fill-ref)*qty
                entry_cost=notion+fee; entry_time=int(t[i]); entry_price=fill
                cash=max(0.0,cash-notion-fee); total_buys+=1
            elif target==0 and qty>0:
                ref=op[i]; fill=ref*(1-slip_rate)
                notion=qty*fill; fee=notion*fee_rate; net=notion-fee
                fees_paid+=fee; slippage_paid+=max(0.0,ref-fill)*qty
                pnl=net-(entry_cost if entry_cost is not None else 0.0)
                closed_pnls.append(pnl); total_sells+=1
                if trade_log:
                    trades.append({"strategy":strategy,"entry_time_utc":pd.to_datetime(entry_time,unit="ms",utc=True).isoformat(),
                                   "exit_time_utc":pd.to_datetime(t[i],unit="ms",utc=True).isoformat(),
                                   "entry_fill":entry_price,"exit_fill":fill,"net_trade_pnl":pnl,
                                   "exit_type":"strategy_signal","fee_bps_per_side":fee_bps,"slippage_bps_per_side":slippage_bps})
                qty=0.0; cash+=net; entry_cost=entry_time=entry_price=None
        pending=None
        # Equity marked at each bar close. If still invested through a gap, the new close captures the price change.
        current_equity=cash+qty*cl[i]
        # Final forced liquidation for measuring a closed-window result.
        if i==end_idx-1 and qty>0:
            ref=cl[i]; fill=ref*(1-slip_rate)
            notion=qty*fill; fee=notion*fee_rate; net=notion-fee
            fees_paid+=fee; slippage_paid+=max(0.0,ref-fill)*qty
            pnl=net-(entry_cost if entry_cost is not None else 0.0)
            closed_pnls.append(pnl); total_sells+=1; cash+=net; qty=0.0
            current_equity=cash
            if trade_log:
                trades.append({"strategy":strategy,"entry_time_utc":pd.to_datetime(entry_time,unit="ms",utc=True).isoformat(),
                               "exit_time_utc":pd.to_datetime(t[i],unit="ms",utc=True).isoformat(),
                               "entry_fill":entry_price,"exit_fill":fill,"net_trade_pnl":pnl,
                               "exit_type":"window_end_liquidation","fee_bps_per_side":fee_bps,"slippage_bps_per_side":slippage_bps})
            entry_cost=entry_time=entry_price=None
        equity.append(current_equity)
        if i+1>=end_idx or not contiguous[i+1]:
            pending=None
            continue
        # Decide at the current completed close, for the next open.
        in_position=qty>0
        if strategy=="EMA_12_26":
            if np.isfinite(emaf[i]) and np.isfinite(emas[i]):
                if not in_position and emaf[i]>emas[i]: pending=1
                elif in_position and emaf[i]<=emas[i]: pending=0
        elif strategy=="RSI14_30_55":
            if np.isfinite(rsi[i]):
                if not in_position and rsi[i]<=30: pending=1
                elif in_position and rsi[i]>=55: pending=0
        elif strategy=="DONCHIAN20_10":
            if not in_position and np.isfinite(ph[i]) and cl[i]>ph[i]: pending=1
            elif in_position and np.isfinite(pl[i]) and cl[i]<pl[i]: pending=0
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    met=metrics_from_equity(equity,int(t[start_idx]),int(t[end_idx-1]))
    return {
        "status":"OK","strategy":strategy,"fee_bps_per_side":fee_bps,"slippage_bps_per_side":slippage_bps,
        **met,"closed_trades":len(closed_pnls),"buy_fills":total_buys,"sell_fills":total_sells,
        "win_rate_pct":(sum(p>0 for p in closed_pnls)/len(closed_pnls)*100) if closed_pnls else None,
        "net_realized_pnl":float(sum(closed_pnls)),"fees_paid":fees_paid,"estimated_slippage_cost":slippage_paid,
        "trade_log":trades
    }

def simulate_benchmark(df, start_idx, end_idx, name, fee_bps, slippage_bps):
    t=df["open_time_ms"].to_numpy(dtype=np.int64)
    op=df["open"].to_numpy(dtype=np.float64); cl=df["close"].to_numpy(dtype=np.float64)
    fee=fee_bps/10000.0; slip=slippage_bps/10000.0
    if name=="CASH":
        return {"status":"OK","strategy":"CASH","fee_bps_per_side":fee_bps,"slippage_bps_per_side":slippage_bps,
                **metrics_from_equity([INITIAL_CAPITAL]*(end_idx-start_idx),int(t[start_idx]),int(t[end_idx-1])),
                "closed_trades":0,"buy_fills":0,"sell_fills":0,"win_rate_pct":None,
                "net_realized_pnl":0.0,"fees_paid":0.0,"estimated_slippage_cost":0.0,"trade_log":[]}
    buy_ref=op[start_idx]; buy_fill=buy_ref*(1+slip)
    qty=INITIAL_CAPITAL/(buy_fill*(1+fee))
    buy_notional=qty*buy_fill; buy_fee=buy_notional*fee
    entry_cost=buy_notional+buy_fee
    fee_total=buy_fee
    slip_cost=max(0,buy_fill-buy_ref)*qty
    eq=[]
    for i in range(start_idx,end_idx):
        if i<end_idx-1:
            eq.append(qty*cl[i])
        else:
            sell_ref=cl[i]; sell_fill=sell_ref*(1-slip)
            sell_notional=qty*sell_fill; sell_fee=sell_notional*fee
            net=sell_notional-sell_fee
            fee_total+=sell_fee; slip_cost+=max(0,sell_ref-sell_fill)*qty
            eq.append(net)
    final=eq[-1] if eq else INITIAL_CAPITAL
    met=metrics_from_equity(eq,int(t[start_idx]),int(t[end_idx-1]))
    return {"status":"OK","strategy":"BUY_AND_HOLD","fee_bps_per_side":fee_bps,"slippage_bps_per_side":slippage_bps,
            **met,"closed_trades":1,"buy_fills":1,"sell_fills":1,
            "win_rate_pct":(100.0 if final-entry_cost>0 else 0.0),
            "net_realized_pnl":float(final-entry_cost),"fees_paid":fee_total,"estimated_slippage_cost":slip_cost,"trade_log":[]}

def get_slice(df, period):
    ts=pd.to_datetime(df["open_time_ms"],unit="ms",utc=True)
    if period=="TRAIN":
        mask=ts<TRAIN_END
    elif period=="VALIDATION":
        mask=(ts>=TRAIN_END)&(ts<OOS_START)
    elif period=="OOS":
        mask=(ts>=OOS_START)&(ts<OOS_END)
    else: raise ValueError(period)
    idx=np.flatnonzero(mask.to_numpy())
    return (int(idx[0]),int(idx[-1])+1) if len(idx)>=2 else None

def result_row(interval, period, stats):
    row={"interval":interval,"period":period}
    for k,v in stats.items():
        if k!="trade_log": row[k]=v
    return row

def summarize_data_quality(df, interval, meta):
    step=STEP_MS.get(interval)
    times=df["open_time_ms"].to_numpy(dtype=np.int64)
    diffs=np.diff(times)
    if step:
        gaps=diffs>step
        missing=int(np.sum(np.maximum(0,diffs[gaps]//step-1)))
        nonintegral=int(np.sum(diffs[gaps]%step!=0))
    else:
        opens=pd.to_datetime(times,unit="ms",utc=True)
        periods=np.asarray(opens.year*12+opens.month)
        dd=np.diff(periods)
        gaps=dd>1
        missing=int(np.sum(np.maximum(0,dd[gaps]-1)))
        nonintegral=0
    return {
        "interval":interval,"rows_used":len(df),"candidate_sha256":meta["sha256"],
        "gaps_events":int(np.sum(gaps)),"estimated_missing_intervals":missing,
        "non_integral_gaps":nonintegral,
        "off_grid_rows":int(np.sum(df["open_time_ms"].to_numpy(dtype=np.int64)%step!=0)) if step else 0,
        "source_type_counts":json.dumps(meta.get("source_types",{}),ensure_ascii=False),
        "partial_months_excluded":meta.get("partial_month_rows_excluded",0),
        "first_time":meta["first_open_time_utc"],"last_time":meta["last_open_time_utc"]
    }

def main():
    from g0_execution_guard import require_authenticated_g0
    require_authenticated_g0("cp0027_baseline_backtest")
    root=get_root()
    candidate_dir=root/"derived"/"research_candidate_v1"/SYMBOL/"intervals"
    result_dir=root/"derived"/"research_candidate_v1"/SYMBOL/"backtest_cp0027"
    report_dir=root/"reports"
    manifest_path=report_dir/"cp0026_research_candidate_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"CP-0026 manifest missing: {manifest_path}. Run CP-0026 first.")
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    result_dir.mkdir(parents=True,exist_ok=True); report_dir.mkdir(parents=True,exist_ok=True)
    all_results=[]; quality=[]; oos_sensitivity=[]; primary_trade_logs=[]
    assumptions={
        "project":"AISTS CP-0027",
        "symbol":"BTCUSDT","market":"Binance Spot",
        "initial_equity_usdt":INITIAL_CAPITAL,
        "fee_bps_per_side":FEE_BPS_PER_SIDE,
        "fee_rate_note":"Assumption only; not verified against user's Binance account tier/BNB fee settings.",
        "slippage_scenarios_bps_per_side":[0.0,5.0,10.0],
        "default_slippage_bps_per_side":DEFAULT_SLIPPAGE_BPS,
        "leverage":1,"short_selling":False,"long_only":True,
        "signals":"Computed at completed close; fill at next contiguous candle open.",
        "gap_policy":"Never interpolate. Indicators reset at gaps. Signals are not filled across a data gap. Existing spot position is held across a gap and marked at next observed prices.",
        "periods":{
            "TRAIN":"start of available history to before 2023-01-01 UTC",
            "VALIDATION":"2023-01-01 UTC to before 2025-01-01 UTC",
            "OOS":"2025-01-01 UTC to before 2026-10-01 UTC"
        },
        "strategies":{
            "EMA_12_26":"Long when EMA(12)>EMA(26); exit when EMA(12)<=EMA(26).",
            "RSI14_30_55":"Long entry when RSI(14)<=30; exit when RSI(14)>=55.",
            "DONCHIAN20_10":"Long entry when close > prior 20-bar high; exit when close < prior 10-bar low."
        },
        "benchmark":"Buy-and-hold, with entry at first open and window-end sale at last close including fee/slippage; Cash/no trade.",
        "optimization":"None. Fixed ex ante parameters; do not tune based on OOS results.",
        "monthly_partial_bar":"First partial month excluded from 1mo backtest (BTCUSDT data begins mid-August 2017).",
        "limitations":[
            "Candidate dataset is provisional and uses day-level daily-archive overrides on flagged dates.",
            "Time gaps remain. No candles are synthesized.",
            "This baseline is a research diagnostic, not proof of future profitability.",
            "No actual account commission or live order execution tests included."
        ]
    }
    (result_dir/"assumptions.json").write_text(json.dumps(assumptions,indent=2,ensure_ascii=False),encoding="utf-8")
    print("AISTS CP-0027 | deterministic gap-aware baseline backtest")
    print("No downloads, no API keys, no live trading, no strategy parameter search.")
    print("Fee assumption:",FEE_BPS_PER_SIDE,"bps/side; slippage scenarios 0/5/10 bps.")
    print("Expected runtime: several minutes or less on standard Colab; each timeframe processed independently.")
    for interval in INTERVALS:
        df,meta=load_candidate(root,interval,manifest)
        df=add_features(df,interval)
        q=summarize_data_quality(df,interval,meta); quality.append(q)
        interval_results=[]
        for period in PERIODS:
            sl=get_slice(df,period)
            if sl is None:
                all_results.append({"interval":interval,"period":period,"strategy":"ALL","status":"INSUFFICIENT_BARS"})
                continue
            start_i,end_i=sl
            # Fixed baseline: default cost case for train, validation and OOS.
            for strategy in ["CASH","BUY_AND_HOLD"]+STRATEGIES:
                if strategy in ("CASH","BUY_AND_HOLD"):
                    stats=simulate_benchmark(df,start_i,end_i,strategy,FEE_BPS_PER_SIDE,DEFAULT_SLIPPAGE_BPS)
                else:
                    stats=simulate_strategy(df,interval,start_i,end_i,strategy,FEE_BPS_PER_SIDE,DEFAULT_SLIPPAGE_BPS,trade_log=(period=="OOS"))
                row=result_row(interval,period,stats)
                all_results.append(row); interval_results.append(row)
                if period=="OOS" and strategy not in ("CASH","BUY_AND_HOLD") and DEFAULT_SLIPPAGE_BPS==5.0:
                    for tr in stats.get("trade_log",[]):
                        tr["interval"]=interval;tr["period"]=period
                        primary_trade_logs.append(tr)
            # OOS cost sensitivity only; 5 bps already produced above.
            if period=="OOS":
                for slip in (0.0,10.0):
                    for strategy in ["BUY_AND_HOLD"]+STRATEGIES:
                        stats=simulate_benchmark(df,start_i,end_i,strategy,FEE_BPS_PER_SIDE,slip) if strategy=="BUY_AND_HOLD" else simulate_strategy(df,interval,start_i,end_i,strategy,FEE_BPS_PER_SIDE,slip,trade_log=False)
                        row=result_row(interval,"OOS_SENSITIVITY_SLIP_"+str(int(slip)),stats)
                        oos_sensitivity.append(row)
        print(json.dumps({"interval":interval,"quality":q,"results_written":len(interval_results)}))
        del df
        gc.collect()
    result_path=result_dir/"baseline_results.csv"
    quality_path=result_dir/"data_quality.csv"
    sensitivity_path=result_dir/"oos_slippage_sensitivity.csv"
    trades_path=result_dir/"oos_trades_5bps.csv.gz"
    write_dict_csv(result_path,all_results)
    write_dict_csv(quality_path,quality)
    write_dict_csv(sensitivity_path,oos_sensitivity)
    if primary_trade_logs:
        pd.DataFrame(primary_trade_logs).to_csv(trades_path,index=False,compression="gzip")
    else:
        pd.DataFrame(columns=["interval","period","strategy"]).to_csv(trades_path,index=False,compression="gzip")
    # Baseline is considered executable/completed, but strategy acceptance remains a separate decision.
    errors=[r for r in all_results if r.get("status") not in (None,"OK")]
    report={
        "project":"AISTS CP-0027","generated_at_utc":now_utc(),"symbol":SYMBOL,"market":"Binance Spot",
        "input_manifest_sha256":sha256_file(manifest_path),
        "intervals":INTERVALS,"initial_equity_usdt":INITIAL_CAPITAL,
        "fee_bps_per_side_assumed":FEE_BPS_PER_SIDE,"default_slippage_bps_per_side":DEFAULT_SLIPPAGE_BPS,
        "oos_slippage_sensitivity_bps_per_side":OOS_SLIPPAGE_SCENARIOS,
        "periods":assumptions["periods"],"strategies":assumptions["strategies"],
        "results_file":str(result_path),"data_quality_file":str(quality_path),
        "sensitivity_file":str(sensitivity_path),"oos_trade_log_file":str(trades_path),
        "rows_of_results":len(all_results),"rows_of_oos_sensitivity":len(oos_sensitivity),
        "errors_or_insufficient_slices":len(errors),"execution_status":"COMPLETE" if not errors else "COMPLETE_WITH_INSUFFICIENT_WINDOWS",
        "decision_gate":"RESEARCH_RESULTS_ONLY_NOT_LIVE_APPROVAL",
        "important":"These results are preliminary on the provisional CP-0026 candidate. No strategy is approved. Actual account fees, execution, spread/impact and live behavior remain unverified."
    }
    report_path=report_dir/"cp0027_backtest_summary.json"
    report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    bundle=report_dir/"AISTS_CP0027_Baseline_Backtest_Report_Bundle.zip"
    members=[report_path,result_path,quality_path,sensitivity_path,result_dir/"assumptions.json",trades_path]
    with zipfile.ZipFile(bundle,"w",compression=zipfile.ZIP_DEFLATED) as zf:
        for p in members:
            if p.exists(): zf.write(p,arcname=p.name)
    print("\nCP-0027 COMPLETE")
    print("Results:",result_path)
    print("Report bundle:",bundle)
    print("Upload the compact report bundle here; all inputs and detailed trade logs remain in Drive.")
    print("Do not enable live trading from these research baselines.")

if __name__=="__main__":
    main()