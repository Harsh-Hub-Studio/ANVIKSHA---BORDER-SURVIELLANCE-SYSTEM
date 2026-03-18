import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';

const socket = io('http://localhost:5000');
const FLASK_IP = 'http://20.20.20.87:5001';;

const getMilTime = () => new Date().toTimeString().slice(0, 8).replace(/:/g, '') + 'Z';

const C = {
  bg:       '#06070f',
  panel:    '#090b18',
  border:   '#141c3a',
  borderLo: '#0e1228',
  blue:     '#3b6ef8',
  blueDim:  '#1a3a8a',
  violet:   '#7c3aed',
  violetLo: '#2a1050',
  green:    '#00e87a',
  greenDim: '#00a855',
  amber:    '#f59e0b',
  red:      '#ef4444',
  cyan:     '#00d4ff',
  orange:   '#ff6b35',
  text:     '#8aaad8',
  textDim:  '#2e4070',
  white:    '#ddeeff',
};

const Bx = ({ c = C.green, s = 9 }) => (
  <>
    {[
      [{ top:0, left:0 },   { borderTop:`1.5px solid ${c}`, borderLeft:`1.5px solid ${c}` }],
      [{ top:0, right:0 },  { borderTop:`1.5px solid ${c}`, borderRight:`1.5px solid ${c}` }],
      [{ bottom:0, left:0 },{ borderBottom:`1.5px solid ${c}`, borderLeft:`1.5px solid ${c}` }],
      [{ bottom:0, right:0},{ borderBottom:`1.5px solid ${c}`, borderRight:`1.5px solid ${c}` }],
    ].map(([pos, brd], i) => (
      <div key={i} style={{ position:'absolute', width:s, height:s, ...pos, ...brd }} />
    ))}
  </>
);

const threatColor = t => t === 'HIGH' ? C.red : t === 'MED' ? C.amber : C.green;

const calcRisk = ({ fog, visibility, wind, humidity, moonPhase, cloudCover, isDay }) => {
  let s = 0;
  if (!isDay)              s += 25;
  if (fog)                 s += 20;
  if (visibility < 3)      s += 15;
  else if (visibility < 7) s += 7;
  if (cloudCover > 70)     s += 10;
  if (wind < 5)            s += 5;
  if (humidity > 80)       s += 5;
  if (moonPhase < 0.2 || moonPhase > 0.8) s += 10;
  return Math.min(s, 100);
};

