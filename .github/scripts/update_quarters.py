from pathlib import Path

p = Path('index.html')
s = p.read_text()

# Add Penalty button to game actions.
old_btn = '<button class="btn red" onclick="turnover()">Turnover</button\n            ><button class="btn" onclick="timeout()">Timeout</button'
new_btn = '<button class="btn red" onclick="turnover()">Turnover</button\n            ><button class="btn gold" onclick="penalty()">Penalty</button\n            ><button class="btn" onclick="timeout()">Timeout</button'
if old_btn not in s:
    raise SystemExit('Could not find game action buttons')
s = s.replace(old_btn, new_btn)

# Penalty helpers before timeout().
needle = '      function timeout() {'
penalty_code = '''      function enforcePenaltyYards(team, yards) {
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
      }
      function penalty() {
        if (S.kick) {
          alert("Complete the kickoff or return first.");
          return;
        }
        picktitle.textContent = "Penalty";
        picktext.textContent = "Select the penalty.";
        choices.innerHTML =
          '<button class="btn" onclick="penaltyTeam(\'foul\')">Foul-Line Violation — 5 yd</button>' +
          '<button class="btn" onclick="penaltyTeam(\'turn\')">Throwing Out of Turn — 5 yd</button>' +
          '<button class="btn" onclick="penaltyTeam(\'bags\')">Touching / Moving Live Bags — 10 yd</button>' +
          '<button class="btn red" onclick="penaltyTeam(\'interference\')">Interference — 15 yd + Automatic 4-Bagger</button>' +
          '<button class="btn" onclick="penaltyTeam(\'delay\')">Delay of Game — 5 yd</button>';
        pick.classList.add("show");
      }
      function penaltyTeam(type) {
        mode = "penalty:" + type;
        picktitle.textContent = "Penalty — Offending Team";
        picktext.textContent = "Which team committed the penalty?";
        choices.innerHTML =
          '<button class="btn" onclick="penaltyResolve(0)">' + S.names[0] + '</button>' +
          '<button class="btn" onclick="penaltyResolve(1)">' + S.names[1] + '</button>';
      }
      function penaltyResolve(team) {
        let type = mode.split(":")[1];
        let info = {
          foul: [5, "FOUL-LINE VIOLATION"],
          turn: [5, "THROWING OUT OF TURN"],
          bags: [10, "TOUCHING / MOVING LIVE BAGS"],
          interference: [15, "INTERFERENCE"],
          delay: [5, "DELAY OF GAME"],
        }[type];
        snap();
        let yards = info[0], label = info[1];
        if (type === "foul" || type === "turn") {
          S.log.push("<b>PENALTY — " + label + ":</b> " + S.names[team] + " — " + yards + " yards. The illegal bag does not count and is removed. Any affected bags belonging to the offending team that fall in do not count and are removed; any opponent bag knocked into the hole counts normally.");
        } else if (type === "bags") {
          S.log.push("<b>PENALTY — " + label + ":</b> " + S.names[team] + " — 10 yards. Any moved/affected bags belonging to the offending team do not count and are removed. Any moved/affected opponent bags count as bags in the hole. Play resumes normally.");
        } else if (type === "delay") {
          S.log.push("<b>PENALTY — DELAY OF GAME:</b> " + S.names[team] + " — 5 yards. Play resumes normally.");
        }
        if (type === "interference") {
          closeM("pick");
          penaltyInterference(team);
          return;
        }
        enforcePenaltyYards(team, yards);
        closeM("pick");
        render();
      }
      function penaltyInterference(team) {
        let opponent = 1 - team;
        picktitle.textContent = "Interference — Offending Team's Completed Bags";
        picktext.textContent = "Enter only the offending team's bags already thrown before the interference. Those completed bags still count normally. Unthrown bags count as 0. The opponent receives an automatic 4-bagger and the round ends.";
        choices.innerHTML =
          '<div style="width:100%"><label>Offending bags in hole</label><input class="name" id="penHole" type="number" min="0" max="4" value="0"><label>Offending bags on board</label><input class="name" id="penBoard" type="number" min="0" max="4" value="0"><button class="btn red full" onclick="resolveInterference(' + team + ')">ENFORCE INTERFERENCE</button></div>';
        pick.classList.add("show");
      }
      function resolveInterference(team) {
        let holes = Math.max(0, Math.min(4, Number(document.getElementById("penHole").value) || 0));
        let boards = Math.max(0, Math.min(4 - holes, Number(document.getElementById("penBoard").value) || 0));
        let offense = S.pos;
        let teamYards = holes * (team === offense ? 4 : 3) + boards;
        let opponent = 1 - team;
        let opponentYards = opponent === offense ? 16 : 12;
        let net = offense === team ? teamYards - opponentYards : opponentYards - teamYards;
        S.log.push("<b>PENALTY — INTERFERENCE:</b> " + S.names[team] + " — 15 yards + automatic 4-bagger for " + S.names[opponent] + ". Offending team's completed bags count normally; unthrown bags count as 0. Round ends. Net round yardage: " + (net >= 0 ? "+" : "") + net + ".");
        let os = S.stats[offense], ds = S.stats[1 - offense];
        os.offRounds++;
        ds.defRounds++;
        if (team === offense) {
          os.offHoles += holes;
          os.offBoards += boards;
          ds.defHoles += 4;
        } else {
          ds.defHoles += holes;
          ds.defBoards += boards;
          os.offHoles += 4;
        }
        os.netYards += net;
        os.biggestGain = os.biggestGain === null ? net : Math.max(os.biggestGain, net);
        apply(net);
        if (!S.otGameOver) enforcePenaltyYards(team, 15);
        resetBags();
        closeM("pick");
        render();
      }
'''
if penalty_code not in s:
    s = s.replace(needle, penalty_code + needle)

