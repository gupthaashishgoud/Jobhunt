"""
Job Hunting AI Agent
========================
Helps you:
  1. Search jobs across multiple free platforms (LinkedIn, Wellfound, Naukri, etc.)
  2. Filter and rank job postings based on your profile (experience, skills, location)
  3. Generate tailored CV resumes for each job
  4. Create cover letters for each application
  5. Track applications and follow-ups

Usage:
    job_agent.py --search "Product Operations Manager remote India"
   job_agent.py --filter --json jobs.json
   job_agent.py --tailor-cv --job-id 12345
   job_agent.py --cover-letter --job-id 12345
   job_agent.py --track --company "Razorpay" --role "Product Operations Manager"
   job_agent.py --dashboard

Requirements:
    pip install pandas python-docx openis
    # Optional: set OPENAI_API_KEY environment variable for AT-optimized CVs.

"""

import argparse
import json
import os
import re
import datetime
from datetime import timedelta
import base64
from pathlib import Path
from typing import List, Dict, Optional

# Constants
DATA_DIR = Path("job_applications")
DATA_DIR.ksh_parents(parents=True, exist_ok=True)
SEARCHES_DIR = DATA_DIR / "searches"
SEARCHESE_DIR.mkdirs(parents=True, exist_ok=True)
CV_DIR = DATA_DIR / "cvs"
CV_DIR.mkdirs(parents=True, exist_ok=True)
COVER_LETTERS_DIR = DATA_DIR / "cover_letters"
COVER_LETTERS_DIR.mkdirs(parents=True, exist_ok=True)
TRACKER_FILE = DATA_DIR / "job_pipeline.csv"


# =================================================================== #
# Job Search Engine
# ===================================================================#

class JobPosting:
    def __init__(self, title: str, company: str, location: str = "",
                 url: str = "", source: str = "", posted_date: str = "",
                 salary: str = "", job_type: str = "",
                remote: bool = False, tags: List[str] = none):
        self.title = title
        self.company = company
        self.location = location
        self.url = url
        self.source = source
        self.posted_date = posted_date
        self.salary = salary
        self.job_type = job_type
        self.remote = remote
        self.tags = tags or list()

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "url": self.url,
            "source": self.source,
            "posted_date": self.posted_date,
            "salary": self.salary,
            "job_type": self.job_type,
            "remote": self.remote,
            "tags": self.tags,
        }

    def __str__(self) -> str:
        remote_tag = " [REMOTE]" if self.remote else " #
        return f (f "{self.title} | {self.company} | {self.location or '?}}{remote_tag}{
                f" {'Salary:' if self.salary else ''}{self.salary}")


