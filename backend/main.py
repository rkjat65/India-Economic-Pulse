from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
from pathlib import Path
import os
import json
import warnings
import httpx
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(os.path.abspath(__file__)).parent / ".env")

warnings.filterwarnings("ignore")

app = FastAPI(title="India Economic Pulse API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

RAW = Path(os.path.abspath(__file__)).parent.parent / "raw_data"


# ── serialization ────────────────────────────────────────────
def clean(v):
    if v is None:
        return None
    if isinstance(v, float) and np.isnan(v):
        return None
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, np.floating):
        return None if np.isnan(v) else round(float(v), 4)
    if hasattr(v, "strftime"):
        return v.strftime("%Y-%m-%d")
    return v


def to_records(df: pd.DataFrame):
    return [{k: clean(v) for k, v in row.items()} for row in df.to_dict("records")]


# ── data loaders ─────────────────────────────────────────────
def _load_gdp():
    df = pd.read_excel(RAW / "gdp_data.xlsx", sheet_name=0)
    df = df.rename(columns={
        "Item/ Year": "year", "Quarter": "quarter",
        "1. PFCE": "pfce", "2. GFCE": "gfce", "3. GFCF": "gfcf",
        "6. Export of goods & services": "exports",
        "7. Import of goods & services": "imports",
        "9. Gross Domestic Product": "gdp_growth",
    })
    df["year"] = df["year"].ffill()
    df = df.dropna(subset=["quarter"])
    df["year_num"] = df["year"].astype(str).str.split("-").str[0].astype(int)
    qmap = {"Q1": 4, "Q2": 7, "Q3": 10, "Q4": 1}
    df["month"] = df["quarter"].map(qmap)
    df["cal_year"] = df["year_num"]
    df.loc[df["quarter"] == "Q4", "cal_year"] += 1
    df["date"] = pd.to_datetime(
        df["cal_year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2) + "-01"
    )
    keep = ["date", "year", "quarter", "gdp_growth", "pfce", "gfce", "gfcf", "exports", "imports"]
    df = df[[c for c in keep if c in df.columns]].sort_values("date").reset_index(drop=True)
    df["gdp_ma4"] = df["gdp_growth"].rolling(4).mean()
    return df


def _load_inflation():
    df = pd.read_excel(RAW / "inflation_data.xlsx", sheet_name=0)
    valid = []
    for i, v in enumerate(df.iloc[:, 0]):
        if pd.isna(v) or "Note" in str(v) or "See" in str(v):
            break
        valid.append(i)
    df = df.iloc[valid]
    df = df.rename(columns={
        df.columns[0]: "date",
        df.columns[1]: "cpi",
        df.columns[2]: "cpi_rural",
        df.columns[3]: "cpi_urban",
        df.columns[6]: "wpi",
    })
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for c in ["cpi", "cpi_rural", "cpi_urban", "wpi"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c].replace("-", np.nan), errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    df["cpi_yoy"] = df["cpi"].pct_change(12) * 100
    df["cpi_rural_yoy"] = df["cpi_rural"].pct_change(12) * 100
    df["cpi_urban_yoy"] = df["cpi_urban"].pct_change(12) * 100
    df["wpi_yoy"] = df["wpi"].pct_change(12) * 100
    keep = ["date", "cpi_yoy", "cpi_rural_yoy", "cpi_urban_yoy", "wpi_yoy"]
    return df[[c for c in keep if c in df.columns]]


def _load_trade():
    df = pd.read_excel(RAW / "Foreign Trade.xlsx", sheet_name=0)
    df = df.iloc[1:].reset_index(drop=True)
    cols = [
        "year", "month",
        "exports_inr", "exports_usd", "exp_oil_inr", "exp_oil_usd",
        "exp_nonoil_inr", "exp_nonoil_usd",
        "imports_inr", "imports_usd", "imp_oil_inr", "imp_oil_usd",
        "imp_nonoil_inr", "imp_nonoil_usd",
        "balance_inr", "balance_usd",
        "bal_oil_inr", "bal_oil_usd", "bal_nonoil_inr", "bal_nonoil_usd",
    ]
    df.columns = cols[: len(df.columns)]
    df["date"] = pd.to_datetime(df["month"], errors="coerce")
    for c in [x for x in df.columns if x not in ("year", "month", "date")]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    df["exports_growth_yoy"] = df["exports_usd"].pct_change(12) * 100
    df["imports_growth_yoy"] = df["imports_usd"].pct_change(12) * 100
    keep = ["date", "exports_usd", "imports_usd", "balance_usd",
            "exports_inr", "imports_inr", "balance_inr",
            "exports_growth_yoy", "imports_growth_yoy"]
    return df[[c for c in keep if c in df.columns]]


def _load_forex():
    df = pd.read_excel(RAW / "Forex.xlsx", sheet_name=0)
    df = df.iloc[5:].reset_index(drop=True)
    df.columns = [
        "date", "total_inr", "total_usd",
        "fca_inr", "fca_usd", "gold_inr", "gold_usd",
        "sdr_inr", "sdr_usd", "imf_inr", "imf_usd",
    ][: len(df.columns)]
    valid = []
    for i, v in enumerate(df["date"]):
        try:
            pd.to_datetime(v)
            valid.append(i)
        except Exception:
            break
    df = df.iloc[valid]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for c in [x for x in df.columns if x != "date"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    if "total_usd" in df.columns and "gold_usd" in df.columns:
        df["gold_pct"] = (df["gold_usd"] / df["total_usd"]) * 100
        df["fca_pct"] = (df["fca_usd"] / df["total_usd"]) * 100
    return df


def _load_rbi():
    df = pd.read_excel(RAW / "RBI Rates.xlsx", sheet_name=0)
    df = df.iloc[1:].reset_index(drop=True)
    df.columns = ["date", "bank_rate", "repo_rate", "reverse_repo",
                  "sdf_rate", "msf_rate", "crr", "slr"][: len(df.columns)]
    valid = []
    for i, v in enumerate(df["date"]):
        try:
            pd.to_datetime(v)
            valid.append(i)
        except Exception:
            break
    df = df.iloc[valid]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for c in [x for x in df.columns if x != "date"]:
        df[c] = pd.to_numeric(df[c].replace("-", np.nan), errors="coerce")
        df[c] = df[c].ffill()
    return df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)


# ── endpoints ────────────────────────────────────────────────
@app.get("/api/gdp")
def get_gdp():
    try:
        return {"data": to_records(_load_gdp())}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/inflation")
def get_inflation():
    try:
        return {"data": to_records(_load_inflation())}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/trade")
def get_trade():
    try:
        return {"data": to_records(_load_trade())}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/forex")
def get_forex():
    try:
        return {"data": to_records(_load_forex())}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/rbi-rates")
def get_rbi():
    try:
        return {"data": to_records(_load_rbi())}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/overview")
def get_overview():
    out = {}
    try:
        gdp = _load_gdp()
        row = gdp.dropna(subset=["gdp_growth"]).iloc[-1]
        out["gdp_growth"] = clean(row["gdp_growth"])
        out["gdp_label"] = f"{row['quarter']} {row['year']}"
    except Exception:
        pass
    try:
        inf = _load_inflation()
        row = inf.dropna(subset=["cpi_yoy"]).iloc[-1]
        out["cpi_yoy"] = clean(row["cpi_yoy"])
        out["wpi_yoy"] = clean(row.get("wpi_yoy"))
        out["inflation_date"] = clean(row["date"])
    except Exception:
        pass
    try:
        trade = _load_trade()
        row = trade.dropna(subset=["balance_usd"]).iloc[-1]
        out["balance_usd"] = clean(row["balance_usd"])
        out["exports_usd"] = clean(row["exports_usd"])
        out["imports_usd"] = clean(row["imports_usd"])
    except Exception:
        pass
    try:
        forex = _load_forex()
        row = forex.dropna(subset=["total_usd"]).iloc[-1]
        out["forex_usd"] = clean(row["total_usd"])
        out["forex_date"] = clean(row["date"])
    except Exception:
        pass
    try:
        rbi = _load_rbi()
        row = rbi.dropna(subset=["repo_rate"]).iloc[-1]
        out["repo_rate"] = clean(row["repo_rate"])
        out["reverse_repo"] = clean(row.get("reverse_repo"))
        out["crr"] = clean(row.get("crr"))
        out["slr"] = clean(row.get("slr"))
    except Exception:
        pass
    return out


# ── AI endpoints ─────────────────────────────────────────────
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_TEXT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
GEMINI_IMG  = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateImages"


class AnalyzeReq(BaseModel):
    topic: str
    question: str = ""


class ImageReq(BaseModel):
    prompt: str
    model: str = "imagen-4.0-generate-001"


def _build_context(topic: str) -> str:
    try:
        if topic == "gdp":
            df = _load_gdp().dropna(subset=["gdp_growth"]).tail(8)
            rows = df[["date", "quarter", "year", "gdp_growth"]].to_string(index=False)
            return f"India GDP Growth (last 8 quarters, % YoY):\n{rows}"
        elif topic == "inflation":
            df = _load_inflation().dropna(subset=["cpi_yoy"]).tail(12)
            cols = [c for c in ["date", "cpi_yoy", "wpi_yoy"] if c in df.columns]
            return f"India Inflation data (last 12 months, % YoY):\n{df[cols].to_string(index=False)}"
        elif topic == "trade":
            df = _load_trade().dropna(subset=["balance_usd"]).tail(12)
            cols = [c for c in ["date", "exports_usd", "imports_usd", "balance_usd"] if c in df.columns]
            return f"India Trade data (last 12 months, USD millions):\n{df[cols].to_string(index=False)}"
        elif topic == "forex":
            df = _load_forex().dropna(subset=["total_usd"]).tail(8)
            cols = [c for c in ["date", "total_usd", "gold_usd", "fca_usd"] if c in df.columns]
            return f"India Forex Reserves (last 8 data points, USD millions):\n{df[cols].to_string(index=False)}"
        elif topic == "rbi":
            df = _load_rbi().dropna(subset=["repo_rate"]).tail(8)
            cols = [c for c in ["date", "repo_rate", "reverse_repo", "crr", "slr"] if c in df.columns]
            return f"India RBI Policy Rates (last 8 changes):\n{df[cols].to_string(index=False)}"
    except Exception as e:
        return f"Data unavailable: {e}"
    return ""


@app.post("/api/ai/analyze")
async def ai_analyze(req: AnalyzeReq):
    if not GEMINI_KEY:
        raise HTTPException(500, "GEMINI_API_KEY not set in backend .env")

    context = _build_context(req.topic)
    question = req.question.strip() or f"Analyse the current trend in India's {req.topic} data."

    prompt = (
        "You are a senior macroeconomic analyst specialising in the Indian economy. "
        "Use the data below to answer the question. Be specific, cite numbers.\n\n"
        f"{context}\n\n"
        f"Question: {question}\n\n"
        "Respond ONLY with valid JSON — no markdown fences — in exactly this shape:\n"
        '{"summary":"2-3 sentence insight","key_points":["point1","point2","point3"],'
        '"trend":"rising|falling|stable|volatile","sentiment":"positive|negative|neutral"}'
    )

    payload = {"contents": [{"parts": [{"text": prompt}]}],
               "generationConfig": {"temperature": 0.4, "maxOutputTokens": 512}}

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{GEMINI_TEXT}?key={GEMINI_KEY}", json=payload)
        if not r.is_success:
            raise HTTPException(r.status_code, r.text)

    raw = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    # Strip markdown fences if model adds them anyway
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"summary": raw, "key_points": [], "trend": "stable", "sentiment": "neutral"}


