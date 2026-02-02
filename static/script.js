// Basic interactivity for LifeLens
document.addEventListener('DOMContentLoaded', () => {
    // --- Pomodoro Timer Logic ---
    let timerInterval;
    let timeLeft = 25 * 60; // 25 minutes
    let isRunning = false;
    let startTime;

    const timerDisplay = document.getElementById('timer');
    const startBtn = document.getElementById('startTimer');
    const pauseBtn = document.getElementById('pauseTimer');
    const resetBtn = document.getElementById('resetTimer');
    const sessionMsg = document.getElementById('sessionMessage');

    function updateTimerDisplay() {
        const mins = Math.floor(timeLeft / 60);
        const secs = timeLeft % 60;
        timerDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        document.title = `(${timerDisplay.textContent}) LifeLens`;
    }

    function startTimer() {
        if (!isRunning) {
            isRunning = true;
            if (!startTime) startTime = new Date();

            startBtn.style.display = 'none';
            pauseBtn.style.display = 'inline-block';
            resetBtn.style.display = 'inline-block';
            sessionMsg.style.display = 'block';

            timerInterval = setInterval(() => {
                timeLeft--;
                updateTimerDisplay();
                if (timeLeft <= 0) {
                    clearInterval(timerInterval);
                    timerFinished();
                }
            }, 1000);
        }
    }

    function pauseTimer() {
        isRunning = false;
        clearInterval(timerInterval);
        startBtn.textContent = 'Resume Session';
        startBtn.style.display = 'inline-block';
        pauseBtn.style.display = 'none';
        sessionMsg.textContent = 'Session Paused';
    }

    function resetTimer() {
        clearInterval(timerInterval);
        isRunning = false;
        timeLeft = 25 * 60;
        startTime = null;
        updateTimerDisplay();
        startBtn.textContent = 'Start Focus Session';
        startBtn.style.display = 'inline-block';
        pauseBtn.style.display = 'none';
        resetBtn.style.display = 'none';
        sessionMsg.style.display = 'none';
        sessionMsg.textContent = 'Focusing... Keep your phone away!';
        document.title = 'LifeLens — Personal Productivity Time Tracker';
    }

    function timerFinished() {
        isRunning = false;
        startBtn.style.display = 'inline-block';
        pauseBtn.style.display = 'none';
        sessionMsg.textContent = 'Session Complete! Well done.';

        const audio = new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg');
        audio.play().catch(e => console.log("Audio play failed: ", e));

        if (confirm('Great job! Would you like to log this 25-minute focus session?')) {
            const now = new Date();
            const startStr = startTime.getHours().toString().padStart(2, '0') + ':' + startTime.getMinutes().toString().padStart(2, '0');
            const endStr = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');

            // Auto-fill form if present
            const nameInput = document.getElementsByName('activity_name')[0];
            if (nameInput) {
                nameInput.value = 'Focus Session';
                document.getElementsByName('category')[0].value = 'productive';
                document.getElementsByName('start_time')[0].value = startStr;
                document.getElementsByName('end_time')[0].value = endStr;
                document.querySelector('.activity-form').scrollIntoView({ behavior: 'smooth' });
            } else {
                window.location.href = '/add_activity_page';
            }
        }
        resetTimer();
    }

    if (startBtn) {
        startBtn.addEventListener('click', startTimer);
        pauseBtn.addEventListener('click', pauseTimer);
        resetBtn.addEventListener('click', resetTimer);
    }

    // --- Theme Toggle ---
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;

    // Check for saved theme
    if (localStorage.getItem('theme') === 'dark') {
        body.classList.add('dark-mode');
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            const mode = body.classList.contains('dark-mode') ? 'dark' : 'light';
            localStorage.setItem('theme', mode);
        });
    }

    // --- Alert Auto-dismiss ---
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});
