import { useState, useEffect } from "react";

const C = {
  bg:      "#06070f",
  panel:   "#090b18",
  border:  "#141c3a",
  blue:    "#3b6ef8",
  blueDim: "#1a3a8a",
  violet:  "#7c3aed",
  green:   "#00e87a",
  amber:   "#f59e0b",
  red:     "#ef4444",
  text:    "#8aaad8",
  textDim: "#2e4070",
  white:   "#ddeeff",
};

const STATS = [
  { val:"99.97%", label:"UPTIME SLA" },
  { val:"<80ms", label:"ALERT LATENCY" },
  { val:"256-AES", label:"ENCRYPTION" },
  { val:"∞", label:"DATA RETENTION" },
];

const FEATURES = [
  { icon:"◈", title:"MULTI-FEED SURVEILLANCE", desc:"Monitor up to 32 simultaneous camera feeds with colour-graded, thermal IR, and night-vision overlays — all in one unified command view." },
  { icon:"≋", title:"THERMAL IR DETECTION", desc:"Dedicated black-and-white thermal imaging pipeline for low-light and zero-visibility perimeter monitoring. Automatic heat-signature flagging." },
  { icon:"⚡", title:"REAL-TIME INCIDENT LOG", desc:"Socket.IO-powered live alert feed. Every motion event, perimeter breach, and anomaly is timestamped and logged the moment it's detected." },
  { icon:"◑", title:"INFILTRATION RISK ENGINE", desc:"Dynamic threat scoring computed from weather, visibility, wind speed, moon phase, humidity, and cloud cover to quantify infiltration probability." },
  { icon:"☁", title:"ENVIRONMENTAL INTEL", desc:"Live environmental factor analysis — 10 variables tracked continuously, each scored for threat impact and displayed with tactical notes." },
  { icon:"⊞", title:"SECTOR MANAGEMENT", desc:"Assign cameras to named sectors (Alpha, Bravo, Charlie…), monitor status (LIVE / STANDBY / OFFLINE), and receive sector-level breach alerts." },
];

const TICKER_ITEMS = [
  "Anviksha SENTINEL — NEXT-GEN PERIMETER INTELLIGENCE",
  "ZERO BLIND SPOTS",
  "THERMAL + OPTICAL FUSION",
  "REAL-TIME THREAT SCORING",
  "MILITARY-GRADE ENCRYPTION",
  "24/7 AUTOMATED MONITORING",
];

function CornerBox({ c = C.blue, s = 10 }) {
  return (
    <>
      {[
        [{ top:0, left:0 },   { borderTop:`1.5px solid ${c}`, borderLeft:`1.5px solid ${c}` }],
        [{ top:0, right:0 },  { borderTop:`1.5px solid ${c}`, borderRight:`1.5px solid ${c}` }],
        [{ bottom:0, left:0 },{ borderBottom:`1.5px solid ${c}`, borderLeft:`1.5px solid ${c}` }],
        [{ bottom:0, right:0},{ borderBottom:`1.5px solid ${c}`, borderRight:`1.5px solid ${c}` }],
      ].map(([pos, brd], i) => (
        <div key={i} style={{ position:"absolute", width:s, height:s, ...pos, ...brd }} />
      ))}
    </>
  );
}