@app.post("/api/ai/image")
async def ai_image(req: ImageReq):
    if not GEMINI_KEY:
        raise HTTPException(500, "GEMINI_API_KEY not set in backend .env")

    url = GEMINI_IMG.format(model=req.model) + f"?key={GEMINI_KEY}"
    payload = {"prompt": {"text": req.prompt}, "number_of_images": 1}

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, json=payload)
        if not r.is_success:
            raise HTTPException(r.status_code, r.json().get("error", {}).get("message", r.text))

    data = r.json()
    b64 = data.get("generated_images", [{}])[0].get("image", {}).get("image_bytes")
    if not b64:
        raise HTTPException(500, "No image returned from Imagen API")
    return {"image_b64": b64}


# ── Studio data endpoints ─────────────────────────────────────

def _fiscal_range(year_num: int):
    """April year_num → March year_num+1"""
    return pd.Timestamp(year_num, 4, 1), pd.Timestamp(year_num + 1, 3, 31)


@app.get("/api/studio/snapshot")
def studio_snapshot():
    out = {}
    try:
        g = _load_gdp().dropna(subset=["gdp_growth"])
        r, p = g.iloc[-1], g.iloc[-2] if len(g) >= 2 else None
        out["gdp"] = {"label": "GDP Growth", "value": clean(r["gdp_growth"]), "unit": "%",
                      "period": f"{r['quarter']} {r['year']}", "prev": clean(p["gdp_growth"]) if p is not None else None,
                      "color": "#22C55E", "source": "MoSPI"}
    except: pass
    try:
        inf = _load_inflation().dropna(subset=["cpi_yoy"])
        r, p = inf.iloc[-1], inf.iloc[-2] if len(inf) >= 2 else None
        out["cpi"] = {"label": "CPI Inflation", "value": clean(r["cpi_yoy"]), "unit": "%",
                      "period": clean(r["date"]), "prev": clean(p["cpi_yoy"]) if p is not None else None,
                      "color": "#F59E0B", "source": "MoSPI"}
        wdf = inf.dropna(subset=["wpi_yoy"])
        if len(wdf):
            wr, wp = wdf.iloc[-1], wdf.iloc[-2] if len(wdf) >= 2 else None
            out["wpi"] = {"label": "WPI Inflation", "value": clean(wr["wpi_yoy"]), "unit": "%",
                          "period": clean(wr["date"]), "prev": clean(wp["wpi_yoy"]) if wp is not None else None,
                          "color": "#8B5CF6", "source": "MoSPI"}
    except: pass
    try:
        tr = _load_trade().dropna(subset=["balance_usd"])
        r, p = tr.iloc[-1], tr.iloc[-2] if len(tr) >= 2 else None
        out["trade"] = {"label": "Trade Balance", "value": round(clean(r["balance_usd"]) / 1000, 2),
                        "unit": "B$", "period": clean(r["date"]),
                        "prev": round(clean(p["balance_usd"]) / 1000, 2) if p is not None else None,
                        "color": "#EF4444", "source": "DGCI&S"}
    except: pass
    try:
        fx = _load_forex().dropna(subset=["total_usd"])
        r, p = fx.iloc[-1], fx.iloc[-4] if len(fx) >= 4 else None
        out["forex"] = {"label": "Forex Reserves", "value": round(clean(r["total_usd"]) / 1000, 1),
                        "unit": "B$", "period": clean(r["date"]),
                        "prev": round(clean(p["total_usd"]) / 1000, 1) if p is not None else None,
                        "color": "#06B6D4", "source": "RBI"}
    except: pass
    try:
        rb = _load_rbi().dropna(subset=["repo_rate"])
        r, p = rb.iloc[-1], rb.iloc[-2] if len(rb) >= 2 else None
        out["repo"] = {"label": "Repo Rate", "value": clean(r["repo_rate"]), "unit": "%",
                       "period": clean(r["date"]), "prev": clean(p["repo_rate"]) if p is not None else None,
                       "color": "#7C3AED", "source": "RBI"}
    except: pass
    return out


