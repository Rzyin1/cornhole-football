from pathlib import Path
p=Path('index.html'); s=p.read_text()

# Expand player stat model, preserving old saves via ensureRoster defaults.
old='''      const blankPlayerStat = () => ({
        offRounds: 0,
        offHoles: 0,
        offBoards: 0,
        defRounds: 0,
        defHoles: 0,
        defBoards: 0,
        netYards: 0,
      });'''
new='''      const blankPlayerStat = () => ({
        offRounds:0, totalYards:0, firstDowns:0, touchdowns:0, longestGain:null, turnovers:0,
        defRounds:0, yardsAllowed:0, tacklesForLoss:0, stops:0, safeties:0,
        kickoffYards:0, kickReturnYards:0, kickReturnTD:0, puntYards:0, puntReturnYards:0, puntReturnTD:0,
        fieldGoalsMade:0, fieldGoalsAttempted:0, patMade:0, patAttempted:0, twoPtMade:0, twoPtAttempted:0
      });'''
if old not in s: raise SystemExit('blankPlayerStat missing')
s=s.replace(old,new,1)

old='''        S.roster.forEach((p) => {
          if (!S.playerStats[p.id]) S.playerStats[p.id] = blankPlayerStat();
        });'''
new='''        S.roster.forEach((p) => {
          if (!S.playerStats[p.id]) S.playerStats[p.id] = blankPlayerStat();
          else {
            let base=blankPlayerStat(), x=S.playerStats[p.id];
            Object.keys(base).forEach(k=>{ if(x[k]==null) x[k]=base[k]; });
          }
        });'''
if old not in s: raise SystemExit('ensure stats missing')
s=s.replace(old,new,1)

# Replace individual throwing display with football box-score style stats.
start=s.index('        ensureRoster();\n        if (S.roster.length > 2) {', s.index('function renderLive'))
end=s.index('      }\n      function render()', start)
block='''        ensureRoster();
        if (S.roster.length) {
          liveStats.innerHTML += '<div style="width:100%;margin-top:12px"><b>INDIVIDUAL PLAYER STATS</b></div>' +
            S.roster.map((p)=>{
              let x=S.playerStats[p.id]||blankPlayerStat();
              let avg=x.offRounds?(x.totalYards/x.offRounds).toFixed(2):"0.00";
              return '<div class="liveplayer"><div class="live-name">'+p.name+' — '+S.names[p.team]+'</div>'+
                '<div style="margin:7px 0 4px"><b>OFFENSE</b></div><div class="livegrid">'+
                '<div class="liveitem"><b>'+x.offRounds+'</b><small>ROUNDS</small></div><div class="liveitem"><b>'+x.totalYards+'</b><small>TOTAL YARDS</small></div><div class="liveitem"><b>'+avg+'</b><small>YARDS / ROUND</small></div><div class="liveitem"><b>'+x.firstDowns+'</b><small>FIRST DOWNS</small></div><div class="liveitem"><b>'+x.touchdowns+'</b><small>TOUCHDOWNS</small></div><div class="liveitem"><b>'+(x.longestGain??0)+'</b><small>LONGEST GAIN</small></div><div class="liveitem"><b>'+x.turnovers+'</b><small>TURNOVERS</small></div></div>'+
                '<div style="margin:9px 0 4px"><b>DEFENSE</b></div><div class="livegrid">'+
                '<div class="liveitem"><b>'+x.defRounds+'</b><small>ROUNDS</small></div><div class="liveitem"><b>'+x.yardsAllowed+'</b><small>YARDS ALLOWED</small></div><div class="liveitem"><b>'+x.tacklesForLoss+'</b><small>TACKLES FOR LOSS</small></div><div class="liveitem"><b>'+x.stops+'</b><small>STOPS / NO GAIN</small></div><div class="liveitem"><b>'+x.safeties+'</b><small>SAFETIES</small></div></div>'+
                '<div style="margin:9px 0 4px"><b>SPECIAL TEAMS</b></div><div class="livegrid">'+
                '<div class="liveitem"><b>'+x.kickoffYards+'</b><small>KICKOFF YARDS</small></div><div class="liveitem"><b>'+x.kickReturnYards+'</b><small>KICK RETURN YARDS</small></div><div class="liveitem"><b>'+x.kickReturnTD+'</b><small>KICK RETURN TD</small></div><div class="liveitem"><b>'+x.puntYards+'</b><small>PUNT YARDS</small></div><div class="liveitem"><b>'+x.puntReturnYards+'</b><small>PUNT RETURN YARDS</small></div><div class="liveitem"><b>'+x.puntReturnTD+'</b><small>PUNT RETURN TD</small></div><div class="liveitem"><b>'+x.fieldGoalsMade+'/'+x.fieldGoalsAttempted+'</b><small>FG MADE / ATT</small></div><div class="liveitem"><b>'+x.patMade+'/'+x.patAttempted+'</b><small>PAT MADE / ATT</small></div><div class="liveitem"><b>'+x.twoPtMade+'/'+x.twoPtAttempted+'</b><small>2PT MADE / ATT</small></div></div></div>';
            }).join('');
        }
'''
s=s[:start]+block+s[end:]

