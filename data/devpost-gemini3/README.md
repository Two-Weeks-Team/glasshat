# Gemini 3 Devpost Crawl Dataset

This directory contains a crawl of the **Gemini 3 Hackathon** on Devpost.
It is intended to be consumed by LLMs, data scripts, and analysis notebooks.

- Source hackathon: <https://gemini3.devpost.com/>
- Rules page: <https://gemini3.devpost.com/rules>
- Project gallery: <https://gemini3.devpost.com/project-gallery>
- Crawl time: `2026-05-15T07:16:29Z` → `2026-05-15T07:30:45Z`
- Crawl strategy: sequentially paginated gallery pages and stopped after collecting at least 500 submissions.
- Pages crawled: `1` through `21`
- Submissions collected: `503`
- Project detail pages fetched: `503`
- Winner-labelled submissions in collected set: `13`
- Project detail fetch errors: `0`

> Important: Devpost exposes more than 503 gallery entries for this hackathon. This dataset intentionally stops after the first `>=500` gallery submissions, per collection requirement.

## Quick Start for LLMs

If you are an LLM reading this dataset:

1. Start with `gemini3_dataset.json` if you need everything in one file.
2. Use `projects.json` if you need each submitted project's detailed content, including GitHub repositories and video links.
3. Use `submissions.csv` or `submissions.json` if you only need gallery-level metadata.
4. Use `winners.json` for the subset of collected gallery entries marked as winners.
5. Use `rules.txt` for the hackathon rules in plain text.

Recommended primary file for most analysis:

```text
data/devpost-gemini3/projects.json
```

Each object in `projects.json` corresponds to one Devpost project detail page.

## Files

| File | Purpose | When to use |
|---|---|---|
| `gemini3_dataset.json` | Full combined dataset: crawl metadata, hackathon metadata, overview, rules references, submissions, winners, projects | Best single-file entry point |
| `projects.json` | Detailed data from each project page | Use for analysis of project ideas, GitHub repos, demos, videos, tech stack, descriptions |
| `submissions.json` | Gallery-level submissions only | Use for lightweight listing, pagination order, winner flags |
| `submissions.csv` | CSV version of gallery-level submissions | Use for spreadsheets or quick tabular filtering |
| `winners.json` | Gallery entries that showed a Devpost `Winner` badge | Use for winner-only analysis |
| `rules.txt` | Plain-text hackathon rules | Use for LLM ingestion and rule summarization |
| `rules.html` | Raw HTML snapshot of the rules page | Use when plain text loses structure |

## High-Level Counts

```json
{
  "submissions": 503,
  "projects": 503,
  "winners": 13,
  "project_errors": 0,
  "projects_with_github": 297,
  "projects_with_video": 462,
  "projects_with_description": 425,
  "projects_with_built_with": 496
}
```

Notes:

- Not every Devpost project includes a GitHub link.
- Not every project includes a long story/description section.
- `github_repos`, `video_links`, and `description` are extracted from public project detail pages when present.
- Empty arrays/strings usually mean the project page did not expose that field publicly, not necessarily that the project lacks it.

## Data Model

### `gemini3_dataset.json`

Top-level shape:

```json
{
  "crawl": {},
  "hackathon": {},
  "overview": {},
  "rules": {},
  "submissions": [],
  "winners": [],
  "projects": []
}
```

#### `crawl`

Metadata about this crawl run.

| Field | Meaning |
|---|---|
| `started_at` | UTC start timestamp |
| `finished_at` | UTC finish timestamp |
| `target_count` | Requested target count (`540`) |
| `stop_at` | Stop threshold (`500`) |
| `stop_goal_effective` | Effective threshold used by crawler (`500`) |
| `pages_crawled` | Number of gallery pages crawled (`21`) |
| `submission_count` | Number of gallery submissions collected (`503`) |
| `project_detail_count` | Number of project detail pages fetched (`503`) |
| `winner_count_in_collected_gallery` | Winner-labelled submissions in collected gallery subset (`13`) |

#### `hackathon`

Hackathon-level metadata from Devpost's public hackathon API.

