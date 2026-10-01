from pathlib import Path

p = Path('index.html')
s = p.read_text()

# The penalty menu was written with single-quoted HTML strings containing
# single-quoted onclick arguments. That terminates the JavaScript string early
# and prevents the entire tracker script (including New Game) from loading.
replacements = {
    ''''<button class="btn" onclick="penaltyTeam('foul')">Foul-Line Violation — 5 yd</button>' +''': ''''<button class="btn" onclick="penaltyTeam(&quot;foul&quot;)">Foul-Line Violation — 5 yd</button>' +''',
    ''''<button class="btn" onclick="penaltyTeam('turn')">Throwing Out of Turn — 5 yd</button>' +''': ''''<button class="btn" onclick="penaltyTeam(&quot;turn&quot;)">Throwing Out of Turn — 5 yd</button>' +''',
    ''''<button class="btn" onclick="penaltyTeam('bags')">Touching / Moving Live Bags — 10 yd</button>' +''': ''''<button class="btn" onclick="penaltyTeam(&quot;bags&quot;)">Touching / Moving Live Bags — 10 yd</button>' +''',
    ''''<button class="btn red" onclick="penaltyTeam('interference')">Interference — 15 yd + Automatic 4-Bagger</button>' +''': ''''<button class="btn red" onclick="penaltyTeam(&quot;interference&quot;)">Interference — 15 yd + Automatic 4-Bagger</button>' +''',
    ''''<button class="btn" onclick="penaltyTeam('delay')">Delay of Game — 5 yd</button>';''': ''''<button class="btn" onclick="penaltyTeam(&quot;delay&quot;)">Delay of Game — 5 yd</button>';''',
}

for old, new in replacements.items():
    if old not in s:
        raise SystemExit(f'Expected broken penalty string not found: {old}')
    s = s.replace(old, new)

p.write_text(s)
