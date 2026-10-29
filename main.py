import streamlit as st
import streamlit.components.v1 as components

# 페이지 기본 설정
st.set_page_config(
    page_title="3D 마리오 카트 8 - 디테일 업그레이드",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 스타일링
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
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

track_type = st.sidebar.selectbox(
    "🗺️ 트랙 코스 선택",
    ["무지개 로드 (Rainbow Road)", "마리오 서킷 (Mario Circuit)", "사막 힐스 (Desert Hills)"]
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
* **[ W / ↑ ]** : 가속 | **[ S / ↓ ]** : 감속/후진
* **[ A, D / ←, → ]** : 조향 (스티어링)
* **[ Shift ]** : 드리프트 (코너링 중 부스터 스파크!)
* **[ Space / E ]** : 아이템 사용
* **[ C ]** : 카메라인 시점 변경
* **[ R ]** : 게임 재시작
""")

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
    <title>3D Mario Kart Streamlit Enhanced</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; user-select: none; }}
        body {{ overflow: hidden; background: #000; width: 100vw; height: 100vh; }}
        #game-container {{ width: 100%; height: 100vh; position: relative; }}
        canvas {{ width: 100%; height: 100%; display: block; }}

        /* HUD 오버레이 */
        #hud {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            pointer-events: none; padding: 16px;
            display: flex; flex-direction: column; justify-content: space-between;
        }}
        .top-bar {{ display: flex; justify-content: space-between; align-items: flex-start; }}
        .glass-box {{
            background: rgba(15, 23, 42, 0.7);
            backdrop-filter: blur(10px);
            border: 1.5px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 10px 16px;
            color: #fff;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        }}
        .rank-display {{
            font-size: 36px; font-weight: 900; font-style: italic;
            background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }}
        .item-box {{
            width: 64px; height: 64px; border-radius: 14px;
            display: flex; align-items: center; justify-content: center;
            font-size: 32px; border: 2.5px solid #ffd700;
            background: rgba(0,0,0,0.65); box-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
        }}
        
        .speedometer {{
            position: absolute; bottom: 16px; right: 16px;
            text-align: right; font-family: monospace;
        }}
        .speed-val {{ font-size: 38px; font-weight: bold; color: #00f2fe; text-shadow: 0 0 10px #00f2fe; }}
        .speed-unit {{ font-size: 14px; color: #aaa; }}

        /* 축소 및 가독성 개선된 미니맵 */
        #minimap-canvas {{
            position: absolute; bottom: 16px; left: 16px;
            width: 110px; height: 110px;
            border-radius: 50%; border: 2px solid rgba(255,255,255,0.5);
            background: rgba(0, 0, 0, 0.65); box-shadow: 0 4px 15px rgba(0,0,0,0.7);
            z-index: 10;
        }}

        #countdown {{
            position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%);
            font-size: 110px; font-weight: 900; color: #fff; text-shadow: 0 0 25px #ff0055;
            display: none; z-index: 100;
        }}

        #result-modal {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.85); display: none; flex-direction: column;
            align-items: center; justify-content: center; color: white; z-index: 200;
            pointer-events: auto;
        }}
        .btn-restart {{
            margin-top: 20px; padding: 12px 32px; font-size: 20px; font-weight: bold;
            background: linear-gradient(45deg, #ff0055, #ff5000); border: none;
            color: white; border-radius: 25px; cursor: pointer; transition: 0.2s;
            box-shadow: 0 0 15px rgba(255, 0, 85, 0.6);
        }}
        .btn-restart:hover {{ transform: scale(1.08); box-shadow: 0 0 25px rgba(255, 0, 85, 0.9); }}
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
        let itemBoxes = [], bananas = [];
        
        let keys = {{}};
        let speed = 0, maxSpeed = 1.35 * SPEED_MULT, accel = 0.028, turnSpeed = 0.04;
        let steeringAngle = 0, driftTime = 0, isDrifting = false;
        let currentLap = 1, totalLaps = 3, totalProgress = 0;
        let raceState = 'COUNTDOWN';
        let raceStartTime = 0, elapsedTime = 0;
        let currentItem = null;
        let cameraMode = 0;

        // --- 사운드 효과 ---
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
                    osc.type = 'sawtooth'; osc.frequency.setValueAtTime(250, now);
                    osc.frequency.exponentialRampToValueAtTime(900, now + 0.35);
                    gain.gain.setValueAtTime(0.2, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
                    osc.start(now); osc.stop(now + 0.35);
                }} else if (type === 'item') {{
                    osc.type = 'sine'; osc.frequency.setValueAtTime(523, now);
                    osc.frequency.setValueAtTime(659, now + 0.08); osc.frequency.setValueAtTime(783, now + 0.16);
                    gain.gain.setValueAtTime(0.25, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
                    osc.start(now); osc.stop(now + 0.3);
                }} else if (type === 'hit') {{
                    osc.type = 'square'; osc.frequency.setValueAtTime(140, now);
                    osc.frequency.exponentialRampToValueAtTime(30, now + 0.4);
                    gain.gain.setValueAtTime(0.3, now); gain.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
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

        // --- 초기화 ---
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

            // 조명 설정
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
            scene.add(ambientLight);

            const sunLight = new THREE.DirectionalLight(0xffffff, 1.2);
            sunLight.position.set(120, 180, 80);
            sunLight.castShadow = true;
            sunLight.shadow.mapSize.width = 2048; sunLight.shadow.mapSize.height = 2048;
            sunLight.shadow.camera.near = 10; sunLight.shadow.camera.far = 500;
            const d = 200;
            sunLight.shadow.camera.left = -d; sunLight.shadow.camera.right = d;
            sunLight.shadow.camera.top = d; sunLight.shadow.camera.bottom = -d;
            scene.add(sunLight);

            createEnvironment();
            createTrackAndStructures();

            // 플레이어
            playerKart = createKartMesh(PLAYER_COLOR, "PLAYER");
            scene.add(playerKart.mesh);
            playerKart.posProgress = 0;

            // AI 카트들
            const aiColors = ['#00d2ff', '#ff0055', '#00ff88', '#ffcc00', '#aa00ff', '#ff8800', '#00ffcc'];
            for(let i=0; i<AI_COUNT; i++) {{
                const ai = createKartMesh(aiColors[i % aiColors.length], `AI_${{i+1}}`);
                ai.posProgress = - (i + 1) * 0.015;
                ai.speed = maxSpeed * (0.86 + Math.random() * 0.18);
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

        // --- 복잡해진 트랙 & 테마별 3D 구조물 생성 ---
        function createTrackAndStructures() {{
            let points = [];
            if (TRACK_TYPE === 'rainbow') {{
                // 높은 고저차의 스파이럴 무지개 트랙
                points = [
                    new THREE.Vector3(-160, 0, -120),
                    new THREE.Vector3(-180, 20, -20),
                    new THREE.Vector3(-130, 35, 90),
                    new THREE.Vector3(-40, 20, 160),
                    new THREE.Vector3(50, -5, 140),
                    new THREE.Vector3(120, -25, 60),
                    new THREE.Vector3(170, 5, -20),
                    new THREE.Vector3(140, 30, -120),
                    new THREE.Vector3(20, 15, -170),
                    new THREE.Vector3(-80, 0, -150)
                ];
            }} else if (TRACK_TYPE === 'circuit') {{
                // 시케인 코너와 S자가 섞인 마리오 서킷
                points = [
                    new THREE.Vector3(-160, 0, -120),
                    new THREE.Vector3(-180, 0, -20),
                    new THREE.Vector3(-130, 8, 80),
                    new THREE.Vector3(-60, 15, 140),
                    new THREE.Vector3(20, 5, 160),
                    new THREE.Vector3(90, -5, 100),
                    new THREE.Vector3(50, 0, 30),    // 급격한 시케인 코너
                    new THREE.Vector3(130, 0, -30),
                    new THREE.Vector3(170, 0, -110),
                    new THREE.Vector3(80, 0, -160),
                    new THREE.Vector3(-40, 0, -130)
                ];
            }} else {{
                // 사막 협곡 힐스
                points = [
                    new THREE.Vector3(-140, 0, -140),
                    new THREE.Vector3(-180, 10, -40),
                    new THREE.Vector3(-110, 22, 60),
                    new THREE.Vector3(-30, 8, 150),
                    new THREE.Vector3(70, 0, 170),
                    new THREE.Vector3(150, -10, 100),
                    new THREE.Vector3(180, 8, -20),
                    new THREE.Vector3(110, 18, -120),
                    new THREE.Vector3(0, 0, -180)
                ];
            }}

            trackCurve = new THREE.CatmullRomCurve3(points, true, 'centripetal', 0.5);
            
            // 1. 메인 도로 메쉬
            const samples = 400;
            const trackWidth = 20;
            const geometry = new THREE.BufferGeometry();
            const positions = [], uvs = [], normals = [];

            const leftBorderPts = [], rightBorderPts = [];

            for (let i = 0; i <= samples; i++) {{
                const t = i / samples;
                const pt = trackCurve.getPointAt(t);
                const tangent = trackCurve.getTangentAt(t).normalize();
                const up = new THREE.Vector3(0, 1, 0);
                const side = new THREE.Vector3().crossVectors(tangent, up).normalize();

                const p1 = pt.clone().add(side.clone().multiplyScalar(trackWidth / 2));
                const p2 = pt.clone().add(side.clone().multiplyScalar(-trackWidth / 2));

                positions.push(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z);
                uvs.push(0, t * 30, 1, t * 30);
                normals.push(0, 1, 0, 0, 1, 0);

                // 가드레일/커브용 포인트 저장
                leftBorderPts.push(p1.add(new THREE.Vector3(0, 0.4, 0)));
                rightBorderPts.push(p2.add(new THREE.Vector3(0, 0.4, 0)));
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
                    transparent: true, opacity: 0.88, emissive: 0x442266
                }});
            }} else if (TRACK_TYPE === 'circuit') {{
                mat = new THREE.MeshStandardMaterial({{ color: 0x222225, roughness: 0.7 }});
            }} else {{
                mat = new THREE.MeshStandardMaterial({{ color: 0x8d6e63, roughness: 0.9 }});
            }}

            trackMesh = new THREE.Mesh(geometry, mat);
            trackMesh.receiveShadow = true;
            scene.add(trackMesh);

            // 2. 가시성을 극대화하는 트랙 테두리 가드레일 (Glowing Border / Curbs)
            createTrackBorders(leftBorderPts, rightBorderPts);

            // 3. 출발선 아치
            createStartArch();

            // 4. 테마별 3D 구조물 대량 배치
            buildWorldStructures();
        }}

        // --- 트랙 경계 선명화 (가드레일 & 커브) ---
        function createTrackBorders(leftPts, rightPts) {{
            const borderMat = (TRACK_TYPE === 'rainbow') 
                ? new THREE.MeshStandardMaterial({{ color: 0x00ffff, emissive: 0x00ffff, emissiveIntensity: 0.8 }})
                : new THREE.MeshStandardMaterial({{ color: (TRACK_TYPE === 'circuit') ? 0xff0055 : 0xffb300, roughness: 0.4 }});

            [leftPts, rightPts].forEach(pts => {{
                const curve = new THREE.CatmullRomCurve3(pts, true);
                const tubeGeo = new THREE.TubeGeometry(curve, 300, 0.4, 8, true);
                const borderMesh = new THREE.Mesh(tubeGeo, borderMat);
                scene.add(borderMesh);
            }});
        }}

        // --- 출발선 아치 ---
        function createStartArch() {{
            const startPt = trackCurve.getPointAt(0);
            const startTan = trackCurve.getTangentAt(0);
            const arch = new THREE.Group();
            const poleMat = new THREE.MeshStandardMaterial({{ color: 0xeeeeee, metalness: 0.8 }});
            
            const p1 = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.6, 14), poleMat);
            const p2 = p1.clone();
            p1.position.set(-11, 7, 0); p2.position.set(11, 7, 0);
            
            const banner = new THREE.Mesh(new THREE.BoxGeometry(23, 3.5, 0.8), new THREE.MeshStandardMaterial({{ color: 0xff0055 }}));
            banner.position.set(0, 12, 0);
            
            arch.add(p1, p2, banner);
            arch.position.copy(startPt);
            arch.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1), startTan);
            scene.add(arch);
        }}

        // --- 테마별 입체 구조물 생성 ---
        function buildWorldStructures() {{
            if (TRACK_TYPE === 'rainbow') {{
                // 네온 관통 링 및 자이언트 크리스탈
                for(let t=0.08; t<0.95; t+=0.1) {{
                    const pt = trackCurve.getPointAt(t);
                    const tan = trackCurve.getTangentAt(t);
                    
                    const ringGeo = new THREE.TorusGeometry(14, 0.8, 16, 32);
                    const ringMat = new THREE.MeshStandardMaterial({{ color: 0xff00cc, emissive: 0xff00cc, emissiveIntensity: 0.6 }});
                    const ring = new THREE.Mesh(ringGeo, ringMat);
                    ring.position.copy(pt).add(new THREE.Vector3(0, 8, 0));
                    ring.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1), tan);
                    scene.add(ring);
                }}
            }} else if (TRACK_TYPE === 'circuit') {{
                // 마리오 캐슬 성벽, 초록 파이프, 나무 배치
                const pipeMat = new THREE.MeshStandardMaterial({{ color: 0x43b047, roughness: 0.3 }});
                const treeMat = new THREE.MeshStandardMaterial({{ color: 0x2e7d32, roughness: 0.8 }});
                const woodMat = new THREE.MeshStandardMaterial({{ color: 0x795548 }});

                for(let t=0.03; t<0.98; t+=0.07) {{
                    const pt = trackCurve.getPointAt(t);
                    const tan = trackCurve.getTangentAt(t);
                    const side = new THREE.Vector3().crossVectors(tan, new THREE.Vector3(0,1,0)).normalize();

                    // 거대 워프 파이프
                    const pipe = new THREE.Mesh(new THREE.CylinderGeometry(3, 3, 7, 16), pipeMat);
                    pipe.position.copy(pt).add(side.clone().multiplyScalar((t % 0.1 > 0.05 ? 1 : -1) * 22));
                    pipe.position.y += 3.5;
                    pipe.castShadow = true;
                    scene.add(pipe);

                    // 버섯 모양 입체 나무
                    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 1, 5), woodMat);
                    const foliage = new THREE.Mesh(new THREE.SphereGeometry(3.5, 8, 8), treeMat);
                    foliage.position.y = 4.5;
                    const tree = new THREE.Group(); tree.add(trunk, foliage);
                    tree.position.copy(pt).add(side.clone().multiplyScalar((t % 0.1 > 0.05 ? -1 : 1) * 28));
                    tree.castShadow = true;
                    scene.add(tree);
                }}
            }} else {{
                // 사막 피라미드, 석조 기둥, 선인장
                const pyramidMat = new THREE.MeshStandardMaterial({{ color: 0xd7ccc8, roughness: 0.9 }});
                const pyr = new THREE.Mesh(new THREE.ConeGeometry(40, 35, 4), pyramidMat);
                pyr.position.set(0, 17.5, 0);
                pyr.rotation.y = Math.PI / 4;
                scene.add(pyr);

                for(let t=0.05; t<0.95; t+=0.08) {{
                    const pt = trackCurve.getPointAt(t);
                    const tan = trackCurve.getTangentAt(t);
                    const side = new THREE.Vector3().crossVectors(tan, new THREE.Vector3(0,1,0)).normalize();

                    // 사막 고대 석조 기둥
                    const pillar = new THREE.Mesh(new THREE.BoxGeometry(3, 16, 3), pyramidMat);
                    pillar.position.copy(pt).add(side.clone().multiplyScalar((t % 0.1 > 0.05 ? 1 : -1) * 20));
                    pillar.position.y += 8;
                    pillar.castShadow = true;
                    scene.add(pillar);
                }}
            }}
        }}

        function createEnvironment() {{
            if (TRACK_TYPE === 'rainbow') {{
                scene.background = new THREE.Color(0x02020a);
                scene.fog = new THREE.FogExp2(0x02020a, 0.0015);
                const starGeo = new THREE.BufferGeometry();
                const starCoords = [];
                for(let i=0; i<2500; i++) starCoords.push((Math.random()-0.5)*900, (Math.random()-0.5)*900, (Math.random()-0.5)*900);
                starGeo.setAttribute('position', new THREE.Float32BufferAttribute(starCoords, 3));
                scene.add(new THREE.Points(starGeo, new THREE.PointsMaterial({{ color: 0xffffff, size: 1.5 }})));
            }} else if (TRACK_TYPE === 'circuit') {{
                scene.background = new THREE.Color(0x64b5f6);
                scene.fog = new THREE.FogExp2(0x64b5f6, 0.0025);
                const plane = new THREE.Mesh(new THREE.PlaneGeometry(1000, 1000), new THREE.MeshStandardMaterial({{ color: 0x388e3c, roughness: 0.9 }}));
                plane.rotation.x = -Math.PI/2; plane.position.y = -0.5; plane.receiveShadow = true;
                scene.add(plane);
            }} else {{
                scene.background = new THREE.Color(0xffb74d);
                scene.fog = new THREE.FogExp2(0xffb74d, 0.0035);
                const plane = new THREE.Mesh(new THREE.PlaneGeometry(1000, 1000), new THREE.MeshStandardMaterial({{ color: 0xe0a96d, roughness: 1.0 }}));
                plane.rotation.x = -Math.PI/2; plane.position.y = -0.5; plane.receiveShadow = true;
                scene.add(plane);
            }}
        }}

        // --- 3D 카트 모델 생성 ---
        function createKartMesh(colorHex, name) {{
            const group = new THREE.Group();
            const bodyMat = new THREE.MeshStandardMaterial({{ color: colorHex, roughness: 0.3, metalness: 0.5 }});
            const wheelMat = new THREE.MeshStandardMaterial({{ color: 0x111111, roughness: 0.8 }});

            const chassis = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.8, 3.8), bodyMat);
            chassis.position.y = 0.6; chassis.castShadow = true;
            group.add(chassis);

            const nose = new THREE.Mesh(new THREE.ConeGeometry(1.2, 1.5, 4), bodyMat);
            nose.rotation.x = Math.PI / 2; nose.position.set(0, 0.5, 2.2);
            group.add(nose);

            const wheelGeo = new THREE.CylinderGeometry(0.5, 0.5, 0.4, 16);
            wheelGeo.rotateZ(Math.PI / 2);
            const wheels = [];
            const offsets = [[-1.2, 0.5, 1.3], [1.2, 0.5, 1.3], [-1.2, 0.5, -1.3], [1.2, 0.5, -1.3]];
            offsets.forEach(pos => {{
                const w = new THREE.Mesh(wheelGeo, wheelMat);
                w.position.set(...pos); w.castShadow = true;
                group.add(w); wheels.push(w);
            }});

            const head = new THREE.Mesh(new THREE.SphereGeometry(0.55, 16, 16), new THREE.MeshStandardMaterial({{ color: 0xffffff }}));
            head.position.set(0, 1.4, -0.2);
            group.add(head);

            return {{ mesh: group, wheels: wheels, name: name, posProgress: 0, speed: 0, spinOut: 0, boostTimer: 0 }};
        }}

        // --- 아이템 박스 ---
        function createItemBoxes() {{
            const boxGeo = new THREE.BoxGeometry(2, 2, 2);
            const boxMat = new THREE.MeshStandardMaterial({{ color: 0xffd700, transparent: true, opacity: 0.85, emissive: 0xaa8800 }});

            for(let t=0.12; t<0.95; t+=0.18) {{
                const pt = trackCurve.getPointAt(t);
                const tan = trackCurve.getTangentAt(t);
                const side = new THREE.Vector3().crossVectors(tan, new THREE.Vector3(0,1,0)).normalize();

                [-4.5, 0, 4.5].forEach(off => {{
                    const box = new THREE.Mesh(boxGeo, boxMat);
                    box.position.copy(pt).add(side.clone().multiplyScalar(off)).add(new THREE.Vector3(0, 1.5, 0));
                    box.castShadow = true;
                    box.userData = {{ active: true, respawnTimer: 0 }};
                    scene.add(box); itemBoxes.push(box);
                }});
            }}
        }}

        // --- 카운트다운 ---
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
            playSound('boost');
            if (currentItem === 'MUSHROOM') playerKart.boostTimer = 110;
            else if (currentItem === 'BANANA') spawnBanana(playerKart.mesh.position);
            else if (currentItem === 'LIGHTNING') aiKarts.forEach(ai => ai.spinOut = 60);

            currentItem = null;
            document.getElementById('item-slot').innerText = '❓';
        }}

        function spawnBanana(pos) {{
            const geo = new THREE.CylinderGeometry(0.1, 0.8, 1.2, 8);
            const banana = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({{ color: 0xffeb3b }}));
            banana.position.copy(pos); scene.add(banana); bananas.push(banana);
        }}

        // --- 루프 애니메이션 ---
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

        // --- 플레이어 물리 ---
        function updatePlayer() {{
            if (playerKart.spinOut > 0) {{
                playerKart.spinOut--; playerKart.mesh.rotation.y += 0.3; speed *= 0.9; return;
            }}

            if (keys['ShiftLeft'] || keys['ShiftRight']) {{
                if ((keys['KeyA'] || keys['ArrowLeft']) || (keys['KeyD'] || keys['ArrowRight'])) {{
                    isDrifting = true; driftTime++;
                    if (driftTime > 40) document.getElementById('drift-indicator').innerText = '⚡ SUPER MINI-TURBO!';
                    else if (driftTime > 20) document.getElementById('drift-indicator').innerText = '🔥 MINI-TURBO!';
                }}
            }} else {{
                if (isDrifting) {{
                    if (driftTime > 40) {{ playerKart.boostTimer = 60; playSound('boost'); }}
                    else if (driftTime > 20) {{ playerKart.boostTimer = 30; playSound('boost'); }}
                    isDrifting = false; driftTime = 0;
                    document.getElementById('drift-indicator').innerText = '';
                }}
            }}

            let targetMaxSpeed = maxSpeed;
            if (playerKart.boostTimer > 0) {{ playerKart.boostTimer--; targetMaxSpeed *= 1.55; }}

            if (keys['KeyW'] || keys['ArrowUp']) speed = Math.min(speed + accel, targetMaxSpeed);
            else if (keys['KeyS'] || keys['ArrowDown']) speed = Math.max(speed - accel * 1.5, -maxSpeed * 0.4);
            else speed *= 0.96;

            if (keys['KeyA'] || keys['ArrowLeft']) steeringAngle = turnSpeed * (isDrifting ? 1.35 : 1.0);
            else if (keys['KeyD'] || keys['ArrowRight']) steeringAngle = -turnSpeed * (isDrifting ? 1.35 : 1.0);
            else steeringAngle = 0;

            playerKart.mesh.rotation.y += steeringAngle * (speed / maxSpeed);

            const dir = new THREE.Vector3(0, 0, 1).applyQuaternion(playerKart.mesh.quaternion);
            playerKart.mesh.position.add(dir.multiplyScalar(speed));
            playerKart.wheels.forEach(w => w.rotation.x += speed * 0.5);

            // 랩 및 진행도 계산
            const pt = playerKart.mesh.position;
            let closestT = 0, minDist = Infinity;
            for(let t=0; t<=1; t+=0.01) {{
                const d = pt.distanceTo(trackCurve.getPointAt(t));
                if (d < minDist) {{ minDist = d; closestT = t; }}
            }}

            if (playerKart.posProgress > 0.85 && closestT < 0.15) {{
                currentLap++;
                if (currentLap > totalLaps) finishRace();
                else {{
                    document.getElementById('lap-text').innerText = `${{currentLap}} / ${{totalLaps}}`;
                    playSound('boost');
                }}
            }}
            playerKart.posProgress = closestT;
            totalProgress = (currentLap - 1) + closestT;

            document.getElementById('speed-text').innerText = Math.round(Math.abs(speed) * 120);
        }}

        // --- AI 레이서 ---
        function updateAI() {{
            aiKarts.forEach(ai => {{
                if (ai.spinOut > 0) {{ ai.spinOut--; ai.mesh.rotation.y += 0.3; return; }}

                ai.posProgress += (ai.speed / 2400);
                if (ai.posProgress >= 1.0) ai.posProgress -= 1.0;

                const targetPt = trackCurve.getPointAt((ai.posProgress + 0.02) % 1.0);
                const currentPt = trackCurve.getPointAt(ai.posProgress % 1.0);
                
                ai.mesh.position.copy(currentPt);
                ai.mesh.lookAt(targetPt);
                ai.wheels.forEach(w => w.rotation.x += 0.3);
            }});
        }}

        // --- 아이템 Box & 바나나 ---
        function updateProjectilesAndItems() {{
            itemBoxes.forEach(box => {{
                if (box.userData.active) {{
                    box.rotation.y += 0.03;
                    if (playerKart.mesh.position.distanceTo(box.position) < 2.5) {{
                        box.userData.active = false; box.visible = false; box.userData.respawnTimer = 280;
                        getRandomItem(); playSound('item');
                    }}
                }} else {{
                    box.userData.respawnTimer--;
                    if (box.userData.respawnTimer <= 0) {{ box.userData.active = true; box.visible = true; }}
                }}
            }});

            bananas.forEach((b, idx) => {{
                if (playerKart.mesh.position.distanceTo(b.position) < 1.8) {{
                    playerKart.spinOut = 45; playSound('hit');
                    scene.remove(b); bananas.splice(idx, 1);
                }}
            }});
        }}

        function getRandomItem() {{
            const items = ['MUSHROOM', 'BANANA', 'LIGHTNING'];
            const icons = {{ 'MUSHROOM': '🍄', 'BANANA': '🍌', 'LIGHTNING': '⚡' }};
            const pick = items[Math.floor(Math.random() * items.length)];
            currentItem = pick;
            document.getElementById('item-slot').innerText = icons[pick];
        }}

        // --- 순위 판정 ---
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

        // --- 카메라 시점 ---
        function updateCamera() {{
            const pPos = playerKart.mesh.position;
            const pQuat = playerKart.mesh.quaternion;

            if (cameraMode === 0) {{
                const offset = new THREE.Vector3(0, 5.5, -12.5).applyQuaternion(pQuat);
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

        // --- 축소된 110px 컴팩트 미니맵 ---
        function drawMinimap() {{
            const canvas = document.getElementById('minimap-canvas');
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, 110, 110);

            const scale = 0.24;
            const centerX = 55, centerY = 55;

            // 트랙 라인
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.6)';
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

            // AI 위치
            aiKarts.forEach(ai => {{
                const x = centerX + ai.mesh.position.x * scale;
                const y = centerY + ai.mesh.position.z * scale;
                ctx.fillStyle = '#ff0055';
                ctx.beginPath(); ctx.arc(x, y, 3, 0, Math.PI*2); ctx.fill();
            }});

            // 플레이어 위치
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
