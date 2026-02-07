/**
 * Galactic Dodge Classic
 * A classic arcade game where you dodge asteroids
 */

class Game {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');

        // Set canvas size
        this.canvas.width = 600;
        this.canvas.height = 700;

        // Game state
        this.isRunning = false;
        this.score = 0;
        this.highScore = parseInt(localStorage.getItem('galacticDodgeHighScore')) || 0;
        this.difficulty = 1;
        this.lastTime = 0;

        // Player
        this.player = {
            x: this.canvas.width / 2,
            y: this.canvas.height - 80,
            width: 50,
            height: 40,
            speed: 350,
            targetX: this.canvas.width / 2
        };

        // Input state
        this.keys = {
            left: false,
            right: false
        };

        // Asteroids
        this.asteroids = [];
        this.asteroidSpawnTimer = 0;
        this.asteroidSpawnInterval = 800; // ms

        // Stars (background)
        this.stars = [];
        this.initStars();

        // UI elements
        this.startScreen = document.getElementById('startScreen');
        this.gameOverScreen = document.getElementById('gameOverScreen');
        this.hud = document.getElementById('hud');
        this.scoreDisplay = document.getElementById('score');
        this.highScoreDisplay = document.getElementById('highScore');
        this.finalScoreDisplay = document.getElementById('finalScore');
        this.highScoreTextDisplay = document.getElementById('highScoreText');

        // Update high score display
        this.highScoreDisplay.textContent = this.highScore;

        // Bind events
        this.bindEvents();

