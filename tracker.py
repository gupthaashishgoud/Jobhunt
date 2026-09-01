"""
Job Application Pipeline Tracker
================================
A full CRM-style tracker for your job search pipeline.
Tracks every stage from application to offer.

Stages:
  APPLIED → RESPONDED → HR_CALL → INTERVIEW_SCHEDULED →
  INTERVIEW_ROUND_1 → INTERVIEW_ROUND_2 → INTERVIEW_ROUND_3 →
  OFFER_RECEIVED → OFFER_ACCEPTED → REJECTED / WITHDRAWN

Features:
  - Add applications with one command
  - Update status of any application
  - Log interview details (date, time, round, notes)
  - View full pipeline dashboard
  - Track response rate, interview rate, offer rate
  - Follow-up reminders (auto-flags applications with no response in 7+ days)
  - Export to CSV for spreadsheet use
  - Interactive CLI mode

Usage:
  python tracker.py --interactive          # Full guided mode (recommended)
  python tracker.py --add                   # Quick add a new application
  python tracker.py --update                # Update status of an application
  python tracker.py --dashboard             # Show full pipeline dashboard
  python tracker.py --stats                 # Show conversion statistics
  python tracker.py --followups             # Show applications needing follow-up
  python tracker.py --export               # Export to Excel-compatible CSV

Data is stored in: job_pipeline.csv (same folder as this script)
"""

import argparse
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import csv

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    os.system("pip install pandas")
    import pandas as pd
    HAS_PANDAS = True


# ============================================================
# PIPELINE STAGES
# ============================================================

STAGES = [
    "APPLIED",
    "RESPONDED",
    "HR_CALL",
    "INTERVIEW_SCHEDULED",
    "INTERVIEW_ROUND_1",
    "INTERVIEW_ROUND_2",
    "INTERVIEW_ROUND_3",
    "OFFER_RECEIVED",
    "OFFER_ACCEPTED",
    "REJECTED",
    "WITHDRAWN",
]

STAGE_ORDER = {stage: i for i, stage in enumerate(STAGES)}

STAGE_COLORS = {
    "APPLIED": "\033[94m",           # Blue
    "RESPONDED": "\033[96m",         # Cyan
    "HR_CALL": "\033[96m",            # Cyan
    "INTERVIEW_SCHEDULED": "\033[93m", # Yellow
    "INTERVIEW_ROUND_1": "\033[93m",  # Yellow
    "INTERVIEW_ROUND_2": "\033[93m",  # Yellow
    "INTERVIEW_ROUND_3": "\033[93m",  # Yellow
    "OFFER_RECEIVED": "\033[92m",     # Green
    "OFFER_ACCEPTED": "\033[92m",    # Green
    "REJECTED": "\033[91m",           # Red
    "WITHDRAWN": "\033[90m",          # Gray
}
RESET = "\033[0m"


# ============================================================
# DATA MODEL
# ============================================================

@dataclass
class Application:
    id: int
    date_applied: str
    company: str
    job_title: str
    platform: str           # LinkedIn, Naukri, Wellfound, Upwork, etc.
    source_url: str         # Link to the job posting
    salary_range: str       # If mentioned in JD
    status: str             # Current pipeline stage
    last_updated: str       # Last status change date
    hr_contact_name: str    # HR/recruiter name if known
    hr_contact_email: str   # HR email if known
    hr_contact_phone: str   # HR phone if known
    interview_date: str     # Next or last interview date
    interview_time: str     # Interview time
    interview_round: str    # Which round (1, 2, 3, final)
    interview_type: str     # Phone, Video, In-person, Technical, HR
    interviewer_name: str   # Who interviewed you
    notes: str              # Any notes about this application
    follow_up_date: str    # When to follow up
    offer_amount: str       # If offer received, the amount
    offer_date: str         # Date offer was made
    rejection_reason: str   # If rejected, why (if known)
    cv_version: str         # Which CV version was sent


# ============================================================
# TRACKER
# ============================================================

