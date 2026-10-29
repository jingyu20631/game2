import streamlit as st
import streamlit.components.v1 as components

# Set page layout to wide and title
st.set_page_config(
    page_title="Streamlit 2D Racing Game",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling Streamlit UI
st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stAppHeader {
        background-color: rgba(15, 23, 42, 0.8);
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar controls & information
with st.sidebar:
    st.title("🏎️ Dash Kart 2D")
    st.markdown("Welcome to the **Streamlit 2D Top-Down Racing Game**!")
    
    st.subheader("🎮 Controls")
    st.markdown("""
    - **Up Arrow / W**: Accelerate
    - **Down Arrow / S**: Reverse / Brake
    - **Left Arrow / A**: Steer Left
    - **Right Arrow / D**: Steer Right
    - **R Key**: Quick Restart Game
    """)
    
    st.subheader("⚙️ Settings")
    laps_to_win = st.slider("Total Laps", min_value=1, max_value=10, value=3, step=1)
    difficulty = st.selectbox("Game Speed / Difficulty", ["Easy", "Medium", "Hard"], index=1)
    
    speed_multiplier = 1.0
    if difficulty == "Easy":
        speed_multiplier = 0.8
    elif difficulty == "Hard":
        speed_multiplier = 1.25

    st.markdown("---")
    st.caption("Built with Python, Streamlit & HTML5 Canvas JS")

st.title("🏎️ Top-Down Mario Kart Style Racing")
st.write("Use your arrow keys or WASD to navigate the track, complete the target laps, and set a high score!")

# HTML/JS Game Code embedded into Streamlit Component
game_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            user-select: none;
        }}
        body {{
            background-color: #0f172a;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
            overflow: hidden;
        }}
        #game-container {{
            position: relative;
            margin-top: 10px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.4);
            border-radius: 12px;
            overflow: hidden;
            border: 3px solid #334155;
        }}
        canvas {{
            display: block;
            background: #1e293b;
        }}
        #hud {{
            position: absolute;
            top: 15px;
            left: 15px;
            right: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            pointer-events: none;
        }}
        .hud-card {{
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(8px);
            padding: 8px 16px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            font-weight: bold;
            font-size: 16px;
            letter-spacing: 0.5px;
            color: #f1f5f9;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        }}
        .hud-value {{
            color: #38bdf8;
            font-size: 20px;
        }}
        #game-over-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 23, 42, 0.85);
            display: none;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            backdrop-filter: blur(4px);
        }}
        #game-over-overlay h1 {{
            font-size: 42px;
            color: #4ade80;
            margin-bottom: 10px;
            text-shadow: 0 0 10px rgba(74, 222, 128, 0.5);
        }}
        #game-over-overlay p {{
            font-size: 20px;
            margin-bottom: 25px;
            color: #cbd5e1;
        }}
        .btn {{
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: white;
            border: none;
            padding: 12px 28px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(37, 99, 235, 0.6);
            background: linear-gradient(135deg, #3b82f6, #2563eb);
        }}
        .btn:active {{
            transform: translateY(0);
        }}
        #controls-bar {{
            margin-top: 12px;
            display: flex;
            gap: 15px;
        }}
    </style>
