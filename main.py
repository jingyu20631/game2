import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="3D 마리오 카트 8 - 정밀 조작 & 스마트 AI",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100% !important;
    }
    .stApp {
        background-color: #0b0d12;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🏎️ 마리오 카트 3D 설정")
st.sidebar.markdown("---")

track_type = st.sidebar.selectbox(
    "🗺️ 트랙 코스 선택",
    ["마리오 서킷 (Mario Circuit)", "무지개 로드 (Rainbow Road)", "사막 힐스 (Desert Hills)"]
)

character = st.sidebar.selectbox(
    "👤 캐릭터 & 카트 컬러",
    ["마리오 (Red)", "루이지 (Green)", "피치 (Pink)", "쿠파 (Dark/Yellow)", "토드 (Blue)", "골드 마리오 (Gold)"]
)

speed_class = st.sidebar.select_slider(
    "⚡ 엔진 속도 클래스",
    options=["50cc (초보)", "100cc (중급)", "150cc (고수/프로)"],
    value="100cc (중급)"
)

ai_count = st.sidebar.slider("🤖 AI 라이벌 카트 수", min_value=3, max_value=7, value=5)
enable_sound = st.sidebar.checkbox("🔊 8Bit 효과음 & 엔진음 켜기", value=True)

st.sidebar.markdown("""
---
### 🎮 게임 조작법
* **[ W / ↑ ]** : 가속 | **[ S / ↓ ]** : 브레이크/후진
* **[ A, D / ←, → ]** : 조향 (핸들링 - 감도 개선됨)
* **[ Shift ]** : 드리프트 (코너링 부스터)
* **[ Space / E ]** : 아이템 사용 (🚀 미사일, 🍌 바나나 후방 설치, 🍄 부스터)
* **[ C ]** : 시점 변경 (3인칭 / 탑뷰 / 1인칭)
* **[ R ]** : 게임 재시작
""")

track_code = "circuit" if "서킷" in track_type else ("rainbow" if "무지개" in track_type else "desert")

color_map = {
    "마리오 (Red)": "#e52521",
    "루이지 (Green)": "#43b047",
    "피치 (Pink)": "#f582ae",
    "쿠파 (Dark/Yellow)": "#333333",
    "토드 (Blue)": "#0099ff",
    "골드 마리오 (Gold)": "#ffd700"
}
player_color = color_map.get(character, "#e52521")

# 조작 편의성을 위한 전체 속도 밸런스 조정
speed_map = {"50cc (초보)": 0.65, "100cc (중급)": 0.85, "150cc (고수/프로)": 1.05}
speed_multiplier = speed_map.get(speed_class, 0.85)

html_code = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>3D Mario Kart Balanced Edition</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; user-select: none; }}
        body {{ overflow: hidden; background: #000; width: 100vw; height: 100vh; }}
        #game-container {{ width: 100%; height: 100vh; position: relative; }}
        canvas {{ width: 100%; height: 100%; display: block; }}

        #hud {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            pointer-events: none; padding: 16px;
            display: flex; flex-direction: column; justify-content: space-between;
        }}
        .top-bar {{ display: flex; justify-content: space-between; align-items: flex-start; }}
        .glass-box {{
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(12px);
            border: 2px solid rgba(255, 255, 255, 0.25);
            border-radius: 14px;
            padding: 10px 18px;
            color: #fff;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
        }}
        .rank-display {{
            font-size: 38px; font-weight: 900; font-style: italic;
            background: linear-gradient(135deg, #ff0055 0%, #ffcc00 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }}
        .item-box {{
            width: 70px; height: 70px; border-radius: 16px;
            display: flex; align-items: center; justify-content: center;
            font-size: 36px; border: 3px solid #ffd700;
            background: rgba(0,0,0,0.75); box-shadow: 0 0 20px rgba(255, 215, 0, 0.6);
        }}
        
        .speedometer {{
            position: absolute; bottom: 16px; right: 16px;
            text-align: right; font-family: monospace;
        }}
        .speed-val {{ font-size: 42px; font-weight: bold; color: #00f2fe; text-shadow: 0 0 12px #00f2fe; }}
        .speed-unit {{ font-size: 14px; color: #aaa; }}

        #minimap-canvas {{
            position: absolute; bottom: 16px; left: 16px;
            width: 110px; height: 110px;
            border-radius: 50%; border: 2.5px solid rgba(255,255,255,0.7);
            background: rgba(0, 0, 0, 0.75); box-shadow: 0 4px 20px rgba(0,0,0,0.8);
            z-index: 10;
        }}

        #countdown {{
            position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%);
            font-size: 120px; font-weight: 900; color: #fff; text-shadow: 0 0 35px #ff0055;
            display: none; z-index: 100;
        }}

        #result-modal {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.88); display: none; flex-direction: column;
            align-items: center; justify-content: center; color: white; z-index: 200;
            pointer-events: auto;
        }}
        .btn-restart {{
            margin-top: 20px; padding: 14px 36px; font-size: 22px; font-weight: bold;
            background: linear-gradient(45deg, #ff0055, #ff5000); border: none;
            color: white; border-radius: 30px; cursor: pointer; transition: 0.2s;
            box-shadow: 0 0 20px rgba(255, 0, 85, 0.7);
        }}
        .btn-restart:hover {{ transform: scale(1.08); box-shadow: 0 0 30px rgba(255, 0, 85, 0.9); }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="game-container">
        <div id="countdown">3</div>
        <div id="hud">
            <div class="top-bar">
                <div class="glass-box">
                    <div style="font-size: 11px; color: #aaa;">RANK</div>
                    <div class="rank-display" id="rank-text">1st</div>
                </div>
                <div class="item-box" id="item-slot">❓</div>
                <div class="glass-box" style="text-align: right;">
                    <div style="font-size: 11px; color: #aaa;">LAP</div>
                    <div style="font-size: 26px; font-weight: bold;" id="lap-text">1 / 3</div>
                    <div style="font-size: 13px; color: #4facfe;" id="time-text">00:00.00</div>
                </div>
            </div>
            
            <canvas id="minimap-canvas" width="110" height="110"></canvas>

            <div class="speedometer glass-box">
                <span class="speed-val" id="speed-text">0</span> <span class="speed-unit">KM/H</span>
                <div id="drift-indicator" style="font-size: 11px; height: 14px; color: #ff0055; font-weight: bold;"></div>
            </div>
        </div>

        <div id="result-modal">
            <h1 id="result-title" style="font-size: 56px; font-weight: 900; margin-bottom: 8px;">🏆 VICTORY!</h1>
            <p id="result-subtitle" style="font-size: 22px; color: #ccc;">최종 순위: <span id="final-rank" style="color: #ffd700; font-weight: bold;">1st</span></p>
            <p id="result-time" style="font-size: 18px; color: #888; margin-top: 6px;">기록: 01:23.45</p>
            <button class="btn-restart" onclick="resetGame()">🔄 다시 레이스하기</button>
        </div>
    </div>

    <script>
        const TRACK_TYPE = "{track_code}";
        const PLAYER_COLOR = "{player_color}";
        const SPEED_MULT = {speed_multiplier};
        const AI_COUNT = {ai_count};
        const SOUND_ENABLED = {str(enable_sound).lower()};

        let scene, camera, renderer;
        let playerKart;
        let aiKarts = [];
        let trackCurve, trackMesh;
        const TRACK_WIDTH = 24;
        let itemBoxes = [], bananas = [], missiles = [], particleEffects = [];
        
        let keys = {{}};
        
        // 🛠️ 조작감 개선: 플레이어 속도 하향 및 핸들링 감도 상향
        let speed = 0;
        let maxSpeed = 0.95 * SPEED_MULT; // 기존 1.45에서 안정적인 0.95로 감소
        let accel = 0.018;                // 출발 시 급발진 방지
        let turnSpeed = 0.045;            // 안정적인 스티어링 제어
        let steeringAngle = 0, driftTime = 0, isDrifting = false;
        
        let currentLap = 1, totalLaps = 3, totalProgress = 0;
        let raceState = 'COUNTDOWN';
        let raceStartTime = 0, elapsedTime = 0;
        let currentItem = null;
        let cameraMode = 0;

        // 효과음
        let audioCtx = null;
        function initAudio() {{ if (!SOUND_ENABLED || audioCtx) return; audioCtx = new (window.AudioContext || window.webkitAudioContext)(); }}
        function playSound(type) {{
            if (!SOUND_ENABLED || !audioCtx) return;
            try {{
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.connect(gain); gain.connect(audioCtx.destination);
                const now = audioCtx.currentTime;

                if (type === 'boost') {{
                    osc.type = 'sawtooth'; osc.frequency.setValueAtTime(300, now);
                    osc.frequency.exponentialRampToValueAtTime(950, now + 0.35);
                    gain.gain.setValueAtTime(0.25, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
                    osc.start(now); osc.stop(now + 0.35);
                }} else if (type === 'missile') {{
                    osc.type = 'sawtooth'; osc.frequency.setValueAtTime(800, now);
                    osc.frequency.exponentialRampToValueAtTime(200, now + 0.3);
                    gain.gain.setValueAtTime(0.3, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
                    osc.start(now); osc.stop(now + 0.3);
                }} else if (type === 'item') {{
                    osc.type = 'sine'; osc.frequency.setValueAtTime(523, now);
                    osc.frequency.setValueAtTime(659, now + 0.08); osc.frequency.setValueAtTime(783, now + 0.16);
                    gain.gain.setValueAtTime(0.25, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
                    osc.start(now); osc.stop(now + 0.3);
                }} else if (type === 'hit') {{
                    osc.type = 'square'; osc.frequency.setValueAtTime(150, now);
                    osc.frequency.exponentialRampToValueAtTime(30, now + 0.4);
                    gain.gain.setValueAtTime(0.4, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
                    osc.start(now); osc.stop(now + 0.4);
                }} else if (type === 'beep') {{
                    osc.type = 'triangle'; osc.frequency.setValueAtTime(440, now);
                    gain.gain.setValueAtTime(0.15, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
                    osc.start(now); osc.stop(now + 0.2);
                }} else if (type === 'go') {{
                    osc.type = 'triangle'; osc.frequency.setValueAtTime(880, now);
                    gain.gain.setValueAtTime(0.3, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.5);
                    osc.start(now); osc.stop(now + 0.5);
                }}
            }} catch(e) {{}}
        }}

        // 메인 초기화
        function init() {{
            const container = document.getElementById('game-container');
            
            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);

            renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: false }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            container.appendChild(renderer.domElement);

            const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
            scene.add(ambientLight);

            const sunLight = new THREE.DirectionalLight(0xffffff, 1.3);
            sunLight.position.set(120, 200, 90);
            sunLight.castShadow = true;
            sunLight.shadow.mapSize.width = 2048; sunLight.shadow.mapSize.height = 2048;
            scene.add(sunLight);

            createEnvironment();
            createFlatTrackAndWalls();

            // 플레이어 카트 생성
            playerKart = createHighDetailKart(PLAYER_COLOR, "PLAYER");
            const startPt = trackCurve.getPointAt(0);
            const startTan = trackCurve.getTangentAt(0);
            playerKart.mesh.position.set(startPt.x, 0, startPt.z);
            playerKart.mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1), startTan);
            playerKart.posProgress = 0;
            scene.add(playerKart.mesh);

            // 🤖 AI 카트 생성: 플레이어와 동일한 속도 조건 + 능숙한 최적 레일 주행
            const aiColors = ['#00d2ff', '#ff0055', '#00ff88', '#ffcc00', '#aa00ff', '#ff8800', '#00ffcc'];
            for(let i=0; i<AI_COUNT; i++) {{
                const ai = createHighDetailKart(aiColors[i % aiColors.length], `AI_${{i+1}}`);
                ai.posProgress = 0.99 - (i * 0.015);
                const aiPt = trackCurve.getPointAt(ai.posProgress);
                const aiTan = trackCurve.getTangentAt(ai.posProgress);
                ai.mesh.position.set(aiPt.x, 0, aiPt.z);
                ai.mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1), aiTan);
                
                // 🔥 AI 속도를 플레이어 최고속도와 거의 비슷하게 조절 (비정상 과속 방지)
                ai.speed = maxSpeed * (0.96 + Math.random() * 0.03);
                aiKarts.push(ai);
                scene.add(ai.mesh);
            }}

            createItemBoxes();

            window.addEventListener('keydown', e => {{ initAudio(); keys[e.code] = true; handleKeyDown(e); }});
            window.addEventListener('keyup', e => keys[e.code] = false);
            window.addEventListener('resize', onWindowResize);

            startCountdown();
            animate();
        }}

        // 수평 트랙 & 경계 벽
        function createFlatTrackAndWalls() {{
            let points = [];
            if (TRACK_TYPE === 'circuit') {{
                points = [
                    new THREE.Vector3(-160, 0, -130), new THREE.Vector3(-180, 0, -20),
                    new THREE.Vector3(-120, 0, 90), new THREE.Vector3(-40, 0, 150),
                    new THREE.Vector3(60, 0, 160), new THREE.Vector3(130, 0, 100),
                    new THREE.Vector3(65, 0, 20), new THREE.Vector3(150, 0, -40),
                    new THREE.Vector3(170, 0, -120), new THREE.Vector3(60, 0, -170),
                    new THREE.Vector3(-40, 0, -140)
                ];
            }} else if (TRACK_TYPE === 'rainbow') {{
                points = [
                    new THREE.Vector3(-170, 0, -130), new THREE.Vector3(-190, 0, -20),
                    new THREE.Vector3(-130, 0, 100), new THREE.Vector3(-40, 0, 170),
                    new THREE.Vector3(60, 0, 150), new THREE.Vector3(140, 0, 70),
                    new THREE.Vector3(180, 0, -20), new THREE.Vector3(150, 0, -130),
                    new THREE.Vector3(20, 0, -180), new THREE.Vector3(-80, 0, -160)
                ];
            }} else {{ // desert
                points = [
                    new THREE.Vector3(-150, 0, -150), new THREE.Vector3(-190, 0, -20),
                    new THREE.Vector3(-120, 0, 80), new THREE.Vector3(-20, 0, 160),
                    new THREE.Vector3(90, 0, 170), new THREE.Vector3(170, 0, 90),
                    new THREE.Vector3(180, 0, -30), new THREE.Vector3(120, 0, -140),
                    new THREE.Vector3(0, 0, -190)
                ];
            }}

            trackCurve = new THREE.CatmullRomCurve3(points, true, 'centripetal', 0.5);
            
            const samples = 400;
            const geometry = new THREE.BufferGeometry();
            const positions = [], uvs = [], normals = [];
            const leftBorderPts = [], rightBorderPts = [];

            for (let i = 0; i <= samples; i++) {{
                const t = i / samples;
                const pt = trackCurve.getPointAt(t);
                const tangent = trackCurve.getTangentAt(t).normalize();
                const up = new THREE.Vector3(0, 1, 0);
                const side = new THREE.Vector3().crossVectors(tangent, up).normalize();

                const p1 = pt.clone().add(side.clone().multiplyScalar(TRACK_WIDTH / 2));
                const p2 = pt.clone().add(side.clone().multiplyScalar(-TRACK_WIDTH / 2));

                positions.push(p1.x, 0.05, p1.z, p2.x, 0.05, p2.z);
                uvs.push(0, t * 35, 1, t * 35);
                normals.push(0, 1, 0, 0, 1, 0);

                leftBorderPts.push(p1);
                rightBorderPts.push(p2);
            }}

            const indices = [];
            for (let i = 0; i < samples; i++) {{
                const row = i * 2;
                indices.push(row, row + 1, row + 2);
                indices.push(row + 1, row + 3, row + 2);
            }}

            geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
            geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
            geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
            geometry.setIndex(indices);

            let mat;
            if (TRACK_TYPE === 'rainbow') {{
                mat = new THREE.MeshStandardMaterial({{
                    color: 0xffffff, roughness: 0.1, metalness: 0.85,
                    transparent: true, opacity: 0.92, emissive: 0x441166
                }});
            }} else if (TRACK_TYPE === 'circuit') {{
                mat = new THREE.MeshStandardMaterial({{ color: 0x1e1e24, roughness: 0.75 }});
            }} else {{
                mat = new THREE.MeshStandardMaterial({{ color: 0x6e482b, roughness: 0.9 }});
            }}

            trackMesh = new THREE.Mesh(geometry, mat);
            trackMesh.receiveShadow = true;
            scene.add(trackMesh);

            buildGuardrailWalls(leftBorderPts, rightBorderPts);
            createStartArch();
            buildHighDetailStructures();
        }}

        function buildGuardrailWalls(leftPts, rightPts) {{
            const wallMat = (TRACK_TYPE === 'rainbow') 
                ? new THREE.MeshStandardMaterial({{ color: 0x00ffff, emissive: 0x00ffff, emissiveIntensity: 0.9 }})
                : new THREE.MeshStandardMaterial({{ color: (TRACK_TYPE === 'circuit') ? 0xff0055 : 0xffb300, roughness: 0.2, metalness: 0.5 }});

            [leftPts, rightPts].forEach(pts => {{
                const curve = new THREE.CatmullRomCurve3(pts, true);
                const tubeGeo = new THREE.TubeGeometry(curve, 350, 1.3, 12, true);
                const wallMesh = new THREE.Mesh(tubeGeo, wallMat);
                wallMesh.position.y = 1.1;
                wallMesh.castShadow = true;
                scene.add(wallMesh);
            }});
        }}

        function createStartArch() {{
            const startPt = trackCurve.getPointAt(0);
            const startTan = trackCurve.getTangentAt(0);
            const arch = new THREE.Group();
            const poleMat = new THREE.MeshStandardMaterial({{ color: 0xffffff, metalness: 0.9, roughness: 0.2 }});
            
            const p1 = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 0.8, 15), poleMat);
            const p2 = p1.clone();
            p1.position.set(-13, 7.5, 0); p2.position.set(13, 7.5, 0);
            
            const banner = new THREE.Mesh(new THREE.BoxGeometry(27, 4.5, 1.2), new THREE.MeshStandardMaterial({{ color: 0xff0055, emissive: 0x550011 }}));
            banner.position.set(0, 13, 0);
            
            arch.add(p1, p2, banner);
            arch.position.set(startPt.x, 0, startPt.z);
            arch.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1), startTan);
            scene.add(arch);
        }}

        function buildHighDetailStructures() {{
            if (TRACK_TYPE === 'circuit') {{
                const castleGroup = new THREE.Group();
                const wallMat = new THREE.MeshStandardMaterial({{ color: 0xf0f0f0, roughness: 0.5 }});
                const roofMat = new THREE.MeshStandardMaterial({{ color: 0xe52521, roughness: 0.3 }});

                const mainKeep = new THREE.Mesh(new THREE.BoxGeometry(26, 22, 26), wallMat);
                mainKeep.position.y = 11;
                const mainRoof = new THREE.Mesh(new THREE.ConeGeometry(20, 16, 4), roofMat);
                mainRoof.position.y = 30; mainRoof.rotation.y = Math.PI/4;

                const towerPos = [[-13, -13], [13, -13], [-13, 13], [13, 13]];
                towerPos.forEach(pos => {{
                    const tower = new THREE.Mesh(new THREE.CylinderGeometry(4, 4, 28, 16), wallMat);
                    tower.position.set(pos[0], 14, pos[1]);
                    const troof = new THREE.Mesh(new THREE.ConeGeometry(5.5, 10, 16), roofMat);
                    troof.position.set(pos[0], 33, pos[1]);
                    castleGroup.add(tower, troof);
                }});

                castleGroup.add(mainKeep, mainRoof);
                castleGroup.position.set(0, 0, 0);
                scene.add(castleGroup);

                const pipeColors = [0x43b047, 0x0099ff, 0xff0055, 0xffcc00];
                for(let t=0.04; t<0.96; t+=0.06) {{
                    const pt = trackCurve.getPointAt(t);
                    const tan = trackCurve.getTangentAt(t);
                    const side = new THREE.Vector3().crossVectors(tan, new THREE.Vector3(0,1,0)).normalize();

                    const pCol = pipeColors[Math.floor(Math.random() * pipeColors.length)];
                    const pMat = new THREE.MeshStandardMaterial({{ color: pCol, roughness: 0.3, metalness: 0.3 }});
                    const pipeGroup = new THREE.Group();
                    const pBody = new THREE.Mesh(new THREE.CylinderGeometry(3.2, 3.2, 9, 16), pMat);
                    pBody.position.y = 4.5;
                    const pRim = new THREE.Mesh(new THREE.CylinderGeometry(3.8, 3.8, 2, 16), pMat);
                    pRim.position.y = 8;
                    pipeGroup.add(pBody, pRim);
                    pipeGroup.position.copy(pt).add(side.clone().multiplyScalar(26));
                    scene.add(pipeGroup);

                    const mColor = pipeColors[(Math.floor(t*100)) % pipeColors.length];
                    const mCapMat = new THREE.MeshStandardMaterial({{ color: mColor, roughness: 0.4 }});
                    const mStemMat = new THREE.MeshStandardMaterial({{ color: 0xfffdd0, roughness: 0.6 }});
                    const mushroom = new THREE.Group();
                    const stem = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.8, 7), mStemMat);
                    stem.position.y = 3.5;
                    const cap = new THREE.Mesh(new THREE.SphereGeometry(5, 16, 12), mCapMat);
                    cap.scale.set(1, 0.6, 1); cap.position.y = 7;
                    mushroom.add(stem, cap);
                    mushroom.position.copy(pt).add(side.clone().multiplyScalar(-28));
                    scene.add(mushroom);
                }}
            }} else if (TRACK_TYPE === 'desert') {{
                const pyrMat = new THREE.MeshStandardMaterial({{ color: 0xd7ccc8, roughness: 0.85 }});
                const pyr = new THREE.Mesh(new THREE.ConeGeometry(60, 45, 4), pyrMat);
                pyr.position.set(0, 22.5, 0); pyr.rotation.y = Math.PI / 4;
                scene.add(pyr);

                for(let t=0.05; t<0.95; t+=0.07) {{
                    const pt = trackCurve.getPointAt(t);
                    const tan = trackCurve.getTangentAt(t);
                    const side = new THREE.Vector3().crossVectors(tan, new THREE.Vector3(0,1,0)).normalize();

                    const pillar = new THREE.Mesh(new THREE.BoxGeometry(4, 20, 4), pyrMat);
                    pillar.position.copy(pt).add(side.clone().multiplyScalar((t % 0.1 > 0.05 ? 1 : -1) * 26));
                    pillar.position.y = 10;
                    scene.add(pillar);
                }}
            }} else {{
                for(let t=0.04; t<0.96; t+=0.08) {{
                    const pt = trackCurve.getPointAt(t);
                    const tan = trackCurve.getTangentAt(t);
                    
                    const ringGeo = new THREE.TorusGeometry(16, 1.2, 16, 32);
                    const ringMat = new THREE.MeshStandardMaterial({{ color: 0x00f2fe, emissive: 0x00f2fe, emissiveIntensity: 0.9 }});
                    const ring = new THREE.Mesh(ringGeo, ringMat);
                    ring.position.copy(pt).add(new THREE.Vector3(0, 9, 0));
                    ring.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1), tan);
                    scene.add(ring);
                }}
            }}
        }}

        function createEnvironment() {{
            if (TRACK_TYPE === 'rainbow') {{
                scene.background = new THREE.Color(0x02020a);
                scene.fog = new THREE.FogExp2(0x02020a, 0.0012);
                const starGeo = new THREE.BufferGeometry();
                const starCoords = [];
                for(let i=0; i<3000; i++) starCoords.push((Math.random()-0.5)*1000, (Math.random()-0.5)*1000, (Math.random()-0.5)*1000);
                starGeo.setAttribute('position', new THREE.Float32BufferAttribute(starCoords, 3));
                scene.add(new THREE.Points(starGeo, new THREE.PointsMaterial({{ color: 0xffffff, size: 1.8 }})));
            }} else if (TRACK_TYPE === 'circuit') {{
                scene.background = new THREE.Color(0x4fc3f7);
                scene.fog = new THREE.FogExp2(0x4fc3f7, 0.0018);
                const plane = new THREE.Mesh(new THREE.PlaneGeometry(1200, 1200), new THREE.MeshStandardMaterial({{ color: 0x2e7d32, roughness: 0.9 }}));
                plane.rotation.x = -Math.PI/2; plane.position.y = 0; plane.receiveShadow = true;
                scene.add(plane);
            }} else {{
                scene.background = new THREE.Color(0xffb74d);
                scene.fog = new THREE.FogExp2(0xffb74d, 0.0028);
                const plane = new THREE.Mesh(new THREE.PlaneGeometry(1200, 1200), new THREE.MeshStandardMaterial({{ color: 0xedc9af, roughness: 1.0 }}));
                plane.rotation.x = -Math.PI/2; plane.position.y = 0; plane.receiveShadow = true;
                scene.add(plane);
            }}
        }}

        function createHighDetailKart(colorHex, name) {{
            const group = new THREE.Group();
            const bodyMat = new THREE.MeshStandardMaterial({{ color: colorHex, roughness: 0.2, metalness: 0.6 }});
            const metalMat = new THREE.MeshStandardMaterial({{ color: 0xdddddd, metalness: 0.9, roughness: 0.1 }});
            const wheelMat = new THREE.MeshStandardMaterial({{ color: 0x151515, roughness: 0.7 }});
            const rimMat = new THREE.MeshStandardMaterial({{ color: 0xffd700, metalness: 0.9 }});

            const chassis = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.7, 4.0), bodyMat);
            chassis.position.y = 0.6; chassis.castShadow = true;
            group.add(chassis);

            const nose = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.3, 1.2), bodyMat);
            nose.position.set(0, 0.3, 2.3);
            group.add(nose);

            const wingPole1 = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 1.2), metalMat);
            wingPole1.position.set(-0.8, 1.4, -1.8);
            const wingPole2 = wingPole1.clone();
            wingPole2.position.set(0.8, 1.4, -1.8);
            const wingBlade = new THREE.Mesh(new THREE.BoxGeometry(3.0, 0.15, 0.8), bodyMat);
            wingBlade.position.set(0, 2.0, -1.8);
            group.add(wingPole1, wingPole2, wingBlade);

            const exhaust = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.25, 0.8), metalMat);
            exhaust.rotation.x = Math.PI / 2;
            exhaust.position.set(0, 0.6, -2.1);
            group.add(exhaust);

            const wheelRim = new THREE.Mesh(new THREE.TorusGeometry(0.3, 0.06, 8, 16), metalMat);
            wheelRim.position.set(0, 1.1, 0.6); wheelRim.rotation.x = Math.PI / 3;
            group.add(wheelRim);

            const wheels = [];
            const offsets = [[-1.35, 0.55, 1.4], [1.35, 0.55, 1.4], [-1.35, 0.55, -1.3], [1.35, 0.55, -1.3]];
            offsets.forEach(pos => {{
                const wGroup = new THREE.Group();
                const wTire = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.55, 0.45, 20), wheelMat);
                wTire.rotateZ(Math.PI / 2);
                const wCap = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 0.47, 12), rimMat);
                wCap.rotateZ(Math.PI / 2);
                wGroup.add(wTire, wCap);
                wGroup.position.set(...pos); wGroup.castShadow = true;
                group.add(wGroup);
                wheels.push(wGroup);
            }});

            const driverGroup = new THREE.Group();
            const helmet = new THREE.Mesh(new THREE.SphereGeometry(0.65, 20, 20), bodyMat);
            helmet.position.set(0, 1.5, -0.1);
            const visor = new THREE.Mesh(new THREE.SphereGeometry(0.66, 16, 16, 0, Math.PI * 2, 0, Math.PI / 2), new THREE.MeshStandardMaterial({{ color: 0x111111, roughness: 0.1, metalness: 0.9 }}));
            visor.rotation.x = Math.PI / 2; visor.position.set(0, 1.55, 0.05); visor.scale.set(0.85, 0.85, 0.85);
            driverGroup.add(helmet, visor);
            group.add(driverGroup);

            return {{ mesh: group, wheels: wheels, name: name, posProgress: 0, speed: 0, spinOut: 0, boostTimer: 0 }};
        }}

        function createItemBoxes() {{
            const boxGeo = new THREE.BoxGeometry(2.2, 2.2, 2.2);
            const boxMat = new THREE.MeshStandardMaterial({{ color: 0xffd700, transparent: true, opacity: 0.88, emissive: 0xbb9900 }});

            for(let t=0.10; t<0.95; t+=0.16) {{
                const pt = trackCurve.getPointAt(t);
                const tan = trackCurve.getTangentAt(t);
                const side = new THREE.Vector3().crossVectors(tan, new THREE.Vector3(0,1,0)).normalize();

                [-5.5, 0, 5.5].forEach(off => {{
                    const box = new THREE.Mesh(boxGeo, boxMat);
                    box.position.copy(pt).add(side.clone().multiplyScalar(off)).add(new THREE.Vector3(0, 1.6, 0));
                    box.castShadow = true;
                    box.userData = {{ active: true, respawnTimer: 0 }};
                    scene.add(box); itemBoxes.push(box);
                }});
            }}
        }}

        function startCountdown() {{
            const cd = document.getElementById('countdown');
            cd.style.display = 'block';
            let count = 3; cd.innerText = count; playSound('beep');

            const timer = setInterval(() => {{
                count--;
                if (count > 0) {{
                    cd.innerText = count; playSound('beep');
                }} else if (count === 0) {{
                    cd.innerText = "GO!"; cd.style.color = "#00ff88"; playSound('go');
                    raceState = 'RACING'; raceStartTime = performance.now();
                }} else {{
                    cd.style.display = 'none'; clearInterval(timer);
                }}
            }}, 1000);
        }}

        function handleKeyDown(e) {{
            if (e.code === 'KeyC') cameraMode = (cameraMode + 1) % 3;
            if (e.code === 'Space' || e.code === 'KeyE') useItem();
            if (e.code === 'KeyR') resetGame();
        }}

        function useItem() {{
            if (!currentItem || raceState !== 'RACING') return;

            if (currentItem === 'MISSILE') {{
                fireMissile();
                playSound('missile');
            }} else if (currentItem === 'BANANA') {{
                dropBananaSafe();
                playSound('item');
            }} else if (currentItem === 'MUSHROOM') {{
                playerKart.boostTimer = 90;
                playSound('boost');
            }}

            currentItem = null;
            document.getElementById('item-slot').innerText = '❓';
        }}

        function fireMissile() {{
            const pPos = playerKart.mesh.position.clone();
            const pQuat = playerKart.mesh.quaternion.clone();
            const forwardDir = new THREE.Vector3(0, 0, 1).applyQuaternion(pQuat);

            const mGroup = new THREE.Group();
            const body = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 1.6, 12), new THREE.MeshStandardMaterial({{ color: 0xff0022, metalness: 0.8 }}));
            body.rotation.x = Math.PI / 2;
            const tip = new THREE.Mesh(new THREE.ConeGeometry(0.35, 0.6, 12), new THREE.MeshStandardMaterial({{ color: 0xffff00 }}));
            tip.rotation.x = Math.PI / 2; tip.position.z = 1.0;
            mGroup.add(body, tip);

            mGroup.position.copy(pPos).add(forwardDir.clone().multiplyScalar(2.5)).add(new THREE.Vector3(0, 1.0, 0));
            mGroup.quaternion.copy(pQuat);
            scene.add(mGroup);

            missiles.push({{ mesh: mGroup, dir: forwardDir, life: 120 }});
            createMuzzleFlash(mGroup.position);
        }}

        function createMuzzleFlash(pos) {{
            const flash = new THREE.Mesh(
                new THREE.SphereGeometry(1.2, 12, 12),
                new THREE.MeshStandardMaterial({{ color: 0xffaa00, emissive: 0xffaa00, transparent: true, opacity: 0.9 }})
            );
            flash.position.copy(pos);
            scene.add(flash);
            particleEffects.push({{ mesh: flash, life: 10, fade: 0.1 }});
        }}

        function dropBananaSafe() {{
            const pPos = playerKart.mesh.position.clone();
            const pQuat = playerKart.mesh.quaternion.clone();
            const backDir = new THREE.Vector3(0, 0, -1).applyQuaternion(pQuat);

            const bananaPos = pPos.add(backDir.multiplyScalar(4.0));
            bananaPos.y = 0.5;

            const geo = new THREE.CylinderGeometry(0.1, 0.8, 1.2, 8);
            const banana = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({{ color: 0xffeb3b, roughness: 0.3 }}));
            banana.position.copy(bananaPos);
            scene.add(banana);
            
            bananas.push({{ mesh: banana, immuneTimer: 40 }});
        }}

        function animate() {{
            requestAnimationFrame(animate);

            if (raceState === 'RACING') {{
                elapsedTime = (performance.now() - raceStartTime) / 1000;
                updateTimeDisplay();
                updatePlayer();
                updateSmartAI();
                updateMissilesAndEffects();
                updateItemBoxesAndBananas();
                updatePositions();
            }}

            updateCamera();
            drawMinimap();
            renderer.render(scene, camera);
        }}

        // 🛠️ 조작 편의성이 대폭 향상된 플레이어 물리
        function updatePlayer() {{
            playerKart.mesh.position.y = 0;

            if (playerKart.spinOut > 0) {{
                playerKart.spinOut--; playerKart.mesh.rotation.y += 0.3; speed *= 0.9; return;
            }}

            // 드리프트
            if (keys['ShiftLeft'] || keys['ShiftRight']) {{
                if ((keys['KeyA'] || keys['ArrowLeft']) || (keys['KeyD'] || keys['ArrowRight'])) {{
                    isDrifting = true; driftTime++;
                    if (driftTime > 35) document.getElementById('drift-indicator').innerText = '⚡ SUPER MINI-TURBO!';
                    else if (driftTime > 18) document.getElementById('drift-indicator').innerText = '🔥 MINI-TURBO!';
                }}
            }} else {{
                if (isDrifting) {{
                    if (driftTime > 35) {{ playerKart.boostTimer = 50; playSound('boost'); }}
                    else if (driftTime > 18) {{ playerKart.boostTimer = 25; playSound('boost'); }}
                    isDrifting = false; driftTime = 0;
                    document.getElementById('drift-indicator').innerText = '';
                }}
            }}

            let targetMaxSpeed = maxSpeed;
            if (playerKart.boostTimer > 0) {{ playerKart.boostTimer--; targetMaxSpeed *= 1.4; }}

            // 가속 / 감속 / 마찰력
            if (keys['KeyW'] || keys['ArrowUp']) speed = Math.min(speed + accel, targetMaxSpeed);
            else if (keys['KeyS'] || keys['ArrowDown']) speed = Math.max(speed - accel * 1.5, -maxSpeed * 0.4);
            else speed *= 0.95; // 자연스러운 자연 감속

            // 스티어링 (속도에 비례한 부드러운 선회)
            if (keys['KeyA'] || keys['ArrowLeft']) steeringAngle = turnSpeed * (isDrifting ? 1.25 : 1.0);
            else if (keys['KeyD'] || keys['ArrowRight']) steeringAngle = -turnSpeed * (isDrifting ? 1.25 : 1.0);
            else steeringAngle = 0;

            playerKart.mesh.rotation.y += steeringAngle * Math.min(1.0, (speed / (maxSpeed * 0.5)));

            const dir = new THREE.Vector3(0, 0, 1).applyQuaternion(playerKart.mesh.quaternion);
            playerKart.mesh.position.add(dir.multiplyScalar(speed));
            playerKart.wheels.forEach(w => w.rotation.x += speed * 0.4);

            // 트랙 이탈 방지
            const pPos = playerKart.mesh.position;
            let closestT = playerKart.posProgress;
            let minDist = Infinity;
            let closestCenterPt = null;

            for(let dt = -0.04; dt <= 0.04; dt += 0.004) {{
                const t = (playerKart.posProgress + dt + 1.0) % 1.0;
                const pt = trackCurve.getPointAt(t);
                const d = Math.hypot(pPos.x - pt.x, pPos.z - pt.z);
                if (d < minDist) {{ minDist = d; closestT = t; closestCenterPt = pt; }}
            }}

            const maxAllowedDist = (TRACK_WIDTH / 2) - 1.2;
            if (minDist > maxAllowedDist && closestCenterPt) {{
                const pushDir = new THREE.Vector3(pPos.x - closestCenterPt.x, 0, pPos.z - closestCenterPt.z).normalize();
                pPos.x = closestCenterPt.x + pushDir.x * maxAllowedDist;
                pPos.z = closestCenterPt.z + pushDir.z * maxAllowedDist;
                if (Math.abs(speed) > 0.15) {{ playSound('hit'); speed *= 0.75; }}
            }}

            if (playerKart.posProgress > 0.85 && closestT < 0.15) {{
                currentLap++;
                if (currentLap > totalLaps) finishRace();
                else {{ document.getElementById('lap-text').innerText = `${{currentLap}} / ${{totalLaps}}`; playSound('boost'); }}
            }}
            playerKart.posProgress = closestT;
            totalProgress = (currentLap - 1) + closestT;

            document.getElementById('speed-text').innerText = Math.round(Math.abs(speed) * 120);
        }}

        // 🤖 스마트 AI: 플레이어와 동일한 최고 속도이나, 트랙 중심 레일을 완벽히 조종하여 코너링 미스가 전혀 없음
        function updateSmartAI() {{
            aiKarts.forEach(ai => {{
                ai.mesh.position.y = 0;
                if (ai.spinOut > 0) {{ ai.spinOut--; ai.mesh.rotation.y += 0.3; return; }}

                // 최적 레일 경로를 따라 손실 없이 주행 (따라잡기 까다로운 실력파 AI)
                ai.posProgress += (ai.speed / 3200);
                if (ai.posProgress >= 1.0) ai.posProgress -= 1.0;

                const targetPt = trackCurve.getPointAt((ai.posProgress + 0.02) % 1.0);
                const currentPt = trackCurve.getPointAt(ai.posProgress % 1.0);
                
                ai.mesh.position.set(currentPt.x, 0, currentPt.z);
                ai.mesh.lookAt(new THREE.Vector3(targetPt.x, 0, targetPt.z));
                ai.wheels.forEach(w => w.rotation.x += 0.25);
            }});
        }}

        function updateMissilesAndEffects() {{
            for(let i = missiles.length - 1; i >= 0; i--) {{
                const m = missiles[i];
                m.life--;
                m.mesh.position.add(m.dir.clone().multiplyScalar(2.0));

                let hit = false;
                aiKarts.forEach(ai => {{
                    if (!hit && m.mesh.position.distanceTo(ai.mesh.position) < 3.2) {{
                        hit = true;
                        ai.spinOut = 60;
                        playSound('hit');
                        createMuzzleFlash(ai.mesh.position);
                    }}
                }});

                if (hit || m.life <= 0) {{
                    scene.remove(m.mesh);
                    missiles.splice(i, 1);
                }}
            }}

            for(let i = particleEffects.length - 1; i >= 0; i--) {{
                const p = particleEffects[i];
                p.life--;
                p.mesh.material.opacity -= p.fade;
                if (p.life <= 0) {{
                    scene.remove(p.mesh);
                    particleEffects.splice(i, 1);
                }}
            }}
        }}

        function updateItemBoxesAndBananas() {{
            itemBoxes.forEach(box => {{
                if (box.userData.active) {{
                    box.rotation.y += 0.03;
                    if (playerKart.mesh.position.distanceTo(box.position) < 2.5) {{
                        box.userData.active = false; box.visible = false; box.userData.respawnTimer = 260;
                        getRandomItem(); playSound('item');
                    }}
                }} else {{
                    box.userData.respawnTimer--;
                    if (box.userData.respawnTimer <= 0) {{ box.userData.active = true; box.visible = true; }}
                }}
            }});

            bananas.forEach((bObj, idx) => {{
                if (bObj.immuneTimer > 0) bObj.immuneTimer--;

                if (bObj.immuneTimer === 0 && playerKart.mesh.position.distanceTo(bObj.mesh.position) < 1.8) {{
                    playerKart.spinOut = 45; playSound('hit');
                    scene.remove(bObj.mesh); bananas.splice(idx, 1);
                    return;
                }}

                aiKarts.forEach(ai => {{
                    if (ai.mesh.position.distanceTo(bObj.mesh.position) < 2.0) {{
                        ai.spinOut = 50; playSound('hit');
                        scene.remove(bObj.mesh); bananas.splice(idx, 1);
                    }}
                }});
            }});
        }}

        function getRandomItem() {{
            const items = ['MISSILE', 'BANANA', 'MUSHROOM'];
            const icons = {{ 'MISSILE': '🚀', 'BANANA': '🍌', 'MUSHROOM': '🍄' }};
            const pick = items[Math.floor(Math.random() * items.length)];
            currentItem = pick;
            document.getElementById('item-slot').innerText = icons[pick];
        }}

        function updatePositions() {{
            let racers = [
                {{ name: 'PLAYER', progress: totalProgress }},
                ...aiKarts.map(ai => ({{ name: ai.name, progress: ai.posProgress }}))
            ];
            racers.sort((a, b) => b.progress - a.progress);
            const rank = racers.findIndex(r => r.name === 'PLAYER') + 1;

            const suffixes = ["st", "nd", "rd", "th"];
            document.getElementById('rank-text').innerText = `${{rank}}${{(rank <= 3) ? suffixes[rank - 1] : "th"}}`;
        }}

        function updateCamera() {{
            const pPos = playerKart.mesh.position;
            const pQuat = playerKart.mesh.quaternion;

            if (cameraMode === 0) {{
                const offset = new THREE.Vector3(0, 5.5, -13.0).applyQuaternion(pQuat);
                camera.position.lerp(pPos.clone().add(offset), 0.1);
                camera.lookAt(pPos.clone().add(new THREE.Vector3(0, 1.8, 0)));
            }} else if (cameraMode === 1) {{
                camera.position.set(pPos.x, pPos.y + 75, pPos.z);
                camera.lookAt(pPos);
            }} else {{
                const offset = new THREE.Vector3(0, 1.5, 0.5).applyQuaternion(pQuat);
                camera.position.copy(pPos.clone().add(offset));
                camera.lookAt(pPos.clone().add(new THREE.Vector3(0, 1.5, 10).applyQuaternion(pQuat)));
            }}
        }}

        function drawMinimap() {{
            const canvas = document.getElementById('minimap-canvas');
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, 110, 110);

            const scale = 0.24;
            const centerX = 55, centerY = 55;

            ctx.strokeStyle = 'rgba(255, 255, 255, 0.65)';
            ctx.lineWidth = 4;
            ctx.beginPath();
            for(let t=0; t<=1; t+=0.01) {{
                const pt = trackCurve.getPointAt(t);
                const x = centerX + pt.x * scale;
                const y = centerY + pt.z * scale;
                if (t === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }}
            ctx.closePath();
            ctx.stroke();

            aiKarts.forEach(ai => {{
                const x = centerX + ai.mesh.position.x * scale;
                const y = centerY + ai.mesh.position.z * scale;
                ctx.fillStyle = '#ff0055';
                ctx.beginPath(); ctx.arc(x, y, 3, 0, Math.PI*2); ctx.fill();
            }});

            const px = centerX + playerKart.mesh.position.x * scale;
            const py = centerY + playerKart.mesh.position.z * scale;
            ctx.fillStyle = '#00f2fe';
            ctx.shadowColor = '#00f2fe'; ctx.shadowBlur = 6;
            ctx.beginPath(); ctx.arc(px, py, 4.5, 0, Math.PI*2); ctx.fill();
            ctx.shadowBlur = 0;
        }}

        function updateTimeDisplay() {{
            const mins = Math.floor(elapsedTime / 60).toString().padStart(2, '0');
            const secs = Math.floor(elapsedTime % 60).toString().padStart(2, '0');
            const ms = Math.floor((elapsedTime % 1) * 100).toString().padStart(2, '0');
            document.getElementById('time-text').innerText = `${{mins}}:${{secs}}.${{ms}}`;
        }}

        function finishRace() {{
            raceState = 'FINISHED'; playSound('boost');
            const modal = document.getElementById('result-modal');
            modal.style.display = 'flex';
            document.getElementById('final-rank').innerText = document.getElementById('rank-text').innerText;
            document.getElementById('result-time').innerText = `기록: ${{document.getElementById('time-text').innerText}}`;
        }}

        function resetGame() {{ location.reload(); }}

        function onWindowResize() {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }}

        window.onload = init;
    </script>
</body>
</html>
"""

components.html(html_code, height=820, scrolling=False)
