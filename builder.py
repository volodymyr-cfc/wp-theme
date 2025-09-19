import os, shutil, zipfile, json, datetime, argparse

def build_theme(project, slug, author, extra_templates, acf_blocks):
    base_dir = os.path.dirname(__file__)
    theme_dir = os.path.join(base_dir, "new-wp-theme")  # your starter theme
    new_theme = os.path.join(base_dir, slug)

    if os.path.exists(new_theme):
        shutil.rmtree(new_theme)
    shutil.copytree(theme_dir, new_theme)

    today = datetime.date.today().isoformat()

    # style.css
    style_path = os.path.join(new_theme, "style.css")
    header = f"""/*
Theme Name: {project}
Description: Updated on {today}
Version: 1.0
Author: {author}
Text Domain: {slug}
*/\n\n"""
    with open(style_path, "w") as f:
        f.write(header)

    # package.json
    pkg_path = os.path.join(new_theme, "package.json")
    if os.path.exists(pkg_path):
        pkg = json.load(open(pkg_path))
    else:
        pkg = {}
    pkg["name"] = slug
    pkg.setdefault("version", "1.0.0")
    json.dump(pkg, open(pkg_path, "w"), indent=2)

    # Extra templates
    for name, file in extra_templates:
        path = os.path.join(new_theme, file)
        tpl = f"""<?php
/*
Template Name: {name}
*/
get_header();
while(have_posts()): the_post(); ?>
<main><h1><?php the_title(); ?></h1><?php the_content(); ?></main>
<?php endwhile;
get_footer();
"""
        with open(path, "w") as f:
            f.write(tpl)

    # ACF blocks (with renamed files)
    blocks_dir = os.path.join(new_theme, "tpl-acf-blocks")
    os.makedirs(blocks_dir, exist_ok=True)
    for b in acf_blocks:
        b_dir = os.path.join(blocks_dir, b)
        os.makedirs(b_dir, exist_ok=True)
        open(os.path.join(b_dir, f"{b}.js"), "w").write(f"// JS for {b}\n")
        json.dump({"name": f"{slug}/{b}", "title": b.title()}, open(os.path.join(b_dir, f"{b}.json"), "w"), indent=2)
        open(os.path.join(b_dir, f"{b}.php"), "w").write(f"<?php echo '<div>{b} block</div>'; ?>")
        open(os.path.join(b_dir, f"{b}.scss"), "w").write(f".block-{b} {{}}")

    # Zip it
    zip_path = os.path.join(base_dir, f"{slug}.zip")
    shutil.make_archive(zip_path.replace(".zip", ""), "zip", new_theme)
    print(f"✅ Built theme: {zip_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project")
    parser.add_argument("--slug")
    parser.add_argument("--author")
    parser.add_argument("--extra", nargs="*")
    parser.add_argument("--blocks", nargs="*")
    args = parser.parse_args()

    extras = []
    for e in args.extra or []:
        if ":" in e:
            name, file = e.split(":", 1)
            extras.append((name, file))

    build_theme(args.project, args.slug, args.author, extras, args.blocks or [])
