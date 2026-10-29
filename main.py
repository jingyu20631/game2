import streamlit as st
import streamlit.components.v1 as components

# 페이지 기본 설정
st.set_page_config(
    page_title="3D 마리오 카트 8 레이싱 - Streamlit Edition",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 스타일링
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
        max-width: 100% !important;
    }
    .stApp {
        background-color: #0e1117;
    }
</style>
""", unsafe_allow_html=True)

# 사이드바 설정 메뉴
st.sidebar.title("🏎️ 마리오 카트 3D 설정")
st.sidebar.markdown("---")

# 트랙 선택
track_type = st.sidebar.selectbox(
    "🗺️ 트랙 코스 선택",
    ["무지개 로드 (Rainbow Road)", "마리오 서킷 (Mario Circuit)", "사막 힐스 (Desert Hills)"]
)

# 카트 & 캐릭터 선택
character = st.sidebar.selectbox(
    "👤 캐릭터 & 카트 컬러",
    ["마리오 (Red)", "루이지 (Green)", "피치 (Pink)", "쿠파 (Dark/Yellow)", "토드 (Blue)", "골드 마리오 (Gold)"]
)

# 엔진 클래스 (난이도)
speed_class = st.sidebar.select_slider(
    "⚡ 엔진 속도 클래스",
    options=["50cc (초보)", "100cc (중급)", "150cc (고수/프로)"],
    value="100cc (중급)"
)

# AI 라이벌 수
ai_count = st.sidebar.slider("🤖 AI 라이벌 카트 수", min_value=3, max_value=7, value=5)

# 음향 설정
enable_sound = st.sidebar.checkbox("🔊 8Bit 효과음 & 엔진음 켜기", value=True)

st.sidebar.markdown("""
---
### 🎮 게임 조작법
* **[ W ] / [ ↑ ]** : 가속 (Accelerate)
* **[ S ] / [ ↓ ]** : 브레이크 / 후진
* **[ A / D ] or [ ← / → ]** : 조향 (Left/Right)
* **[ Shift ]** : 드리프트 (코너링 중 홀드 ➔ 부스터 스파크!)
* **[ Space ] / [ E ]** : 아이템 사용
* **[ C ]** : 시점 변경 (3인칭 / 탑뷰 / 1인칭)
* **[ R ]** : 리셋 / 재시작
""")

# 파라미터 매핑
track_code = "rainbow" if "무지개" in track_type else ("circuit" if "서킷" in track_type else "desert")

color_map = {
    "마리오 (Red)": "#e52521",
    "루이지 (Green)": "#43b047",
    "피치 (Pink)": "#f582ae",
    "쿠파 (Dark/Yellow)": "#2b2b2b",
    "토드 (Blue)": "#0099ff",
    "골드 마리오 (Gold)": "#ffd700"
}
player_color = color_map.get(character, "#e52521")

speed_map = {"50cc (초보)": 0.85, "100cc (중급)": 1.1, "150cc (고수/프로)": 1.4}
speed_multiplier = speed_map.get(speed_class, 1.1)

# HTML/JS 게임 임베딩
html_code = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>3D Mario Kart Streamlit</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; user-select: none; }}
        body {{ overflow: hidden; background: #000; width: 100vw; height: 100vh; }}
        #game-container {{ width: 100%; height: 100vh; position: relative; }}
        canvas {{ width: 100%; height: 100%; display: block; }}

        /* HUD 오버레이 */
        #hud {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            pointer-events: none; padding: 20px;
            display: flex; flex-direction: column; justify-content: space-between;
        }}
        .top-bar {{ display: flex; justify-content: space-between; align-items: flex-start; }}
        .glass-box {{
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(12px);
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 16px;
            padding: 12px 20px;
            color: #fff;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        }}
        .rank-display {{
            font-size: 42px; font-weight: 900; font-style: italic;
            background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            text-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }}
        .item-box {{
            width: 80px; height: 80px; border-radius: 16px;
            display: flex; align-items: center; justify-content: center;
            font-size: 40px; border: 3px solid #ffd700;
            background: rgba(0,0,0,0.6); box-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
            animation: pulse 2s infinite alternate;
        }}
        @keyframes pulse {{ 0% {{ transform: scale(1); }} 100% {{ transform: scale(1.05); }} }}
        
        .speedometer {{
            position: absolute; bottom: 20px; right: 20px;
            text-align: right; font-family: monospace;
        }}
        .speed-val {{ font-size: 48px; font-weight: bold; color: #00f2fe; text-shadow: 0 0 12px #00f2fe; }}
        .speed-unit {{ font-size: 16px; color: #aaa; }}

        #minimap-canvas {{
            border-radius: 50%; border: 3px solid rgba(255,255,255,0.4);
            background: rgba(0,0,0,0.6); box-shadow: 0 4px 20px rgba(0,0,0,0.6);
        }}

        #countdown {{
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            font-size: 120px; font-weight: 900; color: #fff; text-shadow: 0 0 30px #ff0055;
            display: none; z-index: 100;
        }}

        #result-modal {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.85); display: none; flex-direction: column;
            align-items: center; justify-content: center; color: white; z-index: 200;
            pointer-events: auto;
        }}
        .btn-restart {{
            margin-top: 20px; padding: 14px 36px; font-size: 22px; font-weight: bold;
            background: linear-gradient(45deg, #ff0055, #ff5000); border: none;
            color: white; border-radius: 30px; cursor: pointer; transition: 0.2s;
            box-shadow: 0 0 20px rgba(255, 0, 85, 0.6);
        }}
        .btn-restart:hover {{ transform: scale(1.1); box-shadow: 0 0 30px rgba(255, 0, 85, 0.9); }}
    </style>
    <!-- Three.js CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="game-container">
        <div id="countdown">3</div>
        <div id="hud">
            <div class="top-bar">
                <div class="glass-box">
                    <div style="font-size: 14px; color: #888;">CURRENT RANK</div>
                    <div class="rank-display" id="rank-text">1st</div>
                </div>
                <div class="item-box" id="item-slot">❓</div>
                <div class="glass-box" style="text-align: right;">
                    <div style="font-size: 14px; color: #888;">LAP</div>
                    <div style="font-size: 32px; font-weight: bold;" id="lap-text">1 / 3</div>
                    <div style="font-size: 14px; color: #4facfe;" id="time-text">00:00.00</div>
                </div>
            </div>
            
            <canvas id="minimap-canvas" width="160" height="160" style="position: absolute; bottom: 20px; left: 20px;"></canvas>

            <div class="speedometer glass-box">
                <span class="speed-val" id="speed-text">0</span> <span class="speed-unit">KM/H</span>
                <div id="drift-indicator" style="font-size: 12px; height: 16px; color: #ff0055; font-weight: bold;"></div>
            </div>
        </div>

        <div id="result-modal">
            <h1 id="result-title" style="font-size: 64px; font-weight: 900; margin-bottom: 10px;">🏆 VICTORY!</h1>
            <p id="result-subtitle" style="font-size: 24px; color: #ccc;">당신의 최종 순위: <span id="final-rank" style="color: #ffd700; font-weight: bold;">1st</span></p>
            <p id="result-time" style="font-size: 20px; color: #888; margin-top: 8px;">기록: 01:23.45</p>
            <button class="btn-restart" onclick="resetGame()">🔄 다시 레이스하기</button>
        </div>
    </div>

    <script>
        // --- 설정 및 전역 변수 ---
        const TRACK_TYPE = "{track_code}";
        const PLAYER_COLOR = "{player_color}";
        const SPEED_MULT = {speed_multiplier};
        const AI_COUNT = {ai_count};
        const SOUND_ENABLED = {str(enable_sound).lower()};

        let scene, camera, renderer;
        let playerKart, playerMesh;
        let aiKarts = [];
        let trackCurve, trackMesh;
        let itemBoxes = [], projectiles = [], bananas = [];
        
        let keys = {{}};
        let speed = 0, maxSpeed = 1.3 * SPEED_MULT, accel = 0.025, turnSpeed = 0.038;
        let steeringAngle = 0, driftAngle = 0, driftTime = 0, isDrifting = false, driftBoost = 0;
        let currentLap = 1, totalLaps = 3, lapProgress = 0, totalProgress = 0;
        let raceState = 'COUNTDOWN'; // COUNTDOWN, RACING, FINISHED
        let raceStartTime = 0, elapsedTime = 0;
        let currentItem = null; // 'MUSHROOM', 'GREEN_SHELL', 'RED_SHELL', 'BANANA', 'LIGHTNING'
        let cameraMode = 0; // 0: 3인칭, 1: 탑뷰, 2: 1인칭

        // --- 오디오 합성기 (Web Audio API) ---
        let audioCtx = null;
        function initAudio() {{
            if (!SOUND_ENABLED || audioCtx) return;
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }}

        function playSound(type) {{
            if (!SOUND_ENABLED || !audioCtx) return;
            try {{
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                const now = audioCtx.currentTime;

                if (type === 'boost') {{
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(300, now);
                    osc.frequency.exponentialRampToValueAtTime(800, now + 0.4);
                    gain.gain.setValueAtTime(0.2, now);
                    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
                    osc.start(now); osc.stop(now + 0.4);
                }} else if (type === 'item') {{
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime(523.25, now); // C5
                    osc.frequency.setValueAtTime(659.25, now + 0.1); // E5
                    osc.frequency.setValueAtTime(783.99, now + 0.2); // G5
                    gain.gain.setValueAtTime(0.3, now);
                    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
                    osc.start(now); osc.stop(now + 0.35);
                }} else if (type === 'hit') {{
                    osc.type = 'square';
                    osc.frequency.setValueAtTime(150, now);
                    osc.frequency.exponentialRampToValueAtTime(40, now + 0.5);
                    gain.gain.setValueAtTime(0.4, now);
                    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.5);
                    osc.start(now); osc.stop(now + 0.5);
                }} else if (type === 'beep') {{
                    osc.type = 'triangle';
                    osc.frequency.setValueAtTime(440, now);
                    gain.gain.setValueAtTime(0.2, now);
                    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
                    osc.start(now); osc.stop(now + 0.2);
                }} else if (type === 'go') {{
                    osc.type = 'triangle';
                    osc.frequency.setValueAtTime(880, now);
                    gain.gain.setValueAtTime(0.3, now);
                    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.6);
                    osc.start(now); osc.stop(now + 0.6);
                }}
            }} catch(e) {{}}
        }}

        // --- 초기화 ---
        function init() {{
            const container = document.getElementById('game-container');
            
            // 씬 & 카메라
            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);

            // 렌더러
            renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: false }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            container.appendChild(renderer.domElement);

            // 조명
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
            scene.add(ambientLight);

            const sunLight = new THREE.DirectionalLight(0xffffff, 1.2);
            sunLight.position.set(100, 150, 50);
            sunLight.castShadow = true;
            sunLight.shadow.mapSize.width = 2048;
            sunLight.shadow.mapSize.height = 2048;
            sunLight.shadow.camera.near = 10;
            sunLight.shadow.camera.far = 400;
            const d = 150;
            sunLight.shadow.camera.left = -d; sunLight.shadow.camera.right = d;
            sunLight.shadow.camera.top = d; sunLight.shadow.camera.bottom = -d;
            scene.add(sunLight);

            // 트랙 및 배경 생성
            createEnvironment();
            createTrack();

            // 플레이어 카트
            playerKart = createKartMesh(PLAYER_COLOR, "PLAYER");
            scene.add(playerKart.mesh);
            playerKart.posProgress = 0;

            // AI 카트들
            const aiColors = ['#00d2ff', '#ff0055', '#00ff88', '#ffcc00', '#aa00ff', '#ff8800', '#00ffcc'];
            for(let i=0; i<AI_COUNT; i++) {{
                const ai = createKartMesh(aiColors[i % aiColors.length], `AI_${{i+1}}`);
                ai.posProgress = - (i + 1) * 0.015;
                ai.speed = maxSpeed * (0.85 + Math.random() * 0.2);
                aiKarts.push(ai);
                scene.add(ai.mesh);
            }}

            // 아이템 박스 생성
            createItemBoxes();

            // 이벤트 리스너
            window.addEventListener('keydown', e => {{ initAudio(); keys[e.code] = true; handleKeyDown(e); }});
            window.addEventListener('keyup', e => keys[e.code] = false);
            window.addEventListener('resize', onWindowResize);

            startCountdown();
            animate();
        }}

        // --- 트랙 커브 및 월드 생성 ---
        function createTrack() {{
            let points = [];
            if (TRACK_TYPE === 'rainbow') {{
                points = [
                    new THREE.Vector3(-120, 0, -80),
                    new THREE.Vector3(-120, 15, 80),
                    new THREE.Vector3(-40, 0, 140),
                    new THREE.Vector3(60, -10, 100),
                    new THREE.Vector3(140, 10, 40),
                    new THREE.Vector3(120, 0, -80),
                    new THREE.Vector3(0, -5, -120)
                ];
            }} else if (TRACK_TYPE === 'circuit') {{
                points = [
                    new THREE.Vector3(-140, 0, -100),
                    new THREE.Vector3(-140, 0, 100),
                    new THREE.Vector3(-60, 0, 150),
                    new THREE.Vector3(40, 0, 120),
                    new THREE.Vector3(140, 0, 80),
                    new THREE.Vector3(160, 0, -40),
                    new THREE.Vector3(60, 0, -140),
                    new THREE.Vector3(-40, 0, -100)
                ];
            }} else {{
                points = [
                    new THREE.Vector3(-100, 0, -100),
                    new THREE.Vector3(-150, 0, 0),
                    new THREE.Vector3(-80, 0, 120),
                    new THREE.Vector3(80, 0, 140),
                    new THREE.Vector3(150, 0, 20),
                    new THREE.Vector3(80, 0, -120)
                ];
            }}

            trackCurve = new THREE.CatmullRomCurve3(points, true, 'centripetal', 0.5);
            
            // 트랙 리본 메쉬 생성
            const samples = 300;
            const trackWidth = 18;
            const geometry = new THREE.BufferGeometry();
            const positions = [], uvs = [], normals = [];

            for (let i = 0; i <= samples; i++) {{
                const t = i / samples;
                const pt = trackCurve.getPointAt(t);
                const tangent = trackCurve.getTangentAt(t).normalize();
                const up = new THREE.Vector3(0, 1, 0);
                const side = new THREE.Vector3().crossVectors(tangent, up).normalize();

                const p1 = pt.clone().add(side.clone().multiplyScalar(trackWidth / 2));
                const p2 = pt.clone().add(side.clone().multiplyScalar(-trackWidth / 2));

                positions.push(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z);
                uvs.push(0, t * 20, 1, t * 20);
                normals.push(0, 1, 0, 0, 1, 0);
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
                    color: 0xffffff, roughness: 0.1, metalness: 0.8,
                    wireframe: false, transparent: true, opacity: 0.85,
                    emissive: 0x332266
                }});
            }} else {{
                mat = new THREE.MeshStandardMaterial({{ color: 0x333333, roughness: 0.8 }});
            }}

            trackMesh = new THREE.Mesh(geometry, mat);
            trackMesh.receiveShadow = true;
            scene.add(trackMesh);

            // 출발선 아치
            const startPt = trackCurve.getPointAt(0);
            const startTan = trackCurve.getTangentAt(0);
            const arch = new THREE.Group();
            const poleMat = new THREE.MeshStandardMaterial({{ color: 0xdddddd, metalness: 0.8 }});
            const p1 = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 12), poleMat);
            const p2 = p1.clone();
            p1.position.set(-10, 6, 0); p2.position.set(10, 6, 0);
            const banner = new THREE.Mesh(new THREE.BoxGeometry(21, 3, 0.5), new THREE.MeshStandardMaterial({{ color: 0xff0055 }}));
            banner.position.set(0, 10, 0);
            arch.add(p1, p2, banner);
            arch.position.copy(startPt);
            arch.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1), startTan);
            scene.add(arch);
        }}

        function createEnvironment() {{
            if (TRACK_TYPE === 'rainbow') {{
                scene.background = new THREE.Color(0x030310);
                scene.fog = new THREE.FogExp2(0x030310, 0.002);
                // 우주 별가루
                const starGeo = new THREE.BufferGeometry();
                const starCoords = [];
                for(let i=0; i<2000; i++) {{
                    starCoords.push((Math.random()-0.5)*800, (Math.random()-0.5)*800, (Math.random()-0.5)*800);
                }}
                starGeo.setAttribute('position', new THREE.Float32BufferAttribute(starCoords, 3));
                const starMat = new THREE.PointsMaterial({{ color: 0xffffff, size: 1.5 }});
                scene.add(new THREE.Points(starGeo, starMat));
            }} else if (TRACK_TYPE === 'circuit') {{
                scene.background = new THREE.Color(0x70c0ff);
                scene.fog = new THREE.FogExp2(0x70c0ff, 0.003);
                // 잔디 바닥
                const plane = new THREE.Mesh(new THREE.PlaneGeometry(800, 800), new THREE.MeshStandardMaterial({{ color: 0x43a047, roughness: 0.9 }}));
                plane.rotation.x = -Math.PI/2;
                plane.position.y = -0.5;
                plane.receiveShadow = true;
                scene.add(plane);
            }} else {{
                scene.background = new THREE.Color(0xffa726);
                scene.fog = new THREE.FogExp2(0xffa726, 0.004);
                // 사막 바닥
                const plane = new THREE.Mesh(new THREE.PlaneGeometry(800, 800), new THREE.MeshStandardMaterial({{ color: 0xedc9af, roughness: 1.0 }}));
                plane.rotation.x = -Math.PI/2;
                plane.position.y = -0.5;
                plane.receiveShadow = true;
                scene.add(plane);
            }}
        }}

        // --- 3D 카트 모델 생성 ---
        function createKartMesh(colorHex, name) {{
            const group = new THREE.Group();
            const bodyMat = new THREE.MeshStandardMaterial({{ color: colorHex, roughness: 0.3, metalness: 0.5 }});
            const wheelMat = new THREE.MeshStandardMaterial({{ color: 0x111111, roughness: 0.8 }});

            // 차체
            const chassis = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.8, 3.8), bodyMat);
            chassis.position.y = 0.6;
            chassis.castShadow = true;
            group.add(chassis);

            // 범퍼/노즈
            const nose = new THREE.Mesh(new THREE.ConeGeometry(1.2, 1.5, 4), bodyMat);
            nose.rotation.x = Math.PI / 2;
            nose.position.set(0, 0.5, 2.2);
            group.add(nose);

            // 바퀴 4개
            const wheelGeo = new THREE.CylinderGeometry(0.5, 0.5, 0.4, 16);
            wheelGeo.rotateZ(Math.PI / 2);
            const wheels = [];
            const offsets = [[-1.2, 0.5, 1.3], [1.2, 0.5, 1.3], [-1.2, 0.5, -1.3], [1.2, 0.5, -1.3]];
            offsets.forEach(pos => {{
                const w = new THREE.Mesh(wheelGeo, wheelMat);
                w.position.set(...pos);
                w.castShadow = true;
                group.add(w);
                wheels.push(w);
            }});

            // 운전자 머리 (헬멧)
            const head = new THREE.Mesh(new THREE.SphereGeometry(0.55, 16, 16), new THREE.MeshStandardMaterial({{ color: 0xffffff }}));
            head.position.set(0, 1.4, -0.2);
            group.add(head);

            return {{ mesh: group, wheels: wheels, name: name, posProgress: 0, speed: 0, spinOut: 0, boostTimer: 0 }};
        }}

        // --- 아이템 박스 생성 ---
        function createItemBoxes() {{
            const boxGeo = new THREE.BoxGeometry(2, 2, 2);
            const boxMat = new THREE.MeshStandardMaterial({{ color: 0xffd700, transparent: true, opacity: 0.8, emissive: 0x886600 }});

            for(let t=0.15; t<0.95; t+=0.2) {{
                const pt = trackCurve.getPointAt(t);
                const tan = trackCurve.getTangentAt(t);
                const side = new THREE.Vector3().crossVectors(tan, new THREE.Vector3(0,1,0)).normalize();

                [-4, 0, 4].forEach(off => {{
                    const box = new THREE.Mesh(boxGeo, boxMat);
                    box.position.copy(pt).add(side.clone().multiplyScalar(off)).add(new THREE.Vector3(0, 1.5, 0));
                    box.castShadow = true;
                    box.userData = {{ active: true, respawnTimer: 0 }};
                    scene.add(box);
                    itemBoxes.push(box);
                }});
            }}
        }}

        // --- 카운트다운 ---
        function startCountdown() {{
            const cd = document.getElementById('countdown');
            cd.style.display = 'block';
            let count = 3;
            cd.innerText = count;
            playSound('beep');

            const timer = setInterval(() => {{
                count--;
                if (count > 0) {{
                    cd.innerText = count;
                    playSound('beep');
                }} else if (count === 0) {{
                    cd.innerText = "GO!";
                    cd.style.color = "#00ff88";
                    playSound('go');
                    raceState = 'RACING';
                    raceStartTime = performance.now();
                }} else {{
                    cd.style.display = 'none';
                    clearInterval(timer);
                }}
            }}, 1000);
        }}

        // --- 조작 및 키보드 입출력 ---
        function handleKeyDown(e) {{
            if (e.code === 'KeyC') cameraMode = (cameraMode + 1) % 3;
            if (e.code === 'Space' || e.code === 'KeyE') useItem();
            if (e.code === 'KeyR') resetGame();
        }}

        function useItem() {{
            if (!currentItem || raceState !== 'RACING') return;
            
            playSound('boost');
            if (currentItem === 'MUSHROOM') {{
                playerKart.boostTimer = 120; // 스피드 부스트
            }} else if (currentItem === 'GREEN_SHELL') {{
                spawnProjectile(playerKart.mesh.position, playerKart.mesh.quaternion, 'GREEN');
            }} else if (currentItem === 'BANANA') {{
                spawnBanana(playerKart.mesh.position);
            }} else if (currentItem === 'LIGHTNING') {{
                aiKarts.forEach(ai => ai.spinOut = 60);
            }}

            currentItem = null;
            document.getElementById('item-slot').innerText = '❓';
        }}

        function spawnProjectile(pos, quat, type) {{
            const geo = new THREE.SphereGeometry(0.8, 16, 16);
            const mat = new THREE.MeshStandardMaterial({{ color: 0x00ff00, emissive: 0x00aa00 }});
            const proj = new THREE.Mesh(geo, mat);
            proj.position.copy(pos).add(new THREE.Vector3(0, 1, 0));
            proj.quaternion.copy(quat);
            proj.userData = {{ type: type, life: 180, speed: 2.5 }};
            scene.add(proj);
            projectiles.push(proj);
        }}

        function spawnBanana(pos) {{
            const geo = new THREE.CylinderGeometry(0.1, 0.8, 1.2, 8);
            const mat = new THREE.MeshStandardMaterial({{ color: 0xffeb3b }});
            const banana = new THREE.Mesh(geo, mat);
            banana.position.copy(pos);
            scene.add(banana);
            bananas.push(banana);
        }}

        // --- 메인 애니메이션 루프 ---
        function animate() {{
            requestAnimationFrame(animate);

            if (raceState === 'RACING') {{
                elapsedTime = (performance.now() - raceStartTime) / 1000;
                updateTimeDisplay();
                updatePlayer();
                updateAI();
                updateProjectilesAndItems();
                updatePositions();
            }}

            updateCamera();
            drawMinimap();
            renderer.render(scene, camera);
        }}

        // --- 플레이어 물리 & 이동 ---
        function updatePlayer() {{
            // 스핀아웃 처리
            if (playerKart.spinOut > 0) {{
                playerKart.spinOut--;
                playerKart.mesh.rotation.y += 0.3;
                speed *= 0.9;
                return;
            }}

            // 드리프트 처리
            if (keys['ShiftLeft'] || keys['ShiftRight']) {{
                if ((keys['KeyA'] || keys['ArrowLeft']) || (keys['KeyD'] || keys['ArrowRight'])) {{
                    isDrifting = true;
                    driftTime++;
                    if (driftTime > 40) document.getElementById('drift-indicator').innerText = '⚡ SUPER MINI-TURBO!';
                    else if (driftTime > 20) document.getElementById('drift-indicator').innerText = '🔥 MINI-TURBO!';
                }}
            }} else {{
                if (isDrifting) {{
                    if (driftTime > 40) {{ playerKart.boostTimer = 60; playSound('boost'); }}
                    else if (driftTime > 20) {{ playerKart.boostTimer = 30; playSound('boost'); }}
                    isDrifting = false;
                    driftTime = 0;
                    document.getElementById('drift-indicator').innerText = '';
                }}
            }}

            // 가속 / 브레이크
            let targetMaxSpeed = maxSpeed;
            if (playerKart.boostTimer > 0) {{
                playerKart.boostTimer--;
                targetMaxSpeed *= 1.6;
            }}

            if (keys['KeyW'] || keys['ArrowUp']) speed = Math.min(speed + accel, targetMaxSpeed);
            else if (keys['KeyS'] || keys['ArrowDown']) speed = Math.max(speed - accel * 1.5, -maxSpeed * 0.4);
            else speed *= 0.96; // 마찰력

            // 조향
            if (keys['KeyA'] || keys['ArrowLeft']) steeringAngle = turnSpeed * (isDrifting ? 1.4 : 1.0);
            else if (keys['KeyD'] || keys['ArrowRight']) steeringAngle = -turnSpeed * (isDrifting ? 1.4 : 1.0);
            else steeringAngle = 0;

            playerKart.mesh.rotation.y += steeringAngle * (speed / maxSpeed);

            // 이동
            const dir = new THREE.Vector3(0, 0, 1).applyQuaternion(playerKart.mesh.quaternion);
            playerKart.mesh.position.add(dir.multiplyScalar(speed));

            // 바퀴 회전
            playerKart.wheels.forEach(w => w.rotation.x += speed * 0.5);

            // 트랙 진행률 (Lap / Progress)
            const pt = playerKart.mesh.position;
            let closestT = 0, minDist = Infinity;
            for(let t=0; t<=1; t+=0.02) {{
                const p = trackCurve.getPointAt(t);
                const d = pt.distanceTo(p);
                if (d < minDist) {{ minDist = d; closestT = t; }}
            }}

            // 완주 및 랩 체크
            if (playerKart.posProgress > 0.85 && closestT < 0.15) {{
                currentLap++;
                if (currentLap > totalLaps) {{
                    finishRace();
                }} else {{
                    document.getElementById('lap-text').innerText = `${{currentLap}} / ${{totalLaps}}`;
                    playSound('boost');
                }}
            }}
            playerKart.posProgress = closestT;
            totalProgress = (currentLap - 1) + closestT;

            // 속도계 UI
            document.getElementById('speed-text').innerText = Math.round(Math.abs(speed) * 120);
        }}

        // --- AI 레이서 제어 ---
        function updateAI() {{
            aiKarts.forEach(ai => {{
                if (ai.spinOut > 0) {{
                    ai.spinOut--;
                    ai.mesh.rotation.y += 0.3;
                    return;
                }}

                ai.posProgress += (ai.speed / 2000);
                if (ai.posProgress >= 1.0) ai.posProgress -= 1.0;

                const targetPt = trackCurve.getPointAt((ai.posProgress + 0.02) % 1.0);
                const currentPt = trackCurve.getPointAt(ai.posProgress % 1.0);
                
                ai.mesh.position.copy(currentPt);
                ai.mesh.lookAt(targetPt);
                ai.wheels.forEach(w => w.rotation.x += 0.3);
            }});
        }}

        // --- 투사체, 아이템 박스 & 충돌 ---
        function updateProjectilesAndItems() {{
            // 아이템 박스 회전 & 획득
            itemBoxes.forEach(box => {{
                if (box.userData.active) {{
                    box.rotation.y += 0.03;
                    box.rotation.x += 0.02;

                    if (playerKart.mesh.position.distanceTo(box.position) < 2.5) {{
                        box.userData.active = false;
                        box.visible = false;
                        box.userData.respawnTimer = 300;
                        getRandomItem();
                        playSound('item');
                    }}
                }} else {{
                    box.userData.respawnTimer--;
                    if (box.userData.respawnTimer <= 0) {{
                        box.userData.active = true;
                        box.visible = true;
                    }}
                }}
            }});

            // 바나나 충돌
            bananas.forEach((b, idx) => {{
                if (playerKart.mesh.position.distanceTo(b.position) < 1.8) {{
                    playerKart.spinOut = 45;
                    playSound('hit');
                    scene.remove(b);
                    bananas.splice(idx, 1);
                }}
            }});
        }}

        function getRandomItem() {{
            const items = ['MUSHROOM', 'GREEN_SHELL', 'BANANA', 'LIGHTNING'];
            const icons = {{ 'MUSHROOM': '🍄', 'GREEN_SHELL': '🐢', 'BANANA': '🍌', 'LIGHTNING': '⚡' }};
            const pick = items[Math.floor(Math.random() * items.length)];
            currentItem = pick;
            document.getElementById('item-slot').innerText = icons[pick];
        }}

        // --- 순위 산정 ---
        function updatePositions() {{
            let racers = [
                {{ name: 'PLAYER', progress: totalProgress }},
                ...aiKarts.map(ai => ({{ name: ai.name, progress: ai.posProgress }}))
            ];

            racers.sort((a, b) => b.progress - a.progress);
            const rank = racers.findIndex(r => r.name === 'PLAYER') + 1;

            const suffixes = ["st", "nd", "rd", "th"];
            const suffix = (rank <= 3) ? suffixes[rank - 1] : "th";
            document.getElementById('rank-text').innerText = `${{rank}}${{suffix}}`;
        }}

        // --- 카메라 제어 ---
        function updateCamera() {{
            const pPos = playerKart.mesh.position;
            const pQuat = playerKart.mesh.quaternion;

            if (cameraMode === 0) {{ // 3인칭 체이스
                const offset = new THREE.Vector3(0, 5, -12).applyQuaternion(pQuat);
                camera.position.lerp(pPos.clone().add(offset), 0.1);
                camera.lookAt(pPos.clone().add(new THREE.Vector3(0, 1.8, 0)));
            }} else if (cameraMode === 1) {{ // 탑뷰
                camera.position.set(pPos.x, pPos.y + 60, pPos.z);
                camera.lookAt(pPos);
            }} else {{ // 1인칭
                const offset = new THREE.Vector3(0, 1.5, 0.5).applyQuaternion(pQuat);
                camera.position.copy(pPos.clone().add(offset));
                const lookAtPt = pPos.clone().add(new THREE.Vector3(0, 1.5, 10).applyQuaternion(pQuat));
                camera.lookAt(lookAtPt);
            }}
        }}

        // --- 미니맵 렌더링 ---
        function drawMinimap() {{
            const canvas = document.getElementById('minimap-canvas');
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, 160, 160);

            // 트랙 경로 그리기
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
            ctx.lineWidth = 6;
            ctx.beginPath();
            for(let t=0; t<=1; t+=0.02) {{
                const pt = trackCurve.getPointAt(t);
                const x = 80 + pt.x * 0.4;
                const y = 80 + pt.z * 0.4;
                if (t === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }}
            ctx.closePath();
            ctx.stroke();

            // AI 위치 점
            aiKarts.forEach(ai => {{
                const x = 80 + ai.mesh.position.x * 0.4;
                const y = 80 + ai.mesh.position.z * 0.4;
                ctx.fillStyle = '#ff0055';
                ctx.beginPath(); ctx.arc(x, y, 4, 0, Math.PI*2); ctx.fill();
            }});

            // 플레이어 위치 점
            const px = 80 + playerKart.mesh.position.x * 0.4;
            const py = 80 + playerKart.mesh.position.z * 0.4;
            ctx.fillStyle = '#00f2fe';
            ctx.shadowColor = '#00f2fe'; ctx.shadowBlur = 8;
            ctx.beginPath(); ctx.arc(px, py, 6, 0, Math.PI*2); ctx.fill();
            ctx.shadowBlur = 0;
        }}

        function updateTimeDisplay() {{
            const mins = Math.floor(elapsedTime / 60).toString().padStart(2, '0');
            const secs = Math.floor(elapsedTime % 60).toString().padStart(2, '0');
            const ms = Math.floor((elapsedTime % 1) * 100).toString().padStart(2, '0');
            document.getElementById('time-text').innerText = `${{mins}}:${{secs}}.${{ms}}`;
        }}

        function finishRace() {{
            raceState = 'FINISHED';
            playSound('boost');
            const modal = document.getElementById('result-modal');
            modal.style.display = 'flex';
            document.getElementById('final-rank').innerText = document.getElementById('rank-text').innerText;
            document.getElementById('result-time').innerText = `기록: ${{document.getElementById('time-text').innerText}}`;
        }}

        function resetGame() {{
            location.reload();
        }}

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

# Streamlit HTML 컴포넌트로 렌더링 (높이 820px)
components.html(html_code, height=820, scrolling=False)
