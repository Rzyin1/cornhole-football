from pathlib import Path

p = Path('index.html')
s = p.read_text()

s = s.replace('lastTD: null,\n        stats: blankStats(),', 'lastTD: null,\n        openingReceiver: null,\n        quarterRoundFinished: false,\n        stats: blankStats(),')
s = s.replace('if (S.clockHoldRound == null) S.clockHoldRound = false;', 'if (S.clockHoldRound == null) S.clockHoldRound = false;\n      if (S.quarterRoundFinished == null) S.quarterRoundFinished = false;')
s = s.replace('function submitRound() {\n        if (S.kick) {', 'function submitRound() {\n        if (S.sec <= 0 && S.quarterRoundFinished) {\n          alert("The quarter is over. Advance to the next quarter before starting another round.");\n          return;\n        }\n        if (S.kick) {')
s = s.replace('apply(y);\n        resetBags();', 'apply(y);\n        resetBags();\n        if (S.sec <= 0) S.quarterRoundFinished = true;')
s = s.replace('S.pos = r;\n        S.log.push(', 'S.pos = r;\n        S.openingReceiver = r;\n        S.quarterRoundFinished = false;\n        S.log.push(')

start = s.index('      function nextQuarter() {')
end = s.index('      function undo() {', start)
new_func = '''      function nextQuarter() {
        snap();
        stop();
        if (S.q < 4) {
          S.q++;
          S.sec = 1200;
          S.clockHoldRound = false;
          S.quarterRoundFinished = false;
          if (S.q == 3) {
            S.to = [4, 4];
            S.log.push("<b>HALFTIME</b> — timeouts reset. Second-half kickoff.");
            let openingReceiver = S.openingReceiver == null ? S.pos : S.openingReceiver;
            S.pos = 1 - openingReceiver;
            S.kick = true;
            render();
            airmail("kickoff");
            return;
          }
          S.log.push("<b>START OF Q" + S.q + "</b> — possession, field position, down and distance carry over.");
          render();
          startClock();
        } else if (S.score[0] == S.score[1]) {
          S.ot = true;
          S.to = [3, 3];
          S.sec = 1200;
          S.clockHoldRound = false;
          S.quarterRoundFinished = false;
          S.log.push("<b>OVERTIME</b>");
          render();
        } else alert("Game over.");
      }
'''
s = s[:start] + new_func + s[end:]
p.write_text(s)

rp = Path('rules.html')
r = rp.read_text()
old = '<div class="rule"><b>Quarter breaks:</b> When a quarter ends, play advances to the next quarter. Halftime occurs after the 2nd quarter.</div>'
new = '<div class="rule"><b>End of a quarter:</b> If the clock reaches 0:00 while a round is already being played, that round is finished normally. All 4 offensive bags and all 4 defensive bags are thrown, and the result of the down still counts. No new round may begin after the final round is scored.</div><div class="rule"><b>Q1 to Q2:</b> Possession, field position, down, and distance all carry over. The clock resets to 20:00 and there is no kickoff.</div><div class="rule"><b>Halftime:</b> After Q2, the first-half possession ends. Both teams reset to 4 timeouts. The team that received the opening kickoff kicks off to begin the second half, so the team that kicked to start the game receives the Q3 kickoff. The clock stays stopped during the kickoff and return and begins running when the return ends.</div><div class="rule"><b>Q3 to Q4:</b> Possession, field position, down, and distance carry over unchanged. The clock resets to 20:00 and there is no kickoff.</div>'
if old in r:
    r = r.replace(old, new)
rp.write_text(r)
