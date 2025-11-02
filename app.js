class TelegramWebApp {
    constructor() {
        this.tg = window.Telegram.WebApp;
        this.user = null;
        this.currentTask = null;
        this.init();
    }

    init() {
        this.tg.expand();
        this.user = this.tg.initDataUnsafe.user;
        
        this.loadUserData();
        this.setupEventListeners();
        this.loadTasks();
    }

    async loadUserData() {
        try {
            const response = await fetch(`/api/user/${this.user.id}`);
            const userData = await response.json();
            
            document.getElementById('balance').textContent = `$${userData.balance}`;
            document.getElementById('profile-uid').textContent = userData.user_id;
            document.getElementById('profile-username').textContent = userData.username;
            document.getElementById('profile-balance').textContent = `$${userData.balance}`;
        } catch (error) {
            console.error('Error loading user data:', error);
        }
    }

    async loadTasks() {
        try {
            const response = await fetch('/api/tasks');
            const tasks = await response.json();
            this.renderTasks(tasks);
        } catch (error) {
            console.error('Error loading tasks:', error);
        }
    }

    renderTasks(tasks) {
        const tasksList = document.getElementById('tasks-list');
        tasksList.innerHTML = '';

        tasks.forEach(task => {
            const taskElement = document.createElement('div');
            taskElement.className = 'task-card';
            taskElement.innerHTML = `
                <h4>${task.title}</h4>
                <p>${task.description}</p>
                <div class="task-reward">Reward: $${task.reward}</div>
            `;
            taskElement.addEventListener('click', () => this.openTaskModal(task));
            tasksList.appendChild(taskElement);
        });
    }

    openTaskModal(task) {
        this.currentTask = task;
        document.getElementById('modal-task-title').textContent = task.title;
        document.getElementById('modal-task-desc').textContent = task.description;
        document.getElementById('modal-task-reward').textContent = task.reward;
        document.getElementById('task-modal').style.display = 'block';
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.dataset.tab;
                this.switchTab(tab);
            });
        });

        // Task submission
        document.getElementById('submit-task').addEventListener('click', () => {
            this.submitTask();
        });

        // Payout submission
        document.getElementById('submit-payout').addEventListener('click', () => {
            this.submitPayout();
        });

        // Modal close
        document.querySelector('.close').addEventListener('click', () => {
            document.getElementById('task-modal').style.display = 'none';
        });
    }

    switchTab(tabName) {
        // Remove active class from all tabs and buttons
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Add active class to current tab and button
        document.getElementById(`${tabName}-tab`).classList.add('active');
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    }

    async submitTask() {
        const proofText = document.getElementById('proof-text').value;
        
        if (!proofText) {
            alert('Please enter proof text');
            return;
        }

        try {
            const response = await fetch('/api/submit-task', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.user.id,
                    task_id: this.currentTask.id,
                    proof_text: proofText
                })
            });

            if (response.ok) {
                alert('Task submitted successfully! Wait for admin review.');
                document.getElementById('task-modal').style.display = 'none';
                document.getElementById('proof-text').value = '';
            } else {
                alert('Error submitting task');
            }
        } catch (error) {
            console.error('Error submitting task:', error);
            alert('Error submitting task');
        }
    }

    async submitPayout() {
        const amount = parseFloat(document.getElementById('payout-amount').value);
        const usdtAddress = document.getElementById('usdt-address').value;

        if (!amount || amount < 1) {
            alert('Minimum payout amount is $1');
            return;
        }

        if (!usdtAddress) {
            alert('Please enter USDT address');
            return;
        }

        try {
            const response = await fetch('/api/payout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.user.id,
                    amount: amount,
                    usdt_address: usdtAddress
                })
            });

            const result = await response.json();

            if (response.ok) {
                alert('Payout request submitted successfully!');
                document.getElementById('payout-amount').value = '';
                document.getElementById('usdt-address').value = '';
                this.loadUserData(); // Update balance
            } else {
                alert(result.error || 'Error submitting payout');
            }
        } catch (error) {
            console.error('Error submitting payout:', error);
            alert('Error submitting payout');
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TelegramWebApp();
});
