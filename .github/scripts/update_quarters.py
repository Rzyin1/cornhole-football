from pathlib import Path

p=Path('index.html')
s=p.read_text()

old='''      function refreshThrowers() {
        if (!document.getElementById("offThrower")) return;
        let o = eligible(S.pos, "offense"),
          d = eligible(1 - S.pos, "defense");
        offThrower.innerHTML = o
          .map((p) => '<option value="' + p.id + '">' + p.name + "</option>")
          .join("");
        defThrower.innerHTML = d
          .map((p) => '<option value="' + p.id + '">' + p.name + "</option>")
          .join("");
      }'''
new='''      function refreshThrowers() {
        if (!document.getElementById("offThrower")) return;
        let o = eligible(S.pos, "offense"),
          d = eligible(1 - S.pos, "defense"),
          oldO = offThrower.value,
          oldD = defThrower.value;
        offThrower.innerHTML = '<option value="">Select thrower...</option>' + o
          .map((p) => '<option value="' + p.id + '">' + p.name + "</option>")
          .join("");
        defThrower.innerHTML = '<option value="">Select thrower...</option>' + d
          .map((p) => '<option value="' + p.id + '">' + p.name + "</option>")
          .join("");
        if (o.some((p) => p.id === oldO)) offThrower.value = oldO;
        if (d.some((p) => p.id === oldD)) defThrower.value = oldD;
      }
      function clearThrowerSelections() {
        if (document.getElementById("offThrower")) offThrower.value = "";
        if (document.getElementById("defThrower")) defThrower.value = "";
      }'''
if old not in s:
    raise SystemExit('refreshThrowers not found')
s=s.replace(old,new,1)

old='''        let op = playerById(offThrower.value),
          dp = playerById(defThrower.value);
        if (!op || !dp) {
          alert("Select an offensive and defensive thrower.");
          return;
        }'''
new='''        if (!offThrower.value || !defThrower.value) {
          alert("Select both the offensive thrower and defensive thrower before submitting the round.");
          return;
        }
        let op = playerById(offThrower.value),
          dp = playerById(defThrower.value);
        if (!op || !dp) {
          alert("Select both the offensive thrower and defensive thrower before submitting the round.");
          return;
        }'''
if old not in s:
    raise SystemExit('submit thrower validation not found')
s=s.replace(old,new,1)

old='''        apply(y);
        resetBags();
        if (S.sec <= 0) S.quarterRoundFinished = true;'''
new='''        apply(y);
        resetBags();
        clearThrowerSelections();
        if (S.sec <= 0) S.quarterRoundFinished = true;'''
if old not in s:
    raise SystemExit('round reset point not found')
s=s.replace(old,new,1)

p.write_text(s)
