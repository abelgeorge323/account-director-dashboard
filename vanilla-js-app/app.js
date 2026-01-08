/**
 * Account Director Performance Dashboard
 * Vanilla JavaScript Application
 */

// ==================== STATE MANAGEMENT ====================
const AppState = {
    data: null,
    currentView: 'rankings',
    filters: {
        vertical: 'all',
        account: 'all'
    },
    sort: {
        by: 'totalScore',
        order: 'desc'
    },
    expandedRows: new Set(),
    selectedAD: null
};

// ==================== DATA LOADING ====================
async function loadData() {
    try {
        const response = await fetch('data.json');
        if (!response.ok) throw new Error('Failed to load data');
        AppState.data = await response.json();
        console.log('Data loaded successfully:', AppState.data);
        return true;
    } catch (error) {
        console.error('Error loading data:', error);
        alert('Failed to load dashboard data. Please ensure data.json exists.');
        return false;
    }
}

// ==================== INITIALIZATION ====================
async function init() {
    const success = await loadData();
    if (!success) return;
    
    // Initialize UI
    populateFilters();
    setupEventListeners();
    updateLastUpdated();
    
    // Show initial view
    hideLoading();
    showView('rankings');
}

function hideLoading() {
    document.getElementById('loading-view').classList.add('hidden');
}

function updateLastUpdated() {
    const date = new Date(AppState.data.metadata.lastUpdated);
    document.getElementById('last-updated').textContent = 
        `Updated: ${date.toLocaleDateString()}`;
}

// ==================== VIEW MANAGEMENT ====================
function showView(viewName) {
    AppState.currentView = viewName;
    
    // Update view buttons
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === viewName);
    });
    
    // Hide all views
    ['rankings-view', 'reviews-view', 'rubric-view'].forEach(id => {
        document.getElementById(id).classList.add('hidden');
    });
    
    // Show selected view
    document.getElementById(`${viewName}-view`).classList.remove('hidden');
    
    // Update header
    const titles = {
        rankings: {
            title: 'Account Director Performance Dashboard',
            subtitle: 'Year-End Executive Review • 2025 Performance Evaluation'
        },
        reviews: {
            title: 'Individual Performance Reviews',
            subtitle: 'Detailed breakdown of scores and feedback for each review'
        },
        rubric: {
            title: 'Scoring Rubric & Methodology',
            subtitle: 'Understand how Account Director performance is evaluated'
        }
    };
    
    document.getElementById('page-title').textContent = titles[viewName].title;
    document.getElementById('page-subtitle').textContent = titles[viewName].subtitle;
    
    // Render view content
    if (viewName === 'rankings') renderRankings();
    else if (viewName === 'reviews') renderReviews();
    else if (viewName === 'rubric') renderRubric();
}

// ==================== FILTER MANAGEMENT ====================
function populateFilters() {
    const verticals = new Set();
    const accounts = new Set();
    
    AppState.data.accountDirectors.forEach(ad => {
        if (ad.vertical && ad.vertical !== 'N/A') verticals.add(ad.vertical);
        if (ad.account) accounts.add(ad.account);
    });
    
    // Populate vertical filter
    const verticalSelect = document.getElementById('filter-vertical');
    Array.from(verticals).sort().forEach(vertical => {
        const option = document.createElement('option');
        option.value = vertical;
        option.textContent = vertical;
        verticalSelect.appendChild(option);
    });
    
    // Populate account filter
    const accountSelect = document.getElementById('filter-account');
    Array.from(accounts).sort().forEach(account => {
        const option = document.createElement('option');
        option.value = account;
        option.textContent = account;
        accountSelect.appendChild(option);
    });
}

function getFilteredData() {
    let filtered = AppState.data.accountDirectors.filter(ad => {
        if (AppState.filters.vertical !== 'all' && ad.vertical !== AppState.filters.vertical) {
            return false;
        }
        if (AppState.filters.account !== 'all' && ad.account !== AppState.filters.account) {
            return false;
        }
        return true;
    });
    
    // Sort data
    const sortKey = AppState.sort.by;
    const sortOrder = AppState.sort.order;
    
    filtered.sort((a, b) => {
        let aVal, bVal;
        
        if (sortKey === 'totalScore') {
            aVal = a.avgTotalScore;
            bVal = b.avgTotalScore;
        } else {
            const sectionMap = {
                projects: 'Key Projects & Initiatives',
                valueAdds: 'Value Adds & Cost Avoidance',
                costSavings: 'Cost Savings Delivered',
                innovation: 'Innovation & Continuous Improvement',
                accountability: 'Issues, Challenges & Accountability',
                strategy: '2026 Forward Strategy & Vision',
                goals: 'Personal Goals & Role Maturity',
                execPresence: 'Presentation & Executive Presence'
            };
            const sectionName = sectionMap[sortKey];
            aVal = a.avgScores[sectionName] || 0;
            bVal = b.avgScores[sectionName] || 0;
        }
        
        return sortOrder === 'desc' ? bVal - aVal : aVal - bVal;
    });
    
    return filtered;
}