@app.get("/api/studio/timeseries")
def studio_timeseries(indicator: str = "gdp", n: int = 16):
    loaders = {
        "gdp":   lambda: _load_gdp().dropna(subset=["gdp_growth"]).tail(n)[["date", "gdp_growth"]].rename(columns={"gdp_growth": "value"}),
        "cpi":   lambda: _load_inflation().dropna(subset=["cpi_yoy"]).tail(n)[["date", "cpi_yoy"]].rename(columns={"cpi_yoy": "value"}),
        "wpi":   lambda: _load_inflation().dropna(subset=["wpi_yoy"]).tail(n)[["date", "wpi_yoy"]].rename(columns={"wpi_yoy": "value"}),
        "trade": lambda: _load_trade().dropna(subset=["balance_usd"]).tail(n).assign(value=lambda d: (d["balance_usd"] / 1000).round(2))[["date", "value"]],
        "forex": lambda: _load_forex().dropna(subset=["total_usd"]).tail(n).assign(value=lambda d: (d["total_usd"] / 1000).round(1))[["date", "value"]],
        "repo":  lambda: _load_rbi().dropna(subset=["repo_rate"]).tail(n)[["date", "repo_rate"]].rename(columns={"repo_rate": "value"}),
    }
    if indicator not in loaders:
        raise HTTPException(400, "Unknown indicator")
    try:
        df = loaders[indicator]()
        return {"data": [{"date": clean(row["date"]), "value": clean(row["value"])} for _, row in df.iterrows()]}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/studio/rankings")
