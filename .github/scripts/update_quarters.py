from pathlib import Path
p=Path('index.html'); s=p.read_text()

# Generic special-teams player picker. Any player on the team can handle special teams.
needle='''      function playerById(id) {
        ensureRoster();
        return S.roster.find((p) => p.id === id);
      }'''
add=needle+'''
      function specialTeamSelect(team, label) {
        ensureRoster();
        return '<label style="display:block;margin:10px 0 5px">'+label+'</label><select class="name" id="specialThrower"><option value="">Select player...</option>'+S.roster.filter(p=>p.team===team).map(p=>'<option value="'+p.id+'">'+p.name+'</option>').join('')+'</select>';
      }
      function requireSpecialThrower() {
        let el=document.getElementById("specialThrower");
        if(!el || !el.value){ alert("Select the player making this special-teams throw first."); return null; }
        return playerById(el.value);
      }'''
if needle not in s: raise SystemExit('playerById marker missing')
s=s.replace(needle,add,1)

# Kickoff picker belongs to kicking team (opposite current receiving possession).
old='''        picktext.textContent = "How many of the four airmails were made?";
        choices.innerHTML = "";'''
new='''        picktext.textContent = "How many of the four airmails were made?";
        choices.innerHTML = specialTeamSelect(1-S.pos, "Kickoff Player");'''
if old not in s: raise SystemExit('kickoff picker missing')
s=s.replace(old,new,1)
# preserve select while adding number buttons (currently append works)

old='''      function airResolve(n) {
        snap();
        stop();
        let k = 1 - S.pos;'''
new='''      function airResolve(n) {
        let thrower=requireSpecialThrower();
        if(!thrower) return;
        snap();
        stop();
        let k = 1 - S.pos;'''
if old not in s: raise SystemExit('airResolve missing')
s=s.replace(old,new,1)
s=s.replace('''            S.names[k] +
            " " +
            n +''','''            S.names[k] + " (" + thrower.name + ") " + n +''',1)

# Return picker and validation; same selected player stays for consecutive return airmails.
old='''        choices.innerHTML =
          '<button class="btn primary" onclick="kickReturnThrow(true)">AIRMAIL MADE</button><button class="btn red" onclick="kickReturnThrow(false)">MISS</button>';'''
new='''        choices.innerHTML = specialTeamSelect(S.pos, label + " Player") +
          '<button class="btn primary" onclick="kickReturnThrow(true)">AIRMAIL MADE</button><button class="btn red" onclick="kickReturnThrow(false)">MISS</button>';'''
if old not in s: raise SystemExit('return choices missing')
s=s.replace(old,new,1)
old='''      function kickReturnThrow(made) {
        let r = S.pos,'''
new='''      function kickReturnThrow(made) {
        let thrower=requireSpecialThrower();
        if(!thrower) return;
        let r = S.pos,'''
if old not in s: raise SystemExit('return function missing')
s=s.replace(old,new,1)
s=s.replace('''            "<b>RETURN:</b> airmail " + kickReturnCount + " made (+10 yards)",''','''            "<b>RETURN:</b> " + thrower.name + " airmail " + kickReturnCount + " made (+10 yards)",''',1)

# Punt: select punter before choosing holes; selection is retained through board-bag step.
old='''        choices.innerHTML = "";
        for (let i = 0; i <= 4; i++) {'''
new='''        choices.innerHTML = specialTeamSelect(S.pos, "Punter");
        for (let i = 0; i <= 4; i++) {'''
# first occurrence after punt() only; locate safely
idx=s.index('      function punt() {'); pos=s.index(old,idx); s=s[:pos]+s[pos:].replace(old,new,1)
# store chosen punter when moving to boards
old='''      function puntPickHoles(n) {
        puntHoles = n;'''
new='''      let selectedPunter = null;
      function puntPickHoles(n) {
        let thrower=requireSpecialThrower();
        if(!thrower) return;
        selectedPunter=thrower.id;
        puntHoles = n;'''
if old not in s: raise SystemExit('puntPick missing')
s=s.replace(old,new,1)
# log punter
old='''          "<b>PUNT:</b> " +
            puntHoles +'''
new='''          "<b>PUNT:</b> " +
            (playerById(selectedPunter)?.name || "Unknown") + " — " + puntHoles +'''
if old not in s: raise SystemExit('punt log missing')
s=s.replace(old,new,1)

# Field goal selection and validation.
old='''        choices.innerHTML =
          '<button class="btn primary" onclick="fgR(true)">GOOD</button><button class="btn red" onclick="fgR(false)">NO GOOD</button>';'''
new='''        choices.innerHTML = specialTeamSelect(S.pos, "Field Goal Player") +
          '<button class="btn primary" onclick="fgR(true)">GOOD</button><button class="btn red" onclick="fgR(false)">NO GOOD</button>';'''
if old not in s: raise SystemExit('fg choices missing')
s=s.replace(old,new,1)
old='''      function fgR(ok) {
        snap();'''
new='''      function fgR(ok) {
        let thrower=requireSpecialThrower();
        if(!thrower) return;
        snap();'''
if old not in s: raise SystemExit('fgR missing')
s=s.replace(old,new,1)
s=s.replace('''          S.log.push("<b>FIELD GOAL GOOD!</b> +3");''','''          S.log.push("<b>FIELD GOAL GOOD!</b> " + thrower.name + " +3");''',1)
s=s.replace('''          S.log.push("<b>FIELD GOAL NO GOOD.</b> Turnover at " + spotText());''','''          S.log.push("<b>FIELD GOAL NO GOOD.</b> " + thrower.name + ". Turnover at " + spotText());''',1)

# Conversion selection and validation.
old='''        choices.innerHTML =
          '<button class="btn" onclick="conv(1,true)">PAT Good</button><button class="btn red" onclick="conv(1,false)">PAT Miss</button><button class="btn" onclick="conv(2,true)">2PT Good</button><button class="btn red" onclick="conv(2,false)">2PT Miss</button>';'''
new='''        let t=S.lastTD ?? S.pos;
        choices.innerHTML = specialTeamSelect(t, "Conversion Player") +
          '<button class="btn" onclick="conv(1,true)">PAT Good</button><button class="btn red" onclick="conv(1,false)">PAT Miss</button><button class="btn" onclick="conv(2,true)">2PT Good</button><button class="btn red" onclick="conv(2,false)">2PT Miss</button>';'''
if old not in s: raise SystemExit('conversion choices missing')
s=s.replace(old,new,1)
old='''      function conv(p, ok) {
        snap();'''
new='''      function conv(p, ok) {
        let thrower=requireSpecialThrower();
        if(!thrower) return;
        snap();'''
if old not in s: raise SystemExit('conv missing')
s=s.replace(old,new,1)
s=s.replace('''          S.log.push("<b>" + (p == 1 ? "PAT" : "2-POINT") + " GOOD</b> +" + p);''','''          S.log.push("<b>" + (p == 1 ? "PAT" : "2-POINT") + " GOOD</b> " + thrower.name + " +" + p);''',1)
s=s.replace('''          S.log.push("<b>" + (p == 1 ? "PAT" : "2-POINT") + " NO GOOD</b>");''','''          S.log.push("<b>" + (p == 1 ? "PAT" : "2-POINT") + " NO GOOD</b> " + thrower.name);''',1)

p.write_text(s)
