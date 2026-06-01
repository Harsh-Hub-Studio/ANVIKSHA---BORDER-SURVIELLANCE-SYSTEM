import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';

const socket = io('http://localhost:5001');
const FLASK_IP = 'http://localhost:5001';

const getMilTime = () => new Date().toTimeString().slice(0, 8).replace(/:/g, '') + 'Z';

const C = {
  bg: '#06070f',
  panel: '#090b18',
  border: '#141c3a',
  borderLo: '#0e1228',
  blue: '#3b6ef8',
  blueDim: '#1a3a8a',
  violet: '#7c3aed',
  violetLo: '#2a1050',
  green: '#00e87a',
  greenDim: '#00a855',
  amber: '#f59e0b',
  red: '#ef4444',
  cyan: '#00d4ff',
  orange: '#ff6b35',
  text: '#8aaad8',
  textDim: '#2e4070',
  white: '#ddeeff',
};

const Bx = ({ c = C.green, s = 9 }) => (
  <>
    {[
      [{ top: 0, left: 0 }, { borderTop: `1.5px solid ${c}`, borderLeft: `1.5px solid ${c}` }],
      [{ top: 0, right: 0 }, { borderTop: `1.5px solid ${c}`, borderRight: `1.5px solid ${c}` }],
      [{ bottom: 0, left: 0 }, { borderBottom: `1.5px solid ${c}`, borderLeft: `1.5px solid ${c}` }],
      [{ bottom: 0, right: 0 }, { borderBottom: `1.5px solid ${c}`, borderRight: `1.5px solid ${c}` }],
    ].map(([pos, brd], i) => (
      <div key={i} style={{ position: 'absolute', width: s, height: s, ...pos, ...brd }} />
    ))}
  </>
);

const threatColor = t => t === 'HIGH' ? C.red : t === 'MED' ? C.amber : C.green;

const calcRisk = ({ fog, visibility, wind, humidity, moonPhase, cloudCover, isDay }) => {
  let s = 0;
  if (!isDay) s += 25;
  if (fog) s += 20;
  if (visibility < 3) s += 15;
  else if (visibility < 7) s += 7;
  if (cloudCover > 70) s += 10;
  if (wind < 5) s += 5;
  if (humidity > 80) s += 5;
  if (moonPhase < 0.2 || moonPhase > 0.8) s += 10;
  return Math.min(s, 100);
};

