from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
import uuid
import json
import os
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime
from user_register import router as user_router
from whatsapp_utils import broadcast_alert_whatsapp


app = FastAPI()
app.include_router(user_router)

REPORTS_FILE = "reports.json"
DEFAULT_RADIUS_KM = 5

# ---------- Models ----------
class ReportInput(BaseModel):
    user_id: str
    report_text: str
    disaster_type: str
    severity: Literal["Low", "Medium", "High"]
    explanation: Optional[str] = None
    status: Literal["ACTIVE", "RESOLVED", "EXPIRED", "IGNORED"]
    timestamp: str
    location: str  # Format: "Lat: ..., Lon: ..."

class VoteInput(BaseModel):
    report_id: str
    user_id: str
    vote_type: Literal["up", "down"]

# ---------- Helpers ----------
def load_reports():
    if not os.path.exists(REPORTS_FILE):
        return []
    with open(REPORTS_FILE, "r") as f:
        return json.load(f)

def save_reports(reports):
    with open(REPORTS_FILE, "w") as f:
        json.dump(reports, f, indent=2)

def is_duplicate_recent(new_report, r, time_window_hours=24):
    # ✅ If the new report is RESOLVED, always allow it (even from same user)
    if new_report.get("status") == "RESOLVED":
        return False

    same_user = new_report["user_id"] == r["user_id"]
    same_disaster = new_report["disaster_type"].lower() == r["disaster_type"].lower()

    try:
        time1 = datetime.fromisoformat(new_report["timestamp"].replace("Z", "+00:00"))
        time2 = datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
    except Exception:
        return False

    within_window = abs((time1 - time2).total_seconds()) < time_window_hours * 3600
    return same_user and same_disaster and within_window


def parse_location(loc_str):
    try:
        parts = loc_str.replace("Lat:", "").replace("Lon:", "").split(",")
        lat = float(parts[0].strip())
        lon = float(parts[1].strip())
        return lat, lon
    except Exception:
        return None, None

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# ---------- Routes ----------

@app.post("/submit_report")
def submit_report(report: ReportInput):
    if report.status in ["EXPIRED", "IGNORED"]:
        return {
            "msg": f"Report not saved because status is '{report.status}'"
        }

    reports = load_reports()
    new_report = report.dict()

    for r in reports:
        if is_duplicate_recent(new_report, r):
            raise HTTPException(
                status_code=400,
                detail="You have already reported this disaster recently. Please wait before reporting again."
            )

    new_report["report_id"] = str(uuid.uuid4())
    new_report["upvotes"] = 0
    new_report["downvotes"] = 0
    new_report["voters"] = {}
    new_report["status_in_system"] = "pending"

    if report.status == "RESOLVED":
        report_lat, report_lon = parse_location(report.location)
        for r in reports:
            if r["disaster_type"].lower() == report.disaster_type.lower():
                r_lat, r_lon = parse_location(r["location"])
                if None not in (report_lat, report_lon, r_lat, r_lon):
                    distance = haversine(report_lat, report_lon, r_lat, r_lon)
                    if distance <= DEFAULT_RADIUS_KM and r["status_in_system"] in ["pending", "alert_triggered"]:
                        r["status_in_system"] = "resolved_by_followup"

    reports.append(new_report)
    save_reports(reports)

    return {
        "msg": "Report submitted",
        "report_id": new_report["report_id"]
    }

@app.post("/vote")
def vote(vote: VoteInput):
    reports = load_reports()
    for report in reports:
        if report["report_id"] == vote.report_id:
            if vote.user_id == report["user_id"]:
                raise HTTPException(status_code=403, detail="You cannot vote on your own report.")

            prev_vote = report["voters"].get(vote.user_id)

            if prev_vote == vote.vote_type:
                return {"msg": "You already voted this way"}
            elif prev_vote:
                if prev_vote == "up":
                    report["upvotes"] -= 1
                else:
                    report["downvotes"] -= 1

            if vote.vote_type == "up":
                report["upvotes"] += 1
            else:
                report["downvotes"] += 1

            # ✅ Prevent negative votes
            report["upvotes"] = max(0, report["upvotes"])
            report["downvotes"] = max(0, report["downvotes"])

            report["voters"][vote.user_id] = vote.vote_type

            if report["upvotes"] >= 3:
                report["status_in_system"] = "alert_triggered"
                broadcast_alert_whatsapp(report)

            save_reports(reports)
            return {
                "msg": "Vote recorded",
                "status": report["status_in_system"]
            }

    raise HTTPException(status_code=404, detail="Report not found")
@app.get("/reports")
def get_reports():
    return load_reports()

@app.get("/alerts")
def get_alerts():
    return [
        r for r in load_reports()
        if r["status_in_system"] == "alert_triggered"
    ]