Important fields:

| Field | Meaning |
|---|---|
| `id` | Devpost challenge ID (`27555`) |
| `title` | Hackathon title |
| `url` | Hackathon URL |
| `open_state` | Devpost state, e.g. `ended` |
| `submission_period_dates` | Public submission period text |
| `registrations_count` | Public registration count |
| `organization_name` | Organizer |
| `themes` | Devpost themes/categories |
| `prize_amount` | Prize amount HTML/text from API |
| `winners_announced` | Whether Devpost says winners are announced |
| `submission_gallery_url` | Gallery URL |

#### `overview`

Text and metadata extracted from the hackathon landing page.

| Field | Meaning |
|---|---|
| `url` | Hackathon landing page |
| `title` | HTML page title |
| `meta_description` | Meta description if present |
| `text` | Plain text extracted from the overview page |

#### `rules`

References to rule files written in this directory.

| Field | Meaning |
|---|---|
| `url` | Rules URL |
| `html_path` | Relative path to saved HTML (`rules.html`) |
| `text_path` | Relative path to saved text (`rules.txt`) |
| `chars` | Character count of extracted rules text |

### `submissions.json`

Gallery-level data. These records come from paginated gallery pages, not the full project detail page.

Each item shape:

```json
{
  "software_id": "1156703",
  "title": "Globot",
  "tagline": "Multi-Agents...",
  "url": "https://devpost.com/software/globot-341w9q",
  "page": 1,
  "is_winner": true,
  "thumbnail_url": "https://...",
  "member_names": ["Victor Mei", "Yihang Deng"]
}
```

Field guide:

| Field | Meaning |
|---|---|
| `software_id` | Devpost internal software/project ID from gallery HTML |
| `title` | Project title shown in gallery |
| `tagline` | Short gallery tagline |
| `url` | Project detail page URL |
| `page` | Gallery page number where this item was found |
| `is_winner` | Whether the gallery card displayed a `Winner` badge |
| `thumbnail_url` | Gallery thumbnail image URL |
| `member_names` | Names shown on member avatars in gallery card |

### `projects.json`

Detailed data extracted from each project detail page.
This is the most important file for LLM analysis of submitted projects.

Each item shape:

```json
{
  "url": "https://devpost.com/software/globot-341w9q",
  "title": "Globot",
  "tagline": "Multi-Agents...",
  "video_links": ["https://www.youtube.com/embed/..."],
  "github_repos": ["https://github.com/Vector897/Globot"],
  "built_with": ["chromadb", "clerk", "crewai", "fastapi", "gemini-3-flash"],
  "story_sections": {
    "inspiration": "...",
    "what_it_does": "...",
    "how_we_built_it": "..."
  },
  "description": "Combined story text...",
  "external_links": [],
  "award_text": "Submitted to Gemini 3 Hackathon Winner Grand Prize",
  "fetched_at": "2026-05-15T07:16:...Z",
  "software_id": "1156703",
  "gallery_page": 1,
  "is_winner": true
}
```

Field guide:

| Field | Meaning |
|---|---|
| `url` | Devpost project page URL |
| `title` | Project title from project page |
| `tagline` | Short project description from meta/project header |
| `video_links` | Public video embeds found on the project page, usually YouTube/Vimeo |
| `github_repos` | GitHub repository links found on the project page |
| `built_with` | Technologies/tags listed in Devpost's `Built With` section |
| `story_sections` | Sectioned project writeup, keyed by normalized headings |
| `description` | Combined long-form project story text from available sections |
| `external_links` | Other non-Devpost external links found on the page |
| `award_text` | Text from the Devpost submitted-to/award area; may include prize name |
| `fetched_at` | UTC timestamp for detail page fetch |
| `software_id` | Devpost internal project ID, copied from gallery data |
| `gallery_page` | Gallery page where the project was discovered |
| `is_winner` | Winner flag copied from gallery data |

#### Where are GitHub repositories?

GitHub links are in:

```text
projects.json -> each item -> github_repos
```

And in the combined file:

```text
gemini3_dataset.json -> projects[] -> github_repos
```

