// =====================================================
// GITHUB PAGES COMPATIBLE - NO BACKEND VERSION
// Smart Grievance System - Standalone Demo
// =====================================================

// Demo Mode Configuration
const DEMO_MODE = true;

// Demo Users Database
const DEMO_USERS = [
    { 
        id: 1,
        email: 'admin@grievance.gov', 
        password: 'admin123', 
        role: 'ADMIN', 
        name: 'Admin User',
        phone: '9999999999'
    },
    { 
        id: 2,
        email: 'electricity@grievance.gov', 
        password: 'officer123', 
        role: 'OFFICER', 
        name: 'Electricity Officer', 
        department: 'Electricity',
        phone: '9876543210'
    },
    { 
        id: 3,
        email: 'water@grievance.gov', 
        password: 'officer123', 
        role: 'OFFICER', 
        name: 'Water Officer', 
        department: 'Water Supply',
        phone: '9876543211'
    },
    { 
        id: 4,
        email: 'citizen@example.com', 
        password: 'citizen123', 
        role: 'CITIZEN', 
        name: 'Demo Citizen',
        phone: '9123456789'
    }
];

// Demo Grievances Database
function getDemoGrievances() {
    const stored = localStorage.getItem('demoGrievances');
    if (stored) {
        return JSON.parse(stored);
    }
    
    const demo = [
        {
            id: 'GRV001',
            title: 'Street Light Not Working',
            description: 'Street light near my house has been out for 2 weeks',
            department: 'Electricity',
            status: 'Under Progress',
            priority: 'Medium',
            userId: 4,
            createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
            updates: [
                { status: 'Received', date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), comment: 'Complaint received' },
                { status: 'Assigned to Department', date: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(), comment: 'Assigned to electricity department' },
                { status: 'Under Progress', date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), comment: 'Technician assigned' }
            ]
        },
        {
            id: 'GRV002',
            title: 'Water Leakage on Main Road',
            description: 'Continuous water leakage causing road damage',
            department: 'Water Supply',
            status: 'Resolved',
            priority: 'High',
            userId: 4,
            createdAt: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
            resolvedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
            updates: [
                { status: 'Received', date: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(), comment: 'Complaint registered' },
                { status: 'Under Progress', date: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(), comment: 'Site inspection completed' },
                { status: 'Resolved', date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), comment: 'Leakage fixed' }
            ]
        }
    ];
    
    localStorage.setItem('demoGrievances', JSON.stringify(demo));
    return demo;
}

// Authentication Functions
function getToken() {
    return localStorage.getItem('token');
}

function setToken(token) {
    localStorage.setItem('token', token);
}

function removeToken() {
    localStorage.removeItem('token');
}

function getUser() {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    return JSON.parse(userStr);
}

function setUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
}

function removeUser() {
    localStorage.removeItem('user');
}

// Check if user is logged in
function isLoggedIn() {
    return localStorage.getItem('isLoggedIn') === 'true' && getUser() !== null;
}

// Logout function
function logout() {
    removeToken();
    removeUser();
    localStorage.removeItem('isLoggedIn');
    window.location.href = 'login.html';
}

// Check authentication and redirect if not logged in
function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

// Check role access
function requireRole(allowedRoles) {
    if (!requireAuth()) return false;
    
    const user = getUser();
    if (!allowedRoles.includes(user.role)) {
        alert('Access denied! You do not have permission to view this page.');
        window.location.href = 'index.html';
        return false;
    }
    return true;
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Format date only (no time)
function formatDateOnly(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Get status badge class
function getStatusBadgeClass(status) {
    const statusMap = {
        'Received': 'badge-received',
        'Assigned to Department': 'badge-assigned',
        'Under Progress': 'badge-progress',
        'Investigation': 'badge-investigation',
        'Reviewed': 'badge-reviewed',
        'Resolved': 'badge-resolved',
        'Closed': 'badge-closed'
    };
    return statusMap[status] || 'badge-received';
}

// Show alert message
function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) {
        console.log(message);
        return;
    }
    
    const alertClass = `alert-${type}`;
    const alertHTML = `
        <div class="alert ${alertClass} show">
            ${message}
        </div>
    `;
    
    alertContainer.innerHTML = alertHTML;
    
    if (duration > 0) {
        setTimeout(() => {
            const alert = alertContainer.querySelector('.alert');
            if (alert) {
                alert.classList.remove('show');
                setTimeout(() => {
                    if (alertContainer.innerHTML.includes(message)) {
                        alertContainer.innerHTML = '';
                    }
                }, 300);
            }
        }, duration);
    }
}

