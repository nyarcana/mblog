import markdown
import os
import shutil
from datetime import datetime

POST_DIR = "posts/"

def compile_post_contents(post_path):
    md = markdown.Markdown(extensions=["meta", "fenced_code", "nl2br"])
    with open(post_path, "r") as f:
        html = md.convert(f.read())
        return md.Meta, html
    
def fill_template(template, contents):
    return template.format_map(contents)

def load_templates():
    templates = {}
    for filename in os.listdir("templates"):
        filepath = os.path.join("templates", filename)
        if os.path.isfile(filepath):
            with open(filepath, "r") as f:
                templates[filename] = f.read()
    return templates

class Post:
    def __init__(self, name, metadata, html, card_html):
        self.name = name
        self.metadata = metadata
        self.html = html
        self.card_html = card_html

        
        self.date = datetime.strptime(metadata["date"][0], "%Y-%m-%d %H:%M")

def main():
    build_dir = "build"
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    
    # Copy statics over
    shutil.copytree("static", f"{build_dir}/static")

    # Read in templates
    templates = load_templates()

    # Build posts
    posts = []
    for post_file in os.listdir("posts"):
        metadata, html = compile_post_contents(f"posts/{post_file}")
        html_name = post_file.replace(".md", ".html")
        card_html = fill_template(templates["post_panel.html"], {"post_title": metadata["title"][0], "post_description": metadata["description"][0], "post_date": metadata["date"][0], "post_link": f"/posts/{html_name}"})
        post = Post(html_name, metadata, html, card_html)
        posts.append(post)
    
    # Sort by the date
    posts.sort(key=lambda p: p.date, reverse=True)

    post_panels_html = ""
    for post in posts:
        post_panels_html += post.card_html
        post_panels_html += "\n"
    
    # Create index
    with open(f"{build_dir}/index.html", "w") as f:
        contents = fill_template(templates["index.html"], {"header": templates["header.html"], "footer": templates["footer.html"], "head": templates["head.html"], "posts": post_panels_html})
        f.write(contents)
    
    # Create posts
    os.makedirs(f"{build_dir}/posts")
    for post in posts:
        with open(f"{build_dir}/posts/{post.name}", "w") as f:
            args = {
                "header": templates["header.html"],
                "footer": templates["footer.html"],
                "head": templates["head.html"],
                "post": post.html
            }
            f.write(fill_template(templates["post.html"], args))
if __name__ == "__main__":
    main()