// ==================== RANKINGS VIEW ====================
function renderRankings() {
    const filtered = getFilteredData();
    
    // Render metrics
    renderMetrics(filtered);
    
    // Render leaderboard
    renderLeaderboard(filtered);
}

function renderMetrics(data) {
    const container = document.getElementById('metrics-grid');
    
    const totalCount = data.length;
    const avgScore = totalCount > 0 
        ? (data.reduce((sum, ad) => sum + ad.avgTotalScore, 0) / totalCount).toFixed(1)
        : '0.0';
    const topScore = totalCount > 0 
        ? Math.max(...data.map(ad => ad.avgTotalScore)).toFixed(1)
        : '0.0';
    const lowScore = totalCount > 0 
        ? Math.min(...data.map(ad => ad.avgTotalScore)).toFixed(1)
        : '0.0';
    
    container.innerHTML = `
        <div class="metric-card fade-in">
            <div class="metric-label">Total</div>
            <div class="metric-value">${totalCount}</div>
        </div>
        <div class="metric-card fade-in">
            <div class="metric-label">Avg</div>
            <div class="metric-value">${avgScore}</div>
        </div>
        <div class="metric-card fade-in">
            <div class="metric-label">Top</div>
            <div class="metric-value">${topScore}</div>
        </div>
        <div class="metric-card fade-in">
            <div class="metric-label">Low</div>
            <div class="metric-value">${lowScore}</div>
        </div>
    `;
}

function renderLeaderboard(data) {
    const container = document.getElementById('leaderboard');
    
    if (data.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 40px;">No Account Directors match the current filters.</p>';
        return;
    }
    
    container.innerHTML = data.map((ad, index) => {
        const rank = index + 1;
        const rankClass = rank === 1 ? 'rank-1' : rank === 2 ? 'rank-2' : rank === 3 ? 'rank-3' : 'rank-other';
        
        // Add special card classes for top 3
        const cardClass = rank <= 3 ? 'rank-top-3' : '';
        const rankCardClass = rank === 1 ? 'rank-1-card' : rank === 2 ? 'rank-2-card' : rank === 3 ? 'rank-3-card' : '';
        
        const perfBadge = getPerformanceBadge(ad.avgTotalScore);
        const isExpanded = AppState.expandedRows.has(ad.accountDirector);
        
        return `
            <div class="leaderboard-row ${cardClass} ${rankCardClass} ${isExpanded ? 'expanded' : ''} fade-in" data-ad="${ad.accountDirector}">
                <div class="rank-badge ${rankClass}">${rank}</div>
                <div class="ad-info">
                    <div class="ad-name">${ad.accountDirector}</div>
                    <div class="ad-account">${ad.account}</div>
                </div>
                <div class="ad-vertical">
                    📂 ${ad.vertical || 'N/A'}
                </div>
                <div class="ad-score-container">
                    <div class="ad-score">${ad.avgTotalScore.toFixed(1)}</div>
                    <div class="ad-score-max">of ${AppState.data.metadata.totalMaxScore}</div>
                    <div class="perf-badge ${perfBadge.class}">${perfBadge.label}</div>
                </div>
                <button class="expand-btn ${isExpanded ? 'expanded' : ''}" data-ad="${ad.accountDirector}">
                    ${isExpanded ? '▼' : '▶'}
                </button>
            </div>
            ${isExpanded ? renderExpandedSection(ad) : ''}
        `;
    }).join('');
    
    // Attach event listeners
    container.querySelectorAll('.expand-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleExpandedRow(btn.dataset.ad);
        });
    });
    
    container.querySelectorAll('.view-details-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            AppState.selectedAD = btn.dataset.ad;
            showView('reviews');
            document.getElementById('ad-select').value = btn.dataset.ad;
            renderReviewsForAD(btn.dataset.ad);
        });
    });
}

