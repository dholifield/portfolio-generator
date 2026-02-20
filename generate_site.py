import frontmatter
import glob
import markdown
import os
from datetime import date
from PIL import Image

# open profile.md with frontmatter
profile = frontmatter.load("profile.md")

# look through all .md files in the projects folder
projects = []
for path in glob.glob("projects/*.md"):
    project = frontmatter.load(path)
    if "title" not in project or "description" not in project:
        print(f"Warning: skipping {path} (missing title or description)")
        continue
    projects.append((path, project))
projects.sort(key=lambda x: x[1].get("order", 999))

year = date.today().year

# clean and set up output directory
for f in glob.glob("site/*.html"):
    os.remove(f)
for f in glob.glob("site/projects/*.html"):
    os.remove(f)
os.makedirs("site/projects", exist_ok=True)

# --- index.html generation ---

name = profile["name"]
bio = profile["bio"].strip()
portrait = profile["portrait"]

INDEX_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name}</title>
<link rel="stylesheet" href="style.css">

<body>
  <header>
    <h1>{name}</h1>
    <nav>
{nav_links}
    </nav>
  </header>

  <main>
    <div class="intro">
      <img src="photos/{portrait}" alt="{name}" class="portrait">
      <p>{bio}</p>
    </div>

    <div class="skills">
{skills_spans}
    </div>

    <p class="links">
{ext_links}
    </p>

    <h2>Projects</h2>
    <ul class="projects">
{project_items}
    </ul>
  </main>

  <footer><p>{name} · {year}</p><a href="https://github.com/dholifield/portfolio-generator">generate</a></footer>
</body>
"""


def build_project_item(slug, project):
    """Build a single <li> for the project list on the index page."""
    title = project["title"]
    desc = project["description"].strip()
    link = f"site/projects/{slug}.html"

    thumbnail = project.get("thumbnail")
    thumbnail_alt = project.get("thumbnail_alt", title)
    thumbnail_class = project.get("thumbnail_class")

    img = ""
    if thumbnail:
        cls = f' class="{thumbnail_class}"' if thumbnail_class else ""
        img = f'\n        <img src="photos/{thumbnail}" alt="{thumbnail_alt}"{cls}>'

    return f"""\
      <li>
        <div class="info">
          <h3>{title}</h3>
          <p>{desc}</p>
          <a href="{link}">read more ↝</a>
        </div>{img}
      </li>"""


nav_links = "\n".join(
    f'      <a href="{n["url"]}">{n["label"]}</a>' for n in profile["nav"]
)
skills_spans = "\n".join(
    f"      <span>{s}</span>" for s in profile["skills"]
)
ext_links = "\n".join(
    f'      <a href="{l["url"]}">{l["label"]}</a>' for l in profile["links"]
)
project_items = "\n".join(
    build_project_item(os.path.splitext(os.path.basename(p))[0], proj)
    for p, proj in projects
)

index_html = INDEX_TEMPLATE.format(
    name=name,
    bio=bio,
    portrait=portrait,
    nav_links=nav_links,
    skills_spans=skills_spans,
    ext_links=ext_links,
    project_items=project_items,
    year=year,
)

with open("index.html", "w") as f:
    f.write(index_html)
print("Generated index.html")

# --- photography.html generation ---

PHOTOGRAPHY_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Photography — {name}</title>
<link rel="stylesheet" href="../style.css">
<body>
  <header>
    <nav><a href="../index.html">↜ {name}</a></nav>
    <h1>Photography</h1>
  </header>

  <main>
    <div class="grid">
{photo_imgs}
    </div>
  </main>

  <footer><p>{name} · {year}</p><a href="https://github.com/dholifield/portfolio-generator">generate</a></footer>
</body>
"""

exts = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
photo_files = sorted(
    f for f in os.listdir("photography")
    if os.path.splitext(f)[1].lower() in exts
)

# read aspect ratios so we can balance the two CSS columns
ratios = {}
for f in photo_files:
    with Image.open(f"photography/{f}") as img:
        w, h = img.size
        ratios[f] = h / w  # height relative to width (all rendered same width)

# greedily assign images to two columns to balance total height
col1, col2 = [], []
h1, h2 = 0, 0
for f in sorted(photo_files, key=lambda f: ratios[f], reverse=True):
    if h1 <= h2:
        col1.append(f)
        h1 += ratios[f]
    else:
        col2.append(f)
        h2 += ratios[f]

# CSS columns: 2 fills top-to-bottom in col1, then col2
ordered = col1 + col2
photo_imgs = "\n".join(
    f'      <img src="../photography/{f}" alt="">' for f in ordered
)

photography_html = PHOTOGRAPHY_TEMPLATE.format(
    name=name, photo_imgs=photo_imgs, year=year
)
with open("site/photography.html", "w") as f:
    f.write(photography_html)
print("Generated site/photography.html")

# --- resume.html generation ---

resume_files = glob.glob("*.pdf")
if resume_files:
    resume_pdf = resume_files[0]

    RESUME_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Resume — {name}</title>
<link rel="stylesheet" href="../style.css">
<body>
  <header>
    <nav>
      <a href="../index.html">↜ {name}</a>
      <a href="../{resume_pdf}" download>Download</a>
    </nav>
    <h1>Resume</h1>
  </header>

  <main>
    <iframe class="resume" src="../{resume_pdf}"></iframe>
  </main>

  <footer><p>{name} · {year}</p><a href="https://github.com/dholifield/portfolio-generator">generate</a></footer>
</body>"""

    resume_html = RESUME_TEMPLATE.format(
        name=name, resume_pdf=resume_pdf, year=year
    )
    with open("site/resume.html", "w") as f:
        f.write(resume_html)
    print("Generated site/resume.html")

# --- project page generation ---

PROJECT_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — {name}</title>
<link rel="stylesheet" href="../../style.css">

<body>
  <header>
    <nav><a href="../../index.html">↜ {name}</a></nav>
    <h1>{title}</h1>
    <p>{description}</p>
  </header>

  <main>
    {body}
  </main>

  <footer><p>{name} · {year}</p><a href="https://github.com/dholifield/portfolio-generator">generate</a></footer>
</body>"""

# generate html for each project with markdown content
for path, project in projects:
    if not project.content.strip():
        continue
    body = markdown.markdown(project.content, extensions=["fenced_code"])
    html = PROJECT_TEMPLATE.format(
        name=name,
        title=project["title"],
        description=project["description"].strip(),
        body=body,
        year=year,
    )
    slug = os.path.splitext(os.path.basename(path))[0]
    output_path = f"site/projects/{slug}.html"
    with open(output_path, "w") as f:
        f.write(html)
    print(f"Generated {output_path}")
