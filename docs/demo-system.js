// =====================================================
// ENHANCED DEMO SYSTEM WITH AI & FRAUD DETECTION
// Smart Grievance System - Complete Professional Version
// =====================================================

const DEMO_MODE = true;

// Demo Users Database
const DEMO_USERS = [
    { 
        id: 1,
        email: 'admin@grievance.gov', 
        password: 'admin123', 
        role: 'ADMIN', 
        name: 'Admin User',
        phone: '9999999999',
        canEditProfile: true,
        canEditUsers: true
    },
    { 
        id: 2,
        email: 'electricity@grievance.gov', 
        password: 'officer123', 
        role: 'OFFICER', 
        name: 'Electricity Officer', 
        department: 'Electricity',
        phone: '9876543210',
        canEditProfile: true,
        canChangeContact: false
    },
    { 
        id: 3,
        email: 'water@grievance.gov', 
        password: 'officer123', 
        role: 'OFFICER', 
        name: 'Water Officer', 
        department: 'Water Supply',
        phone: '9876543211',
        canEditProfile: true,
        canChangeContact: false
    },
    { 
        id: 4,
        email: 'citizen@example.com', 
        password: 'citizen123', 
        role: 'CITIZEN', 
        name: 'Demo Citizen',
        phone: '9123456789',
        canEditProfile: true,
        canChangeContact: false
    }
];

// AI Keywords for Department Classification
const DEPARTMENT_KEYWORDS = {
    'Electricity': ['electricity', 'power', 'light', 'pole', 'wire', 'transformer', 'blackout', 'voltage', 'meter', 'bill'],
    'Water Supply': ['water', 'pipe', 'leak', 'tank', 'supply', 'tap', 'drainage', 'sewage', 'bore', 'pump'],
    'Roads': ['road', 'street', 'pothole', 'highway', 'pavement', 'footpath', 'bridge', 'traffic', 'signal'],
    'Sanitation': ['garbage', 'waste', 'trash', 'cleanliness', 'sweeping', 'dustbin', 'smell', 'dirty'],
    'Public Transport': ['bus', 'metro', 'train', 'station', 'railway', 'transport', 'ticket', 'route'],
    'Healthcare': ['hospital', 'doctor', 'medicine', 'health', 'clinic', 'ambulance', 'treatment', 'medical'],
    'Education': ['school', 'college', 'teacher', 'student', 'education', 'class', 'exam', 'admission'],
    'Police': ['police', 'theft', 'crime', 'security', 'law', 'FIR', 'complaint', 'officer']
};

// Fraud Detection Keywords
const FRAUD_KEYWORDS = [
    'fake', 'fraud', 'scam', 'cheat', 'lie', 'false', 'spam', 'test123', 'asdf', 
    'qwerty', 'dummy', 'abcde', 'testing', 'check', 'trial'
];

// Profanity Filter
const PROFANITY_LIST = [
    'badword1', 'badword2', 'offensive1', 'offensive2' // Add actual words as needed
];

// =====================================================
// AI CLASSIFICATION ENGINE
// =====================================================

function classifyDepartmentAI(title, description) {
    const text = (title + ' ' + description).toLowerCase();
    const scores = {};
    
    // Calculate scores for each department
    for (const [dept, keywords] of Object.entries(DEPARTMENT_KEYWORDS)) {
        let score = 0;
        keywords.forEach(keyword => {
            const regex = new RegExp(keyword, 'gi');
            const matches = text.match(regex);
            score += matches ? matches.length : 0;
        });
        scores[dept] = score;
    }
    
    // Find department with highest score
    let maxScore = 0;
    let detectedDept = 'Other';
    for (const [dept, score] of Object.entries(scores)) {
        if (score > maxScore) {
            maxScore = score;
            detectedDept = dept;
        }
    }
    
    return {
        department: detectedDept,
        confidence: maxScore > 0 ? Math.min((maxScore / 5) * 100, 100) : 0,
        scores: scores
    };
}

// =====================================================
// FRAUD DETECTION ENGINE
// =====================================================