function renderExpandedSection(ad) {
    const sections = AppState.data.metadata.scoringSections;
    const shortNames = AppState.data.metadata.sectionShortNames;
    
    const sectionsHTML = sections.map((section, idx) => {
        const score = ad.avgScores[section] || 0;
        const percentage = (score / 5) * 100;
        const color = getScoreColor(score);
        
        return `
            <div class="section-score-item">
                <div class="section-score-header">
                    <span class="section-name">${shortNames[idx]}</span>
                    <span class="section-value">${score.toFixed(1)}/5</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${percentage}%; background: ${color};"></div>
                </div>
            </div>
        `;
    });
    
    // Split evenly: 4 left, 4 right
    const leftSections = sectionsHTML.slice(0, 4).join('');
    const rightSections = sectionsHTML.slice(4, 8).join('');
    
    return `
        <div class="expanded-section active">
            <div class="section-scores-grid">
                <div>${leftSections}</div>
                <div>${rightSections}</div>
            </div>
            <button class="view-details-btn" data-ad="${ad.accountDirector}">
                View Full Reviews
            </button>
        </div>
    `;
}

function toggleExpandedRow(adName) {
    if (AppState.expandedRows.has(adName)) {
        AppState.expandedRows.delete(adName);
    } else {
        AppState.expandedRows.add(adName);
    }
    renderLeaderboard(getFilteredData());
}

function getPerformanceBadge(score) {
    const maxScore = AppState.data.metadata.totalMaxScore;
    const ratio = score / maxScore;
    
    if (ratio >= 0.9) return { label: 'Outstanding', class: 'perf-outstanding' };
    if (ratio >= 0.8) return { label: 'Strong', class: 'perf-strong' };
    if (ratio >= 0.6) return { label: 'Solid', class: 'perf-solid' };
    return { label: 'Developing', class: 'perf-developing' };
}

function getScoreColor(score) {
    const ratio = score / 5;
    if (ratio >= 0.9) return '#10b981';
    if (ratio >= 0.8) return '#3b82f6';
    if (ratio >= 0.6) return '#f59e0b';
    return '#94a3b8';
}

// ==================== REVIEWS VIEW ====================
function renderReviews() {
    const adSelect = document.getElementById('ad-select');
    
    // Populate AD selector
    if (adSelect.options.length === 1) {
        AppState.data.accountDirectors
            .sort((a, b) => a.accountDirector.localeCompare(b.accountDirector))
            .forEach(ad => {
                const option = document.createElement('option');
                option.value = ad.accountDirector;
                option.textContent = ad.accountDirector;
                adSelect.appendChild(option);
            });
    }
    
    // If we have a selected AD, render their reviews
    if (AppState.selectedAD) {
        adSelect.value = AppState.selectedAD;
        renderReviewsForAD(AppState.selectedAD);
    }
}

function renderReviewsForAD(adName) {
    const container = document.getElementById('reviews-content');
    const ad = AppState.data.accountDirectors.find(a => a.accountDirector === adName);
    
    if (!ad) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 40px;">Please select an Account Director</p>';
        return;
    }
    
    const headerHTML = `
        <div class="review-header fade-in">
            <div class="review-ad-name">${ad.accountDirector}</div>
            <div class="ad-account" style="font-size: 1.1em; color: var(--text-secondary);">${ad.account}</div>
            <div class="review-meta">
                <div class="review-meta-item">
                    <div class="review-meta-label">Avg Total Score</div>
                    <div class="review-meta-value">${ad.avgTotalScore.toFixed(1)}</div>
                </div>
                <div class="review-meta-item">
                    <div class="review-meta-label">Max Possible</div>
                    <div class="review-meta-value">${AppState.data.metadata.totalMaxScore}</div>
                </div>
                <div class="review-meta-item">
                    <div class="review-meta-label">Total Reviews</div>
                    <div class="review-meta-value">${ad.reviewCount}</div>
                </div>
            </div>
        </div>
    `;
    
    const reviewsHTML = ad.reviews.map((review, idx) => {
        const sectionsHTML = AppState.data.metadata.scoringSections.map((section, sIdx) => {
            const score = review.scores[section] || 0;
            const feedback = review.feedback[section] || 'No feedback provided.';
            const percentage = (score / 5) * 100;
            const shortName = AppState.data.metadata.sectionShortNames[sIdx];
            
            return `
                <div class="review-section">
                    <div class="review-section-title">
                        <span>${shortName}</span>
                        <span class="review-section-score">${score.toFixed(1)}/5</span>
                    </div>
                    <div class="progress-bar" style="margin-bottom: 12px;">
                        <div class="progress-fill" style="width: ${percentage}%; background: ${getScoreColor(score)};"></div>
                    </div>
                    <div class="review-feedback">${feedback}</div>
                </div>
            `;
        }).join('');
        
        return `
            <div class="individual-review fade-in">
                <div class="individual-review-header">
                    Review ${idx + 1} by ${review.reviewerName}
                    <span style="font-weight: 600; color: var(--primary-blue); margin-left: 16px;">
                        Total: ${review.totalScore.toFixed(1)}/${AppState.data.metadata.totalMaxScore}
                    </span>
                </div>
                ${sectionsHTML}
            </div>
        `;
    }).join('');
    
    container.innerHTML = headerHTML + reviewsHTML;
}