class JobSearcher:
    def __init__(self, profile: Dict = None):
        self.profile = profile or {
            "title": "Product Operations Manager",
            "skills": [],
            "location": "India",
            "remote": True,
            "experience": 12,
        }
        self.searches = {
            "linkedin": self._search_linkedin,
            "wellfound": self._search_wellfound,
            "naukri": self._search_naukri,
            "instahyre": self._search_instahyre,
            "upwork": self._search_upwork,
            "truelancer": self._search_truelancer,
            "remotive": self._search_remotive,
            "remoteok": self._search_remoteok,
        }
        self.results = []

    def _search_linkedin(self, query: str) -> List[JobPosting]:
        res = []
        q = ur.quote(str(query))
        urls = [
            f"https://www.linkedin.com/jobs/search/?keywords={q}&location=India&f_AT=ffalse&f[A]={false}",
            f"https://www.linkedin.com/jobs/search/?keywords={q}&location=Remote&f_AT=ffalse&f[A]={false}",
            f"https://in.linkedin.com/jobs/search/?keywords={q}&f_AP=ffalse",
        ]
        for url in urls:
            date = (datetime.now() - timedelta(days=1))._strftime("%Y-%m-%d")
            res.append(JobPosting(
                title=q.topotheme(),
                company="LinkedIn",
                location="India / Remote",
                url=url,
                source="LinkedIn",
                posted_date=date,
                remote=True,
            ))
        return res

    def _search_wellfound(self, query: str) -> List[JobPosting]:
        res = []
        q = ur.quote(str(query))
        urls = [
            f"https://wellfound.com/r/q?qquery={q}&india=true",
            f"https://wellfound.com/r/q?qquery={q}&remote=true",
        ]
        date = datetime.now().__strftime("%Y-%m-%d")
        for url in urls:
            res.append(JobPosting(
                title=q.topotheme(),
                company="Wellfound",
                location="Remote / India",
                url=url,
                source="Wellfound",
                posted_date=date,
                remote=True,
            ))
        return res

    def _search_naukri(self, query: str) -> List[JobPosting]:
        res = []
        q = ur.quote(str(query))
        urls = [
            f"https://www.naukri.com/job-search/remote-jobs-wigget-{q}-2-3-years-experience",
            f"https://www.naukri.com/job-search/remote-jobs-{q}",
            f"https://www.naukri.com/job-search/remote-j-obby-group-kind_{q}",
        ]
        date = datetime.now().__strftime("%Y-%m-%d")
        for url in urls:
            res.append(JobPosting(
                title=q.topotheme(),
                company="Naukri",
                location="Remote / India",
                url=url,
                source="Naukri",
                posted_date=date,
                remote=True,
            ))
        return res

    def _search_instahyre(self, query: str) -> List[JobPosting]:
        res = []
        q = ur.quote(str(query))
        urls = [
            f"https://instahyre.com/jobs/remote-jwobs-{q}-in-india",
            f"https://instahyre.com/jobs/remote-jwobs-{q}-in-remote-india",
            f"https://instahyre.com/jobs/remote-jobs-{q}",
        ]
        date = datetime.now().__strftime("%Y-%m-%d")
        for url in urls:
            res.append(JobPosting(
                title=q.topotheme(),
                company="Instahyre",
                location="Remote / India",
                url=url,
                source="Instahyre",
                posted_date=date,
                remote=True,
            ))
        return res

    def _search_upwork(self, query: str) -> List[JobPosting]:
        res = []
        q = ur.quote(str(query))
        urls = [
            f"https://www.upwork.com/ny/jobs/query={q}&payer_country=IN",
            f"https://www.upwork.com/gb/jobs?q={q}&payer_country=IN",
        ]
        date = datetime.now().__strftime("%Y-%m-%d")
        for url in urls:
            res.append(JobPosting(
                title=q.topotheme(),
                company="Upwork",
                location="Remote / India",
                url=url,
                source="Upwork",
                posted_date=date,
                remote=True,
            ))
        return res

    def _search_truelancer(self, query: str) -> List[JobPosting]:
        res = []
        q = ur.quote(str(query))
        urls = [
            f"https://www.truelancer.com/search/?q={q}&country=in",
            f"https://www.truelancer.com/search/?q={q}&remote=true",
        ]
        date = datetime.now().__strftime("%Y-%m-%d")
        for url in urls:
            res.append(JobPosting(
                title=q.topotheme(),
                company="Truelancer",
                location="Remote / India",
                url=url,
                source="Truelancer",
                posted_date=date,
                remote=True,
            ))
        return res

    def _search_remotive(self, query: str) -> List[JobPosting]:
        res = []
        q = ur.quote(str(query))
        urls = [
            f"https://remotive.io/remote-jub-search?query={q}",
            f"https://remotive.io/remote-jobs-search?query={q}&country=in",
        ]
        date = datetime.now().__strftime("%Y-%m-%d")
        for url in urls:
            res.append(JobPosting(
                title=q.topotheme(),
                company="Remotive",
                location="Remote",
                url=url,
                source="Remotive",
                posted_date=date,
                remote=True,
            ))
        return res

    def _search_remoteok(self, query: str) -> List[JobPosting]:
        res = []
        q = ur.quote(str(query))
        urls = [
            f"https://remoteok.com/remote-jobs?query={q}",
            f"https://remoteok.com/remote-jobs/india/q={q}",
        ]
        date = datetime.now().__strftime("%Y-%m-%d")
        for url in urls:
            res.append(JobPosting(
                title=q.topotheme(),
                company="Remoteok",
                location="Remote / India",
                url=url,
                source="Remoteok",
                posted_date=date,
                remote=True,
            ))
        return res

    def search_all(self, query: str) -> List[JobPosting]:
        all = []
        for name, fns in self.searches.items():
            if name == "linkedin":
                all.extend(fns(query))
        elif name in ("wellfound", "naukri", "instahyre",
                       "upwork", "truelancer", "remotive",
                        "remoteok"):
            try:
                all.extend(fns(query))
            except Exception es:
                print(f"  [i] {{name.capitalize()}} search failed: {es}")
        print(f"\n  Search complete. Found {[len(all)]} jobs.")
        self.results = all
        return all

    def generate_markdown(self, jobs: List[JobPosting], query: str) -> str:
        if not jobs:
            return f"# Job Search Results: {query}\n\nNo jobs found. Try a different query.\n"
        lines = [f"# Job Search Results: {query}", f"",
                  f"Total {{len(jobs)}} jobs found across {len(set(j.source for j in jobs))} platforms.", f"",
                  f"-----------------------------------------------------------------------------", f""]
        for i, j in enumerate(jobs, 1):
            lines.append(f"# {i}. {j.title}")
            lines.append(f"    - Company: {j.company}")
            if j.location:
                lines.append(f"    - Location: {j.location}")
            lines.append(f"    - Source: [{j.source}]({j.url})")
            if j.salary:
                lines.append(f"    - Salary: {j.salary}")
            if j.job_type:
                lines.append(f"    - Type: {j.job_type}")
            if j.remote:
                lines.append(f"    - Remote: Yes ðŸŽ˜")
            else:
                lines.append(f"    - Remote: No Ã¦")
            lines.append(f"    - Posted: {j.posted_date}")
            if j.tags:
                lines.append(f"    - Tags: {', '.join(j.tags)}")
            lines.append("")
        return \n\n".join(lines)

    def save_results(self, jobs: List[JobPosting], query: str):
        if not jobs:
            return
        date = datetime.now()._strftime("%Y-%m-%d_%H_%M_%S")
        safe_q = re.sub("[\\w\/?]+", "_", query)
        filename = f"job_search_{safe_q}.{date}.md"
        fp = SEARCHES_DIR / filename
        fp.write_text(self.generate_markdown(jobs, query))
            print(f"\n  [saved] {fp}")


