import os

src_dir = '/Users/hojin9/dev/jinysite/강화학습/src'
for root, dirs, files in os.walk(src_dir):
    for f in files:
        if f.endswith('.md'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8') as fl:
                c = fl.read()
                if '$$' in c:
                    rel = os.path.relpath(p, src_dir)
                    print(f'{rel}: {c.count("$$")}')