        // Start render loop for background
        this.renderBackground();
    }

    initStars() {
        for (let i = 0; i < 100; i++) {
            this.stars.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                size: Math.random() * 2 + 0.5,
                speed: Math.random() * 50 + 20
            });
        }
    }

    bindEvents() {
        // Keyboard events
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft' || e.key === 'a') {
                this.keys.left = true;
            }
            if (e.key === 'ArrowRight' || e.key === 'd') {
                this.keys.right = true;
            }
        });

        document.addEventListener('keyup', (e) => {
            if (e.key === 'ArrowLeft' || e.key === 'a') {
                this.keys.left = false;
            }
            if (e.key === 'ArrowRight' || e.key === 'd') {
                this.keys.right = false;
            }
        });

        // Mouse events
        this.canvas.addEventListener('mousemove', (e) => {
            if (this.isRunning) {
                const rect = this.canvas.getBoundingClientRect();
                this.player.targetX = e.clientX - rect.left;
            }
        });

        this.canvas.addEventListener('touchmove', (e) => {
            if (this.isRunning) {
                e.preventDefault();
                const rect = this.canvas.getBoundingClientRect();
                this.player.targetX = e.touches[0].clientX - rect.left;
            }
        }, { passive: false });

        // Button events
        document.getElementById('startButton').addEventListener('click', () => this.start());
        document.getElementById('restartButton').addEventListener('click', () => this.start());
    }

    start() {
        // Reset game state
        this.isRunning = true;
        this.score = 0;
        this.difficulty = 1;
        this.asteroids = [];
        this.asteroidSpawnTimer = 0;
        this.asteroidSpawnInterval = 800;
        this.player.x = this.canvas.width / 2;
        this.player.targetX = this.canvas.width / 2;
        this.lastTime = performance.now();

        // Update UI
        this.startScreen.classList.add('hidden');
        this.gameOverScreen.classList.add('hidden');
        this.hud.classList.remove('hidden');
        this.scoreDisplay.textContent = '0';

        // Start game loop
        this.gameLoop(this.lastTime);
    }

    gameOver() {
        this.isRunning = false;

        // Update high score
        if (this.score > this.highScore) {
            this.highScore = this.score;
            localStorage.setItem('galacticDodgeHighScore', this.highScore);
            this.highScoreDisplay.textContent = this.highScore;
        }

        // Update UI
        this.gameOverScreen.classList.remove('hidden');
        this.hud.classList.add('hidden');
        this.finalScoreDisplay.textContent = `Score: ${Math.floor(this.score)}`;
        this.highScoreTextDisplay.textContent = `High Score: ${this.highScore}`;

        // Continue background animation
        this.renderBackground();
    }

    gameLoop(currentTime) {
        if (!this.isRunning) return;

        const deltaTime = (currentTime - this.lastTime) / 1000;
        this.lastTime = currentTime;

        this.update(deltaTime);
        this.render();

        requestAnimationFrame((time) => this.gameLoop(time));
    }

    update(deltaTime) {
        // Update score based on survival time
        this.score += deltaTime * 100;
        this.scoreDisplay.textContent = Math.floor(this.score);

        // Increase difficulty every 500 points
        const newDifficulty = 1 + Math.floor(this.score / 500) * 0.2;
        if (newDifficulty !== this.difficulty) {
            this.difficulty = newDifficulty;
            this.asteroidSpawnInterval = Math.max(200, 800 - (this.difficulty - 1) * 100);
        }

        // Update player position (smooth movement towards target)
        if (this.keys.left) {
            this.player.targetX -= this.player.speed * deltaTime;
        }
        if (this.keys.right) {
            this.player.targetX += this.player.speed * deltaTime;
        }

        // Smooth interpolation
        const diff = this.player.targetX - this.player.x;
        this.player.x += diff * 10 * deltaTime;

        // Clamp player position
        this.player.x = Math.max(this.player.width / 2,
                                Math.min(this.canvas.width - this.player.width / 2,
                                        this.player.x));

        // Update target X bounds
        this.player.targetX = Math.max(this.player.width / 2,
                                      Math.min(this.canvas.width - this.player.width / 2,
                                              this.player.targetX));

        // Spawn asteroids
        this.asteroidSpawnTimer += deltaTime * 1000;
        if (this.asteroidSpawnTimer >= this.asteroidSpawnInterval) {
            this.spawnAsteroid();
            this.asteroidSpawnTimer = 0;
        }

        // Update asteroids
        for (let i = this.asteroids.length - 1; i >= 0; i--) {
            const asteroid = this.asteroids[i];
            asteroid.y += asteroid.speed * this.difficulty * deltaTime;
            asteroid.rotation += asteroid.rotationSpeed * deltaTime;

            // Check collision with player
            if (this.checkCollision(asteroid)) {
                this.gameOver();
                return;
            }

            // Remove off-screen asteroids
            if (asteroid.y > this.canvas.height + asteroid.size) {
                this.asteroids.splice(i, 1);
            }
        }

        // Update stars
        for (const star of this.stars) {
            star.y += star.speed * deltaTime;
            if (star.y > this.canvas.height) {
                star.y = 0;
                star.x = Math.random() * this.canvas.width;
            }
        }
    }

    spawnAsteroid() {
        const size = Math.random() * 30 + 15; // 15-45 pixels
        const x = Math.random() * (this.canvas.width - size * 2) + size;

        this.asteroids.push({
            x: x,
            y: -size,
            size: size,
            speed: Math.random() * 100 + 150, // 150-250 pixels per second
            rotation: Math.random() * Math.PI * 2,
            rotationSpeed: (Math.random() - 0.5) * 4,
            vertices: this.generateAsteroidVertices()
        });
    }

    generateAsteroidVertices() {
        const numVertices = Math.floor(Math.random() * 4) + 6; // 6-9 vertices
        const vertices = [];

        for (let i = 0; i < numVertices; i++) {
            const angle = (i / numVertices) * Math.PI * 2;
            const radius = 0.7 + Math.random() * 0.3; // 0.7-1.0 of the size
            vertices.push({ angle, radius });
        }

        return vertices;
    }

    checkCollision(asteroid) {
        // Simple circle-based collision
        const playerRadius = this.player.width / 2;
        const dx = this.player.x - asteroid.x;
        const dy = (this.player.y + this.player.height / 2) - asteroid.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        // Use a slightly smaller radius for more forgiving hit detection
        return distance < (playerRadius * 0.7 + asteroid.size * 0.7);
    }

    render() {
        // Clear canvas
        this.ctx.fillStyle = '#0c0c1e';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw stars
        this.ctx.fillStyle = '#ffffff';
        for (const star of this.stars) {
            this.ctx.globalAlpha = 0.3 + star.size * 0.3;
            this.ctx.beginPath();
            this.ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
            this.ctx.fill();
        }
        this.ctx.globalAlpha = 1;

        // Draw asteroids
        for (const asteroid of this.asteroids) {
            this.drawAsteroid(asteroid);
        }

        // Draw player spaceship
        this.drawPlayer();
    }

    renderBackground() {
        if (this.isRunning) return;

        // Clear and draw animated background
        this.ctx.fillStyle = '#0c0c1e';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Update and draw stars
        const deltaTime = 0.016; // Approximate for 60fps
        for (const star of this.stars) {
            star.y += star.speed * deltaTime;
            if (star.y > this.canvas.height) {
                star.y = 0;
                star.x = Math.random() * this.canvas.width;
            }

            this.ctx.globalAlpha = 0.3 + star.size * 0.3;
            this.ctx.fillStyle = '#ffffff';
            this.ctx.beginPath();
            this.ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
            this.ctx.fill();
        }
        this.ctx.globalAlpha = 1;

        requestAnimationFrame(() => this.renderBackground());
    }

    drawAsteroid(asteroid) {
        this.ctx.save();
        this.ctx.translate(asteroid.x, asteroid.y);
        this.ctx.rotate(asteroid.rotation);

        // Draw asteroid body
        this.ctx.fillStyle = '#8b7355';
        this.ctx.strokeStyle = '#6b5345';
        this.ctx.lineWidth = 2;

        this.ctx.beginPath();
        for (let i = 0; i < asteroid.vertices.length; i++) {
            const vertex = asteroid.vertices[i];
            const x = Math.cos(vertex.angle) * asteroid.size * vertex.radius;
            const y = Math.sin(vertex.angle) * asteroid.size * vertex.radius;

            if (i === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        }
        this.ctx.closePath();
        this.ctx.fill();
        this.ctx.stroke();

        // Add some crater details
        this.ctx.fillStyle = '#6b5345';
        for (let i = 0; i < 3; i++) {
            const craterX = (Math.random() - 0.5) * asteroid.size * 0.6;
            const craterY = (Math.random() - 0.5) * asteroid.size * 0.6;
            const craterSize = Math.random() * asteroid.size * 0.15 + 2;
            this.ctx.beginPath();
            this.ctx.arc(craterX, craterY, craterSize, 0, Math.PI * 2);
            this.ctx.fill();
        }

        this.ctx.restore();
    }

    drawPlayer() {
        const x = this.player.x;
        const y = this.player.y;
        const width = this.player.width;
        const height = this.player.height;

        this.ctx.save();

        // Engine glow
        const gradient = this.ctx.createRadialGradient(
            x, y + height / 2, 0,
            x, y + height / 2, width
        );
        gradient.addColorStop(0, 'rgba(74, 158, 255, 0.8)');
        gradient.addColorStop(0.5, 'rgba(74, 158, 255, 0.3)');
        gradient.addColorStop(1, 'rgba(74, 158, 255, 0)');
        this.ctx.fillStyle = gradient;
        this.ctx.beginPath();
        this.ctx.arc(x, y + height / 2, width, 0, Math.PI * 2);
        this.ctx.fill();

        // Main body
        this.ctx.fillStyle = '#4a9eff';
        this.ctx.strokeStyle = '#2d7dd2';
        this.ctx.lineWidth = 2;

        this.ctx.beginPath();
        this.ctx.moveTo(x, y - height / 2); // Top
        this.ctx.lineTo(x + width / 2, y + height / 2); // Bottom right
        this.ctx.lineTo(x, y + height / 4); // Center indent
        this.ctx.lineTo(x - width / 2, y + height / 2); // Bottom left
        this.ctx.closePath();
        this.ctx.fill();
        this.ctx.stroke();

        // Cockpit
        this.ctx.fillStyle = '#b8e0ff';
        this.ctx.beginPath();
        this.ctx.ellipse(x, y, 8, 12, 0, 0, Math.PI * 2);
        this.ctx.fill();

        // Wings
        this.ctx.fillStyle = '#2d7dd2';
        this.ctx.beginPath();
        this.ctx.moveTo(x - width / 2, y + height / 4);
        this.ctx.lineTo(x - width / 2 - 10, y + height / 2 + 5);
        this.ctx.lineTo(x - width / 4, y + height / 2);
        this.ctx.closePath();
        this.ctx.fill();

        this.ctx.beginPath();
        this.ctx.moveTo(x + width / 2, y + height / 4);
        this.ctx.lineTo(x + width / 2 + 10, y + height / 2 + 5);
        this.ctx.lineTo(x + width / 4, y + height / 2);
        this.ctx.closePath();
        this.ctx.fill();

        this.ctx.restore();
    }
}

// Initialize game when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new Game();
});