Example:

```json
{
  "title": "Globot",
  "github_repos": [
    "https://github.com/Vector897/Globot"
  ]
}
```

#### Where are video links?

Video links are in:

```text
projects.json -> each item -> video_links
```

They are usually YouTube embed URLs from Devpost project media galleries.

#### Where are descriptions?

Use either:

```text
projects.json -> each item -> description
```

or the more structured:

```text
projects.json -> each item -> story_sections
```

Common `story_sections` keys include:

- `inspiration`
- `what_it_does`
- `how_we_built_it`
- `challenges_we_ran_into`
- `accomplishments_we_re_proud_of`
- `what_we_learned`
- `what_s_next_for_*`

Keys are normalized from the original Devpost headings, so they may vary by project.

### `winners.json`

Subset of `submissions.json` where `is_winner` is `true`.
These are based on the Devpost gallery `Winner` badge within the first 503 collected submissions.

Important limitation:

- `winners.json` is gallery-card level data.
- For detailed winner project information, join by `url` or `software_id` against `projects.json`.

Example join logic:

```python
import json

submissions = json.load(open("submissions.json"))
projects = json.load(open("projects.json"))
projects_by_url = {p["url"]: p for p in projects}

winner_details = [projects_by_url[w["url"]] for w in submissions if w["is_winner"]]
```

## Suggested LLM Workflows

### 1. Analyze product ideas

Use `projects.json` and read:

- `title`
- `tagline`
- `description`
- `story_sections.what_it_does`
- `story_sections.how_we_built_it`
- `built_with`

### 2. Analyze implementation/open-source repos

Use `projects.json` and filter:

```python
[p for p in projects if p["github_repos"]]
```

Read:

- `title`
- `github_repos`
- `built_with`
- `description`

### 3. Analyze winning projects

Use `winners.json` for the winner list, then join with `projects.json` by `url`.

Read:

- `award_text`
- `title`
- `tagline`
- `description`
- `github_repos`
- `video_links`
- `built_with`

### 4. Summarize rules

Use `rules.txt` for plain-text rule analysis.
Use `rules.html` only if formatting or original structure is needed.

## Python Examples

### Load all project details

```python
import json
from pathlib import Path

base = Path("data/devpost-gemini3")
projects = json.loads((base / "projects.json").read_text())
print(len(projects))
```

### Find projects with GitHub repositories

```python
with_github = [p for p in projects if p.get("github_repos")]
for p in with_github[:10]:
    print(p["title"], p["github_repos"])
```

### Find projects with videos but no GitHub

```python
video_no_github = [
    p for p in projects
    if p.get("video_links") and not p.get("github_repos")
]
```

### Join winners with full project details

```python
winners = json.loads((base / "winners.json").read_text())
projects_by_url = {p["url"]: p for p in projects}
winner_details = [projects_by_url[w["url"]] for w in winners if w["url"] in projects_by_url]
```

### Export a compact LLM prompt context

```python
compact = [
    {
        "title": p["title"],
        "url": p["url"],
        "tagline": p.get("tagline", ""),
        "github_repos": p.get("github_repos", []),
        "video_links": p.get("video_links", []),
        "built_with": p.get("built_with", []),
        "description": p.get("description", "")[:2000],
        "is_winner": p.get("is_winner", False),
        "award_text": p.get("award_text", "")
    }
    for p in projects
]
```

## Known Limitations

- Dataset covers the first 503 submissions discovered by sequential gallery pagination, not the entire hackathon gallery.
- Devpost page content can change after crawl time.
- Some projects do not publish GitHub repos, demos, or detailed writeups.
- `is_winner` comes from the gallery badge in the collected pages.
- `award_text` is parsed from project detail pages and may include surrounding text, not a perfectly normalized award category.
- `description` is extracted from public HTML and may omit unusual custom formatting.

## Provenance

The crawler used:

- Devpost public hackathon API for hackathon metadata.
- Server-rendered Devpost HTML for rules, gallery cards, and project detail pages.
- Sequential pagination from page 1 until collected submissions exceeded 500.

No private authentication was used.