const WeatherPanel = ({ intruderBoost = 0 }) => {
  const [time, setTime] = useState(getMilTime());
  const [wx, setWx] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const t = setInterval(() => setTime(getMilTime()), 1000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    const fetchWeather = async (lat, lon) => {
      try {
        const res = await fetch(
          `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,cloud_cover,pressure_msl,wind_speed_10m,is_day,weather_code&hourly=visibility,dew_point_2m&timezone=auto`
        );
        const data = await res.json();

        const current = data.current;
        const nowIndex = data.hourly.time.findIndex(t =>
          t.startsWith(current.time.slice(0, 13))
        );

        const visibilityMeters = nowIndex >= 0 ? data.hourly.visibility[nowIndex] : 10000;
        const dewpointC = nowIndex >= 0 ? data.hourly.dew_point_2m[nowIndex] : 20;

        const visibilityKm = (visibilityMeters / 1000).toFixed(1);
        const tempF = ((current.temperature_2m * 9) / 5 + 32).toFixed(1);
        const dewpointF = ((dewpointC * 9) / 5 + 32).toFixed(1);

        const weatherCodeMap = {
          0: 'CLEAR',
          1: 'MAINLY CLEAR',
          2: 'PARTLY CLOUDY',
          3: 'OVERCAST',
          45: 'FOG',
          48: 'RIME FOG',
          51: 'LIGHT DRIZZLE',
          53: 'DRIZZLE',
          55: 'HEAVY DRIZZLE',
          61: 'LIGHT RAIN',
          63: 'RAIN',
          65: 'HEAVY RAIN',
          71: 'LIGHT SNOW',
          73: 'SNOW',
          75: 'HEAVY SNOW',
          80: 'RAIN SHOWERS',
          81: 'HEAVY SHOWERS',
          82: 'VIOLENT SHOWERS',
          95: 'THUNDERSTORM'
        };

        setWx({
          location: `OPS ZONE // ${lat.toFixed(2)}N ${lon.toFixed(2)}E`,
          temp: parseFloat(tempF),
          condition: weatherCodeMap[current.weather_code] || 'UNKNOWN',
          isDay: current.is_day === 1,
          fog: [45, 48].includes(current.weather_code),
          visibility: parseFloat(visibilityKm),
          wind: Math.round(current.wind_speed_10m * 0.54),
          humidity: current.relative_humidity_2m,
          cloudCover: current.cloud_cover,
          pressure: Math.round(current.pressure_msl),
          moonPhase: 0.5,
          moonLabel: 'ESTIMATED',
          dewpoint: parseFloat(dewpointF),
        });

        setLoading(false);
      } catch (err) {
        console.error('Weather fetch failed:', err);
        setLoading(false);
      }
    };

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          fetchWeather(pos.coords.latitude, pos.coords.longitude);
        },
        () => {
          fetchWeather(19.0760, 72.8777);
        }
      );
    } else {
      fetchWeather(19.0760, 72.8777);
    }
  }, []);

  if (loading || !wx) {
    return (
      <div className="panel" style={{ backgroundColor: C.panel, border: `1px solid ${C.border}`, padding: '12px 14px', position: 'relative' }}>
        <Bx c={C.blue} s={8} />
        <div style={{ fontSize: '12px', color: C.textDim, letterSpacing: '2px' }}>
          <span className="blink">_</span> LOADING ENVIRONMENTAL DATA...
        </div>
      </div>
    );
  }

  const baseRisk = calcRisk(wx);
  const risk = Math.min(baseRisk + intruderBoost, 100);
  const rc = risk >= 70 ? C.red : risk >= 40 ? C.amber : C.green;
  const rl = risk >= 70 ? 'CRITICAL' : risk >= 40 ? 'ELEVATED' : 'LOW';

  const factors = [
    {
      label: 'LIGHT COND.', icon: '◑', val: wx.isDay ? 'DAYLIGHT' : 'NIGHT OPS', threat: wx.isDay ? 'LOW' : 'HIGH',
      note: wx.isDay ? 'Full daylight — max visibility' : 'Night — thermal/NVG required'
    },
    {
      label: 'VISIBILITY', icon: '◈', val: `${wx.visibility} KM`,
      threat: wx.visibility < 3 ? 'HIGH' : wx.visibility < 7 ? 'MED' : 'LOW',
      note: wx.visibility < 3 ? 'Severe — movement undetectable' : wx.visibility < 7 ? 'Reduced — partial concealment' : 'Clear — full surveillance'
    },
    {
      label: 'FOG STATUS', icon: '≋', val: wx.fog ? 'ACTIVE' : 'NONE',
      threat: wx.fog ? 'HIGH' : 'LOW',
      note: wx.fog ? 'Dense cover — camera blind zones likely' : 'No fog — normal ops'
    },
    {
      label: 'WIND SPEED', icon: '≈', val: `${wx.wind} KT`,
      threat: wx.wind < 5 ? 'HIGH' : wx.wind > 20 ? 'MED' : 'LOW',
      note: wx.wind < 5 ? 'Calm — footsteps audible' : wx.wind > 20 ? 'High wind — noise masks movement' : 'Moderate — standard ambient noise'
    },
    {
      label: 'HUMIDITY', icon: '◉', val: `${wx.humidity}%`,
      threat: wx.humidity > 85 ? 'HIGH' : wx.humidity > 70 ? 'MED' : 'LOW',
      note: wx.humidity > 85 ? 'Near saturation — fog imminent' : wx.humidity > 70 ? 'Elevated — monitor for fog' : 'Normal range'
    },
    {
      label: 'CLOUD COVER', icon: '☁', val: `${wx.cloudCover}%`,
      threat: wx.cloudCover > 70 ? 'HIGH' : wx.cloudCover > 40 ? 'MED' : 'LOW',
      note: wx.cloudCover > 70 ? 'Overcast — aerial detection impaired' : wx.cloudCover > 40 ? 'Partial cloud' : 'Clear skies — full aerial surveillance'
    },
    {
      label: 'MOON PHASE', icon: '☽', val: wx.moonLabel,
      threat: 'MED',
      note: 'Moon phase estimated for atmospheric context'
    },
    {
      label: 'DEW POINT', icon: '◌', val: `${wx.dewpoint}F`,
      threat: wx.dewpoint > 80 ? 'HIGH' : wx.dewpoint > 70 ? 'MED' : 'LOW',
      note: wx.dewpoint > 80 ? 'High — condensation on sensors likely' : wx.dewpoint > 70 ? 'Elevated — monitor sensors' : 'Low — sensors clear'
    },
    { label: 'PRESSURE', icon: '⊞', val: `${wx.pressure} MB`, threat: 'LOW', note: 'Stable — no rapid weather change' },
    { label: 'TEMPERATURE', icon: '⊕', val: `${wx.temp}F`, threat: 'LOW', note: 'Ambient normal — no thermal masking' },
  ];

  const factorRows = (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {factors.map((f, i) => (
        <div key={i} style={{ borderLeft: `2px solid ${threatColor(f.threat)}44`, paddingLeft: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', gap: '5px', alignItems: 'center' }}>
              <span style={{ color: threatColor(f.threat), fontSize: '14px' }}>{f.icon}</span>
              <span style={{ fontSize: '11px', color: C.textDim, letterSpacing: '1px' }}>{f.label}</span>
            </div>
            <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
              <span style={{ fontSize: '12px', color: C.white }}>{f.val}</span>
              <span style={{ fontSize: '10px', color: threatColor(f.threat), border: `1px solid ${threatColor(f.threat)}44`, padding: '1px 4px', letterSpacing: '1px' }}>{f.threat}</span>
            </div>
          </div>
          <div style={{ fontSize: '11px', color: C.textDim, marginTop: '2px', lineHeight: '1.5' }}>{f.note}</div>
        </div>
      ))}
    </div>
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      {/* Time / Weather bar */}
      <div className="panel" style={{ backgroundColor: C.panel, border: `1px solid ${C.border}`, padding: '9px 13px', position: 'relative', display: 'flex', justifyContent: 'space-between', alignItems: 'center', overflow: 'hidden' }}>
        <Bx c={C.violet} s={8} />
        <div style={{ overflow: 'hidden', height: '34px', flex: 1 }}>
          <div className="scroll-panel" style={{ animationDuration: '18s' }}>
            <div style={{ fontSize: '14px', color: C.textDim, letterSpacing: '2px' }}>{wx.location}</div>
            <div style={{ fontSize: '16px', color: C.text, marginTop: '2px', letterSpacing: '1px' }}>{wx.condition} // {wx.isDay ? 'DAYLIGHT' : 'NIGHT OPS'}</div>
            <div style={{ fontSize: '13px', color: C.textDim, marginTop: '10px' }}>TEMP {wx.temp}°F // WIND {wx.wind}KT // HUM {wx.humidity}%</div>
            <div style={{ fontSize: '13px', color: C.textDim, marginTop: '4px' }}>PRESSURE {wx.pressure}MB // CLOUD {wx.cloudCover}% // VIS {wx.visibility}KM</div>

            <div style={{ fontSize: '14px', color: C.textDim, letterSpacing: '2px', marginTop: '10px' }}>{wx.location}</div>
            <div style={{ fontSize: '16px', color: C.text, marginTop: '2px', letterSpacing: '1px' }}>{wx.condition} // {wx.isDay ? 'DAYLIGHT' : 'NIGHT OPS'}</div>
            <div style={{ fontSize: '13px', color: C.textDim, marginTop: '10px' }}>TEMP {wx.temp}°F // WIND {wx.wind}KT // HUM {wx.humidity}%</div>
            <div style={{ fontSize: '13px', color: C.textDim, marginTop: '4px' }}>PRESSURE {wx.pressure}MB // CLOUD {wx.cloudCover}% // VIS {wx.visibility}KM</div>
          </div>
        </div>
        <div style={{ textAlign: 'right', marginLeft: '12px', flexShrink: 0 }}>
          <div className="glow" style={{ fontSize: '30px', color: C.green, fontFamily: "'Oswald',sans-serif", letterSpacing: '2px' }}>{time}</div>
          <div style={{ fontSize: '12px', color: C.textDim }}>ZULU TIME</div>
        </div>
      </div>

      {/* Infiltration Risk */}
      <div className="panel" style={{ backgroundColor: C.panel, border: `1px solid ${rc}55`, padding: '12px 13px', position: 'relative', overflow: 'hidden' }}>
        <Bx c={rc} s={9} />
        <div style={{ fontSize: '13px', color: C.textDim, letterSpacing: '3px', marginBottom: '8px', fontFamily: "'Oswald',sans-serif" }}>▸ INFILTRATION RISK</div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <div>
            <div style={{ fontSize: '36px', fontFamily: "'Oswald',sans-serif", color: rc, lineHeight: 1, textShadow: `0 0 20px ${rc}66` }}>
              {risk}<span style={{ fontSize: '14px' }}>%</span>
            </div>
            <div style={{ fontSize: '13px', color: rc, letterSpacing: '3px', marginTop: '2px' }}>{rl} THREAT</div>
          </div>
          <div style={{ fontSize: '13px', color: C.textDim, textAlign: 'right', lineHeight: 2 }}>
            <div>NIGHT OPS <span style={{ color: !wx.isDay ? C.red : C.green }}>{!wx.isDay ? '+25' : '+0'}</span></div>
            <div>FOG STATUS <span style={{ color: wx.fog ? C.amber : C.green }}>{wx.fog ? '+20' : '+0'}</span></div>
            <div>VISIBILITY <span style={{ color: wx.visibility < 7 ? C.amber : C.green }}>{wx.visibility < 3 ? '+15' : wx.visibility < 7 ? '+7' : '+0'}</span></div>
            {intruderBoost > 0 && (
              <div className="blink">INTRUDER <span style={{ color: C.red }}>+{intruderBoost}</span></div>
            )}
          </div>
        </div>
        <div style={{ height: '4px', backgroundColor: C.borderLo, marginBottom: '6px' }}>
          <div style={{ height: '100%', width: `${risk}%`, background: `linear-gradient(90deg,${C.violet},${rc})`, boxShadow: `0 0 8px ${rc}88` }} />
        </div>
        <div style={{ fontSize: '11px', color: C.textDim, letterSpacing: '1px' }}>
          {risk >= 70 ? '⚠ HEIGHTEN PERIMETER — CONDITIONS FAVOUR INFILTRATOR'
            : risk >= 40 ? '△ ELEVATED CAUTION — MONITOR ALL SECTORS'
              : '✓ CONDITIONS UNFAVOURABLE FOR INFILTRATION'}
        </div>
      </div>

      {/* Environmental Factors */}
      <div className="panel" style={{ backgroundColor: C.panel, border: `1px solid ${C.border}`, padding: '12px 13px', position: 'relative', overflow: 'hidden' }}>
        <Bx c={C.blue} s={9} />
        <div style={{ fontSize: '12px', color: C.blue, letterSpacing: '3px', marginBottom: '10px', borderBottom: `1px solid ${C.borderLo}`, paddingBottom: '6px', fontFamily: "'Oswald',sans-serif" }}>
          ▸ ENVIRONMENTAL FACTORS
        </div>
        <div style={{ overflow: 'hidden', height: '220px' }}>
          <div className="scroll-panel" style={{ animationDuration: '35s' }}>
            {factorRows}
            <div style={{ marginTop: '16px' }}>{factorRows}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

const SurveillanceDashboard = () => {
  const [alerts, setAlerts] = useState([]);
  const [detections, setDetections] = useState([]);
  const [zoomedCam, setZoomedCam] = useState(null);
  const [intruderBoost, setIntruderBoost] = useState(0);

  useEffect(() => {
    const handleAlert = (a) => {
      setAlerts(prev => [a, ...prev].slice(0, 15));
    };

    const handleDetection = (d) => {
      const detection = {
        camId: d.camId,
        label: d.label || 'UNKNOWN OBJECT',
        type: d.type || 'object',
        suspicious: !!d.suspicious,
        confidence: d.confidence || 0,
        timestamp: d.timestamp || new Date().toISOString(),
      };

      setDetections(prev => [detection, ...prev].slice(0, 30));

      if (detection.suspicious) {
        // Intruder detected — boost risk only, NO zoom
        setIntruderBoost(30);
        setTimeout(() => setIntruderBoost(0), 30000);
      } else {
        // Non-intruder (authorized / YOLO person) — auto-zoom to that camera
        setZoomedCam(detection.camId);
        setTimeout(() => {
          setZoomedCam(current => (current === detection.camId ? null : current));
        }, 8000);
      }
    };

    socket.on('new_alert', handleAlert);
    socket.on('detection_event', handleDetection);

    return () => {
      socket.off('new_alert', handleAlert);
      socket.off('detection_event', handleDetection);
    };
  }, []);

  const cams = [
    { id: 1, feed: `${FLASK_IP}/video_feed_1`, label: 'MAIN GATE', sector: 'ALPHA', status: 'LIVE', color: C.green, thermal: false },
    { id: 2, feed: `${FLASK_IP}/video_feed_2`, label: 'PERIMETER N', sector: 'BRAVO', status: 'LIVE', color: C.cyan, thermal: false },
    { id: 3, feed: `${FLASK_IP}/video_feed_3`, label: 'SECTOR WEST', sector: 'CHARLIE', status: 'STANDBY', color: C.amber, thermal: false },
    { id: 4, feed: `${FLASK_IP}/video_feed_4`, label: 'AERIAL OPS', sector: 'DELTA', status: 'OFFLINE', color: C.red, thermal: false },
    { id: 5, feed: `${FLASK_IP}/video_feed_5`, label: 'THERMAL IR', sector: 'ECHO', status: 'LIVE', color: '#aaaaaa', thermal: true },
    { id: 6, feed: `${FLASK_IP}/video_feed_6`, label: 'EAST FLANK', sector: 'FOXTROT', status: 'LIVE', color: C.orange, thermal: false },
    { id: 7, feed: `${FLASK_IP}/video_feed_7`, label: 'ROOF OPS', sector: 'GOLF', status: 'LIVE', color: C.violet, thermal: false },
    { id: 8, feed: `${FLASK_IP}/video_feed_8`, label: 'SOUTH GATE', sector: 'HOTEL', status: 'STANDBY', color: C.blue, thermal: false },
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

  const getLatestDetectionForCam = (camId) => {
    return detections.find(d => d.camId === camId);
  };

  const combinedActivity = [
    ...alerts.map(a => ({
      entryType: 'alert',
      timestamp: a.timestamp,
      message: a.message,
    })),
    ...detections.map(d => ({
      entryType: 'detection',
      ...d,
    })),
  ]
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    .slice(0, 25);

  return (
    <div style={{
      backgroundColor: C.bg,
      color: C.text,
      minHeight: '100vh',
      padding: '14px',
      fontFamily: "'Share Tech Mono','Courier New',monospace",
      backgroundImage: `radial-gradient(ellipse at 15% 0%,${C.violetLo}99 0%,transparent 45%),radial-gradient(ellipse at 85% 100%,${C.blueDim}55 0%,transparent 45%),repeating-linear-gradient(0deg,transparent,transparent 39px,rgba(59,110,248,0.025) 40px),repeating-linear-gradient(90deg,transparent,transparent 39px,rgba(59,110,248,0.025) 40px)`,
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Oswald:wght@600;700&display=swap');
        @keyframes blink   {0%,100%{opacity:1}  50%{opacity:.1}}
        @keyframes flicker {0%,100%{opacity:1} 93%{opacity:.95} 95%{opacity:.8} 97%{opacity:.95}}
        @keyframes glow    {0%,100%{text-shadow:0 0 8px #00e87a} 50%{text-shadow:0 0 22px #00e87a,0 0 44px #00e87a33}}
        @keyframes scan    {0%{top:-4px} 100%{top:100%}}
        @keyframes scrollUp {0%{transform:translateY(0)} 100%{transform:translateY(-50%)}}
        @keyframes dangerPulse {0%,100%{box-shadow:0 0 10px rgba(239,68,68,0.2)} 50%{box-shadow:0 0 24px rgba(239,68,68,0.55)}}
        .blink   {animation:blink 1.4s step-end infinite}
        .flicker {animation:flicker 8s infinite}
        .glow    {animation:glow 3s ease-in-out infinite}
        .scroll-panel {animation:scrollUp linear infinite; will-change:transform;}
        .scan-overlay{position:absolute;inset:0;pointer-events:none;z-index:2;background:repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(0,0,0,.07) 4px)}
        .scan-line{position:absolute;left:0;right:0;height:4px;z-index:3;pointer-events:none;background:linear-gradient(transparent,rgba(0,232,122,.1),transparent);animation:scan 5s linear infinite}
        .panel{position:relative}
        .danger-pulse{animation:dangerPulse 1s infinite}
        ::-webkit-scrollbar{width:3px}
        ::-webkit-scrollbar-track{background:${C.bg}}
        ::-webkit-scrollbar-thumb{background:${C.blueDim}}
      `}</style>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 200px', gap: '12px', alignItems: 'start' }}>
        {/* Left Side */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {/* 4×2 camera grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
            {cams.map(cam => {
              const latestDetection = getLatestDetectionForCam(cam.id);
              const isZoomed = zoomedCam === cam.id;
              const isSuspicious = latestDetection?.suspicious;

              return (
                <div
                  key={cam.id}
                  className={`panel flicker`}
                  style={{
                    backgroundColor: C.panel,
                    border: `1px solid ${isSuspicious ? C.red : isZoomed ? C.green : cam.color}55`,
                    position: 'relative',
                    boxShadow: isZoomed
                      ? `0 0 30px ${C.green}55`
                      : `0 0 16px ${cam.color}12`,
                    transform: isZoomed ? 'scale(1.06)' : 'scale(1)',
                    transition: 'all 0.4s ease',
                    zIndex: isZoomed ? 20 : 1,
                  }}
                >
                  <Bx c={isSuspicious ? C.red : cam.color} s={8} />

                  {/* Header */}
                  <div style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    padding: '10px 14px',
                    backgroundColor: `${(isSuspicious ? C.red : cam.color)}08`,
                    borderBottom: `1px solid ${(isSuspicious ? C.red : cam.color)}2a`,
                  }}>
                    <span style={{ fontSize: '14px', color: isSuspicious ? C.red : cam.color, letterSpacing: '1px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '72%' }}>
                      {cam.thermal ? '⬜ THERMAL IR' : `CAM-0${cam.id} // ${cam.label}`}
                    </span>
                    <span className={cam.status === 'LIVE' ? 'blink' : ''} style={{ fontSize: '14px', color: isSuspicious ? C.red : cam.color }}>
                      {cam.status === 'LIVE' ? '●' : cam.status === 'STANDBY' ? '◐' : '○'}
                    </span>
                  </div>

                  {/* Feed */}
                  <div style={{ position: 'relative', backgroundColor: '#000', aspectRatio: '16/9', overflow: 'hidden' }}>
                    <div className="scan-overlay" />
                    <div className="scan-line" />

                    <img
                      src={cam.feed}
                      style={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover',
                        display: 'block',
                        filter: camFilter(cam),
                        transform: isZoomed ? 'scale(1.25)' : 'scale(1)',
                        transition: 'transform 0.5s ease',
                      }}
                      alt={`cam${cam.id}`}
                    />

                    {/* Detection badge */}
                    {latestDetection && (
                      <div
                        style={{
                          position: 'absolute',
                          top: 5,
                          left: 6,
                          fontSize: '9px',
                          color: latestDetection.suspicious ? C.red : C.green,
                          zIndex: 4,
                          border: `1px solid ${latestDetection.suspicious ? C.red : C.green}55`,
                          padding: '2px 6px',
                          backgroundColor: 'rgba(0,0,0,0.75)',
                          letterSpacing: '1px',
                          fontWeight: 'bold'
                        }}
                      >
                        {latestDetection.suspicious ? '⚠ SUSPICIOUS' : '✓ DETECTED'}
                      </div>
                    )}

                    {/* Auto tracking overlay — shown only on non-intruder zoom */}
                    {isZoomed && (
                      <div
                        style={{
                          position: 'absolute',
                          bottom: 28,
                          left: 6,
                          fontSize: '8px',
                          color: C.green,
                          zIndex: 4,
                          border: `1px solid ${C.green}55`,
                          padding: '2px 6px',
                          backgroundColor: 'rgba(0,0,0,0.7)',
                          letterSpacing: '2px'
                        }}
                      >
                        ✓ TRACKING SUBJECT...
                      </div>
                    )}

                    {/* Crosshair */}
                    <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', width: 20, height: 20, zIndex: 4, pointerEvents: 'none' }}>
                      <div style={{ position: 'absolute', top: '50%', left: 0, right: 0, height: '1px', backgroundColor: `${isSuspicious ? C.red : cam.color}44` }} />
                      <div style={{ position: 'absolute', left: '50%', top: 0, bottom: 0, width: '1px', backgroundColor: `${isSuspicious ? C.red : cam.color}44` }} />
                      <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', width: 5, height: 5, border: `1px solid ${isSuspicious ? C.red : cam.color}77`, borderRadius: '50%' }} />
                    </div>

                    {/* Badges */}
                    <div style={{ position: 'absolute', top: 5, right: 6, fontSize: '9px', color: `${isSuspicious ? C.red : cam.color}cc`, zIndex: 4, border: `1px solid ${isSuspicious ? C.red : cam.color}33`, padding: '1px 5px', backgroundColor: 'rgba(0,0,0,0.65)' }}>
                      0{cam.id}
                    </div>

                    {cam.thermal && (
                      <div style={{ position: 'absolute', bottom: 5, left: 6, fontSize: '9px', color: '#fff', zIndex: 4, border: '1px solid #fff3', padding: '1px 5px', backgroundColor: 'rgba(0,0,0,0.7)', letterSpacing: '1px' }}>
                        IR
                      </div>
                    )}

                    <div style={{ position: 'absolute', bottom: 5, right: 6, fontSize: '8px', color: `${isSuspicious ? C.red : cam.color}88`, zIndex: 4 }}>
                      {`${30 + cam.id * 7}N`}
                    </div>
                  </div>

                  {/* Footer */}
                  <div style={{ padding: '9px 14px', display: 'flex', justifyContent: 'space-between', fontSize: '13px', color: C.textDim, borderTop: `1px solid ${(isSuspicious ? C.red : cam.color)}1a` }}>
                    <span>{cam.sector}</span>
                    <span>30FPS</span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Unified Activity Feed */}
          <div
            className="panel"
            style={{
              backgroundColor: C.panel,
              border: `1px solid ${C.border}`,
              padding: '10px 14px',
              position: 'relative',
              maxHeight: '260px',
              overflow: 'hidden'
            }}
          >
            <Bx c={C.violet} s={8} />
            <div
              style={{
                fontSize: '9px',
                color: C.violet,
                letterSpacing: '3px',
                marginBottom: '8px',
                fontFamily: "'Oswald',sans-serif"
              }}
            >
              ▸ INCIDENTS & DETECTIONS
            </div>

            <div
              style={{
                overflowY: 'auto',
                maxHeight: '215px',
                display: 'flex',
                flexDirection: 'column',
                gap: '6px'
              }}
            >
              {combinedActivity.length === 0 ? (
                <span style={{ fontSize: '8px', color: C.textDim, letterSpacing: '2px' }}>
                  <span className="blink">_</span> MONITORING ALL SECTORS...
                </span>
              ) : (
                combinedActivity.map((item, i) => (
                  <div
                    key={i}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '3px',
                      borderLeft: `2px solid ${item.entryType === 'alert'
                        ? C.violet
                        : item.suspicious
                          ? C.red
                          : C.green
                        }`,
                      paddingLeft: '8px',
                      paddingBottom: '4px'
                    }}
                  >
                    {item.entryType === 'alert' ? (
                      <>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '8px', color: C.violet, letterSpacing: '1px' }}>
                            ALERT EVENT
                          </span>
                          <span style={{ fontSize: '7px', color: C.textDim }}>
                            {new Date(item.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <span style={{ fontSize: '8px', color: C.white }}>
                          {item.message}
                        </span>
                      </>
                    ) : (
                      <>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '8px', color: C.white, letterSpacing: '1px' }}>
                            CAM-0{item.camId} // {item.label.toUpperCase()}
                          </span>
                          <span style={{ fontSize: '7px', color: C.textDim }}>
                            {new Date(item.timestamp).toLocaleTimeString()}
                          </span>
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '7px', color: C.textDim }}>
                            TYPE: {item.type.toUpperCase()} // CONF: {(item.confidence * 100).toFixed(0)}%
                          </span>
                          <span
                            style={{
                              fontSize: '7px',
                              color: item.suspicious ? C.red : C.green,
                              border: `1px solid ${item.suspicious ? C.red : C.green}44`,
                              padding: '1px 4px',
                              letterSpacing: '1px'
                            }}
                          >
                            {item.suspicious ? 'SUSPICIOUS' : 'NORMAL'}
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Side */}
        <WeatherPanel intruderBoost={intruderBoost} />
      </div>
    </div>
  );
};

export default SurveillanceDashboard;