from pathlib import Path

p = Path('index.html')
s = p.read_text()

old = '''      function enforcePenaltyYards(team, yards) {
        let offense = S.pos;
        let movement = team === offense ? -yards : yards;
        S.ball += dir() * movement;
        if (S.ball >= 100 || S.ball <= 0) {
          if ((offense === 0 && S.ball >= 100) || (offense === 1 && S.ball <= 0)) {
            S.ball = offense === 0 ? 100 : 0;
            td();
          } else {
            safety();
          }
          return;
        }
        S.ball = Math.max(1, Math.min(99, S.ball));
      }'''
new = '''      function enforcePenaltyYards(team, yards) {
        let offense = S.pos;
        let movement = team === offense ? -yards : yards;
        let proposed = S.ball + dir() * movement;
        // Penalty yardage alone can never create a touchdown or safety.
        // Enforcement stops at the appropriate 1-yard line.
        S.ball = Math.max(1, Math.min(99, proposed));
        // Penalties do not consume, replay, or otherwise change the current down.
        // There are no automatic first downs. If the enforced spot naturally
        // reaches the existing line to gain, update to a normal first down.
        let reached = dir() === 1 ? S.ball >= S.gain : S.ball <= S.gain;
        if (reached) {
          S.down = 1;
          S.gain = Math.max(0, Math.min(100, S.ball + dir() * 10));
          S.stats[offense].firstDowns++;
          S.log.push("<b>FIRST DOWN</b> reached by penalty yardage.");
        }
      }'''
if old not in s:
    raise SystemExit('Could not find current penalty yardage function')
s = s.replace(old, new)
p.write_text(s)

rp = Path('rules.html')
r = rp.read_text()
needle = '''        <div class="rule"><b>Special-teams throw requirements:</b> When a play requires an airmail, a throw that does not meet that requirement simply does not count. It is not an additional penalty.</div>'''
addition = needle + '''
        <div class="rule"><b>Goal-line enforcement:</b> Penalty yardage can move the ball no farther than the 1-yard line at either end of the field. A penalty by itself cannot result in a touchdown or safety.</div>
        <div class="rule"><b>No automatic first down:</b> A defensive penalty does not automatically award a first down. If the enforced penalty yardage naturally reaches or passes the existing line to gain, it becomes a first down normally.</div>
        <div class="rule"><b>Current play continues:</b> A penalty does not consume the down, replay the down, or start a new down. After the penalty is enforced, the current round/play resumes with the bags that remain, unless the specific penalty says otherwise. Interference is the exception because that penalty ends the round immediately.</div>'''
if needle not in r:
    raise SystemExit('Could not find penalties section insertion point')
r = r.replace(needle, addition)
rp.write_text(r)