// ==================== RUBRIC VIEW ====================
function renderRubric() {
    const container = document.getElementById('rubric-content');
    const rubrics = AppState.data.rubrics;
    const sections = AppState.data.metadata.scoringSections;
    
    container.innerHTML = sections.map((section, idx) => {
        const rubric = rubrics[section];
        if (!rubric) return '';
        
        const criteriaRows = [5, 4, 3, 2, 1].map(score => `
            <tr>
                <td>${score}</td>
                <td>${rubric.criteria[score.toString()]}</td>
            </tr>
        `).join('');
        
        return `
            <div class="rubric-section fade-in">
                <div class="rubric-section-header">${idx + 1}. ${section} (Max Score: 5)</div>
                <div class="rubric-definition">${rubric.definition}</div>
                <table class="rubric-table">
                    <thead>
                        <tr>
                            <th>Score</th>
                            <th>Criteria</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${criteriaRows}
                    </tbody>
                </table>
            </div>
        `;
    }).join('');
}

// ==================== EVENT LISTENERS ====================
function setupEventListeners() {
    // Mobile menu
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileOverlay = document.getElementById('mobile-overlay');
    const sidebar = document.getElementById('sidebar');

    function toggleMobileMenu() {
        mobileMenuBtn.classList.toggle('active');
        mobileOverlay.classList.toggle('active');
        sidebar.classList.toggle('mobile-open');
    }

    function closeMobileMenu() {
        mobileMenuBtn.classList.remove('active');
        mobileOverlay.classList.remove('active');
        sidebar.classList.remove('mobile-open');
    }

    mobileMenuBtn.addEventListener('click', toggleMobileMenu);
    mobileOverlay.addEventListener('click', closeMobileMenu);

    // Close mobile menu when clicking any filter or view button
    sidebar.addEventListener('click', (e) => {
        if (e.target.closest('.view-btn') || e.target.closest('.filter-select') || e.target.closest('.clear-filters-btn')) {
            // Small delay to allow action to complete
            setTimeout(closeMobileMenu, 300);
        }
    });

    // View buttons
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            showView(btn.dataset.view);
        });
    });
    
    // Filters
    document.getElementById('filter-vertical').addEventListener('change', (e) => {
        AppState.filters.vertical = e.target.value;
        if (AppState.currentView === 'rankings') renderRankings();
    });
    
    document.getElementById('filter-account').addEventListener('change', (e) => {
        AppState.filters.account = e.target.value;
        if (AppState.currentView === 'rankings') renderRankings();
    });
    
    document.getElementById('clear-filters').addEventListener('click', () => {
        AppState.filters.vertical = 'all';
        AppState.filters.account = 'all';
        document.getElementById('filter-vertical').value = 'all';
        document.getElementById('filter-account').value = 'all';
        if (AppState.currentView === 'rankings') renderRankings();
    });
    
    // Sort controls
    document.getElementById('sort-by').addEventListener('change', (e) => {
        AppState.sort.by = e.target.value;
        AppState.expandedRows.clear(); // Clear expanded rows when sorting
        renderRankings();
    });
    
    document.getElementById('sort-order').addEventListener('change', (e) => {
        AppState.sort.order = e.target.value;
        AppState.expandedRows.clear(); // Clear expanded rows when sorting
        renderRankings();
    });
    
    // AD selector in reviews view
    document.getElementById('ad-select').addEventListener('change', (e) => {
        if (e.target.value) {
            AppState.selectedAD = e.target.value;
            renderReviewsForAD(e.target.value);
        }
    });
}

// ==================== START APPLICATION ====================
document.addEventListener('DOMContentLoaded', init);

// Close mobile menu on window resize above mobile breakpoint
window.addEventListener('resize', () => {
    if (window.innerWidth > 768) {
        const mobileMenuBtn = document.getElementById('mobile-menu-btn');
        const mobileOverlay = document.getElementById('mobile-overlay');
        const sidebar = document.getElementById('sidebar');
        
        if (sidebar.classList.contains('mobile-open')) {
            mobileMenuBtn.classList.remove('active');
            mobileOverlay.classList.remove('active');
            sidebar.classList.remove('mobile-open');
        }
    }
});