# Export rule summary.
s = s.replace('safety:\n              "If offensive yardage crosses into its own end zone, defense scores 2 and the team that allowed the safety kicks off to the scoring team.",', 'safety:\n              "If offensive yardage crosses into its own end zone, defense scores 2 and the team that allowed the safety kicks off to the scoring team.",\n            penalties:\n              "Foul-line violation 5 yards; throwing out of turn 5 yards; touching/moving live bags 10 yards; interference 15 yards plus automatic 4-bagger; delay of game 5 yards.",')

p.write_text(s)

# Add penalty section to rules before overtime and renumber overtime.
rp = Path('rules.html')
r = rp.read_text()
r = r.replace('<h2>11. Overtime</h2>', '<h2>12. Overtime</h2>')
marker = '      <div class="card">\n        <h2>12. Overtime</h2>'
pen_rules = '''      <div class="card">
        <h2>11. Penalties</h2>
        <div class="rule"><b>Foul-Line Violation — 5 yards:</b> A player must remain behind the foul line until the thrown bag has completely finished moving — stopped on the board, gone into the hole, or finished off the board. If the player crosses early, the thrown bag is dead, does not count, and is removed from play. Any of the offending team's bags knocked into the hole by the illegal bag also do not count and are removed. Any opponent bag knocked into the hole counts normally.</div>
        <div class="rule"><b>Throwing Out of Turn — 5 yards:</b> The illegal bag is dead, does not count, and is removed. Any of the offending team's bags knocked into the hole by that illegal throw do not count and are removed. Any opponent bag knocked into the hole counts normally.</div>
        <div class="rule"><b>Touching or Moving Live Bags — 10 yards:</b> If a player touches or moves bags before the round is complete, any moved or affected bags belonging to the offending player/team do not count and are removed from play. Any moved or affected opponent bags are counted as bags in the hole. After the penalty is enforced, play resumes normally.</div>
        <div class="rule"><b>Interference with an Opponent's Throw — 15 yards + automatic 4-bagger:</b> The opponent receives an automatic 4-bagger and the round ends immediately. Bags already thrown by the offending team count normally whether they are in the hole or on the board. Any bags the offending team had not yet thrown count as 0. Calculate the round result, enforce the additional 15-yard penalty, and resume play normally.</div>
        <div class="rule"><b>Delay of Game — 5 yards:</b> Intentionally delaying or unnecessarily stalling play results in a 5-yard penalty. After enforcement, play resumes normally.</div>
        <div class="rule"><b>Special-teams throw requirements:</b> When a play requires an airmail, a throw that does not meet that requirement simply does not count. It is not an additional penalty.</div>
      </div>
'''
if marker not in r:
    raise SystemExit('Could not find overtime section marker')
r = r.replace(marker, pen_rules + marker)
rp.write_text(r)
