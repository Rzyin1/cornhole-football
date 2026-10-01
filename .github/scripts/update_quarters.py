from pathlib import Path

p=Path('index.html'); s=p.read_text()

# New-game setup: team names, 2-8 players, roles.
old='''        <h2>New Game</h2>
        <input class="name" id="p0" /><input class="name" id="p1" />
        <p>
          Play Rock, Paper, Scissors. The winner chooses who receives the
          opening kickoff.
        </p>
        <div class="row">
          <button class="btn primary" onclick="newGame(0)">
            Player 1 receives</button
          ><button class="btn primary" onclick="newGame(1)">
            Player 2 receives
          </button>
        </div>'''
new='''        <h2>New Game</h2>
        <label>Team 1 Name</label><input class="name" id="p0" />
        <label>Team 2 Name</label><input class="name" id="p1" />
        <label>Total Players (2–8)</label>
        <select class="name" id="playerCount" onchange="buildPlayerSetup()">
          <option>2</option><option>3</option><option>4</option><option>5</option><option>6</option><option>7</option><option>8</option>
        </select>
        <div id="playerSetup"></div>
        <p><b>Roles:</b> Check Both if that player can throw offense and defense. Otherwise select Offense or Defense.</p>
        <p>Play Rock, Paper, Scissors. The winner chooses who receives the opening kickoff.</p>
        <div class="row">
          <button class="btn primary" onclick="newGame(0)">Team 1 receives</button
          ><button class="btn primary" onclick="newGame(1)">Team 2 receives</button>
        </div>'''
if old not in s: raise SystemExit('setup html not found')
s=s.replace(old,new)

# Add active thrower selectors.
needle='''          <b>ENTER BAG RESULTS</b>
          <div class="bagpads">'''
repl='''          <b>ENTER BAG RESULTS</b>
          <div class="row" style="margin:10px 0">
            <div style="flex:1"><label>Offensive Thrower</label><select class="name" id="offThrower"></select></div>
            <div style="flex:1"><label>Defensive Thrower</label><select class="name" id="defThrower"></select></div>
          </div>
          <div class="bagpads">'''
if needle not in s: raise SystemExit('bag header not found')
s=s.replace(needle,repl)

# State supports roster and individual stats while retaining team stats.
s=s.replace('''        names: ["Player 1", "Player 2"],
        score:''','''        names: ["Team 1", "Team 2"],
        roster: [],
        playerStats: {},
        score:''')

# Migration helpers and player stat model.
needle='''      const blankStats = () => [blankStat(), blankStat()];'''
add='''      const blankStats = () => [blankStat(), blankStat()];
      const blankPlayerStat = () => ({offRounds:0,offHoles:0,offBoards:0,defRounds:0,defHoles:0,defBoards:0,netYards:0});
      function ensureRoster(){
        if(!Array.isArray(S.roster)||!S.roster.length){
          S.roster=[{id:"p0",name:S.names[0],team:0,offense:true,defense:true},{id:"p1",name:S.names[1],team:1,offense:true,defense:true}];
        }
        if(!S.playerStats) S.playerStats={};
        S.roster.forEach(p=>{if(!S.playerStats[p.id]) S.playerStats[p.id]=blankPlayerStat();});
      }
      function eligible(team,role){ensureRoster();return S.roster.filter(p=>p.team===team && p[role]);}
      function refreshThrowers(){
        if(!document.getElementById("offThrower")) return;
        let o=eligible(S.pos,"offense"), d=eligible(1-S.pos,"defense");
        offThrower.innerHTML=o.map(p=>'<option value="'+p.id+'">'+p.name+'</option>').join('');
        defThrower.innerHTML=d.map(p=>'<option value="'+p.id+'">'+p.name+'</option>').join('');
      }
      function playerById(id){ensureRoster();return S.roster.find(p=>p.id===id);}
'''
if needle not in s: raise SystemExit('blankstats not found')
s=s.replace(needle,add)

# Ensure old saves migrate.
s=s.replace('''      if (!S.stats) S.stats = blankStats();''','''      if (!S.stats) S.stats = blankStats();
      ensureRoster();''',1)

# Refresh selectors each render.
s=s.replace('''        renderLive();
        drawField();''','''        renderLive();
        refreshThrowers();
        drawField();''',1)

# Individual stat display appended below team stats.
needle='''          .join("");
      }
      function render() {'''
repl='''          .join("");
        ensureRoster();
        if(S.roster.length>2){
          liveStats.innerHTML += '<div style="width:100%;margin-top:12px"><b>INDIVIDUAL THROWING STATS</b></div>' + S.roster.map(p=>{
            let x=S.playerStats[p.id]||blankPlayerStat(), ob=x.offRounds*4, db=x.defRounds*4;
            let op=ob?((100*x.offHoles)/ob).toFixed(1):"0.0", dp=db?((100*x.defHoles)/db).toFixed(1):"0.0";
            return '<div class="liveplayer"><div class="live-name">'+p.name+' — '+S.names[p.team]+'</div><div class="livegrid"><div class="liveitem"><b>'+x.offHoles+'/'+ob+' ('+op+'%)</b><small>OFFENSE HOLES</small></div><div class="liveitem"><b>'+x.defHoles+'/'+db+' ('+dp+'%)</b><small>DEFENSE HOLES</small></div><div class="liveitem"><b>'+x.offBoards+'</b><small>OFFENSE BOARDS</small></div><div class="liveitem"><b>'+x.defBoards+'</b><small>DEFENSE BOARDS</small></div><div class="liveitem"><b>'+x.netYards+'</b><small>NET OFFENSE YARDS</small></div></div></div>';
          }).join('');
        }
      }
      function render() {'''
