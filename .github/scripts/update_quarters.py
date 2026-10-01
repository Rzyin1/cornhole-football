from pathlib import Path

p = Path('index.html')
s = p.read_text()

# Add overtime state fields.
s = s.replace('ot: false,\n        clockHoldRound: false,', 'ot: false,\n        otFirst: null,\n        otPossessions: [0, 0],\n        otSuddenDeath: false,\n        otOpeningFGTeam: null,\n        otGameOver: false,\n        clockHoldRound: false,')
s = s.replace('if (S.quarterRoundFinished == null) S.quarterRoundFinished = false;', 'if (S.quarterRoundFinished == null) S.quarterRoundFinished = false;\n      if (S.otFirst == null) S.otFirst = null;\n      if (!Array.isArray(S.otPossessions)) S.otPossessions = [0, 0];\n      if (S.otSuddenDeath == null) S.otSuddenDeath = false;\n      if (S.otOpeningFGTeam == null) S.otOpeningFGTeam = null;\n      if (S.otGameOver == null) S.otGameOver = false;', 1)

# Overtime helper functions inserted before apply().
needle = '      function apply(y) {'
helpers = '''      function endOT(winner, reason) {
        S.otGameOver = true;
        stop();
        S.log.push("<b>OVERTIME GAME OVER:</b> " + S.names[winner] + " wins" + (reason ? " — " + reason : "") + ".");
        render();
        alert(S.names[winner] + " wins in overtime" + (reason ? " — " + reason : "") + "!");
      }
      function otPossessionEnded(team, scoredType) {
        if (!S.ot || S.otGameOver) return false;
        S.otPossessions[team]++;
        if (scoredType === "TD") {
          endOT(team, "touchdown");
          return true;
        }
        if (scoredType === "SAFETY") {
          endOT(team, "safety");
          return true;
        }
        if (S.otSuddenDeath) {
          if (scoredType === "FG") {
            endOT(team, "field goal in sudden death");
            return true;
          }
          return false;
        }
        if (scoredType === "FG") {
          if (S.otOpeningFGTeam == null) {
            S.otOpeningFGTeam = team;
            S.log.push("<b>OVERTIME:</b> " + S.names[1 - team] + " gets one possession to tie with a field goal or win with a touchdown.");
          } else if (S.otOpeningFGTeam !== team) {
            S.otSuddenDeath = true;
            S.log.push("<b>OVERTIME:</b> Both teams made field goals. Next score wins.");
          }
          return false;
        }
        if (S.otPossessions[0] > 0 && S.otPossessions[1] > 0 && S.score[0] === S.score[1]) {
          S.otSuddenDeath = true;
          S.log.push("<b>OVERTIME:</b> Both teams have had an offensive possession and the game is still tied. Next score wins.");
        } else if (S.otOpeningFGTeam != null && team !== S.otOpeningFGTeam && S.score[team] < S.score[S.otOpeningFGTeam]) {
          endOT(S.otOpeningFGTeam, "opponent failed to answer the field goal");
          return true;
        }
        return false;
      }
'''
if helpers not in s:
    s = s.replace(needle, helpers + needle)

# Turnover on downs ends an OT possession.
s = s.replace('S.log.push("<b>TURNOVER ON DOWNS</b> at " + spotText());\n          switchPos();', 'S.log.push("<b>TURNOVER ON DOWNS</b> at " + spotText());\n          if (S.ot && otPossessionEnded(o, null)) return;\n          switchPos();')

# Forced turnover ends an OT possession.
s = s.replace('S.log.push(\n          "<b>TURNOVER:</b> defensive bag knocked an offensive bag off the board and went in the hole at " +\n            spotText(),\n        );\n        switchPos();', 'S.log.push(\n          "<b>TURNOVER:</b> defensive bag knocked an offensive bag off the board and went in the hole at " +\n            spotText(),\n        );\n        let oldOffense = S.pos;\n        if (S.ot && otPossessionEnded(oldOffense, null)) return;\n        switchPos();')

# Touchdown immediately ends OT, without conversion/kickoff.
s = s.replace('S.log.push("<b>TOUCHDOWN " + S.names[t] + "!</b> +6");\n        stop();\n        render();\n        conversion();', 'S.log.push("<b>TOUCHDOWN " + S.names[t] + "!</b> +6");\n        stop();\n        if (S.ot) {\n          otPossessionEnded(t, "TD");\n          return;\n        }\n        render();\n        conversion();')

# Safety immediately ends OT for the defensive/scoring team.
s = s.replace('S.score[defense] += 2;\n        S.log.push(', 'S.score[defense] += 2;\n        if (S.ot) {\n          S.log.push("<b>SAFETY!</b> " + S.names[defense] + " +2.");\n          otPossessionEnded(defense, "SAFETY");\n          return;\n        }\n        S.log.push(')

# Punt ends the punting team possession in OT but play continues through punt return.
s = s.replace('let p = S.pos,\n          receiver = 1 - p,', 'let p = S.pos,\n          receiver = 1 - p,')
s = s.replace('S.pos = receiver;\n        S.down = 1;', 'if (S.ot) otPossessionEnded(p, null);\n        if (S.otGameOver) return;\n        S.pos = receiver;\n        S.down = 1;', 1)