const WeatherPanel = () => {
  const [time, setTime] = useState(getMilTime());
  useEffect(() => {
    const t = setInterval(() => setTime(getMilTime()), 1000);
    return () => clearInterval(t);
  }, []);

  const wx = {
    location:   'MUMBAI // 19.07N 72.87E',
    temp:       86.7,
    condition:  'CLEAR',
    isDay:      false,
    fog:        false,
    visibility: 10,
    wind:       12,
    humidity:   68,
    cloudCover: 5,
    pressure:   1012,
    moonPhase:  0.15,
    moonLabel:  'WAXING CRESCENT',
    dewpoint:   74,
  };

  const risk = calcRisk(wx);
  const rc   = risk >= 70 ? C.red : risk >= 40 ? C.amber : C.green;
  const rl   = risk >= 70 ? 'CRITICAL' : risk >= 40 ? 'ELEVATED' : 'LOW';

  const factors = [
    { label:'LIGHT COND.',  icon:'◑', val: wx.isDay ? 'DAYLIGHT' : 'NIGHT OPS',  threat: wx.isDay ? 'LOW' : 'HIGH',
      note: wx.isDay ? 'Full daylight — max visibility' : 'Night — thermal/NVG required' },
    { label:'VISIBILITY',   icon:'◈', val:`${wx.visibility} KM`,
      threat: wx.visibility < 3 ? 'HIGH' : wx.visibility < 7 ? 'MED' : 'LOW',
      note: wx.visibility < 3 ? 'Severe — movement undetectable' : wx.visibility < 7 ? 'Reduced — partial concealment' : 'Clear — full surveillance' },
    { label:'FOG STATUS',   icon:'≋', val: wx.fog ? 'ACTIVE' : 'NONE',
      threat: wx.fog ? 'HIGH' : 'LOW',
      note: wx.fog ? 'Dense cover — camera blind zones likely' : 'No fog — normal ops' },
    { label:'WIND SPEED',   icon:'≈', val:`${wx.wind} KT`,
      threat: wx.wind < 5 ? 'HIGH' : wx.wind > 20 ? 'MED' : 'LOW',
      note: wx.wind < 5 ? 'Calm — footsteps audible' : wx.wind > 20 ? 'High wind — noise masks movement' : 'Moderate — standard ambient noise' },
    { label:'HUMIDITY',     icon:'◉', val:`${wx.humidity}%`,
      threat: wx.humidity > 85 ? 'HIGH' : wx.humidity > 70 ? 'MED' : 'LOW',
      note: wx.humidity > 85 ? 'Near saturation — fog imminent' : wx.humidity > 70 ? 'Elevated — monitor for fog' : 'Normal range' },
    { label:'CLOUD COVER',  icon:'☁', val:`${wx.cloudCover}%`,
      threat: wx.cloudCover > 70 ? 'HIGH' : wx.cloudCover > 40 ? 'MED' : 'LOW',
      note: wx.cloudCover > 70 ? 'Overcast — aerial detection impaired' : wx.cloudCover > 40 ? 'Partial cloud' : 'Clear skies — full aerial surveillance' },
    { label:'MOON PHASE',   icon:'☽', val: wx.moonLabel,
      threat: wx.moonPhase < 0.2 || wx.moonPhase > 0.8 ? 'HIGH' : wx.moonPhase > 0.4 && wx.moonPhase < 0.6 ? 'LOW' : 'MED',
      note: wx.moonPhase < 0.25 ? 'Near new moon — near-zero illumination' : 'Partial moon — low ambient light' },
    { label:'DEW POINT',    icon:'◌', val:`${wx.dewpoint}F`,
      threat: wx.dewpoint > 80 ? 'HIGH' : wx.dewpoint > 70 ? 'MED' : 'LOW',
      note: wx.dewpoint > 80 ? 'High — condensation on sensors likely' : wx.dewpoint > 70 ? 'Elevated — monitor sensors' : 'Low — sensors clear' },
    { label:'PRESSURE',     icon:'⊞', val:`${wx.pressure} MB`, threat: 'LOW', note: 'Stable — no rapid weather change' },
    { label:'TEMPERATURE',  icon:'⊕', val:`${wx.temp}F`,       threat: 'LOW', note: 'Ambient normal — no thermal masking' },
  ];

  const factorRows = (
    <div style={{ display:'flex', flexDirection:'column', gap:'8px' }}>
      {factors.map((f, i) => (
        <div key={i} style={{ borderLeft:`2px solid ${threatColor(f.threat)}44`, paddingLeft:'8px' }}>
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
            <div style={{ display:'flex', gap:'5px', alignItems:'center' }}>
              <span style={{ color:threatColor(f.threat), fontSize:'14px' }}>{f.icon}</span>
              <span style={{ fontSize:'11px', color:C.textDim, letterSpacing:'1px' }}>{f.label}</span>
            </div>
            <div style={{ display:'flex', gap:'6px', alignItems:'center' }}>
              <span style={{ fontSize:'12px', color:C.white }}>{f.val}</span>
              <span style={{ fontSize:'10px', color:threatColor(f.threat), border:`1px solid ${threatColor(f.threat)}44`, padding:'1px 4px', letterSpacing:'1px' }}>{f.threat}</span>
            </div>
          </div>
          <div style={{ fontSize:'11px', color:C.textDim, marginTop:'2px', lineHeight:'1.5' }}>{f.note}</div>
        </div>
      ))}
    </div>
  );

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'10px' }}>

      {/* Time / Weather bar — scrolling location & condition */}
      <div className="panel" style={{ backgroundColor:C.panel, border:`1px solid ${C.border}`, padding:'9px 13px', position:'relative', display:'flex', justifyContent:'space-between', alignItems:'center', overflow:'hidden' }}>
        <Bx c={C.violet} s={8} />
        <div style={{ overflow:'hidden', height:'34px', flex:1 }}>
          <div className="scroll-panel" style={{ animationDuration:'18s' }}>
            <div style={{ fontSize:'14px', color:C.textDim, letterSpacing:'2px' }}>{wx.location}</div>
            <div style={{ fontSize:'16px', color:C.text, marginTop:'2px', letterSpacing:'1px' }}>{wx.condition} // {wx.isDay ? 'DAYLIGHT' : 'NIGHT OPS'}</div>
            <div style={{ fontSize:'13px', color:C.textDim, letterSpacing:'2px', marginTop:'10px' }}>TEMP {wx.temp}°F // WIND {wx.wind}KT // HUM {wx.humidity}%</div>
            <div style={{ fontSize:'13px', color:C.textDim, letterSpacing:'2px', marginTop:'4px' }}>PRESSURE {wx.pressure}MB // CLOUD {wx.cloudCover}% // VIS {wx.visibility}KM</div>
            {/* duplicate for seamless loop */}
            <div style={{ fontSize:'14px', color:C.textDim, letterSpacing:'2px', marginTop:'10px' }}>{wx.location}</div>
            <div style={{ fontSize:'16px', color:C.text, marginTop:'2px', letterSpacing:'1px' }}>{wx.condition} // {wx.isDay ? 'DAYLIGHT' : 'NIGHT OPS'}</div>
            <div style={{ fontSize:'13px', color:C.textDim, letterSpacing:'2px', marginTop:'10px' }}>TEMP {wx.temp}°F // WIND {wx.wind}KT // HUM {wx.humidity}%</div>
            <div style={{ fontSize:'13px', color:C.textDim, letterSpacing:'2px', marginTop:'4px' }}>PRESSURE {wx.pressure}MB // CLOUD {wx.cloudCover}% // VIS {wx.visibility}KM</div>
          </div>
        </div>
        <div style={{ textAlign:'right', marginLeft:'12px', flexShrink:0 }}>
          <div className="glow" style={{ fontSize:'30px', color:C.green, fontFamily:"'Oswald',sans-serif", letterSpacing:'2px' }}>{time}</div>
          <div style={{ fontSize:'12px', color:C.textDim }}>ZULU TIME</div>
        </div>
      </div>

      {/* Infiltration Risk — slow scroll */}
      <div className="panel" style={{ backgroundColor:C.panel, border:`1px solid ${rc}55`, padding:'12px 13px', position:'relative', overflow:'hidden' }}>
        <Bx c={rc} s={9} />
        <div style={{ fontSize:'13px', color:C.textDim, letterSpacing:'3px', marginBottom:'8px', fontFamily:"'Oswald',sans-serif" }}>▸ INFILTRATION RISK</div>
        <div style={{ overflow:'hidden', height:'110px' }}>
          <div className="scroll-panel" style={{ animationDuration:'22s' }}>
            {/* block 1 */}
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'8px' }}>
              <div>
                <div style={{ fontSize:'36px', fontFamily:"'Oswald',sans-serif", color:rc, lineHeight:1, textShadow:`0 0 20px ${rc}66` }}>
                  {risk}<span style={{ fontSize:'14px' }}>%</span>
                </div>
                <div style={{ fontSize:'13px', color:rc, letterSpacing:'3px', marginTop:'2px' }}>{rl} THREAT</div>
              </div>
              <div style={{ fontSize:'13px', color:C.textDim, textAlign:'right', lineHeight:2 }}>
                <div>NIGHT OPS <span style={{ color:C.red }}>+25</span></div>
                <div>DARK MOON <span style={{ color:C.amber }}>+10</span></div>
                <div>WIND CALM <span style={{ color:C.green }}>+5</span></div>
              </div>
            </div>
            <div style={{ height:'4px', backgroundColor:C.borderLo, marginBottom:'6px' }}>
              <div style={{ height:'100%', width:`${risk}%`, background:`linear-gradient(90deg,${C.violet},${rc})`, boxShadow:`0 0 8px ${rc}88` }} />
            </div>
            <div style={{ fontSize:'11px', color:C.textDim, letterSpacing:'1px' }}>
              {risk >= 70 ? '⚠ HEIGHTEN PERIMETER — CONDITIONS FAVOUR INFILTRATOR'
               : risk >= 40 ? '△ ELEVATED CAUTION — MONITOR ALL SECTORS'
               : '✓ CONDITIONS UNFAVOURABLE FOR INFILTRATION'}
            </div>
            {/* duplicate for seamless loop */}
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', margin:'18px 0 8px' }}>
              <div>
                <div style={{ fontSize:'36px', fontFamily:"'Oswald',sans-serif", color:rc, lineHeight:1, textShadow:`0 0 20px ${rc}66` }}>
                  {risk}<span style={{ fontSize:'14px' }}>%</span>
                </div>
                <div style={{ fontSize:'13px', color:rc, letterSpacing:'3px', marginTop:'2px' }}>{rl} THREAT</div>
              </div>
              <div style={{ fontSize:'13px', color:C.textDim, textAlign:'right', lineHeight:2 }}>
                <div>NIGHT OPS <span style={{ color:C.red }}>+25</span></div>
                <div>DARK MOON <span style={{ color:C.amber }}>+10</span></div>
                <div>WIND CALM <span style={{ color:C.green }}>+5</span></div>
              </div>
            </div>
            <div style={{ height:'4px', backgroundColor:C.borderLo, marginBottom:'6px' }}>
              <div style={{ height:'100%', width:`${risk}%`, background:`linear-gradient(90deg,${C.violet},${rc})`, boxShadow:`0 0 8px ${rc}88` }} />
            </div>
            <div style={{ fontSize:'11px', color:C.textDim, letterSpacing:'1px' }}>
              {risk >= 70 ? '⚠ HEIGHTEN PERIMETER — CONDITIONS FAVOUR INFILTRATOR'
               : risk >= 40 ? '△ ELEVATED CAUTION — MONITOR ALL SECTORS'
               : '✓ CONDITIONS UNFAVOURABLE FOR INFILTRATION'}
            </div>
          </div>
        </div>
      </div>

      {/* Environmental Factors — slow scroll */}
      <div className="panel" style={{ backgroundColor:C.panel, border:`1px solid ${C.border}`, padding:'12px 13px', position:'relative', overflow:'hidden' }}>
        <Bx c={C.blue} s={9} />
        <div style={{ fontSize:'12px', color:C.blue, letterSpacing:'3px', marginBottom:'10px', borderBottom:`1px solid ${C.borderLo}`, paddingBottom:'6px', fontFamily:"'Oswald',sans-serif" }}>
          ▸ ENVIRONMENTAL FACTORS
        </div>
        <div style={{ overflow:'hidden', height:'220px' }}>
          <div className="scroll-panel" style={{ animationDuration:'35s' }}>
            {factorRows}
            {/* duplicate for seamless loop */}
            <div style={{ marginTop:'16px' }}>{factorRows}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