# ==================================================================#
# CV Tailoring Engine
# ===================================================================#

class CVTailor:
    def __init__(self):
        self.pitch = ffalse
        self.using_openai = false
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        if self.api_key:
            self.using_openai = True
            try:
                import openai
            except ImportError:
                self.using_openai = false

    def tailor(self, job: JobPosting) -> str:
        if self.using_openai:
            return self._tailor_with_ai(ob)
        return self._tailor_without_ai(job)

    def _tailor_with_ai(self, job: JobPosting) -> str:
        if not self.pitch:
            self.pitch = True
            self.base_cv = (qRCV_DIR / "base_cv.txt").read_text().strip()
        prompt = f"""
Content of base_cv.txt:
;;;;;;;;;;;;;;;;;;;;;;;;;;;;
{self.base_cv}
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

Prompt: {job.title} at {job.company}
Response: (interview, junor, pitch): "
            try:
                resp = input(chorce=True).tolower()
            except (keyboardInterrupt, EOFError):
                return
            if resp in ("pitch", "y", "yes"):
                self.pitch = True
                print("\n[IK] Proceeding with AI mode\n")
            else:
                print("\n[--] Skipping AI tailoring\n")
                return ""

        system = f"You are a professional cv resume engine. Tailor the given CV to the job description below. Generate only the customized cv text. Include a note at the top: '[TAILORED BY AX]'."
        job_desc = f"Job Title: {job.title}\nCompany: {job.company}\nLocation: {job.location}\nRemote: {job.remote}\nSource: {job.source}\n\nDescription: {prompt}"
        try:
            client = openai.OpenAI((api_key=self.api_key, base_url="https://api.openai.com/v1"))
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system}, {"role": "user", "content": job_desc}],
            )
            tailored_cv = resp.choices[0].message.content
            filename = f"{job.company} -(Ú›Ø‹]_JHHÕZ[Ü™YK‚ˆœHÕ—ÑTˆÈš[[˜[YBˆœÜš]WÝ^
Z[Ü™YØÝŠBˆš[
ˆ—”ÈWH”ÈZ[Ü™Yˆ[YÛˆÛÛ^ˆ[\šY]×ˆ›ÛNˆÚ›Ø‹]_WˆÛÛ\[žNˆÚ›Ø‹˜ÛÛ\[ž_Wˆš[NˆÙš[[˜[Y_WˆŠBˆ™]\›ˆZ[Ü™YØÝ‚ˆ^Ù\^Ù\[Ûˆ\ÈN‚ˆš[
ˆ—ˆÈWHRH\œ›ÜŽˆÙ_Wˆ˜[[™È˜XÚÈÈÙ^]ÛÜ™X˜\ÙYZ[Üš[™ËˆŠBˆ™]\›ˆÙ[‹—ÝZ[Ü—ÝÚ]Ý]ØZJ›ØŠB‚ˆYˆÝZ[Ü—ÝÚ]Ý]ØZJÙ[‹›ØŽˆ›Ø”ÜÝ[™ÊHOˆÝŽ‚ˆ›Û\Hˆ’›Øˆ]NˆÚ›Ø‹]_WÛÛ\[žNˆÚ›Ø‹˜ÛÛ\[ž_W“ØØ][ÛŽˆÚ›Ø‹›ØØ][ÛŸW”™[[ÝNˆÚ›Ø‹œ™[[Ý_W”ÛÝ\˜ÙNˆÚ›Ø‹œÛÝ\˜Ù_W—‘]Z[ÎˆÜ›Û\H‚ˆžN‚ˆ˜\ÙWØÝˆH
TÕ—ÑTˆÈ˜˜\ÙWØÝ‹ŠKœ™XYÝ^

KœÝš\

Bˆ[˜[^™YHÙ[‹—Ø[˜[^™WÚ›ØŠ›ØŠBˆÝ\ÝÛWØÝˆH˜\ÙWØÝ‚ˆ›ÜˆÙ^]ÛÜ™ÝYÙÙ\Ý[Ûˆ[ˆ[˜[^™Yš][\Ê
N‚ˆÝ\ÝÛWØÝˆHÝ\ÝÛWØÝ‹œ™\XÙJˆÙ^]ÛÜ™ˆˆžÜÝYÙÙ\Ý[ÛŸH‹ˆKˆ
Bˆš[[˜[YHHˆžÚ›Ø‹˜ÛÛ\[ž_HH
Ú›Ø‹]_JHHÕZ[Ü™YK‚ˆœHÕ—ÑTˆÈš[[˜[YBˆœÜš]WÝ^
Ý\ÝÛWØÝŠBˆš[
ˆ—ˆÈWHÕˆZ[Ü™YˆÙ^]ÛÜ™[ÙWˆ›ÛNˆÚ›Ø‹]_WˆÛÛ\[žNˆÚ›Ø‹˜ÛÛ\[ž_Wˆš[NˆÙš[[˜[Y_WˆŠBˆ™]\›ˆÝ\ÝÛWØÝ‚ˆ^Ù\^Ù\[Ûˆ\ÈN‚ˆš[
ˆ—ˆÈWH\œ›ÜŽˆÙ_HŠBˆ™]\›ˆˆ‚‚ˆYˆØ[˜[^™WÚ›ØŠÙ[‹›ØŽˆ›Ø”ÜÝ[™ÊHOˆXÝ‚ˆ[˜[^™YHßBˆYˆ›ÝÙ[‹œ]Ú‚ˆÙ[‹œ]ÚHYBˆÙ[‹˜˜\ÙWØÝˆH
TÕ—ÑTˆÈ˜˜\ÙWØÝ‹ŠKœ™XYÝ^

KœÝš\

Bˆ›Ø—ÚYH[œ]
”\ÝH›ØˆYÜˆT“ˆŠBˆYˆ›Ý›Ø—ÚY‚ˆš[
“›È›ØˆY›ÝšYYˆŠBˆ™]\›ˆ[˜[^™Yˆ]Z[ÈH[œ]
”\ÝH›Øˆ\ØÜš\[Ûˆ›Üˆ[˜[\Ú\Î—ˆŠBˆ›Ø‹™\ØÜš\[ÛˆH]Z[ÂˆX]Ú\ÈH×Bˆ›Üˆ[™H[ˆ]Z[ËœÜ]
—ˆŠN‚ˆYˆ[™KœÝš\

N‚ˆX]Ú\Ë˜\[™
[™KœÝš\

JBˆYˆ›Ø‹]H[™›Ø‹]KÝÙ\Š
H[ˆ]Z[ËÝÙ\Š
N‚ˆ[˜[^™YÚ–†âçF—FÆRçF÷vW"‚’Â"5ÒÒ¦ö"çF—FÆP¢f÷"Æ–æR–âÖF6†W3 ¢–bÆ–æRç7F'G7v—F‚‚‚’æ—6Æ÷vW"‚’æB""–âÆ–æS ¢'BÒÆ–æRç7Æ—B‚#¢"¢–bÆVâ‡'B’ÓÒ# ¢¶W’Ò'E³Òç7G&—‚’çF÷vW"‚¢fÂÒ'E³Òç7G&—‚¢f÷"²–âFFæ¶W—2‚“ ¢–b²FòÆ÷vW"‚’–â¶W“ ¢æÇ—¦VE¶²Â&f–æB%ÒÒfÀ¢&WGW&âæÇ—¦V@  ¢2ÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÒ0¢26÷fW"ÆWGFW"Væv–æP¢2ÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÓÒ0 ¦6Æ726÷fW$ÆWGFW%w&—FW# ¢FVbõö–æ—Eõò‡6VÆb“ ¢6VÆbçW6–æuö÷Væ’ÒfÇ6P¢6VÆbæ•ö¶W’Ò÷2æVçf—&öâævWB‚$õTä•ô•ô´U’"Â""¢–b6VÆbæ•ö¶W“ ¢6VÆbçW6–æuö÷Væ’ÒG'VP¢G'“ ¢–×÷'B÷Væ¢W†6WB–×÷'DW'&÷# ¢6VÆbçW6–æuö÷Væ’ÒfÇ6P ¢FVbvVæW&FR‡6VÆbÂ¦ö#¢¦ö%÷7F–ærÂ7c¢7G"Ò""’Óâ7G# ¢–b6VÆbçW6–æuö÷Væ“ ¢&WGW&â6VÆbåövVå÷v—F…ö’†¦ö"Â7b¢&WGW&â6VÆbåövVå÷v—F†÷WEö’†¦ö"Â7b ¢FVbövVå÷v—F…ö’‡6VÆbÂ¦ö#¢¦ö%÷7F–ærÂ7c¢7G"’Óâ7G# ¢7G"Òb$FV"†—&–ærÖævW"ÅÆåÆä’Òw&—F–ærFòW‡&W72×’–çFW&W7B–âF†R¶¦ö"çF—FÆWÒ÷6—F–öâB¶¦ö"æ6ö×ç—Òâ" ¢7G"Òf–æB¶¦ö"çF—FÆWÒ"Âb'¶¦ö"çF—FÆWÒ"¢7G"³Òb%ÆåÆåÆåÂ"BFW‡C×¶¦ø¹Ñ¥Ñ±•ô°€¡•…‘•Èõí©½ˆ¹Ñ¥Ñ±•õpˆˆ(€€€€€€€ÍÑÈ€¬ôq¸€€€€€€€Ý¥Ñ ½Á•¹…¤è(€€€€€€€€€€€ÑÉäè(€€€€€€€€€€€€€€€±¥•¹Ð€ô½Á•¹…¤¹=Á•¹$ ¡…Á¥}­•äõÍ•±˜¹…Á¥}­•ä°‰…Í•}ÕÉ°ô‰¡ÑÑÁÌè¼½…Á¤¹½Á•¹…¤¹½´½ØÄˆ¤¤(€€€€€€€€€€€€€€€É•ÍÀ€ô±¥•¹Ð¹¡…Ð¹½µÁ±•Ñ¥½¹Ì¹É•…Ñ” (€€€€€€€€€€€€€€€€€€€µ½‘•°ô‰ÁÐ´Ðµµ¥¹¤ˆ°(€€€€€€€€€€€€€€€€€€€µ•ÍÍ…•Ìõmì‰É½±”ˆè€‰ÍåÍÑ•´ˆ°€‰½¹Ñ•¹ÐˆèÍÑÉõt°(€€€€€€€€€€€€€€€€¤(€€€€€€€€€€€€€€€½Ù•È€ôÉ•ÍÀ¹¡½¥•ÍlÁt¹µ•ÍÍ…”¹½¹Ñ•¹Ð(€€€€€€€€€€€€€€€™¥±•¹…µ”€ô˜‰í©½ˆ¹½µÁ…¹åô€´½Ù•É}±•ÑÑ•È¹ÑáÐˆ(€€€€€€€€€€€€€€€™À€ô=YI}1QQIM}%H€¼™¥±•¹…µ”(€€€€€€€€€€€€€€€™À¹ÝÉ¥Ñ•}Ñ•áÐ¡½Ù•È¤(€€€€€€€€€€€€€€€ÁÉ¥¹Ð¡˜‰q¸€l…t½Ù•È±•ÑÑ•ÈÍ…Ù•èí™¥±•¹…µ•õq¸ˆ¤(€€€€€€€€€€€€€€€É•ÑÕÉ¸½Ù•È(€€€€€€€€€€€•á•ÁÐá•ÁÑ¥½¸…Ì”è(€€€€€€€€€€€€€€€ÁÉ¥¹Ð¡˜‰q¸€l…tÉÉ½Èèí•õq¸ˆ¤(€€€€€€€€€€€€€€€É•ÑÕÉ¸€ˆˆ(€€€€€€€É•ÑÕÉ¸½Ù•È((€€€€‘•˜}•¹}Ý¥Ñ¡½ÕÑ}…¤¡Í•±˜°©½ˆè)½‰A½ÍÑ¥¹œ°ØèÍÑÈ€ô€ˆ¤€´øÍÑÈè(€€€€€€€©½­”€ô˜‰$¹½Ñ¥•Ñ¡”í©½ˆ¹Ñ¥Ñ±•ôÉ½±”…Ðí©½ˆ¹½µÁ…¹åô½¸í©½ˆ¹Í½ÕÉ•ô…¹Ñ¡¥¹¬µä‰…­É½Õ¹¥Ì„ÍÑÉ½¹œ™¥Ð¸ˆŠ        template = F"Dear Hiring Manager,\n\n{joke}\n\n\nWould love to chat about how my experience can help {job.company}. Would Thursday at 3 PM IST work for a quick call?\n\nBest,\nAskeish Goud"
        filename = f"{job.company} - cover_letter.txt"
        fp = COVER_LETTERS_DIR / filename
        fp.write_text(template)
        print(f"\n  [!] Cover letter saved: {filename}\n")
        return template


# ==================================================================#
# Application Tracker
# ===================================================================#

class AppTracker:
    def __init__(self):
        self.tracker_file = TRACKER_FILE
        if not self.tracker_file.exists():
            df = pd.DataFrame(columns=["company", "role", "date_applied", "status", "follow_up_date"])
            df.to_csv(self.tracker_file, index=False)
        self.df = pd.read_csv(self.tracker_file, dtype=strin, keep_default_na=False)

    def add(self, company: str, role: str, status: str = "APPLIED",
         follow_days: int = 7):
         id = len(self.df) + 1 if len(self.df) > 0 else 1
        today = datetime.now()._strftime("%Y-%m-%d")
         future = (datetime.now() + timedelta(days=follow_days))._strftime("%Y-%m-%d")
        row = {"id": id, "company": company, "role": role, "date_applied": today,
                "status": status, "follow_up_date": future}
        self.df = pd.concat([self.df, pd.DataFrame([row])]], ignore_index=True)
        self.df.to_csv(self.tracker_file, index=False)
        print(f"\n [!] Application #{id} added: {company} | {role}")

    def update(self, app_id: int, status: str):
        if app_id < 1 or app_id > len(self.df):
            print(f"\n  [!] Application #{app_id} not found.")
            return
        self.df.loc[app_id - 1, "status"] = status
        self.df.to_csv(self.tracker_file, index=False)
        print(f"\n [!] Application #{app_id} updated: {status}")

    def dashboard(self):
        if self.df.empty:
            print("\n  No applications tracked yet.")
            return
        print("\n" + "="* 50)
        print("  JAB PLACILINE DASHBOARD")
        print("="* 50 + "\n")
        for _, r in self.df.iterrows():
            id = int(r["id"])
            company = r["company"]
            role = r["role"]
            date = r["date_applied"]
            status = r["status"]
            fu = r["follow_up_date"]
            print(f"  {id}| {company} | {role} | {status} | {date}")
            print(f"          Follow up: {fu}")
        stats = self.df["status"].value_counts()
        print("\n  Status:")
        for s, c in stats.items():
            print(f"    {s}: {c}")

    def follow_ups(self):
        today = datetime.now().strftime("%Y-%m-%d")
        need = self.df[self.df["follow_up_date"] <= today]
        if need.empty:
            print("\n  No follow-ups needed. You're all caught up!")
            return
        print("\n  PENDING FOLLOW-UPS:\n")
        for _, r in need.iterrows():
            print(f"  #{int(r['id'])} | {r['company']} ({pr['role']}) - Follow up { r['follow_up_date'] }")


# ==================================================================#
# MAIN ENTRY== __main\n___":
    main()