</head>
<body>

    <div id="game-container">
        <canvas id="gameCanvas" width="900" height="600"></canvas>
        
        <div id="hud">
            <div class="hud-card">LAP: <span id="lap-display" class="hud-value">1 / {laps_to_win}</span></div>
            <div class="hud-card">TIME: <span id="timer-display" class="hud-value">00:00.00</span></div>
            <div class="hud-card">SPEED: <span id="speed-display" class="hud-value">0 KM/H</span></div>
        </div>

        <div id="game-over-overlay">
            <h1 id="finish-title">VICTORY!</h1>
            <p id="final-time-text">Your Time: 00:00.00</p>
            <button class="btn" onclick="resetGame()">Play Again (R)</button>
        </div>
    </div>

    <div id="controls-bar">
        <button class="btn" onclick="resetGame()">🔄 Reset Race</button>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        // Target settings from Python Streamlit
        const TOTAL_LAPS = {laps_to_win};
        const SPEED_MULT = {speed_multiplier};

        // Track Path Definition (Inner & Outer Boundary Points for Track Rendering & Collision)
        // Outer track loop coordinates
        const trackCenter = [
            {{ x: 150, y: 150 }},
            {{ x: 450, y: 100 }},
            {{ x: 750, y: 150 }},
            {{ x: 780, y: 300 }},
            {{ x: 700, y: 480 }},
            {{ x: 450, y: 520 }},
            {{ x: 200, y: 480 }},
            {{ x: 120, y: 320 }}
        ];

        // Kart State
        let kart = {{
            x: 450,
            y: 130,
            angle: 0,
            speed: 0,
            maxSpeed: 6.5 * SPEED_MULT,
            accel: 0.15 * SPEED_MULT,
            friction: 0.96,
            turnSpeed: 0.05,
            width: 24,
            height: 38,
            currentLap: 1,
            checkpointPassed: false,
            finished: false
        }};

        // Keys state
        const keys = {{
            ArrowUp: false,
            ArrowDown: false,
            ArrowLeft: false,
            ArrowRight: false,
            w: false,
            s: false,
            a: false,
            d: false
        }};

        // Game loop parameters
        let startTime = null;
        let elapsedTime = 0;
        let isRunning = true;
        let animFrameId = null;

        // Checkpoint & Finish Line Line definitions
        const finishLine = {{ x1: 450, y1: 80, x2: 450, y2: 180 }};
        const midCheckpoint = {{ x1: 450, y1: 450, x2: 450, y2: 550 }};

        // Event Listeners for Key Controls
        window.addEventListener('keydown', (e) => {{
            if (e.key in keys) keys[e.key] = true;
            if (e.key.toLowerCase() === 'r') resetGame();
        }});

        window.addEventListener('keyup', (e) => {{
            if (e.key in keys) keys[e.key] = false;
        }});

        function resetGame() {{
            kart.x = 450;
            kart.y = 130;
            kart.angle = Math.PI; // Face Right
            kart.speed = 0;
            kart.currentLap = 1;
            kart.checkpointPassed = false;
            kart.finished = false;

            startTime = performance.now();
            elapsedTime = 0;
            isRunning = true;

            document.getElementById('game-over-overlay').style.display = 'none';
            document.getElementById('lap-display').innerText = `1 / ${{TOTAL_LAPS}}`;
        }}

        // Format Time Output
        function formatTime(ms) {{
            const totalSeconds = ms / 1000;
            const minutes = Math.floor(totalSeconds / 60);
            const seconds = Math.floor(totalSeconds % 60);
            const hundredths = Math.floor((ms % 1000) / 10);
            return `${{String(minutes).padStart(2, '0')}}:${{String(seconds).padStart(2, '0')}}.${{String(hundredths).padStart(2, '0')}}`;
        }}

        // Check distance to track centerline for off-road physics
        function getOffRoadPenalty(x, y) {{
            let minDistance = Infinity;
            for (let i = 0; i < trackCenter.length; i++) {{
                const p1 = trackCenter[i];
                const p2 = trackCenter[(i + 1) % trackCenter.length];
                
                // Point-to-segment distance calculation
                const dist = distToSegment({{x, y}}, p1, p2);
                if (dist < minDistance) minDistance = dist;
            }}
            // Standard track radius is ~55px. If distance > 55px, car is off-road
            return minDistance > 60;
        }}

        function distToSegment(p, v, w) {{
            const l2 = (v.x - w.x)**2 + (v.y - w.y)**2;
            if (l2 === 0) return Math.hypot(p.x - v.x, p.y - v.y);
            let t = ((p.x - v.x) * (w.x - v.x) + (p.y - v.y) * (w.y - w.y)) / l2;
            t = Math.max(0, Math.min(1, t));
            return Math.hypot(p.x - (v.x + t * (w.x - v.x)), p.y - (v.y + t * (w.y - v.y)));
        }}

        // Movement Physics & Collision Update
        function update() {{
            if (kart.finished) return;

            // Timer Calculation
            if (startTime) {{
                elapsedTime = performance.now() - startTime;
                document.getElementById('timer-display').innerText = formatTime(elapsedTime);
            }}

            // Acceleration / Braking
            const accelerating = keys.ArrowUp || keys.w;
            const braking = keys.ArrowDown || keys.s;
            const steerLeft = keys.ArrowLeft || keys.a;
            const steerRight = keys.ArrowRight || keys.d;

            let maxSpd = kart.maxSpeed;
            
            // Apply Off-Road slowdown penalty (Grass / Off-track)
            const isOffRoad = getOffRoadPenalty(kart.x, kart.y);
            if (isOffRoad) {{
                maxSpd *= 0.4; // 60% speed penalty
            }}

            if (accelerating) {{
                kart.speed += kart.accel;
            }} else if (braking) {{
                kart.speed -= kart.accel * 0.8;
            }} else {{
                kart.speed *= kart.friction;
            }}

            // Clamp max speed
            if (kart.speed > maxSpd) kart.speed = maxSpd;
            if (kart.speed < -maxSpd * 0.4) kart.speed = -maxSpd * 0.4;

            // Steering Logic
            if (Math.abs(kart.speed) > 0.1) {{
                const dir = kart.speed > 0 ? 1 : -1;
                if (steerLeft) kart.angle -= kart.turnSpeed * dir;
                if (steerRight) kart.angle += kart.turnSpeed * dir;
            }}

            // Update position
            const nextX = kart.x + Math.sin(kart.angle) * kart.speed;
            const nextY = kart.y - Math.cos(kart.angle) * kart.speed;

            kart.x = nextX;
            kart.y = nextY;

            // Display speed display HUD
            const kmh = Math.round(Math.abs(kart.speed) * 22);
            document.getElementById('speed-display').innerText = `${{kmh}} KM/H`;

            // Checkpoints & Finish Line Checks
            // Check Mid Checkpoint (bottom curve)
            if (!kart.checkpointPassed && Math.hypot(kart.x - 450, kart.y - 500) < 60) {{
                kart.checkpointPassed = true;
            }}

            // Check Finish Line Crossing
            if (kart.checkpointPassed && Math.hypot(kart.x - 450, kart.y - 130) < 55) {{
                kart.checkpointPassed = false;
                kart.currentLap += 1;

                if (kart.currentLap > TOTAL_LAPS) {{
                    kart.finished = true;
                    document.getElementById('finish-title').innerText = "RACE FINISHED! 🏆";
                    document.getElementById('final-time-text').innerText = `Total Time: ${{formatTime(elapsedTime)}}`;
                    document.getElementById('game-over-overlay').style.display = 'flex';
                }} else {{
                    document.getElementById('lap-display').innerText = `${{kart.currentLap}} / ${{TOTAL_LAPS}}`;
                }}
            }}
        }}

        // Render Canvas Graphics
        function drawTrack() {{
            // Draw Grass background
            ctx.fillStyle = '#15803d';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Draw Off-road sand border track layer
            ctx.beginPath();
            ctx.strokeStyle = '#eab308';
            ctx.lineWidth = 130;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            for (let i = 0; i < trackCenter.length; i++) {{
                const p = trackCenter[i];
                if (i === 0) ctx.moveTo(p.x, p.y);
                else ctx.lineTo(p.x, p.y);
            }}
            ctx.closePath();
            ctx.stroke();

            // Draw Main Asphalt Track Road
            ctx.beginPath();
            ctx.strokeStyle = '#334155';
            ctx.lineWidth = 110;
            for (let i = 0; i < trackCenter.length; i++) {{
                const p = trackCenter[i];
                if (i === 0) ctx.moveTo(p.x, p.y);
                else ctx.lineTo(p.x, p.y);
            }}
            ctx.closePath();
            ctx.stroke();

            // Draw Dashed Center White Line
            ctx.beginPath();
            ctx.strokeStyle = '#f8fafc';
            ctx.lineWidth = 4;
            ctx.setLineDash([15, 15]);
            for (let i = 0; i < trackCenter.length; i++) {{
                const p = trackCenter[i];
                if (i === 0) ctx.moveTo(p.x, p.y);
                else ctx.lineTo(p.x, p.y);
            }}
            ctx.closePath();
            ctx.stroke();
            ctx.setLineDash([]); // Reset line dash

            // Draw Checkered Finish Line
            ctx.save();
            ctx.translate(450, 130);
            ctx.fillStyle = '#ffffff';
            for (let i = -50; i < 50; i += 10) {{
                ctx.fillStyle = (Math.floor(i / 10) % 2 === 0) ? '#ffffff' : '#000000';
                ctx.fillRect(0, i, 12, 10);
            }}
            ctx.restore();
        }}

        function drawKart() {{
            ctx.save();
            ctx.translate(kart.x, kart.y);
            ctx.rotate(kart.angle);

            // Kart Tires
            ctx.fillStyle = '#0f172a';
            ctx.fillRect(-14, -16, 6, 10); // Top left tire
            ctx.fillRect(8, -16, 6, 10);  // Top right tire
            ctx.fillRect(-14, 8, 6, 12);  // Bottom left tire
            ctx.fillRect(8, 8, 6, 12);   // Bottom right tire

            // Kart Main Body
            ctx.fillStyle = '#ef4444'; // Mario Red Body
            ctx.beginPath();
            ctx.roundRect(-10, -18, 20, 34, 6);
            ctx.fill();

            // Front Wing
            ctx.fillStyle = '#dc2626';
            ctx.fillRect(-12, -20, 24, 5);

            // Driver Helmet
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(0, -2, 7, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = '#2563eb'; // Blue Cap detail
            ctx.beginPath();
            ctx.arc(0, -4, 4, 0, Math.PI * 2);
            ctx.fill();

            ctx.restore();
        }}

        function render() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawTrack();
            drawKart();
        }}

        function gameLoop() {{
            update();
            render();
            animFrameId = requestAnimationFrame(gameLoop);
        }}

        // Initialization
        resetGame();
        gameLoop();
    </script>
</body>
</html>
"""

# Render embedded component in Streamlit page
components.html(game_html, height=720, scrolling=False)