const SurveillanceDashboard = () => {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    socket.on('new_alert', a => setAlerts(prev => [a, ...prev].slice(0, 8)));
    return () => socket.off('new_alert');
  }, []);

  // 8 cameras — cam 5 is THERMAL (black & white), all others are colourful
  const cams = [
    { id:1, feed:`${FLASK_IP}/video_feed_1`, label:'MAIN GATE',   sector:'ALPHA',   status:'LIVE',    color:C.green,  thermal:false },
    { id:2, feed:`${FLASK_IP}/video_feed_2`, label:'PERIMETER N', sector:'BRAVO',   status:'LIVE',    color:C.cyan,   thermal:false },
    { id:3, feed:`${FLASK_IP}/video_feed_3`, label:'SECTOR WEST', sector:'CHARLIE', status:'STANDBY', color:C.amber,  thermal:false },
    { id:4, feed:`${FLASK_IP}/video_feed_4`, label:'AERIAL OPS',  sector:'DELTA',   status:'OFFLINE', color:C.red,    thermal:false },
    { id:5, feed:`${FLASK_IP}/video_feed_5`, label:'THERMAL IR',  sector:'ECHO',    status:'LIVE',    color:'#aaaaaa',thermal:true  },
    { id:6, feed:`${FLASK_IP}/video_feed_6`, label:'EAST FLANK',  sector:'FOXTROT', status:'LIVE',    color:C.orange, thermal:false },
    { id:7, feed:`${FLASK_IP}/video_feed_7`, label:'ROOF OPS',    sector:'GOLF',    status:'LIVE',    color:C.violet, thermal:false },
    { id:8, feed:`${FLASK_IP}/video_feed_8`, label:'SOUTH GATE',  sector:'HOTEL',   status:'STANDBY', color:C.blue,   thermal:false },
  ];

  const camFilter = (cam) => {
    if (cam.thermal) return 'grayscale(1) brightness(0.95) contrast(1.15)';
    const grades = {
      1: 'saturate(1.5) hue-rotate(195deg) brightness(0.92)',
      2: 'saturate(1.6) hue-rotate(180deg) brightness(0.95)',
      3: 'saturate(1.4) sepia(0.3) brightness(0.88)',
      4: 'saturate(1.6) hue-rotate(340deg) brightness(0.85)',
      6: 'saturate(1.5) hue-rotate(20deg)  brightness(0.9)',
      7: 'saturate(1.4) hue-rotate(260deg) brightness(0.9)',
      8: 'saturate(1.5) hue-rotate(210deg) brightness(0.92)',
    };
    return grades[cam.id] || 'saturate(1.2)';
  };

  return (
    <div style={{
      backgroundColor: C.bg,
      color: C.text,
      minHeight: '100vh',
      padding: '14px',
      fontFamily: "'Share Tech Mono','Courier New',monospace",
      backgroundImage:`radial-gradient(ellipse at 15% 0%,${C.violetLo}99 0%,transparent 45%),radial-gradient(ellipse at 85% 100%,${C.blueDim}55 0%,transparent 45%),repeating-linear-gradient(0deg,transparent,transparent 39px,rgba(59,110,248,0.025) 40px),repeating-linear-gradient(90deg,transparent,transparent 39px,rgba(59,110,248,0.025) 40px)`,
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Oswald:wght@600;700&display=swap');
        @keyframes blink   {0%,100%{opacity:1}  50%{opacity:.1}}
        @keyframes flicker {0%,100%{opacity:1} 93%{opacity:.95} 95%{opacity:.8} 97%{opacity:.95}}
        @keyframes glow    {0%,100%{text-shadow:0 0 8px #00e87a} 50%{text-shadow:0 0 22px #00e87a,0 0 44px #00e87a33}}
        @keyframes scan    {0%{top:-4px} 100%{top:100%}}
        @keyframes scrollUp {0%{transform:translateY(0)} 100%{transform:translateY(-50%)}}
        .blink   {animation:blink 1.4s step-end infinite}
        .flicker {animation:flicker 8s infinite}
        .glow    {animation:glow 3s ease-in-out infinite}
        .scroll-panel {animation:scrollUp linear infinite; will-change:transform;}
        .scan-overlay{position:absolute;inset:0;pointer-events:none;z-index:2;background:repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(0,0,0,.07) 4px)}
        .scan-line{position:absolute;left:0;right:0;height:4px;z-index:3;pointer-events:none;background:linear-gradient(transparent,rgba(0,232,122,.1),transparent);animation:scan 5s linear infinite}
        .panel{position:relative}
        ::-webkit-scrollbar{width:3px}
        ::-webkit-scrollbar-track{background:${C.bg}}
        ::-webkit-scrollbar-thumb{background:${C.blueDim}}
      `}</style>

      <div style={{ display:'grid', gridTemplateColumns:'1fr 200px', gap:'12px', alignItems:'start' }}>

        {/* 4×2 camera grid */}
        <div style={{ display:'flex', flexDirection:'column', gap:'10px' }}>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:'10px' }}>
            {cams.map(cam => (
              <div key={cam.id} className="panel flicker" style={{
                backgroundColor: C.panel,
                border: `1px solid ${cam.color}44`,
                position: 'relative',
                boxShadow: `0 0 16px ${cam.color}12`,
              }}>
                <Bx c={cam.color} s={8} />

                {/* Header */}
                <div style={{
                  display:'flex', justifyContent:'space-between', alignItems:'center',
                  padding:'10px 14px',
                  backgroundColor:`${cam.color}08`,
                  borderBottom:`1px solid ${cam.color}2a`,
                }}>
                  <span style={{ fontSize:'14px', color:cam.color, letterSpacing:'1px', whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis', maxWidth:'72%' }}>
                    {cam.thermal ? '⬜ THERMAL IR' : `CAM-0${cam.id} // ${cam.label}`}
                  </span>
                  <span className={cam.status==='LIVE'?'blink':''} style={{ fontSize:'14px', color:cam.color }}>
                    {cam.status==='LIVE'?'●':cam.status==='STANDBY'?'◐':'○'}
                  </span>
                </div>

                {/* Feed */}
                <div style={{ position:'relative', backgroundColor:'#000', aspectRatio:'16/9', overflow:'hidden' }}>
                  <div className="scan-overlay" />
                  <div className="scan-line" />
                  <img
                    src={cam.feed}
                    style={{ width:'100%', height:'100%', objectFit:'cover', display:'block', filter:camFilter(cam) }}
                    alt={`cam${cam.id}`}
                  />
                  {/* Crosshair */}
                  <div style={{ position:'absolute', top:'50%', left:'50%', transform:'translate(-50%,-50%)', width:20, height:20, zIndex:4, pointerEvents:'none' }}>
                    <div style={{ position:'absolute', top:'50%', left:0, right:0, height:'1px', backgroundColor:`${cam.color}44` }} />
                    <div style={{ position:'absolute', left:'50%', top:0, bottom:0, width:'1px', backgroundColor:`${cam.color}44` }} />
                    <div style={{ position:'absolute', top:'50%', left:'50%', transform:'translate(-50%,-50%)', width:5, height:5, border:`1px solid ${cam.color}77`, borderRadius:'50%' }} />
                  </div>
                  {/* Badges */}
                  <div style={{ position:'absolute', top:5, right:6, fontSize:'9px', color:`${cam.color}cc`, zIndex:4, border:`1px solid ${cam.color}33`, padding:'1px 5px', backgroundColor:'rgba(0,0,0,0.65)' }}>
                    0{cam.id}
                  </div>
                  {cam.thermal && (
                    <div style={{ position:'absolute', bottom:5, left:6, fontSize:'9px', color:'#fff', zIndex:4, border:'1px solid #fff3', padding:'1px 5px', backgroundColor:'rgba(0,0,0,0.7)', letterSpacing:'1px' }}>
                      IR
                    </div>
                  )}
                  <div style={{ position:'absolute', bottom:5, right:6, fontSize:'8px', color:`${cam.color}88`, zIndex:4 }}>
                    {`${30+cam.id*7}N`}
                  </div>
                </div>

                {/* Footer */}
                <div style={{ padding:'9px 14px', display:'flex', justifyContent:'space-between', fontSize:'13px', color:C.textDim, borderTop:`1px solid ${cam.color}1a` }}>
                  <span>{cam.sector}</span>
                  <span>30FPS</span>
                </div>
              </div>
            ))}
          </div>

          {/* Incident log */}
          <div className="panel" style={{ backgroundColor:C.panel, border:`1px solid ${C.border}`, padding:'10px 14px', position:'relative', maxHeight:'110px' }}>
            <Bx c={C.violet} s={8} />
            <div style={{ fontSize:'8px', color:C.violet, letterSpacing:'3px', marginBottom:'7px', fontFamily:"'Oswald',sans-serif" }}>▸ INCIDENT LOG</div>
            <div style={{ overflowY:'auto', maxHeight:'65px', display:'flex', flexDirection:'column', gap:'5px' }}>
              {alerts.length === 0
                ? <span style={{ fontSize:'8px', color:C.textDim, letterSpacing:'2px' }}><span className="blink">_</span> MONITORING ALL SECTORS...</span>
                : alerts.map((a,i) => (
                    <div key={i} style={{ display:'flex', gap:'12px', borderLeft:`2px solid ${C.violet}`, paddingLeft:'8px' }}>
                      <span style={{ fontSize:'7px', color:C.textDim, whiteSpace:'nowrap' }}>{new Date(a.timestamp).toLocaleTimeString()}</span>
                      <span style={{ fontSize:'8px', color:C.white }}>{a.message}</span>
                    </div>
                  ))
              }
            </div>
          </div>
        </div>

        {/* Weather + infiltration */}
        <WeatherPanel />
      </div>
    </div>
  );
};

export default SurveillanceDashboard;