class PipelineTracker:
    """
    Full pipeline tracker with CSV storage.
    Handles all CRUD operations and reporting.
    """

    COLUMNS = [
        "id", "date_applied", "company", "job_title", "platform", "source_url",
        "salary_range", "status", "last_updated", "hr_contact_name",
        "hr_contact_email", "hr_contact_phone", "interview_date", "interview_time",
        "interview_round", "interview_type", "interviewer_name", "notes",
        "follow_up_date", "offer_amount", "offer_date", "rejection_reason", "cv_version"
    ]

    def __init__(self, filepath: str = "job_pipeline.csv"):
        self.filepath = Path(filepath)
        self.df = self._load()

    def _load(self) -> pd.DataFrame:
        """Load existing data or create new."""
        if self.filepath.exists():
            df = pd.read_csv(self.filepath, dtype=str, keep_default_na=False)
            # Ensure all columns exist
            for col in self.COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            return df
        else:
            # Create empty DF with all columns as object (string) dtype
            df = pd.DataFrame(columns=self.COLUMNS)
            for col in self.COLUMNS:
                df[col] = df[col].astype(str)
            return df

    def _save(self):
        """Save to CSV."""
        self.df.to_csv(self.filepath, index=False)

    def _next_id(self) -> int:
        if self.df.empty or self.df["id"].replace("", "0").astype(int).max() == 0:
            return 1
        return int(self.df["id"].replace("", "0").astype(int).max()) + 1

    # ============================================================
    # ADD
    # ============================================================

    def add(self, company: str, job_title: str, platform: str = "",
            source_url: str = "", salary_range: str = "", cv_version: str = "",
            notes: str = ""):
        """Add a new application to the pipeline."""
        new_id = self._next_id()
        today = datetime.now().strftime("%Y-%m-%d")
        follow_up = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        row = {
            "id": new_id,
            "date_applied": today,
            "company": company,
            "job_title": job_title,
            "platform": platform,
            "source_url": source_url,
            "salary_range": salary_range,
            "status": "APPLIED",
            "last_updated": today,
            "hr_contact_name": "",
            "hr_contact_email": "",
            "hr_contact_phone": "",
            "interview_date": "",
            "interview_time": "",
            "interview_round": "",
            "interview_type": "",
            "interviewer_name": "",
            "notes": notes,
            "follow_up_date": follow_up,
            "offer_amount": "",
            "offer_date": "",
            "rejection_reason": "",
            "cv_version": cv_version,
        }

        self.df = pd.concat([self.df, pd.DataFrame([row])], ignore_index=True)
        self._save()

        print(f"\n  [OK] Application #{new_id} added:")
        print(f"       Company:  {company}")
        print(f"       Role:     {job_title}")
        print(f"       Platform: {platform}")
        print(f"       Date:     {today}")
        print(f"       Follow-up: {follow_up}")
        return new_id

    # ============================================================
    # BULK ADD — for high-volume application days (50-70/day)
    # ============================================================

    def bulk_add(self, entries: list, platform: str = "", cv_version: str = "standard"):
        """
        Add multiple applications at once.
        entries: list of dicts with keys: company, job_title (optional), platform (optional), notes (optional)
        or list of strings (just company names — job_title will be blank)

        Example:
            tracker.bulk_add([
                {"company": "Razorpay", "job_title": "Product Ops Manager", "platform": "LinkedIn"},
                {"company": "Freshworks", "job_title": "BI Analyst", "platform": "Wellfound"},
                {"company": "Zoho", "job_title": "Operations Manager", "platform": "Naukri"},
            ])

        Or simple mode (just company names):
            tracker.bulk_add(["Razorpay", "Freshworks", "Zoho"], platform="LinkedIn")
        """
        added = 0
        skipped = 0
        today = datetime.now().strftime("%Y-%m-%d")
        follow_up = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        new_rows = []
        new_ids = []

        print(f"\n{'='*60}")
        print(f"  BULK ADD — {len(entries)} applications")
        print(f"{'='*60}")

        for entry in entries:
            # Handle both dict and string entries
            if isinstance(entry, str):
                company = entry.strip()
                job_title = ""
                entry_platform = platform
                entry_notes = ""
            elif isinstance(entry, dict):
                company = entry.get("company", "").strip()
                job_title = entry.get("job_title", "")
                entry_platform = entry.get("platform", platform)
                entry_notes = entry.get("notes", "")
            else:
                continue

            if not company:
                continue

            # Duplicate check
            is_dup, dup_id = self._check_duplicate(company, job_title)
            if is_dup:
                print(f"  [SKIP] Duplicate: {company} (already #{dup_id})")
                skipped += 1
                continue

            new_id = self._next_id() + len(new_rows)
            row = {
                "id": new_id,
                "date_applied": today,
                "company": company,
                "job_title": job_title,
                "platform": entry_platform,
                "source_url": "",
                "salary_range": "",
                "status": "APPLIED",
                "last_updated": today,
                "hr_contact_name": "",
                "hr_contact_email": "",
                "hr_contact_phone": "",
                "interview_date": "",
                "interview_time": "",
                "interview_round": "",
                "interview_type": "",
                "interviewer_name": "",
                "notes": entry_notes,
                "follow_up_date": follow_up,
                "offer_amount": "",
                "offer_date": "",
                "rejection_reason": "",
                "cv_version": cv_version,
            }
            new_rows.append(row)
            new_ids.append(new_id)
            print(f"  [ADD] #{new_id} | {company} | {job_title or '(no title)'} | {entry_platform}")
            added += 1

        if new_rows:
            self.df = pd.concat([self.df, pd.DataFrame(new_rows)], ignore_index=True)
            self._save()

        print(f"\n{'='*60}")
        print(f"  BULK ADD COMPLETE")
        print(f"  Added:   {added}")
        print(f"  Skipped: {skipped} (duplicates)")
        print(f"  Total applications: {len(self.df)}")
        print(f"{'='*60}")
        return new_ids

    # ============================================================
    # DUPLICATE DETECTION
    # ============================================================

    def _check_duplicate(self, company: str, job_title: str = "") -> tuple:
        """
        Check if an application already exists for this company + job_title.
        Returns (is_duplicate: bool, existing_id: int or None).
        """
        if self.df.empty:
            return False, None

        # Normalize company name for comparison
        company_lower = company.lower().strip()

        # Check by company name (case-insensitive)
        existing = self.df[self.df["company"].astype(str).str.lower().str.strip() == company_lower]

        if len(existing) == 0:
            return False, None

        # If company exists, check if the same job title exists too
        if job_title:
            job_lower = job_title.lower().strip()
            same_title = existing[existing["job_title"].astype(str).str.lower().str.strip() == job_lower]
            if len(same_title) > 0:
                return True, int(same_title.iloc[0]["id"])

        # Same company, different role — not a duplicate if job_title is different
        if job_title:
            return False, None

        # No job_title specified — if company exists, consider it a potential duplicate
        return True, int(existing.iloc[0]["id"])

    def check_duplicates(self):
        """
        Scan all applications and find potential duplicates.
        Shows companies you've applied to multiple times.
        """
        if self.df.empty:
            print("\n  No applications to check.")
            return

        # Find companies that appear more than once
        company_counts = self.df.groupby(self.df["company"].astype(str).str.lower().str.strip()).size()
        duplicates = company_counts[company_counts > 1]

        if len(duplicates) == 0:
            print("\n  [OK] No duplicate applications found. You're clean!")
            return

        print(f"\n{'='*60}")
        print("  DUPLICATE DETECTION")
        print(f"{'='*60}")
        print(f"  Found {len(duplicates)} companies with multiple applications:\n")

        for company_lower, count in duplicates.items():
            rows = self.df[self.df["company"].astype(str).str.lower().str.strip() == company_lower]
            print(f"  {rows.iloc[0]['company']} ({count} applications):")
            for _, row in rows.iterrows():
                print(f"    #{int(row['id'])} | {row['job_title']} | {row['status']} | {row['date_applied']}")
            print()

        print(f"{'='*60}")

    # ============================================================
    # UPDATE STATUS
    # ============================================================

    def update_status(self, app_id: int, new_status: str, notes: str = ""):
        """Update the status of an application."""
        if str(app_id) not in self.df["id"].astype(str).values:
            print(f"  [!] Application #{app_id} not found.")
            return

        idx = self.df[self.df["id"].astype(str) == str(app_id)].index[0]
        old_status = self.df.loc[idx, "status"]
        self.df.loc[idx, "status"] = new_status
        self.df.loc[idx, "last_updated"] = datetime.now().strftime("%Y-%m-%d")

        if notes:
            existing_notes = str(self.df.loc[idx, "notes"])
            self.df.loc[idx, "notes"] = f"{existing_notes} | {datetime.now().strftime('%m/%d')}: {notes}"

        # Auto-update follow-up date based on new status
        if new_status in ["APPLIED"]:
            self.df.loc[idx, "follow_up_date"] = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        elif new_status in ["RESPONDED", "HR_CALL"]:
            self.df.loc[idx, "follow_up_date"] = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        elif new_status.startswith("INTERVIEW"):
            self.df.loc[idx, "follow_up_date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif new_status in ["OFFER_RECEIVED", "OFFER_ACCEPTED", "REJECTED", "WITHDRAWN"]:
            self.df.loc[idx, "follow_up_date"] = ""

        self._save()

        company = self.df.loc[idx, "company"]
        print(f"\n  [OK] Updated #{app_id} ({company}):")
        print(f"       {old_status} → {new_status}")

    def update_field(self, app_id: int, field: str, value: str):
        """Update a specific field of an application."""
        if str(app_id) not in self.df["id"].astype(str).values:
            print(f"  [!] Application #{app_id} not found.")
            return
        if field not in self.COLUMNS:
            print(f"  [!] Invalid field: {field}")
            print(f"  Available fields: {', '.join(self.COLUMNS)}")
            return

        idx = self.df[self.df["id"].astype(str) == str(app_id)].index[0]
        self.df.loc[idx, field] = value
        self.df.loc[idx, "last_updated"] = datetime.now().strftime("%Y-%m-%d")
        self._save()
        print(f"\n  [OK] Updated #{app_id}: {field} = {value}")

    # ============================================================
    # LOG INTERVIEW
    # ============================================================

    def log_interview(self, app_id: int, interview_date: str, interview_time: str,
                      round_num: str, interview_type: str, interviewer_name: str = "",
                      notes: str = ""):
        """Log interview details for an application."""
        if str(app_id) not in self.df["id"].astype(str).values:
            print(f"  [!] Application #{app_id} not found.")
            return

        idx = self.df[self.df["id"].astype(str) == str(app_id)].index[0]
        self.df.loc[idx, "interview_date"] = interview_date
        self.df.loc[idx, "interview_time"] = interview_time
        self.df.loc[idx, "interview_round"] = round_num
        self.df.loc[idx, "interview_type"] = interview_type
        self.df.loc[idx, "interviewer_name"] = interviewer_name

        # Auto-update status
        round_lower = round_num.lower()
        if "1" in round_lower:
            new_status = "INTERVIEW_ROUND_1"
        elif "2" in round_lower:
            new_status = "INTERVIEW_ROUND_2"
        elif "3" in round_lower or "final" in round_lower:
            new_status = "INTERVIEW_ROUND_3"
        else:
            new_status = "INTERVIEW_SCHEDULED"

        self.df.loc[idx, "status"] = new_status
        self.df.loc[idx, "follow_up_date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        if notes:
            existing_notes = str(self.df.loc[idx, "notes"])
            self.df.loc[idx, "notes"] = f"{existing_notes} | Interview {round_num}: {notes}"

        self.df.loc[idx, "last_updated"] = datetime.now().strftime("%Y-%m-%d")
        self._save()

        company = self.df.loc[idx, "company"]
        print(f"\n  [OK] Interview logged for #{app_id} ({company}):")
        print(f"       Date:      {interview_date}")
        print(f"       Time:      {interview_time}")
        print(f"       Round:     {round_num}")
        print(f"       Type:      {interview_type}")
        print(f"       Interviewer: {interviewer_name}")
        print(f"       Status:    {new_status}")

    # ============================================================
    # LOG OFFER
    # ============================================================

    def log_offer(self, app_id: int, offer_amount: str, offer_date: str = ""):
        """Log an offer received."""
        if str(app_id) not in self.df["id"].astype(str).values:
            print(f"  [!] Application #{app_id} not found.")
            return

        idx = self.df[self.df["id"].astype(str) == str(app_id)].index[0]
        self.df.loc[idx, "offer_amount"] = offer_amount
        self.df.loc[idx, "offer_date"] = offer_date or datetime.now().strftime("%Y-%m-%d")
        self.df.loc[idx, "status"] = "OFFER_RECEIVED"
        self.df.loc[idx, "follow_up_date"] = ""
        self.df.eoc[idx, "last_updated"] = datetime.now().strftime("%Y-%m-%d")
        self._save()

        company = self.df.loc[idx, "company"]
        print(f"\n  [OK] Offer logged for #{app_id} ({company}):")
        print(f"       Amount: {offer_amount}")
        print(f"       Date:   {self.df.loc[idx, 'offer_date']}")

    # ============================================================
    # DASHBOARD
    # ============================================================

    def dashboard(self):
        """Show the full pipeline dashboard."""
        if self.df.empty:
            print("\n  No applications yet. Use --add to add your first.")
            return

        print("\n" + "=" * 80)
        print("  JOB APPLICATION PIPELINE DASHBOARD")
        print(f"  Total Applications: {len(self.df)}")
        print("=" * 80)

        # Group by status
        for stage in STAGES:
            subset = self.df[self.df["status"] == stage]
            if len(subset) > 0:
                color = STAGE_COLORS.get(stage, "")
                print(f"\n  {color}  [{stage}] ({len(subset)}){RESET}")
                print(f"  {'-' * 70}")
                for _, row in subset.iterrows():
                    app_id = int(row["id"])
                    company = row["company"]
                    title = row["job_title"]
                    platform = row["platform"]
                    date = row["date_applied"]
                    interview_date = row.get("interview_date", "")

                    line = f"  #{app_id} | {company} | {title}"
                    if platform:
                        line += f" | {platform}"
                    line += f" | Applied: {date}"
                    if interview_date and str(interview_date) != "nan" and str(interview_date) != "":
                        line += f" | Interview: {interview_date}"
                    print(line)

        print("\n" + "=" * 80)

        # Quick stats
        total = len(self.df)
        responded = len(self.df[self.df["status"].isin(["RESPONDED", "HR_CALL"])])
        interviewing = len(self.df[self.df["status"].str.startswith("INTERVIEW", na=False)])
        offers = len(self.df[self.df["status"].isin(["OFFER_RECEIVED", "OFFER_ACCEPTED"])])
        rejected = len(self.df[self.df["status"] == "REJECTED"])

        print(f"  Response Rate:     {responded}/{total} ({responded/total*100:.1f}%)" if total else "")
        print(f"  Interview Rate:    {interviewing}/{total} ({interviewing/total*100:.1f}%)" if total else "")
        print(f"  Offer Rate:        {offers}/{total} ({offers/total*100:.1f}%)" if total else "")
        print(f"  Rejection Rate:    {rejected}/{total} ({rejected/total*100:.1f}%)" if total else "")
        print("=" * 80 + "\n")

    # ============================================================
    # STATISTICS
    # ============================================================

    def stats(self):
        """Show detailed conversion statistics."""
        if self.df.empty:
            print("\n  No applications yet.")
            return

        total = len(self.df)
        print("\n" + "=" * 60)
        print("  CONVERSION STATISTICS")
        print("=" * 60)

        # By platform
        print("\n  By Platform:")
        platform_stats = self.df.groupby("platform").size().sort_values(ascending=False)
        for platform, count in platform_stats.items():
            if platform and str(platform) != "nan":
                responses = len(self.df[(self.df["platform"] == platform) & (self.df["status"] != "APPLIED")])
                rate = responses / count * 100 if count > 0 else 0
                print(f"    {platform}: {count} applications, {responses} responses ({rate:.0f}%)")

        # By status
        print("\n  By Status:")
        status_counts = self.df["status"].value_counts()
        for status, count in status_counts.items():
            pct = count / total * 100
            print(f"    {status}: {count} ({pct:.1f}%)")

        # Timeline
        print(f"\n  Total Applications: {total}")
        print(f"  First Application:  {self.df['date_applied'].min()}")
        print(f"  Last Application:   {self.df['date_applied'].max()}")

        # Unique companies
        unique_companies = self.df["company"].nunique()
        print(f"  Unique Companies:   {unique_companies}")

        # Applications per day (last 7 days)
        print("\n  Applications in Last 7 Days:")
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        recent = self.df[self.df["date_applied"] >= seven_days_ago]
        if len(recent) > 0:
            daily = recent.groupby("date_applied").size()
            for date, count in daily.items():
                print(f"    {date}: {count} applications")
            print(f"    Total: {len(recent)} | Average: {len(recent)/7:.1f}/day")
        else:
            print("    No applications in the last 7 days.")

        print("\n" + "=" * 60 + "\n")

    # ============================================================
    # FOLLOW-UPS
    # ============================================================

    def followups(self):
        """Show applications that need follow-up."""
        today = datetime.now().strftime("%Y-%m-%d")
        pending = self.df[
            (self.df["follow_up_date"] <= today) &
            (self.df["follow_up_date"] != "") &
            (~self.df["status"].isin(["OFFER_RECEIVED", "OFFER_ACCEPTED", "REJECTED", "WITHDRAWN"]))
        ]

        if len(pending) == 0:
            print("\n  No follow-ups needed right now. You're all caught up!")
            return

        print("\n" + "=" * 70)
        print("  FOLLOW-UPS NEEDED")
        print("=" * 70)

        for _, row in pending.iterrows():
            app_id = int(row["id"])
            company = row["company"]
            title = row["job_title"]
            status = row["status"]
            follow_up = row["follow_up_date"]
            date_applied = row["date_applied"]

            days_since = (datetime.now() - datetime.strptime(date_applied, "%Y-%m-%d")).days

            print(f"\n  #{app_id} | {company} | {title}")
            print(f"       Status: {status}")
            print(f"       Applied: {date_applied} ({days_since} days ago)")
            print(f"       Follow-up due: {follow_up}")

        print("\n" + "=" * 70)
        print(f"  Total follow-ups needed: {len(pending)}")
        print("=" * 70 + "\n")

    # ============================================================
    # SEARCH / FILTER
    # ============================================================

    def search(self, query: str):
        """Search applications by company, job title, or notes."""
        if self.df.empty:
            print("\n  No applications to search.")
            return

        mask = (
            self.df["company"].str.contains(query, case=False, na=False) |
            self.df["job_title"].str.contains(query, case=False, na=False) |
            self.df["notes"].str.contains(query, case=False, na=False)
        )
        results = self.df[mask]

        if len(results) == 0:
            print(f"\n  No applications found matching '{query}'.")
            return

        print(f"\n  Found {len(results)} applications matching '{query}':\n")
        for _, row in results.iterrows():
            print(f"  #{int(row['id'])} | {row['company']} | {row['job_title']} | {row['status']} | Applied: {row['date_applied']}")

    # ============================================================
    # EXPORT
    # ============================================================

    def export(self, filepath: str = "job_pipeline_export.csv"):
        """Export to CSV."""
        self.df.to_csv(filepath, index=False)
        print(f"\n  [OK] Exported {len(self.df)} applications to {filepath}")

    # ============================================================
    # INTERACTIVE MODE
    # ============================================================

    def interactive(self):
        """Full guided interactive mode."""
        while True:
            print("\n" + "=" * 60)
            print("  JOB APPLICATION PIPELINE TRACKER")
            print("=" * 60)
            print(f"  Total Applications: {len(self.df)}")

            # Count by stage
            for stage in ["APPLIED", "RESPONDED", "HR_CALL", "INTERVIEW_SCHEDULED",
                          "INTERVIEW_ROUND_1", "INTERVIEW_ROUND_2", "INTERVIEW_ROUND_3",
                          "OFFER_RECEIVED", "OFFER_ACCEPTED", "REJECTED", "WITHDRAWN"]:
                count = len(self.df[self.df["status"] == stage])
                if count > 0:
                    color = STAGE_COLORS.get(stage, "")
                    print(f"  {color}{stage}: {count}{RESET}")

            print("\n  What would you like to do?")
            print("  1.  Add a new application")
            print("  2.  Update status of an application")
            print("  3.  Log an interview")
            print("  4.  Log an offer")
            print("  5.  View full dashboard")
            print("  6.  View statistics")
            print("  7.  View follow-ups needed")
            print("  8.  Search applications")
            print("  9.  View application details")
            print("  10. Export to CSV")
            print("  11. Exit")
            print()

            choice = input("  Enter choice (1-11): ").strip()

            if choice == "1":
                self._interactive_add()
            elif choice == "2":
                self._interactive_update_status()
            elif choice == "3":
                self._interactive_log_interview()
            elif choice == "4":
                self._interactive_log_offer()
            elif choice == "5":
                self.dashboard()
            elif choice == "6":
                self.stats()
            elif choice == "7":
                self.followups()
            elif choice == "8":
                query = input("  Search for (company, role, or notes): ").strip()
                self.search(query)
            elif choice == "9":
                self._interactive_view_details()
            elif choice == "10":
                self.export()
            elif choice == "11":
                print("\n  Goodbye, Ashish! Keep applying. You've got this.\n")
                break
            else:
                print("  Invalid choice. Try again.")

            # Pause before showing menu again
            if choice != "11":
                input("\n  Press Enter to continue...")

    def _interactive_add(self):
        """Interactive: add a new application."""
        print("\n  --- ADD NEW APPLICATION ---\n")
        company = input("  Company name: ").strip()
        if not company:
            print("  Company name is required. Aborting.")
            return
        job_title = input("  Job title: ").strip()
        platform = input("  Platform (LinkedIn/Naukri/Wellfound/Upwork/etc.): ").strip()
        source_url = input("  Job posting URL (optional): ").strip()
        salary_range = input("  Salary range if known (optional): ").strip()
        cv_version = input("  CV version sent (standard/tailored - optional): ").strip() or "standard"
        notes = input("  Notes (optional): ").strip()

        self.add(company, job_title, platform, source_url, salary_range, cv_version, notes)

    def _interactive_update_status(self):
        """Interactive: update status."""
        self._interactive_view_recent()
        try:
            app_id = int(input("\n  Enter application ID to update: ").strip())
        except ValueError:
            print("  Invalid ID.")
            return

        print("\n  Available statuses:")
        for i, stage in enumerate(STAGES, 1):
            print(f"  {i}. {stage}")

        try:
            choice = int(input("\n  Select new status (1-11): ").strip())
            if 1 <= choice <= len(STAGES):
                new_status = STAGES[choice - 1]
                notes = input("  Notes (optional): ").strip()
                self.update_status(app_id, new_status, notes)
        except (ValueError, IndexError):
            print("  Invalid choice.")

    def _interactive_log_interview(self):
        """Interactive: log interview details."""
        self._interactive_view_recent()
        try:
            app_id = int(input("\n  Enter application ID: ").strip())
        except ValueError:
            print("  Invalid ID.")
            return

        interview_date = input("  Interview date (YYYY-MM-DD): ").strip()
        interview_time = input("  Interview time (e.g. 2:00 PM): ").strip()
        round_num = input("  Round (1/2/3/Final): ").strip()
        interview_type = input("  Type (Phone/Video/In-person/Technical/HR): ").strip()
        interviewer_name = input("  Interviewer name (optional): ").strip()
        notes = input("  Notes (optional): ").strip()

        self.log_interview(app_id, interview_date, interview_time, round_num,
                          interview_type, interviewer_name, notes)

    def _interactive_log_offer(self):
        """Interactive: log an offer."""
        self._interactive_view_recent()
        try:
            app_id = int(input("\n  Enter application ID: ").strip())
        except ValueError:
            print("  Invalid ID.")
            return

        offer_amount = input("  Offer amount (e.g. Rs 60,000/month): ").strip()
        offer_date = input("  Offer date (YYYY-MM-DD, or press Enter for today): ").strip()

        self.log_offer(app_id, offer_amount, offer_date)

    def _interactive_view_recent(self):
        """Show recent applications for selection."""
        recent = self.df.tail(15)
        if len(recent) > 0:
            print("\n  Recent applications:")
            for _, row in recent.iterrows():
                print(f"  #{int(row['id'])} | {row['company']} | {row['job_title']} | {row['status']}")

    def _interactive_view_details(self):
        """View full details of a specific application."""
        self._interactive_view_recent()
        try:
            app_id = int(input("\n  Enter application ID: ").strip())
        except ValueError:
            print("  Invalid ID.")
            return

        if app_id not in self.df["id"].values:
            print(f"  Application #{app_id} not found.")
            return

        row = self.df[self.df["id"] == app_id].iloc[0]
        print("\n" + "=" * 60)
        print(f"  APPLICATION #{app_id} DETAILS")
        print("=" * 60)
        for col in self.COLUMNS:
            if col != "id":
                val = row[col]
                if str(val) != "nan" and str(val) != "":
                    print(f"  {col.replace('_', ' ').title():.<25} {val}")
        print("=" * 60)


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Job Application Pipeline Tracker")
    parser.add_argument('--interactive', action='store_true', help="Run interactive mode (recommended)")
    parser.add_argument('--add', action='store_true', help="Add a new application")
    parser.add_argument('--update', action='store_true', help="Update status of an application")
    parser.add_argument('--interview', action='store_true', help="Log an interview")
    parser.add_argument('--offer', action='store_true', help="Log an offer")
    parser.add_argument('--dashboard', action='store_true', help="Show full pipeline dashboard")
    parser.add_argument('--stats', action='store_true', help="Show conversion statistics")
    parser.add_argument('--followups', action='store_true', help="Show applications needing follow-up")
    parser.add_argument('--search', type=str, help="Search applications")
    parser.add_argument('--export', action='store_true', help="Export to CSV")
    parser.add_argument('--file', type=str, default="job_pipeline.csv", help="CSV file path")

    args = parser.parse_args()
    tracker = PipelineTracker(args.file)

    if args.interactive:
        tracker.interactive()
    elif args.add:
        tracker._interactive_add()
    elif args.update:
        tracker._interactive_update_status()
    elif args.interview:
        tracker._interactive_log_interview()
    elif args.offer:
        tracker._interactive_log_offer()
    elif args.dashboard:
        tracker.dashboard()
    elif args.stats:
        tracker.stats()
    elif args.followups:
        tracker.followups()
    elif args.search:
        tracker.search(args.search)
    elif args.export:
        tracker.export()
    else:
        print("""
  Job Application Pipeline Tracker
  -------------------------------
  Track every stage: Applied → Responded → HR Call → Interview → Offer

  Usage:
    python tracker.py --interactive     # Full guided mode (recommended)
    python tracker.py --add              # Quick add an application
    python tracker.py --dashboard       # View full pipeline
    python tracker.py --stats            # View conversion stats
    python tracker.py --followups        # Check what needs follow-up
    python tracker.py --search "Razorpay"  # Search by company/role
    python tracker.py --export           # Export to CSV

  Data stored in: job_pipeline.csv
  Run --interactive for the best experience.
        """)


if __name__ == "__main__":
    main()