# Field goals use OT response/sudden-death logic. Miss ends possession.
s = s.replace('S.log.push("<b>FIELD GOAL GOOD!</b> +3");\n          S.pos = 1 - t;', 'S.log.push("<b>FIELD GOAL GOOD!</b> +3");\n          if (S.ot) {\n            if (otPossessionEnded(t, "FG")) return;\n          }\n          S.pos = 1 - t;')
s = s.replace('S.log.push("<b>FIELD GOAL NO GOOD.</b> Turnover at " + spotText());\n          switchPos();', 'S.log.push("<b>FIELD GOAL NO GOOD.</b> Turnover at " + spotText());\n          if (S.ot && otPossessionEnded(t, null)) return;\n          switchPos();')

# OT kickoffs do not start a clock.
s = s.replace('if (S.sec > 0) startClock();', 'if (!S.ot && S.sec > 0) startClock();')

# Replace end-of-regulation OT entry with Rock/Paper/Scissors setup and no clock.
old = '''        } else if (S.score[0] == S.score[1]) {
          S.ot = true;
          S.to = [3, 3];
          S.sec = 1200;
          S.clockHoldRound = false;
          S.quarterRoundFinished = false;
          S.log.push("<b>OVERTIME</b>");
          render();
        } else alert("Game over.");'''
new = '''        } else if (S.score[0] == S.score[1]) {
          S.ot = true;
          S.to = [3, 3];
          S.sec = 0;
          S.run = false;
          S.clockHoldRound = false;
          S.quarterRoundFinished = false;
          S.otFirst = null;
          S.otPossessions = [0, 0];
          S.otSuddenDeath = false;
          S.otOpeningFGTeam = null;
          S.otGameOver = false;
          S.log.push("<b>OVERTIME</b> — no time limit. Rock, Paper, Scissors determines who chooses to kick or receive.");
          render();
          overtimeSetup();
        } else alert("Game over.");'''
if old not in s:
    raise SystemExit('Could not find current overtime entry block')
s = s.replace(old, new)

# Add OT setup chooser before undo().
needle2 = '      function undo() {'
ot_setup = '''      function overtimeSetup() {
        picktitle.textContent = "Overtime — Rock, Paper, Scissors";
        picktext.textContent = "Select the team that won Rock, Paper, Scissors.";
        choices.innerHTML =
          '<button class="btn" onclick="overtimeWinner(0)">' + S.names[0] + '</button><button class="btn" onclick="overtimeWinner(1)">' + S.names[1] + '</button>';
        pick.classList.add("show");
      }
      function overtimeWinner(winner) {
        picktitle.textContent = S.names[winner] + " won";
        picktext.textContent = "Choose to receive or kick.";
        choices.innerHTML =
          '<button class="btn primary" onclick="startOvertime(' + winner + ')">RECEIVE</button><button class="btn" onclick="startOvertime(' + (1 - winner) + ')">KICK</button>';
      }
      function startOvertime(receiver) {
        S.otFirst = receiver;
        S.pos = receiver;
        S.kick = true;
        S.ball = receiver === 0 ? 40 : 60;
        S.down = 1;
        S.gain = Math.max(0, Math.min(100, S.ball + dir() * 10));
        S.drive = S.ball;
        S.log.push("<b>OVERTIME START:</b> " + S.names[receiver] + " receives the kickoff.");
        closeM("pick");
        render();
        airmail("kickoff");
      }
'''
if ot_setup not in s:
    s = s.replace(needle2, ot_setup + needle2)

# Clock cannot run in OT.
s = s.replace('function startClock() {\n        if (S.sec <= 0) return;', 'function startClock() {\n        if (S.ot || S.sec <= 0) return;')

p.write_text(s)

# Replace the written overtime section.
rp = Path('rules.html')
r = rp.read_text()
start = r.index('      <div class="card">\n        <h2>11. Overtime</h2>')
end = r.index('      <div class="card">\n        <h2>Quick Reference</h2>', start)
new_rules = '''      <div class="card">
        <h2>11. Overtime</h2>
        <div class="rule"><b>When overtime begins:</b> If all four quarters are complete and the score is tied, the game goes to overtime.</div>
        <div class="rule"><b>No time limit:</b> Overtime has no game clock. Play continues until the overtime rules produce a winner.</div>
        <div class="rule"><b>Starting overtime:</b> The teams play Rock, Paper, Scissors. The winner chooses whether to kick or receive. The normal kickoff and kick-return rules are used, and the receiving team begins the first offensive possession from the resulting field position.</div>
        <div class="rule"><b>Touchdown:</b> If the team with the opening possession scores a touchdown, the game ends immediately. A touchdown at any later point in overtime also ends the game immediately.</div>
        <div class="rule"><b>Opening-possession field goal:</b> If the first team scores a field goal, the opponent receives one possession. A touchdown on that possession wins the game. A field goal ties the overtime score and sends the game to sudden death. If the opponent fails to score, the team that made the original field goal wins.</div>
        <div class="rule"><b>Both teams fail to score:</b> If each team has completed an offensive possession without scoring and the game is still tied, overtime becomes sudden death.</div>
        <div class="rule"><b>Sudden death:</b> Once sudden death begins, the next score wins — touchdown, field goal, or safety.</div>
        <div class="rule"><b>Safety:</b> A safety at any point in overtime ends the game immediately. The team scoring the safety wins.</div>
        <div class="rule">Each team receives <b>3 timeouts in overtime</b>.</div>
      </div>
'''
r = r[:start] + new_rules + r[end:]
rp.write_text(r)