export default function Homepage({ onEnter }) {
  const [time, setTime] = useState("");
  const [activeFeat, setActiveFeat] = useState(0);
  const [glitch, setGlitch] = useState(false);

  useEffect(() => {
    const t = setInterval(() => {
      setTime(new Date().toTimeString().slice(0,8).replace(/:/g,"") + "Z");
    }, 1000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    const t = setInterval(() => setActiveFeat(f => (f+1) % FEATURES.length), 3200);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    const t = setInterval(() => {
      if (Math.random() < 0.07) { setGlitch(true); setTimeout(()=>setGlitch(false),110); }
    }, 1800);
    return () => clearInterval(t);
  }, []);

  return (
    <div style={{
      minHeight:"100vh",
      backgroundColor: C.bg,
      fontFamily:"'Share Tech Mono','Courier New',monospace",
      color: C.text,
      backgroundImage:`
        radial-gradient(ellipse at 10% 10%, #2a105066 0%, transparent 40%),
        radial-gradient(ellipse at 90% 80%, #1a3a8a33 0%, transparent 40%),
        repeating-linear-gradient(0deg,transparent,transparent 39px,rgba(59,110,248,0.025) 40px),
        repeating-linear-gradient(90deg,transparent,transparent 39px,rgba(59,110,248,0.025) 40px)
      `,
      overflowX:"hidden",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@700;900&display=swap');
        @keyframes scanV   { 0%{top:0} 100%{top:100%} }
        @keyframes glitch  { 0%{transform:translate(0)} 25%{transform:translate(-3px,1px)} 50%{transform:translate(3px,-1px)} 75%{transform:translate(-2px,2px)} 100%{transform:translate(0)} }
        @keyframes ticker  { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
        @keyframes fadeUp  { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }
        @keyframes pulse   { 0%,100%{opacity:.5} 50%{opacity:1} }
        @keyframes blink   { 0%,100%{opacity:1} 50%{opacity:0} }
        @keyframes hoverGlow { 0%,100%{box-shadow:0 0 0 transparent} 50%{box-shadow:0 0 20px #3b6ef822} }
        .scan-v { position:fixed; left:0; right:0; height:2px; background:linear-gradient(transparent,rgba(0,232,122,.12),transparent); animation:scanV 6s linear infinite; pointer-events:none; z-index:10; }
        .fade-up { animation:fadeUp .6s ease both; }
        .ticker-wrap { overflow:hidden; white-space:nowrap; }
        .ticker-inner { display:inline-block; animation:ticker 28s linear infinite; }
        .feat-card { cursor:pointer; transition:border-color .3s, background .3s; }
        .feat-card:hover { background:#0e1228 !important; }
        .cta-btn { cursor:pointer; transition:all .2s; position:relative; overflow:hidden; }
        .cta-btn:hover { transform:translateY(-2px); filter:brightness(1.2); }
        .nav-link { cursor:pointer; transition:color .2s; }
        .nav-link:hover { color:#ddeeff !important; }
        .stat-card { transition:border-color .3s; }
        .stat-card:hover { border-color:#3b6ef888 !important; }
      `}</style>

      <div className="scan-v" />

      {/* ─── NAV ─── */}
      <nav style={{
        position:"sticky", top:0, zIndex:100,
        backgroundColor:"#06070fee", backdropFilter:"blur(8px)",
        borderBottom:`1px solid ${C.border}`,
        padding:"0 40px", height:52,
        display:"flex", alignItems:"center", justifyContent:"space-between",
      }}>
        <div style={{ display:"flex", alignItems:"center", gap:10 }}>
          <div style={{
            fontFamily:"'Orbitron',sans-serif", fontSize:18, fontWeight:900,
            color:C.white, letterSpacing:5,
            textShadow:`0 0 20px ${C.blue}66`,
            animation: glitch ? "glitch .11s steps(1) both" : "none",
          }}>Anviksha</div>
          <div style={{ fontSize:8, color:C.textDim, letterSpacing:3, marginTop:2 }}>SENTINEL</div>
        </div>

        <div style={{ display:"flex", gap:32, alignItems:"center" }}>
          {["OVERVIEW","FEATURES","SECTORS","DOCS"].map(l => (
            <span key={l} className="nav-link" style={{ fontSize:10, color:C.textDim, letterSpacing:2 }}>{l}</span>
          ))}
          <button className="cta-btn" onClick={onEnter} style={{
            padding:"7px 20px", border:`1px solid ${C.blue}66`,
            backgroundColor:`${C.blue}11`, color:C.blue,
            fontFamily:"inherit", fontSize:10, letterSpacing:3, cursor:"pointer",
          }}>
            LAUNCH ▸
          </button>
        </div>

        <div style={{ fontSize:11, color:C.green, fontFamily:"'Orbitron',sans-serif", letterSpacing:2 }}>
          {time}
        </div>
      </nav>

      {/* ─── HERO ─── */}
      <section style={{
        padding:"80px 60px 60px", position:"relative",
        display:"flex", flexDirection:"column", alignItems:"center", textAlign:"center",
        borderBottom:`1px solid ${C.border}`,
      }}>
        {/* Big corner ticks */}
        {[{top:20,left:20},{top:20,right:20},{bottom:20,left:20},{bottom:20,right:20}].map((pos,i)=>(
          <div key={i} style={{position:"absolute",width:28,height:28,...pos,
            borderTop: i<2?`1px solid ${C.blue}33`:undefined,
            borderBottom: i>=2?`1px solid ${C.blue}33`:undefined,
            borderLeft: i%2===0?`1px solid ${C.blue}33`:undefined,
            borderRight: i%2===1?`1px solid ${C.blue}33`:undefined,
          }}/>
        ))}

        <div className="fade-up" style={{ fontSize:9, color:C.blue, letterSpacing:5, marginBottom:20, animationDelay:".1s" }}>
          ● SYSTEM ONLINE — ALL SECTORS NOMINAL
        </div>

        <div className="fade-up" style={{ animationDelay:".2s" }}>
          <div style={{
            fontFamily:"'Orbitron',sans-serif", fontSize:58, fontWeight:900,
            color:C.white, letterSpacing:10, lineHeight:1,
            textShadow:`0 0 40px ${C.blue}55, 0 0 80px ${C.blue}22`,
          }}>Anviksha</div>
          <div style={{
            fontFamily:"'Orbitron',sans-serif", fontSize:18, fontWeight:700,
            color:C.blue, letterSpacing:14, marginTop:4,
          }}>SENTINEL</div>
        </div>

        <div className="fade-up" style={{ fontSize:13, color:C.text, maxWidth:520, lineHeight:2, marginTop:28, letterSpacing:1, animationDelay:".35s" }}>
          A unified tactical surveillance platform for perimeter security, thermal imaging,
          real-time threat assessment, and environmental risk intelligence.
        </div>

        <div className="fade-up" style={{ display:"flex", gap:16, marginTop:36, animationDelay:".5s" }}>
          <button className="cta-btn" onClick={onEnter} style={{
            padding:"13px 36px", border:`1px solid ${C.green}`,
            backgroundColor:`${C.green}18`, color:C.green,
            fontFamily:"inherit", fontSize:12, letterSpacing:4, cursor:"pointer",
            boxShadow:`0 0 20px ${C.green}22`,
          }}>
            ▸ ENTER DASHBOARD
          </button>
          <button className="cta-btn" style={{
            padding:"13px 36px", border:`1px solid ${C.blue}44`,
            backgroundColor:"transparent", color:C.blue,
            fontFamily:"inherit", fontSize:12, letterSpacing:4, cursor:"pointer",
          }}>
            VIEW DOCS
          </button>
        </div>

        {/* Stats row */}
        <div className="fade-up" style={{ display:"flex", gap:20, marginTop:52, animationDelay:".65s" }}>
          {STATS.map((s,i) => (
            <div key={i} className="stat-card" style={{
              backgroundColor:C.panel, border:`1px solid ${C.border}`,
              padding:"14px 22px", position:"relative", minWidth:110, textAlign:"center",
              transition:"border-color .3s",
            }}>
              <CornerBox c={C.blue} s={6}/>
              <div style={{ fontFamily:"'Orbitron',sans-serif", fontSize:20, color:C.white, letterSpacing:2 }}>{s.val}</div>
              <div style={{ fontSize:8, color:C.textDim, letterSpacing:2, marginTop:4 }}>{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ─── TICKER ─── */}
      <div style={{ borderBottom:`1px solid ${C.border}`, padding:"10px 0", backgroundColor:`${C.blue}08` }}>
        <div className="ticker-wrap">
          <div className="ticker-inner">
            {[...TICKER_ITEMS,...TICKER_ITEMS].map((item,i)=>(
              <span key={i} style={{ fontSize:9, color:C.blue, letterSpacing:4, marginRight:60 }}>
                ◈ {item}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* ─── FEATURES ─── */}
      <section style={{ padding:"60px 60px", borderBottom:`1px solid ${C.border}` }}>
        <div style={{ fontSize:9, color:C.textDim, letterSpacing:4, marginBottom:8 }}>▸ CAPABILITIES</div>
        <div style={{ fontSize:22, fontFamily:"'Orbitron',sans-serif", color:C.white, letterSpacing:4, marginBottom:36 }}>
          SYSTEM FEATURES
        </div>

        <div style={{ display:"grid", gridTemplateColumns:"repeat(3, 1fr)", gap:14 }}>
          {FEATURES.map((f,i)=>(
            <div key={i}
              className="feat-card"
              onClick={()=>setActiveFeat(i)}
              style={{
                backgroundColor: activeFeat===i ? `${C.blue}0f` : C.panel,
                border:`1px solid ${activeFeat===i ? C.blue+"66" : C.border}`,
                padding:"20px 18px", position:"relative",
              }}>
              <CornerBox c={activeFeat===i ? C.blue : C.textDim} s={7}/>
              <div style={{ display:"flex", gap:10, alignItems:"flex-start", marginBottom:10 }}>
                <span style={{ fontSize:20, color: activeFeat===i ? C.blue : C.textDim }}>{f.icon}</span>
                <div style={{ fontSize:10, color: activeFeat===i ? C.white : C.text, letterSpacing:2, lineHeight:1.5 }}>{f.title}</div>
              </div>
              <div style={{ fontSize:11, color:C.textDim, lineHeight:1.8 }}>{f.desc}</div>
              {activeFeat===i && (
                <div style={{ position:"absolute", bottom:0, left:0, right:0, height:2,
                  background:`linear-gradient(90deg,transparent,${C.blue},transparent)`,
                  boxShadow:`0 0 8px ${C.blue}88`
                }}/>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* ─── SYSTEM SPEC ─── */}
      <section style={{ padding:"60px 60px", borderBottom:`1px solid ${C.border}`, display:"grid", gridTemplateColumns:"1fr 1fr", gap:40 }}>
        <div>
          <div style={{ fontSize:9, color:C.textDim, letterSpacing:4, marginBottom:8 }}>▸ ARCHITECTURE</div>
          <div style={{ fontSize:20, fontFamily:"'Orbitron',sans-serif", color:C.white, letterSpacing:3, marginBottom:24 }}>TECH STACK</div>
          {[
            ["FRONTEND",    "React + Socket.IO client"],
            ["BACKEND",     "Flask + Python"],
            ["VIDEO",       "MJPEG / RTSP stream pipeline"],
            ["REALTIME",    "WebSocket event bus"],
            ["ENCRYPTION",  "AES-256 channel"],
            ["DEPLOYMENT",  "Docker / Nginx"],
          ].map(([k,v],i)=>(
            <div key={i} style={{ display:"flex", justifyContent:"space-between", padding:"9px 0", borderBottom:`1px solid ${C.borderLo}` }}>
              <span style={{ fontSize:10, color:C.textDim, letterSpacing:2 }}>{k}</span>
              <span style={{ fontSize:11, color:C.white }}>{v}</span>
            </div>
          ))}
        </div>

        <div>
          <div style={{ fontSize:9, color:C.textDim, letterSpacing:4, marginBottom:8 }}>▸ CAMERA MODES</div>
          <div style={{ fontSize:20, fontFamily:"'Orbitron',sans-serif", color:C.white, letterSpacing:3, marginBottom:24 }}>FEED TYPES</div>
          {[
            { label:"STANDARD COLOUR",  dot:C.green,  desc:"Vibrant colour-graded feeds for daylight operation" },
            { label:"THERMAL IR",       dot:"#aaa",    desc:"Greyscale black-and-white heat detection" },
            { label:"NIGHT ENHANCED",   dot:C.blue,   desc:"Boosted gain for low-light environments" },
            { label:"AERIAL / DRONE",   dot:C.amber,  desc:"Elevated sector and overhead coverage" },
            { label:"PERIMETER",        dot:C.cyan??C.blue, desc:"Long-range boundary surveillance" },
          ].map((item,i)=>(
            <div key={i} style={{ display:"flex", gap:12, padding:"9px 0", borderBottom:`1px solid ${C.borderLo}`, alignItems:"center" }}>
              <div style={{ width:8, height:8, borderRadius:"50%", backgroundColor:item.dot, flexShrink:0, boxShadow:`0 0 6px ${item.dot}` }}/>
              <div>
                <div style={{ fontSize:10, color:C.white, letterSpacing:1 }}>{item.label}</div>
                <div style={{ fontSize:10, color:C.textDim, marginTop:2 }}>{item.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ─── CTA BANNER ─── */}
      <section style={{
        padding:"60px", textAlign:"center",
        background:`linear-gradient(135deg, ${C.violet}0a, ${C.blue}0a)`,
        borderBottom:`1px solid ${C.border}`, position:"relative",
      }}>
        <CornerBox c={C.violet} s={14}/>
        <div style={{ fontSize:9, color:C.violet, letterSpacing:4, marginBottom:10 }}>▸ READY TO DEPLOY</div>
        <div style={{ fontFamily:"'Orbitron',sans-serif", fontSize:28, color:C.white, letterSpacing:6, marginBottom:16 }}>
          SECURE YOUR PERIMETER
        </div>
        <div style={{ fontSize:12, color:C.text, marginBottom:32, letterSpacing:1 }}>
          Authenticate to access the live surveillance command dashboard
        </div>
        <button className="cta-btn" onClick={onEnter} style={{
          padding:"14px 48px", border:`1px solid ${C.green}`,
          backgroundColor:`${C.green}18`, color:C.green,
          fontFamily:"inherit", fontSize:13, letterSpacing:5, cursor:"pointer",
          boxShadow:`0 0 30px ${C.green}22`,
        }}>
          ▸ AUTHENTICATE &amp; ENTER
        </button>
      </section>

      {/* ─── FOOTER ─── */}
      <footer style={{ padding:"20px 60px", display:"flex", justifyContent:"space-between", alignItems:"center" }}>
        <div style={{ fontFamily:"'Orbitron',sans-serif", fontSize:12, color:C.textDim, letterSpacing:4 }}>ARGUS</div>
        <div style={{ fontSize:9, color:C.textDim, letterSpacing:2 }}>
          © 2026 Anviksha SENTINEL SYSTEMS — ALL ACCESS MONITORED
        </div>
        <div style={{ fontSize:9, color:C.green, letterSpacing:2, animation:"pulse 2s infinite" }}>
          ● SYSTEMS NOMINAL
        </div>
      </footer>
    </div>
  );
}