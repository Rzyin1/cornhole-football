from pathlib import Path

p = Path('index.html')
s = p.read_text()

# Quarter transition logic is already installed in the tracker.
# This migration now keeps the written rules in sync with the agreed final-play rule.
p.write_text(s)

rp = Path('rules.html')
r = rp.read_text()
old = '''        <div class="rule">
          <b>End of a quarter:</b> If the clock reaches 0:00 while a round is
          already being played, that round is finished normally. All 4 offensive
          bags and all 4 defensive bags are thrown, and the result of the down
          still counts. No new round may begin after the final round is scored.
        </div>'''
new = '''        <div class="rule">
          <b>End of a quarter — finish the full play:</b> If the clock reaches
          0:00 while a round is already being played, that round is finished
          normally. All 4 offensive bags and all 4 defensive bags are thrown,
          and the result of the down still counts.
        </div>
        <div class="rule">
          <b>Any result created by the final round must fully play out.</b> If
          the final round produces a touchdown, the touchdown counts and the
          offense still gets its extra-point or 2-point conversion attempt. If
          that score requires a kickoff, the kickoff and kick return are also
          completed normally. A returner continues making 10-yard airmail
          returns until the first miss, just like any other return.
        </div>
        <div class="rule">
          The same principle applies to any other consequence of the final
          round, including a safety or another possession-changing result. The
          entire sequence continues until the game naturally reaches the point
          where a new normal offensive down would begin.
        </div>
        <div class="rule">
          <b>No new timed round begins at 0:00.</b> Once the final play and every
          resulting conversion, kickoff, return, or other required sequence has
          completely resolved, the quarter ends and the game advances normally.
        </div>'''
if old not in r:
    raise SystemExit('Could not find current end-of-quarter rule block')
r = r.replace(old, new)
rp.write_text(r)
