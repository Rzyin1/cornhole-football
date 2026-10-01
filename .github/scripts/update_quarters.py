from pathlib import Path

p=Path('index.html')
s=p.read_text()
needle='''      .modal .card {
        width: min(500px, 100%);
      }'''
replacement='''      .modal .card {
        width: min(500px, 100%);
        max-height: calc(100vh - 30px);
        overflow-y: auto;
        overscroll-behavior: contain;
      }
      #setup {
        align-items: flex-start;
        overflow-y: auto;
      }
      #setup > .card {
        margin: auto;
      }'''
if needle not in s:
    raise SystemExit('modal card CSS not found')
s=s.replace(needle,replacement,1)
p.write_text(s)
