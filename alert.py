from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
import uuid
import json
import os
from datetime import datetime, timedelta

app = FastAPI()
REPORTS_FILE = "reports.json"

# ---------- Models ----------
class ReportInput(BaseModel):
    user_id: str                     # Sent by frontend
    report_text: str
    disaster_type: str
    severity: Literal["Low", "Medium", "High"]
    explanation: Optional[str] = None
    status: Literal["ACTIVE", "RESOLVED", "EXPIRED", "IGNORED"]
    timestamp: str
    location: str                    # Example: "Lat: 9.4980, Lon: 76.3388"

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

from datetime import datetime

def is_duplicate_recent(new_report, r, time_window_hours=24):
    same_user = new_report["user_id"] == r["user_id"]
    same_disaster = new_report["disaster_type"].lower() == r["disaster_type"].lower()
    
    try:
        time1 = datetime.fromisoformat(new_report["timestamp"].replace("Z", "+00:00"))
        time2 = datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
    except Exception:
        return False  # Fail-safe if timestamp format is wrong

    within_window = abs((time1 - time2).total_seconds()) < time_window_hours * 3600
    return same_user and same_disaster and within_window


# ---------- Routes ----------
@app.post("/submit_report")
def submit_report(report: ReportInput):
    reports = load_reports()
    new_report = report.dict()

    for r in reports:
        if is_duplicate_recent(new_report, r):
            raise HTTPException(
                status_code=400,
                detail="You have already reported this disaster recently. Please wait before reporting again."
            )

    new_report["report_id"] = str(uuid.uuid4())  # generated here
    new_report["upvotes"] = 0
    new_report["downvotes"] = 0
    new_report["voters"] = {}
    new_report["status_in_system"] = "pending"  # backend-specific status

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
            # ❌ Prevent voting on your own report
            if vote.user_id == report["user_id"]:
                raise HTTPException(status_code=403, detail="You cannot vote on your own report.")

            # Check previous vote
            prev_vote = report["voters"].get(vote.user_id)

            if prev_vote == vote.vote_type:
                return {"msg": "You already voted this way"}
            elif prev_vote:
                # Undo old vote
                if prev_vote == "up":
                    report["upvotes"] -= 1
                else:
                    report["downvotes"] -= 1

            # Apply new vote
            if vote.vote_type == "up":
                report["upvotes"] += 1
            else:
                report["downvotes"] += 1

            report["voters"][vote.user_id] = vote.vote_type

            # Basic alert trigger logic
            if report["upvotes"] >= 3:
                report["status_in_system"] = "alert_triggered"


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