# Normal round individual football stats. Determine first down/TD before apply changes state.
old='''        let ops = S.playerStats[op.id],
          dps = S.playerStats[dp.id];
        ops.offRounds++;
        ops.offHoles += bags.oh;
        ops.offBoards += bags.ob;
        ops.netYards += y;
        dps.defRounds++;
        dps.defHoles += bags.dh;
        dps.defBoards += bags.db;'''
new='''        let ops=S.playerStats[op.id], dps=S.playerStats[dp.id];
        let projected=S.ball+dir()*y;
        let earnsFirst=dir()===1 ? projected>=S.gain : projected<=S.gain;
        let scoresTD=(o===0 && projected>=100)||(o===1 && projected<=0);
        let scoresSafety=(o===0 && projected<=0)||(o===1 && projected>=100);
        ops.offRounds++; ops.totalYards+=y; ops.longestGain=ops.longestGain===null?y:Math.max(ops.longestGain,y);
        if(earnsFirst && !scoresTD && !scoresSafety) ops.firstDowns++;
        if(scoresTD) ops.touchdowns++;
        dps.defRounds++; dps.yardsAllowed+=y;
        if(y<0) dps.tacklesForLoss++;
        if(y===0) dps.stops++;
        if(scoresSafety) dps.safeties++;'''
if old not in s: raise SystemExit('round player stats block missing')
s=s.replace(old,new,1)

# Turnover button credits selected offensive player when available.
old='''      function turnover() {
        snap();'''
new='''      function turnover() {
        let op=document.getElementById("offThrower") ? playerById(offThrower.value) : null;
        if(op && S.playerStats[op.id]) S.playerStats[op.id].turnovers++;
        snap();'''
if old not in s: raise SystemExit('turnover missing')
s=s.replace(old,new,1)

# Kickoff yards = distance created by kickoff result from the receiving team's normal own-40 starting point.
old='''        S.stats[k].kickoffMade += n;
        S.stats[k].kickoffAtt += 4;
        let ownY = n == 4 ? 1 : 40 - 10 * n;'''
new='''        S.stats[k].kickoffMade += n;
        S.stats[k].kickoffAtt += 4;
        let ownY = n == 4 ? 1 : 40 - 10 * n;
        S.playerStats[thrower.id].kickoffYards += 40-ownY;'''
if old not in s: raise SystemExit('kickoff stats missing')
s=s.replace(old,new,1)

# Return stats: each successful airmail is 10 return yards; distinguish kick vs punt by label/mode state.
# Save return type when started.
old='''        mode = "kickreturn";
        picktitle.textContent = label;'''
new='''        mode = label === "Punt Return" ? "puntreturn" : "kickreturn";
        picktitle.textContent = label;'''
s=s.replace(old,new,1)
old='''          s.kickReturnMade++;
          kickReturnCount++;'''
new='''          s.kickReturnMade++;
          kickReturnCount++;
          if(mode==="puntreturn") S.playerStats[thrower.id].puntReturnYards+=10;
          else S.playerStats[thrower.id].kickReturnYards+=10;'''
s=s.replace(old,new,1)
old='''            s.kickReturnTD++;
            S.score[r] += 6;'''
new='''            s.kickReturnTD++;
            if(mode==="puntreturn") S.playerStats[thrower.id].puntReturnTD++;
            else S.playerStats[thrower.id].kickReturnTD++;
            S.score[r] += 6;'''
s=s.replace(old,new,1)

# Punt yards.
old='''        s.puntYards += dist;
        let raw ='''
new='''        s.puntYards += dist;
        if(selectedPunter && S.playerStats[selectedPunter]) S.playerStats[selectedPunter].puntYards += dist;
        let raw ='''
s=s.replace(old,new,1)

# FG individual stats.
old='''        let t = S.pos;
        S.stats[t].fieldGoalsAttempted++;
        if (ok) {
          S.stats[t].fieldGoalsMade++;'''
new='''        let t = S.pos;
        S.stats[t].fieldGoalsAttempted++;
        S.playerStats[thrower.id].fieldGoalsAttempted++;
        if (ok) {
          S.stats[t].fieldGoalsMade++;
          S.playerStats[thrower.id].fieldGoalsMade++;'''
s=s.replace(old,new,1)

# PAT / 2PT individual stats.
old='''        let t = S.lastTD ?? S.pos;
        if (ok) {
          S.score[t] += p;'''
new='''        let t = S.lastTD ?? S.pos;
        let ps=S.playerStats[thrower.id];
        if(p===1){ ps.patAttempted++; if(ok) ps.patMade++; }
        else { ps.twoPtAttempted++; if(ok) ps.twoPtMade++; }
        if (ok) {
          S.score[t] += p;'''
s=s.replace(old,new,1)

p.write_text(s)
