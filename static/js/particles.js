/* ═══════════════════════════════════════════════════════════════════
   PARTICLES / CONSTELLATION ANIMATION
   Geometric network lines with dots — matches the reference design
   ═══════════════════════════════════════════════════════════════════ */

(function () {
    const canvas = document.getElementById('particles-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let width, height;
    let particles = [];
    let mouse = { x: null, y: null };
    let animationId;

    // ── Configuration ──────────────────────────────────────────
    const CONFIG = {
        particleCount: 80,
        particleSize: { min: 1.5, max: 3.5 },
        speed: { min: 0.15, max: 0.5 },
        connectionDistance: 160,
        mouseRadius: 200,
        lineColor: 'rgba(180, 180, 180,',      // gray lines
        dotColor: 'rgba(160, 160, 160,',        // gray dots
        accentColor: 'rgba(245, 166, 35,',      // orange accent near mouse
    };

    // ── Resize Handler ─────────────────────────────────────────
    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }

    // ── Particle Class ─────────────────────────────────────────
    class Particle {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.size = CONFIG.particleSize.min + Math.random() * (CONFIG.particleSize.max - CONFIG.particleSize.min);
            this.speedX = (Math.random() - 0.5) * (CONFIG.speed.max - CONFIG.speed.min) + (Math.random() > 0.5 ? CONFIG.speed.min : -CONFIG.speed.min);
            this.speedY = (Math.random() - 0.5) * (CONFIG.speed.max - CONFIG.speed.min) + (Math.random() > 0.5 ? CONFIG.speed.min : -CONFIG.speed.min);
            this.opacity = 0.3 + Math.random() * 0.5;
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;

            // Wrap around edges
            if (this.x < -10) this.x = width + 10;
            if (this.x > width + 10) this.x = -10;
            if (this.y < -10) this.y = height + 10;
            if (this.y > height + 10) this.y = -10;

            // Mouse interaction — subtle push
            if (mouse.x !== null) {
                const dx = this.x - mouse.x;
                const dy = this.y - mouse.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < CONFIG.mouseRadius) {
                    const force = (CONFIG.mouseRadius - dist) / CONFIG.mouseRadius * 0.3;
                    this.x += (dx / dist) * force;
                    this.y += (dy / dist) * force;
                }
            }
        }

        draw() {
            const nearMouse = this._nearMouse();
            const color = nearMouse ? CONFIG.accentColor : CONFIG.dotColor;
            const opacity = nearMouse ? Math.min(this.opacity + 0.3, 1) : this.opacity;

            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = color + opacity + ')';
            ctx.fill();
        }

        _nearMouse() {
            if (mouse.x === null) return false;
            const dx = this.x - mouse.x;
            const dy = this.y - mouse.y;
            return Math.sqrt(dx * dx + dy * dy) < CONFIG.mouseRadius;
        }
    }

    // ── Initialize Particles ───────────────────────────────────
    function init() {
        particles = [];
        for (let i = 0; i < CONFIG.particleCount; i++) {
            particles.push(new Particle());
        }
    }

    // ── Draw Connections ───────────────────────────────────────
    function drawConnections() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < CONFIG.connectionDistance) {
                    const opacity = (1 - dist / CONFIG.connectionDistance) * 0.35;
                    const nearMouse = particles[i]._nearMouse() || particles[j]._nearMouse();
                    const color = nearMouse ? CONFIG.accentColor : CONFIG.lineColor;

                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = color + opacity + ')';
                    ctx.lineWidth = nearMouse ? 1.2 : 0.7;
                    ctx.stroke();
                }
            }
        }

        // Connect particles to mouse
        if (mouse.x !== null) {
            for (let i = 0; i < particles.length; i++) {
                const dx = particles[i].x - mouse.x;
                const dy = particles[i].y - mouse.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < CONFIG.mouseRadius) {
                    const opacity = (1 - dist / CONFIG.mouseRadius) * 0.25;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(mouse.x, mouse.y);
                    ctx.strokeStyle = CONFIG.accentColor + opacity + ')';
                    ctx.lineWidth = 0.8;
                    ctx.stroke();
                }
            }
        }
    }

    // ── Animation Loop ─────────────────────────────────────────
    function animate() {
        ctx.clearRect(0, 0, width, height);

        particles.forEach(p => {
            p.update();
            p.draw();
        });

        drawConnections();
        animationId = requestAnimationFrame(animate);
    }

    // ── Event Listeners ────────────────────────────────────────
    window.addEventListener('resize', () => {
        resize();
    });

    window.addEventListener('mousemove', (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });

    window.addEventListener('mouseleave', () => {
        mouse.x = null;
        mouse.y = null;
    });

    // Touch support
    window.addEventListener('touchmove', (e) => {
        mouse.x = e.touches[0].clientX;
        mouse.y = e.touches[0].clientY;
    });

    window.addEventListener('touchend', () => {
        mouse.x = null;
        mouse.y = null;
    });

    // ── Start ──────────────────────────────────────────────────
    resize();
    init();
    animate();
})();