function detectFraud(title, description, userHistory) {
    const issues = [];
    const text = (title + ' ' + description).toLowerCase();
    
    // Check for fraud keywords
    FRAUD_KEYWORDS.forEach(keyword => {
        if (text.includes(keyword)) {
            issues.push(`Suspicious keyword detected: "${keyword}"`);
        }
    });
    
    // Check for profanity
    PROFANITY_LIST.forEach(word => {
        if (text.includes(word)) {
            issues.push('Inappropriate language detected');
        }
    });
    
    // Check length (too short)
    if (description.length < 20) {
        issues.push('Description too short (minimum 20 characters)');
    }
    
    // Check for repeated characters
    if (/(.)\1{5,}/.test(text)) {
        issues.push('Suspicious pattern: repeated characters');
    }
    
    // Check for gibberish
    if (/^[a-z]{1,3}$/i.test(title.trim())) {
        issues.push('Title appears to be gibberish');
    }
    
    // Check duplicate complaints
    if (userHistory && userHistory.length > 0) {
        const recentSimilar = userHistory.filter(c => 
            c.title.toLowerCase() === title.toLowerCase() && 
            (Date.now() - new Date(c.createdAt).getTime()) < 3600000 // Within 1 hour
        );
        if (recentSimilar.length > 0) {
            issues.push('Duplicate complaint detected within 1 hour');
        }
        
        // Check spam (more than 5 in 10 minutes)
        const recent10min = userHistory.filter(c => 
            (Date.now() - new Date(c.createdAt).getTime()) < 600000
        );
        if (recent10min.length >= 5) {
            issues.push('Spam detected: Too many complaints in 10 minutes');
        }
    }
    
    const fraudScore = (issues.length / 7) * 100; // 7 possible checks
    
    return {
        isFraudulent: fraudScore > 30,
        fraudScore: Math.round(fraudScore),
        issues: issues,
        severity: fraudScore > 60 ? 'HIGH' : fraudScore > 30 ? 'MEDIUM' : 'LOW'
    };
}

// =====================================================
// IMAGE ANALYSIS (Simulated)
// =====================================================

function analyzeImage(imageData) {
    // Simulate AI image detection
    const random = Math.random();
    const categories = ['Street Light', 'Pothole', 'Garbage', 'Water Leak', 'Damaged Property'];
    const detected = categories[Math.floor(random * categories.length)];
    
    return {
        detected: detected,
        confidence: Math.round(70 + Math.random() * 30),
        tags: [detected.toLowerCase(), 'infrastructure', 'public'],
        isRelevant: random > 0.1 // 90% relevant
    };
}

// =====================================================
// PRIORITY CALCULATION
// =====================================================

function calculatePriority(title, description, department) {
    const urgentKeywords = ['emergency', 'urgent', 'danger', 'fire', 'accident', 'leak', 'broken'];
    const text = (title + ' ' + description).toLowerCase();
    
    let urgencyScore = 0;
    urgentKeywords.forEach(keyword => {
        if (text.includes(keyword)) urgencyScore += 1;
    });
    
    // High priority departments
    const highPriorityDepts = ['Healthcare', 'Police', 'Electricity'];
    if (highPriorityDepts.includes(department)) urgencyScore += 1;
    
    if (urgencyScore >= 2) return 'High';
    if (urgencyScore === 1) return 'Medium';
    return 'Low';
}

// =====================================================
// NOTIFICATION SYSTEM
// =====================================================

function getNotifications(userId) {
    const notifications = JSON.parse(localStorage.getItem('notifications') || '{}');
    return notifications[userId] || [];
}

function addNotification(userId, notification) {
    const notifications = JSON.parse(localStorage.getItem('notifications') || '{}');
    if (!notifications[userId]) notifications[userId] = [];
    
    notifications[userId].unshift({
        ...notification,
        id: Date.now(),
        timestamp: new Date().toISOString(),
        read: false
    });
    
    // Keep only last 50 notifications
    notifications[userId] = notifications[userId].slice(0, 50);
    localStorage.setItem('notifications', JSON.stringify(notifications));
}