def studio_rankings(indicator: str = "gdp", n: int = 10):
    try:
        if indicator == "gdp":
            df = _load_gdp().dropna(subset=["gdp_growth"]).nlargest(n, "gdp_growth")
            return {"data": to_records(df[["date", "quarter", "year", "gdp_growth"]]),
                    "value_key": "gdp_growth", "label": "GDP Growth %"}
        if indicator == "cpi":
            df = _load_inflation().dropna(subset=["cpi_yoy"]).nlargest(n, "cpi_yoy")
            return {"data": to_records(df[["date", "cpi_yoy"]]), "value_key": "cpi_yoy", "label": "CPI Inflation %"}
        if indicator == "forex":
            df = _load_forex().dropna(subset=["total_usd"]).nlargest(n, "total_usd")
            df = df.assign(total_b=lambda d: (d["total_usd"] / 1000).round(1))
            return {"data": to_records(df[["date", "total_b"]]), "value_key": "total_b", "label": "Forex Reserves $B"}
    except Exception as e:
        raise HTTPException(500, str(e))
    raise HTTPException(400, "Unknown indicator")


@app.get("/api/studio/periods")
def studio_periods():
    try:
        gdp = _load_gdp()
        years = sorted(gdp["year"].dropna().astype(str).str.split("-").str[0].astype(int).unique().tolist(), reverse=True)
        return {"years": years[:10]}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/studio/year-summary")