// Generate random ID
function generateId(prefix = 'GRV') {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 1000);
    return `${prefix}${timestamp}${random}`;
}

// Get all grievances for current user
function getUserGrievances() {
    const user = getUser();
    if (!user) return [];
    
    const allGrievances = getDemoGrievances();
    
    if (user.role === 'ADMIN') {
        return allGrievances;
    } else if (user.role === 'OFFICER') {
        return allGrievances.filter(g => g.department === user.department);
    } else {
        return allGrievances.filter(g => g.userId === user.id);
    }
}

// Submit new grievance
function submitGrievance(grievanceData) {
    const user = getUser();
    if (!user) {
        throw new Error('Please login to submit a grievance');
    }
    
    const allGrievances = getDemoGrievances();
    
    const newGrievance = {
        id: generateId('GRV'),
        ...grievanceData,
        userId: user.id,
        status: 'Received',
        priority: 'Medium',
        createdAt: new Date().toISOString(),
        updates: [{
            status: 'Received',
            date: new Date().toISOString(),
            comment: 'Grievance received and registered'
        }]
    };
    
    allGrievances.push(newGrievance);
    localStorage.setItem('demoGrievances', JSON.stringify(allGrievances));
    
    return newGrievance;
}

// Update grievance status
function updateGrievanceStatus(grievanceId, status, comment) {
    const allGrievances = getDemoGrievances();
    const grievance = allGrievances.find(g => g.id === grievanceId);
    
    if (!grievance) {
        throw new Error('Grievance not found');
    }
    
    grievance.status = status;
    grievance.updates.push({
        status: status,
        date: new Date().toISOString(),
        comment: comment || `Status updated to ${status}`
    });
    
    if (status === 'Resolved' || status === 'Closed') {
        grievance.resolvedAt = new Date().toISOString();
    }
    
    localStorage.setItem('demoGrievances', JSON.stringify(allGrievances));
    
    return grievance;
}

// Track grievance by ID
function trackGrievance(grievanceId) {
    const allGrievances = getDemoGrievances();
    return allGrievances.find(g => g.id.toUpperCase() === grievanceId.toUpperCase());
}

// Get statistics
function getStatistics() {
    const grievances = getDemoGrievances();
    const user = getUser();
    
    let relevantGrievances = grievances;
    if (user && user.role === 'OFFICER') {
        relevantGrievances = grievances.filter(g => g.department === user.department);
    } else if (user && user.role === 'CITIZEN') {
        relevantGrievances = grievances.filter(g => g.userId === user.id);
    }
    
    return {
        total: relevantGrievances.length,
        pending: relevantGrievances.filter(g => !['Resolved', 'Closed'].includes(g.status)).length,
        resolved: relevantGrievances.filter(g => g.status === 'Resolved').length,
        inProgress: relevantGrievances.filter(g => g.status === 'Under Progress').length
    };
}

// Initialize page - update header with user info
function initializePage() {
    const user = getUser();
    if (!user) return;
    
    // Update user info in header
    const userNameEl = document.getElementById('userName');
    const userRoleEl = document.getElementById('userRole');
    
    if (userNameEl) userNameEl.textContent = user.name;
    if (userRoleEl) userRoleEl.textContent = user.role;
    
    // Setup logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }
}

// Run on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializePage);
} else {
    initializePage();
}

// Export for use in other scripts
window.grievanceSystem = {
    isLoggedIn,
    getUser,
    setUser,
    logout,
    requireAuth,
    requireRole,
    getUserGrievances,
    submitGrievance,
    updateGrievanceStatus,
    trackGrievance,
    getStatistics,
    formatDate,
    formatDateOnly,
    getStatusBadgeClass,
    showAlert,
    DEMO_MODE
};