function markNotificationRead(userId, notificationId) {
    const notifications = JSON.parse(localStorage.getItem('notifications') || '{}');
    if (notifications[userId]) {
        const notif = notifications[userId].find(n => n.id === notificationId);
        if (notif) notif.read = true;
        localStorage.setItem('notifications', JSON.stringify(notifications));
    }
}

function getUnreadCount(userId) {
    const notifications = getNotifications(userId);
    return notifications.filter(n => !n.read).length;
}

// =====================================================
// COMMENT SYSTEM
// =====================================================

function getComments(grievanceId, updateIndex) {
    const key = `comments_${grievanceId}_${updateIndex}`;
    return JSON.parse(localStorage.getItem(key) || '[]');
}

function addComment(grievanceId, updateIndex, comment, userId) {
    const key = `comments_${grievanceId}_${updateIndex}`;
    const comments = getComments(grievanceId, updateIndex);
    
    const newComment = {
        id: Date.now(),
        userId: userId,
        userName: getUser().name,
        userRole: getUser().role,
        text: comment,
        timestamp: new Date().toISOString()
    };
    
    comments.push(newComment);
    localStorage.setItem(key, JSON.stringify(comments));
    
    // Send notification if officer replied
    if (getUser().role === 'OFFICER') {
        const grievance = trackGrievance(grievanceId);
        if (grievance) {
            addNotification(grievance.userId, {
                type: 'comment',
                message: `Officer replied to your complaint ${grievanceId}`,
                grievanceId: grievanceId,
                comment: comment
            });
            
            // Simulate email notification
            console.log(`📧 Email sent to user about new comment on ${grievanceId}`);
        }
    }
    
    return newComment;
}

function getCommentsCount(grievanceId, updateIndex) {
    return getComments(grievanceId, updateIndex).length;
}

// =====================================================
// CORE FUNCTIONS
// =====================================================

function getDemoGrievances() {
    const stored = localStorage.getItem('demoGrievances');
    if (stored) return JSON.parse(stored);
    
    const demo = [
        {
            id: 'GRV001',
            title: 'Street Light Not Working',
            description: 'Street light near my house has been out for 2 weeks causing safety issues',
            department: 'Electricity',
            status: 'Under Progress',
            priority: 'Medium',
            userId: 4,
            aiDetected: true,
            aiConfidence: 95,
            fraudScore: 0,
            createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
            updates: [
                { status: 'Received', date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), comment: 'Complaint received and registered', officer: 'System' },
                { status: 'Assigned to Department', date: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(), comment: 'Assigned to electricity department', officer: 'System' },
                { status: 'Under Progress', date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), comment: 'Technician assigned and working on it', officer: 'Electricity Officer' }
            ]
        },
        {
            id: 'GRV002',
            title: 'Water Leakage on Main Road',
            description: 'Continuous water leakage from underground pipe causing road damage and water wastage',
            department: 'Water Supply',
            status: 'Resolved',
            priority: 'High',
            userId: 4,
            aiDetected: true,
            aiConfidence: 98,
            fraudScore: 0,
            createdAt: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
            resolvedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
            updates: [
                { status: 'Received', date: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(), comment: 'Complaint registered', officer: 'System' },
                { status: 'Under Progress', date: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(), comment: 'Site inspection completed, repair scheduled', officer: 'Water Officer' },
                { status: 'Resolved', date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), comment: 'Leakage fixed and pipe repaired', officer: 'Water Officer' }
            ]
        }
    ];
    
    localStorage.setItem('demoGrievances', JSON.stringify(demo));
    return demo;
}

function getToken() { return localStorage.getItem('token'); }
function setToken(token) { localStorage.setItem('token', token); }
function removeToken() { localStorage.removeItem('token'); }

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

function isLoggedIn() {
    return localStorage.getItem('isLoggedIn') === 'true' && getUser() !== null;
}

function logout() {
    removeToken();
    removeUser();
    localStorage.removeItem('isLoggedIn');
    window.location.href = 'login.html';
}

function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

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

function formatDateOnly(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

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

function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) {
        console.log(message);
        return;
    }
    const alertClass = `alert-${type}`;
    const alertHTML = `<div class="alert ${alertClass} show">${message}</div>`;
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

