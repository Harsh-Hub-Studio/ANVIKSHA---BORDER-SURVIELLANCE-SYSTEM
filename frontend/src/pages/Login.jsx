import { useState, useEffect } from "react";

const GRID = 24;

export default function Login({ onLogin }) {
  const [user, setUser] = useState("");
  const [pass, setPass] = useState("");
  const [phase, setPhase] = useState("idle"); // idle | scanning | error | success
  const [scanPct, setScanPct] = useState(0);
  const [glitch, setGlitch] = useState(false);
  const [dots, setDots] = useState("");
  const [bootLines, setBootLines] = useState([]);
  const [showForm, setShowForm] = useState(false);

  const BOOT_SEQ = [
    "Anviksha SENTINEL OS v4.2.1 — INITIALISING...",
    "LOADING ENCRYPTION MODULE ............. OK",
    "CONNECTING TO SECURE RELAY ............ OK",
    "BIOMETRIC LAYER STANDBY ............... READY",
    "PERIMETER FEED HANDSHAKE .............. LIVE",
    "SYSTEM INTEGRITY CHECK ................ PASSED",
    "▸ AWAITING OPERATOR AUTHENTICATION",
  ];

  useEffect(() => {
    let i = 0;
    const iv = setInterval(() => {
      if (i < BOOT_SEQ.length) {
        setBootLines(p => [...p, BOOT_SEQ[i]]);
        i++;
      } else {
        clearInterval(iv);
        setTimeout(() => setShowForm(true), 400);
      }
    }, 280);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    const iv = setInterval(() => setDots(d => d.length >= 3 ? "" : d + "."), 500);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    const iv = setInterval(() => {
      if (Math.random() < 0.08) {
        setGlitch(true);
        setTimeout(() => setGlitch(false), 120);
      }
    }, 1200);
    return () => clearInterval(iv);
  }, []);

  const handleSubmit = () => {
    if (!user || !pass) return;
    setPhase("scanning");
    setScanPct(0);
    let p = 0;
    const iv = setInterval(() => {
      p += Math.random() * 14 + 3;
      setScanPct(Math.min(p, 100));
      if (p >= 100) {
        clearInterval(iv);
        if (user === "ADMIN" && pass === "1234") {
          setPhase("success");
          setTimeout(() => onLogin && onLogin(), 1400);
        } else {
          setPhase("error");
          setTimeout(() => setPhase("idle"), 2200);
        }
      }
    }, 80);
  };

  const statusColor = phase === "error" ? "#ef4444" : phase === "success" ? "#00e87a" : "#3b6ef8";

  return (
    <div style={{
      minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
      backgroundColor: "#06070f",
      backgroundImage: `
        radial-gradient(ellipse at 20% 50%, #2a105055 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, #1a3a8a33 0%, transparent 50%),
        repeating-linear-gradient(0deg, transparent, transparent ${GRID-1}px, rgba(59,110,248,0.03) ${GRID}px),
        repeating-linear-gradient(90deg, transparent, transparent ${GRID-1}px, rgba(59,110,248,0.03) ${GRID}px)
      `,
      fontFamily: "'Share Tech Mono', 'Courier New', monospace",
      position: "relative", overflow: "hidden",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@700;900&display=swap');
        @keyframes scanV    { 0%{top:0} 100%{top:100%} }
        @keyframes pulse    { 0%,100%{opacity:.6} 50%{opacity:1} }
        @keyframes fadeUp   { from{opacity:0;transform:translateY(14px)} to{opacity:1;transform:translateY(0)} }
        @keyframes blink    { 0%,100%{opacity:1} 50%{opacity:0} }
        @keyframes glitch   { 0%{transform:translate(0)} 20%{transform:translate(-3px,1px)} 40%{transform:translate(3px,-1px)} 60%{transform:translate(-2px,2px)} 80%{transform:translate(2px,-2px)} 100%{transform:translate(0)} }
        @keyframes borderPulse { 0%,100%{box-shadow:0 0 0px #3b6ef800} 50%{box-shadow:0 0 22px #3b6ef844} }
        .scan-v { position:absolute; left:0; right:0; height:2px; background:linear-gradient(transparent,rgba(0,232,122,.18),transparent); animation:scanV 4s linear infinite; pointer-events:none; z-index:0; }
        .fade-up { animation: fadeUp .5s ease both; }
        .blink-cur { animation: blink 1s step-end infinite; }
        .login-btn { cursor:pointer; transition: all .2s; }
        .login-btn:hover { filter: brightness(1.25); transform: translateY(-1px); }
        .input-field { background:transparent; border:none; outline:none; width:100%; color:#ddeeff; font-family:inherit; font-size:14px; letter-spacing:1px; caret-color:#00e87a; }
        .input-field::placeholder { color:#2e4070; }
      `}</style>

      {/* Full-page scan line */}
      <div className="scan-v" />

      {/* Corner decoration — large */}
      {[
        { top:16, left:16, borderTop:"2px solid #3b6ef844", borderLeft:"2px solid #3b6ef844" },
        { top:16, right:16, borderTop:"2px solid #3b6ef844", borderRight:"2px solid #3b6ef844" },
        { bottom:16, left:16, borderBottom:"2px solid #3b6ef844", borderLeft:"2px solid #3b6ef844" },
        { bottom:16, right:16, borderBottom:"2px solid #3b6ef844", borderRight:"2px solid #3b6ef844" },
      ].map((s,i) => <div key={i} style={{ position:"absolute", width:48, height:48, ...s }} />)}

      {/* Vertical rule left */}
      <div style={{ position:"absolute", left:80, top:0, bottom:0, width:"1px", background:"linear-gradient(transparent,#3b6ef822,transparent)" }} />
      <div style={{ position:"absolute", right:80, top:0, bottom:0, width:"1px", background:"linear-gradient(transparent,#3b6ef822,transparent)" }} />

      <div style={{ width: 480, display:"flex", flexDirection:"column", gap:0, position:"relative", zIndex:1 }}>

        {/* Header logo */}
        <div style={{ textAlign:"center", marginBottom:28 }} className="fade-up">
          <div style={{
            fontFamily:"'Orbitron',sans-serif", fontSize:34, fontWeight:900,
            color:"#ddeeff", letterSpacing:8,
            textShadow:"0 0 30px #3b6ef888, 0 0 60px #3b6ef844",
            animation: glitch ? "glitch .12s steps(1) both" : "none",
          }}>
            Anviksha
          </div>
          <div style={{ fontSize:9, color:"#2e4070", letterSpacing:6, marginTop:4 }}>
            SENTINEL SURVEILLANCE SYSTEM
          </div>
          <div style={{ width:120, height:1, background:"linear-gradient(90deg,transparent,#3b6ef888,transparent)", margin:"12px auto 0" }} />
        </div>

        {/* Boot sequence terminal */}
        <div style={{
          backgroundColor:"#090b18", border:"1px solid #141c3a",
          padding:"14px 16px", marginBottom:16,
          position:"relative",
        }}>
          {/* corner ticks */}
          {[{top:0,left:0,borderTop:"1.5px solid #3b6ef8",borderLeft:"1.5px solid #3b6ef8"},
            {top:0,right:0,borderTop:"1.5px solid #3b6ef8",borderRight:"1.5px solid #3b6ef8"},
            {bottom:0,left:0,borderBottom:"1.5px solid #3b6ef8",borderLeft:"1.5px solid #3b6ef8"},
            {bottom:0,right:0,borderBottom:"1.5px solid #3b6ef8",borderRight:"1.5px solid #3b6ef8"},
          ].map((s,i)=><div key={i} style={{position:"absolute",width:8,height:8,...s}}/>)}

          <div style={{ fontSize:8, color:"#2e4070", letterSpacing:3, marginBottom:8 }}>▸ SYSTEM BOOT LOG</div>
          <div style={{ display:"flex", flexDirection:"column", gap:4 }}>
           // FIXED — filters undefined and guards .startsWith
{bootLines.filter(Boolean).map((l, i) => (
  <div key={i} className="fade-up" style={{
    fontSize:11, letterSpacing:.5, lineHeight:1.5,
    color: l && l.startsWith("▸") ? "#00e87a" : "#8aaad8",
    animationDelay:`${i*0.05}s`
  }}>{l}</div>
))}
            {!showForm && bootLines.length < BOOT_SEQ.length && (
              <div style={{ fontSize:11, color:"#2e4070" }}>_{dots}</div>
            )}
          </div>
        </div>

        {/* Login form */}
        {showForm && (
          <div className="fade-up" style={{
            backgroundColor:"#090b18",
            border:`1px solid ${statusColor}44`,
            padding:"20px 20px",
            position:"relative",
            animation:"borderPulse 3s ease infinite",
          }}>
            {[{top:0,left:0,bT:`1.5px solid ${statusColor}`,bL:`1.5px solid ${statusColor}`},
              {top:0,right:0,bT:`1.5px solid ${statusColor}`,bR:`1.5px solid ${statusColor}`},
              {bot:0,left:0,bB:`1.5px solid ${statusColor}`,bL:`1.5px solid ${statusColor}`},
              {bot:0,right:0,bB:`1.5px solid ${statusColor}`,bR:`1.5px solid ${statusColor}`},
            ].map((s,i)=>(
              <div key={i} style={{position:"absolute",width:10,height:10,
                top:s.top??undefined,bottom:s.bot??undefined,left:s.left??undefined,right:s.right??undefined,
                borderTop:s.bT,borderLeft:s.bL,borderBottom:s.bB,borderRight:s.bR
              }}/>
            ))}

            <div style={{ fontSize:9, color:"#2e4070", letterSpacing:3, marginBottom:16 }}>▸ OPERATOR AUTHENTICATION</div>

            {/* Username */}
            <div style={{ marginBottom:14 }}>
              <div style={{ fontSize:9, color:"#3b6ef8", letterSpacing:2, marginBottom:6 }}>OPERATOR ID</div>
              <div style={{
                borderBottom:"1px solid #141c3a", paddingBottom:8, display:"flex", alignItems:"center", gap:8,
                borderColor: user ? "#3b6ef8aa" : "#141c3a",
                transition:"border-color .3s",
              }}>
                <span style={{ color:"#3b6ef8", fontSize:12 }}>◈</span>
                <input
                  className="input-field"
                  placeholder="ENTER OPERATOR ID"
                  value={user}
                  onChange={e => setUser(e.target.value.toUpperCase())}
                  onKeyDown={e => e.key==="Enter" && handleSubmit()}
                />
              </div>
            </div>

            {/* Password */}
            <div style={{ marginBottom:22 }}>
              <div style={{ fontSize:9, color:"#3b6ef8", letterSpacing:2, marginBottom:6 }}>ACCESS CODE</div>
              <div style={{
                borderBottom:"1px solid #141c3a", paddingBottom:8, display:"flex", alignItems:"center", gap:8,
                borderColor: pass ? "#3b6ef8aa" : "#141c3a",
                transition:"border-color .3s",
              }}>
                <span style={{ color:"#3b6ef8", fontSize:12 }}>◉</span>
                <input
                  className="input-field"
                  type="password"
                  placeholder="ENTER ACCESS CODE"
                  value={pass}
                  onChange={e => setPass(e.target.value)}
                  onKeyDown={e => e.key==="Enter" && handleSubmit()}
                />
              </div>
            </div>

            {/* Scan bar */}
            {phase === "scanning" && (
              <div style={{ marginBottom:14 }}>
                <div style={{ fontSize:9, color:"#3b6ef8", letterSpacing:2, marginBottom:6 }}>
                  VERIFYING CREDENTIALS{dots}
                </div>
                <div style={{ height:3, backgroundColor:"#0e1228", borderRadius:2 }}>
                  <div style={{
                    height:"100%", width:`${scanPct}%`,
                    background:"linear-gradient(90deg,#7c3aed,#3b6ef8)",
                    boxShadow:"0 0 8px #3b6ef888",
                    transition:"width .1s linear",
                  }}/>
                </div>
              </div>
            )}

            {phase === "error" && (
              <div style={{ fontSize:11, color:"#ef4444", letterSpacing:2, marginBottom:14, animation:"fadeUp .3s ease" }}>
                ⚠ ACCESS DENIED — INVALID CREDENTIALS
              </div>
            )}

            {phase === "success" && (
              <div style={{ fontSize:11, color:"#00e87a", letterSpacing:2, marginBottom:14, animation:"fadeUp .3s ease" }}>
                ✓ IDENTITY CONFIRMED — LOADING DASHBOARD{dots}
              </div>
            )}

            {/* Submit */}
            <button
              className="login-btn"
              onClick={handleSubmit}
              disabled={phase === "scanning" || phase === "success"}
              style={{
                width:"100%", padding:"11px", border:`1px solid ${statusColor}66`,
                backgroundColor:`${statusColor}11`, color:statusColor,
                fontFamily:"inherit", fontSize:12, letterSpacing:4,
                cursor: phase==="scanning"||phase==="success" ? "not-allowed" : "pointer",
                opacity: phase==="scanning"||phase==="success" ? .6 : 1,
                transition:"all .2s",
              }}
            >
              {phase==="scanning" ? "VERIFYING..." : phase==="success" ? "ACCESS GRANTED" : "AUTHENTICATE ▸"}
            </button>

            <div style={{ fontSize:8, color:"#2e4070", textAlign:"center", marginTop:12, letterSpacing:1 }}>
              UNAUTHORISED ACCESS IS MONITORED AND PROSECUTED
            </div>
          </div>
        )}

        {/* Footer */}
        <div style={{ display:"flex", justifyContent:"space-between", marginTop:14, fontSize:8, color:"#2e4070", letterSpacing:1 }}>
          <span>Anviksha SENTINEL v4.2.1</span>
          <span style={{ animation:"pulse 2s infinite" }}>● SECURE CHANNEL ACTIVE</span>
          <span>AES-256 ENCRYPTED</span>
        </div>
      </div>
    </div>
  );
}