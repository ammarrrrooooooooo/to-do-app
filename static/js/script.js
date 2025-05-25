document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const tasksList = document.getElementById('tasksList');
    const taskModal = document.getElementById('taskModal');
    const taskForm = document.getElementById('taskForm');
    const addTaskBtn = document.getElementById('addTaskBtn');
    const closeModalBtn = document.getElementById('closeModal');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const searchInput = document.getElementById('searchTasks');
    const sortSelect = document.getElementById('sortTasks');
    const resetFormBtn = document.getElementById('resetForm');
    const confirmModal = document.getElementById('confirmModal');
    const confirmYesBtn = document.getElementById('confirmYes');
    const confirmNoBtn = document.getElementById('confirmNo');

    // State
    let currentFilter = 'all';
    let currentSort = 'date-desc';
    let searchQuery = '';
    let pendingAction = null;

    // Load tasks on page load
    loadTasks();
    updateStatistics();

    // Event Listeners
    addTaskBtn.addEventListener('click', () => openModal());
    closeModalBtn.addEventListener('click', closeModal);
    taskForm.addEventListener('submit', handleAddTask);
    resetFormBtn.addEventListener('click', () => taskForm.reset());
    filterBtns.forEach(btn => btn.addEventListener('click', handleFilterChange));
    searchInput.addEventListener('input', debounce(handleSearch, 300));
    sortSelect.addEventListener('change', handleSort);
    confirmNoBtn.addEventListener('click', closeConfirmModal);
    confirmYesBtn.addEventListener('click', handleConfirmAction);

    // Close modals when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === taskModal) closeModal();
        if (e.target === confirmModal) closeConfirmModal();
    });

    function openModal(taskId = null) {
        const modalTitle = document.getElementById('modalTitle');
        if (taskId) {
            modalTitle.textContent = 'تعديل المهمة';
            loadTaskForEdit(taskId);
        } else {
            modalTitle.textContent = 'إضافة مهمة جديدة';
            taskForm.reset();
            document.getElementById('taskId').value = '';
        }
        taskModal.style.display = 'block';
    }

    function closeModal() {
        taskModal.style.display = 'none';
        taskForm.reset();
        document.getElementById('taskId').value = '';
    }

    function openConfirmModal(message, action) {
        document.getElementById('confirmMessage').textContent = message;
        confirmModal.style.display = 'block';
        pendingAction = action;
    }

    function closeConfirmModal() {
        confirmModal.style.display = 'none';
        pendingAction = null;
    }

    function handleConfirmAction() {
        if (pendingAction) {
            pendingAction();
            closeConfirmModal();
        }
    }

    async function loadTaskForEdit(taskId) {
        try {
            const response = await fetch(`/api/tasks/${taskId}`);
            const task = await response.json();
            
            document.getElementById('taskId').value = task.id;
            document.getElementById('title').value = task.title;
            document.getElementById('description').value = task.description;
            document.getElementById('due_date').value = task.due_date;
            document.getElementById('priority').value = task.priority;
            document.getElementById('tags').value = task.tags.join(', ');
        } catch (error) {
            console.error('Error loading task for edit:', error);
            showError('حدث خطأ أثناء تحميل بيانات المهمة');
        }
    }

    async function loadTasks() {
        try {
            const url = new URL('/api/tasks', window.location.origin);
            if (currentFilter !== 'all') url.searchParams.append('status', currentFilter);
            if (searchQuery) url.searchParams.append('search', searchQuery);
            if (currentSort) url.searchParams.append('sort', currentSort);
            
            const response = await fetch(url);
            const tasks = await response.json();
            renderTasks(tasks);
            updateStatistics();
        } catch (error) {
            console.error('Error loading tasks:', error);
            showError('حدث خطأ أثناء تحميل المهام');
        }
    }

    async function updateStatistics() {
        try {
            const response = await fetch('/api/statistics');
            const stats = await response.json();
            
            document.getElementById('activeTasks').textContent = stats.active_tasks;
            document.getElementById('completedTasks').textContent = stats.completed_tasks;
            document.getElementById('totalTasks').textContent = stats.total_tasks;
            
            const progressBar = document.getElementById('taskProgress');
            progressBar.style.width = `${stats.completion_rate}%`;
            progressBar.textContent = `${stats.completion_rate}%`;
        } catch (error) {
            console.error('Error updating statistics:', error);
        }
    }

    function renderTasks(tasks) {
        tasksList.innerHTML = '';
        
        if (tasks.length === 0) {
            tasksList.innerHTML = '<div class="no-tasks">لا توجد مهام</div>';
            return;
        }

        tasks.forEach(task => {
            const taskCard = document.createElement('div');
            taskCard.className = 'task-card';
            taskCard.setAttribute('data-priority', task.priority);
            taskCard.setAttribute('data-id', task.id);
            
            const dueDate = new Date(task.due_date);
            const isOverdue = task.status === 'Pending' && dueDate < new Date();
            
            taskCard.innerHTML = `
                <div class="task-header">
                    <h3 class="task-title">${task.title}</h3>
                    <span class="task-priority priority-${task.priority.toLowerCase()}">
                        <i class="fas fa-flag"></i> ${getPriorityText(task.priority)}
                    </span>
                </div>
                <p class="task-description">${task.description}</p>
                <div class="task-meta">
                    <div class="task-tags">
                        ${task.tags.map(tag => `
                            <span class="task-tag">
                                <i class="fas fa-tag"></i> ${tag}
                            </span>
                        `).join('')}
                    </div>
                    ${isOverdue ? '<span class="overdue-badge"><i class="fas fa-exclamation-circle"></i> متأخرة</span>' : ''}
                </div>
                <div class="task-dates">
                    <div><i class="fas fa-calendar-plus"></i> تاريخ الإنشاء: ${formatDate(task.creation_date)}</div>
                    <div><i class="fas fa-calendar-alt"></i> تاريخ الاستحقاق: ${formatDate(task.due_date)}</div>
                    ${task.completion_date ? 
                        `<div><i class="fas fa-calendar-check"></i> تاريخ الإكمال: ${formatDate(task.completion_date)}</div>` : 
                        ''}
                </div>
                <div class="task-actions">
                    ${task.status === 'Pending' ? `
                        <button class="edit-btn" onclick="editTask('${task.id}')">
                            <i class="fas fa-edit"></i> تعديل
                        </button>
                        <button class="complete-btn" onclick="completeTask('${task.id}')">
                            <i class="fas fa-check"></i> إكمال
                        </button>
                    ` : `
                        <span class="completed-badge">
                            <i class="fas fa-check-circle"></i> مكتملة
                        </span>
                    `}
                    <button class="delete-btn" onclick="confirmDelete('${task.id}')">
                        <i class="fas fa-trash"></i> حذف
                    </button>
                </div>
            `;
            tasksList.appendChild(taskCard);
            
            // Add entrance animation
            requestAnimationFrame(() => {
                taskCard.style.opacity = '0';
                taskCard.style.transform = 'translateY(20px)';
                requestAnimationFrame(() => {
                    taskCard.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
                    taskCard.style.opacity = '1';
                    taskCard.style.transform = 'translateY(0)';
                });
            });
        });
    }

    async function handleAddTask(e) {
        e.preventDefault();
        
        const taskId = document.getElementById('taskId').value;
        const formData = {
            title: document.getElementById('title').value,
            description: document.getElementById('description').value,
            due_date: document.getElementById('due_date').value,
            priority: document.getElementById('priority').value,
            tags: document.getElementById('tags').value
        };

        try {
            const url = taskId ? `/api/tasks/${taskId}` : '/api/tasks';
            const method = taskId ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                closeModal();
                loadTasks();
                showSuccess(taskId ? 'تم تحديث المهمة بنجاح' : 'تمت إضافة المهمة بنجاح');
            } else {
                throw new Error('Failed to save task');
            }
        } catch (error) {
            console.error('Error saving task:', error);
            showError('حدث خطأ أثناء حفظ المهمة');
        }
    }

    function handleFilterChange(e) {
        filterBtns.forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        currentFilter = e.target.dataset.status;
        loadTasks();
    }

    function handleSearch(e) {
        searchQuery = e.target.value;
        loadTasks();
    }

    function handleSort(e) {
        currentSort = e.target.value;
        loadTasks();
    }

    // Utility functions
    function getPriorityText(priority) {
        const priorities = {
            'High': 'عالية',
            'Medium': 'متوسطة',
            'Low': 'منخفضة'
        };
        return priorities[priority] || priority;
    }

    function formatDate(dateString) {
        const options = { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return new Date(dateString).toLocaleDateString('ar-EG', options);
    }

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    function showSuccess(message) {
        Toastify({
            text: message,
            duration: 3000,
            gravity: "top",
            position: 'left',
            backgroundColor: "var(--success-color)",
            stopOnFocus: true,
            className: "toast-notification",
            style: {
                borderRadius: '12px',
                padding: '12px 24px',
                boxShadow: '0 4px 15px rgba(0, 200, 83, 0.3)',
                fontSize: '1rem'
            }
        }).showToast();
    }

    function showError(message) {
        Toastify({
            text: message,
            duration: 3000,
            gravity: "top",
            position: 'left',
            backgroundColor: "var(--danger-color)",
            stopOnFocus: true,
            className: "toast-notification",
            style: {
                borderRadius: '12px',
                padding: '12px 24px',
                boxShadow: '0 4px 15px rgba(255, 61, 87, 0.3)',
                fontSize: '1rem'
            }
        }).showToast();
    }

    // Make functions available globally
    window.editTask = (taskId) => openModal(taskId);
    window.confirmDelete = (taskId) => {
        openConfirmModal('هل أنت متأكد من حذف هذه المهمة؟', () => deleteTask(taskId));
    };
});