def studio_year_summary(year: int):
    start, end = _fiscal_range(year)
    out = {"year": year, "fiscal_year": f"{year}-{str(year + 1)[-2:]}"}
    try:
        g = _load_gdp().dropna(subset=["gdp_growth"])
        g["_yn"] = g["year"].astype(str).str.split("-").str[0].astype(int)
        fy = g[g["_yn"] == year]
        if len(fy):
            out["gdp"] = {"avg": round(fy["gdp_growth"].mean(), 2), "unit": "%"}
    except: pass
    try:
        inf = _load_inflation().dropna(subset=["cpi_yoy"])
        fy = inf[(inf["date"] >= start) & (inf["date"] <= end)]
        if len(fy):
            out["cpi"] = {"avg": round(fy["cpi_yoy"].mean(), 2), "unit": "%"}
        wdf = inf.dropna(subset=["wpi_yoy"])
        fyw = wdf[(wdf["date"] >= start) & (wdf["date"] <= end)]
        if len(fyw):
            out["wpi"] = {"avg": round(fyw["wpi_yoy"].mean(), 2), "unit": "%"}
    except: pass
    try:
        tr = _load_trade().dropna(subset=["balance_usd"])
        fy = tr[(tr["date"] >= start) & (tr["date"] <= end)]
        if len(fy):
            out["trade"] = {"avg": round((fy["balance_usd"].mean()) / 1000, 2), "unit": "B$"}
    except: pass
    try:
        fx = _load_forex().dropna(subset=["total_usd"])
        fy = fx[(fx["date"] >= start) & (fx["date"] <= end)]
        if len(fy):
            out["forex"] = {"avg": round(fy["total_usd"].iloc[-1] / 1000, 1), "unit": "B$"}
    except: pass
    try:
        rb = _load_rbi().dropna(subset=["repo_rate"])
        fy = rb[(rb["date"] >= start) & (rb["date"] <= end)]
        if len(fy):
            out["repo"] = {"avg": round(fy["repo_rate"].mean(), 2), "unit": "%"}
    except: pass
    return out


# ── AI caption endpoint ───────────────────────────────────────

class CaptionReq(BaseModel):
    template: str
    data: dict
    platform: str = "twitter"


@app.post("/api/ai/caption")
async def ai_caption(req: CaptionReq):
    if not GEMINI_KEY:
        raise HTTPException(500, "GEMINI_API_KEY not set in backend .env")

    hints = {
        "twitter":   "Max 280 chars, punchy, 2-3 hashtags like #IndiaEconomy #EconomicData",
        "instagram": "Engaging storytelling, 5-8 hashtags at end, emojis welcome",
        "linkedin":  "Professional tone, 2-3 sentences, 1 key insight, minimal hashtags",
        "portrait":  "Very short bold statement, 1-2 hashtags",
    }
    prompt = (
        f"Write a {req.platform} social media caption for this India economic data graphic.\n"
        f"Template: {req.template}\nData context: {json.dumps(req.data, default=str)}\n"
        f"Requirements: {hints.get(req.platform, hints['twitter'])}\n"
        "Mention specific numbers. Brand: India Economic Pulse · @rkjat65 · rkjat.in\n"
        "Return ONLY the caption text."
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}],
               "generationConfig": {"temperature": 0.7, "maxOutputTokens": 300}}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{GEMINI_TEXT}?key={GEMINI_KEY}", json=payload)
        if not r.is_success:
            raise HTTPException(r.status_code, r.text)
    return {"caption": r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()}


# ── serve React SPA ──────────────────────────────────────────
DIST = Path(os.path.abspath(__file__)).parent.parent / "frontend" / "dist"

if DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(DIST / "assets")), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        index = DIST / "index.html"
        return FileResponse(str(index))