if needle not in s: raise SystemExit('renderLive end not found')
s=s.replace(needle,repl)

# Credit normal rounds to selected players.
needle='''        s.offRounds++;
        s.offHoles += bags.oh;'''
repl='''        let op=playerById(offThrower.value), dp=playerById(defThrower.value);
        if(!op || !dp){ alert("Select an offensive and defensive thrower."); return; }
        let ops=S.playerStats[op.id], dps=S.playerStats[dp.id];
        ops.offRounds++; ops.offHoles+=bags.oh; ops.offBoards+=bags.ob; ops.netYards+=y;
        dps.defRounds++; dps.defHoles+=bags.dh; dps.defBoards+=bags.db;
        s.offRounds++;
        s.offHoles += bags.oh;'''
if needle not in s: raise SystemExit('submit stats not found')
s=s.replace(needle,repl,1)

# Include player names in play log.
s=s.replace('''          S.names[o] +
            ": " +''','''          S.names[o] + " (" + op.name + " offense vs " + dp.name + " defense): " +''',1)

# Replace setup/newGame functions.
start=s.index('      function setup() {')
end=s.index('      function editPlayers() {',start)
newfunc='''      function buildPlayerSetup(){
        let n=Math.max(2,Math.min(8,Number(playerCount.value)||2));
        let html='';
        for(let i=0;i<n;i++){
          let team=i%2;
          html += '<div class="card" style="padding:10px;margin:8px 0"><b>Player '+(i+1)+'</b><input class="name roster-name" data-i="'+i+'" placeholder="Player name"><select class="name roster-team" data-i="'+i+'"><option value="0" '+(team===0?'selected':'')+'>Team 1</option><option value="1" '+(team===1?'selected':'')+'>Team 2</option></select><select class="name roster-role" data-i="'+i+'"><option value="offense">Offense</option><option value="defense">Defense</option><option value="both" selected>Both</option></select></div>';
        }
        playerSetup.innerHTML=html;
      }
      function setup() {
        p0.value = S.names[0] || "Team 1";
        p1.value = S.names[1] || "Team 2";
        playerCount.value = Math.max(2,Math.min(8,(S.roster&&S.roster.length)||2));
        buildPlayerSetup();
        if(S.roster&&S.roster.length){
          S.roster.forEach((p,i)=>{
            let nm=document.querySelector('.roster-name[data-i="'+i+'"]'), tm=document.querySelector('.roster-team[data-i="'+i+'"]'), rl=document.querySelector('.roster-role[data-i="'+i+'"]');
            if(nm) nm.value=p.name;if(tm) tm.value=p.team;if(rl) rl.value=p.offense&&p.defense?'both':p.offense?'offense':'defense';
          });
        }
        document.getElementById("setup").classList.add("show");
      }
      function newGame(r) {
        let teamNames=[p0.value.trim()||"Team 1",p1.value.trim()||"Team 2"];
        let n=Math.max(2,Math.min(8,Number(playerCount.value)||2)), roster=[];
        for(let i=0;i<n;i++){
          let name=document.querySelector('.roster-name[data-i="'+i+'"]').value.trim()||"Player "+(i+1);
          let team=Number(document.querySelector('.roster-team[data-i="'+i+'"]').value);
          let role=document.querySelector('.roster-role[data-i="'+i+'"]').value;
          roster.push({id:"p"+i,name,team,offense:role==="offense"||role==="both",defense:role==="defense"||role==="both"});
        }
        for(let t=0;t<2;t++){
          if(!roster.some(p=>p.team===t)) return alert("Each team needs at least one player.");
          if(!roster.some(p=>p.team===t&&p.offense)) return alert(teamNames[t]+" needs at least one offensive player.");
          if(!roster.some(p=>p.team===t&&p.defense)) return alert(teamNames[t]+" needs at least one defensive player.");
        }
        S=fresh(); S.names=teamNames; S.roster=roster; S.playerStats={}; roster.forEach(p=>S.playerStats[p.id]=blankPlayerStat());
        S.pos=r; S.openingReceiver=r; S.quarterRoundFinished=false;
        S.log.push("<b>ROCK, PAPER, SCISSORS:</b> "+S.names[r]+" selected to receive the opening kickoff.");
        resetBags(); closeM("setup"); render(); airmail("kickoff");
      }
'''
s=s[:start]+newfunc+s[end:]

p.write_text(s)

# Add team-format rules.
rp=Path('rules.html'); r=rp.read_text()
marker='''      <div class="card">
        <h2>12. Overtime</h2>'''
section='''      <div class="card">
        <h2>12. Teams & Player Roles</h2>
        <div class="rule">A game may have <b>2 to 8 total players</b>, with players assigned to one of two teams.</div>
        <div class="rule">Each player is assigned as <b>Offense</b>, <b>Defense</b>, or <b>Both</b>. An offense-only player throws the team's offensive rounds; a defense-only player throws the team's defensive rounds. A player marked Both is eligible for either role.</div>
        <div class="rule">If a team has more than one eligible player for a role, the team may choose which eligible player throws that round. There is no required automatic rotation.</div>
        <div class="rule">Scoring, possession, downs, field position, timeouts, and the game result belong to the <b>team</b>. Throwing performance is also tracked to the <b>individual player</b> who made those throws.</div>
      </div>
'''
if marker not in r: raise SystemExit('OT marker not found')
r=r.replace(marker,section+marker.replace('12. Overtime','13. Overtime'))
rp.write_text(r)