// Global functions for task actions
window.deleteTask = async function(taskId) {
    const taskCard = document.querySelector(`.task-card[data-id="${taskId}"]`);
    if (!taskCard) return;

    try {
        // Add removing animation class
        taskCard.classList.add('removing');
        
        // Send delete request
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            // Wait for animation to complete
            setTimeout(() => {
                taskCard.remove();
                updateStatistics();
            }, 500);
            
            showSuccess('تم حذف المهمة بنجاح');
        } else {
            throw new Error('Failed to delete task');
        }
    } catch (error) {
        console.error('Error deleting task:', error);
        showError('حدث خطأ أثناء حذف المهمة');
        // Remove animation class if error occurs
        taskCard.classList.remove('removing');
    }
};

window.completeTask = async function(taskId) {
    const taskCard = document.querySelector(`.task-card[data-id="${taskId}"]`);
    if (!taskCard) return;

    try {
        const response = await fetch(`/api/tasks/${taskId}/complete`, {
            method: 'PUT'
        });

        if (response.ok) {
            const task = await response.json();
            
            // Add completion animation
            taskCard.style.transform = 'scale(1.05)';
            taskCard.style.boxShadow = '0 10px 30px rgba(0, 200, 83, 0.2)';
            
            setTimeout(() => {
                taskCard.style.transform = 'scale(1)';
                // Update the task card content
                const actionsDiv = taskCard.querySelector('.task-actions');
                actionsDiv.innerHTML = `
                    <span class="completed-badge">
                        <i class="fas fa-check-circle"></i> مكتملة
                    </span>
                    <button class="delete-btn" onclick="confirmDelete('${taskId}')">
                        <i class="fas fa-trash"></i> حذف
                    </button>
                `;
                
                // Add completion date
                const datesDiv = taskCard.querySelector('.task-dates');
                datesDiv.innerHTML += `
                    <div><i class="fas fa-calendar-check"></i> تاريخ الإكمال: ${formatDate(task.completion_date)}</div>
                `;
                
                updateStatistics();
            }, 300);
            
            showSuccess('تم إكمال المهمة بنجاح');
        } else {
            throw new Error('Failed to complete task');
        }
    } catch (error) {
        console.error('Error completing task:', error);
        showError('حدث خطأ أثناء إكمال المهمة');
    }
}; 