function generateId(prefix = 'GRV') {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 1000);
    return `${prefix}${timestamp}${random}`;
}

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

function submitGrievance(grievanceData) {
    const user = getUser();
    if (!user) throw new Error('Please login to submit a grievance');
    
    const userHistory = getUserGrievances();
    
    // AI Classification
    const aiResult = classifyDepartmentAI(grievanceData.title, grievanceData.description);
    
    // Fraud Detection
    const fraudResult = detectFraud(grievanceData.title, grievanceData.description, userHistory);
    
    // Block if high fraud score
    if (fraudResult.fraudScore > 60) {
        throw new Error('Complaint blocked: ' + fraudResult.issues.join(', '));
    }
    
    // Warn if medium fraud
    if (fraudResult.fraudScore > 30) {
        console.warn('⚠️ Fraud Warning:', fraudResult.issues);
    }
    
    // Use AI detected department if confidence is high
    const finalDepartment = aiResult.confidence > 50 ? aiResult.department : grievanceData.department;
    
    // Calculate priority
    const priority = calculatePriority(grievanceData.title, grievanceData.description, finalDepartment);
    
    const allGrievances = getDemoGrievances();
    
    const newGrievance = {
        id: generateId('GRV'),
        ...grievanceData,
        department: finalDepartment,
        userId: user.id,
        status: 'Received',
        priority: priority,
        aiDetected: aiResult.confidence > 50,
        aiConfidence: Math.round(aiResult.confidence),
        fraudScore: fraudResult.fraudScore,
        createdAt: new Date().toISOString(),
        updates: [{
            status: 'Received',
            date: new Date().toISOString(),
            comment: `Complaint received and registered. ${aiResult.confidence > 50 ? `AI detected department: ${finalDepartment} (${Math.round(aiResult.confidence)}% confidence)` : ''}`,
            officer: 'System'
        }]
    };
    
    allGrievances.push(newGrievance);
    localStorage.setItem('demoGrievances', JSON.stringify(allGrievances));
    
    // Send notification to user
    addNotification(user.id, {
        type: 'success',
        message: `Complaint ${newGrievance.id} submitted successfully`,
        grievanceId: newGrievance.id
    });
    
    // Simulate email
    console.log(`📧 Email confirmation sent to ${user.email} for complaint ${newGrievance.id}`);
    
    return newGrievance;
}

function updateGrievanceStatus(grievanceId, status, comment) {
    const allGrievances = getDemoGrievances();
    const grievance = allGrievances.find(g => g.id === grievanceId);
    if (!grievance) throw new Error('Grievance not found');
    
    const user = getUser();
    grievance.status = status;
    grievance.updates.push({
        status: status,
        date: new Date().toISOString(),
        comment: comment || `Status updated to ${status}`,
        officer: user ? user.name : 'Officer'
    });
    
    if (status === 'Resolved' || status === 'Closed') {
        grievance.resolvedAt = new Date().toISOString();
    }
    
    localStorage.setItem('demoGrievances', JSON.stringify(allGrievances));
    
    // Notify user
    addNotification(grievance.userId, {
        type: 'update',
        message: `Your complaint ${grievanceId} status updated to: ${status}`,
        grievanceId: grievanceId
    });
    
    // Simulate email
    console.log(`📧 Status update email sent for ${grievanceId}: ${status}`);
    
    return grievance;
}

function trackGrievance(grievanceId) {
    const allGrievances = getDemoGrievances();
    return allGrievances.find(g => g.id.toUpperCase() === grievanceId.toUpperCase());
}

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

function initializePage() {
    const user = getUser();
    if (!user) return;
    const userNameEl = document.getElementById('userName');
    const userRoleEl = document.getElementById('userRole');
    if (userNameEl) userNameEl.textContent = user.name;
    if (userRoleEl) userRoleEl.textContent = user.role;
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializePage);
} else {
    initializePage();
}

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
    classifyDepartmentAI,
    detectFraud,
    analyzeImage,
    calculatePriority,
    getNotifications,
    addNotification,
    markNotificationRead,
    getUnreadCount,
    getComments,
    addComment,
    getCommentsCount,
    DEMO_MODE
};
