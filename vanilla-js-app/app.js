/**
 * Account Director Performance Dashboard
 * Vanilla JavaScript Application
 */

// ==================== STATE MANAGEMENT ====================
const AppState = {
    data: null,
    bestPractices: null,
    currentView: 'rankings',
    filters: {
        vertical: 'all',
        account: 'all',
        tier: 'all',
        role: 'all'
    },
    bestPracticesFilters: {
        adName: 'all',
        category: 'all',
        replicability: 'all',
        status: 'all',
        vertical: 'all',
        account: 'all',
        featuredOnly: false
    },
    sort: {
        by: 'totalScore',
        order: 'desc'
    },
    atbSort: {
        by: 'totalAtb',
        order: 'desc'
    },
    expandedRows: new Set(),
    expandedPractices: new Set(),
    expandedATBRows: new Set(),
    selectedAD: null
};

// ==================== GLOBAL MOBILE-FRIENDLY HANDLERS ====================
// These global functions ensure mobile compatibility with inline onclick handlers
window.toggleRow = function(adName) {
    console.log('🎯 TOGGLE ROW CALLED:', adName);
    toggleExpandedRow(adName);
};

window.togglePracticeExpand = function(practiceKey) {
    const isExpanded = AppState.expandedPractices.has(practiceKey);
    if (isExpanded) {
        AppState.expandedPractices.delete(practiceKey);
    } else {
        AppState.expandedPractices.add(practiceKey);
    }
    const card = document.querySelector(`.practice-card[data-practice-key="${practiceKey}"]`);
    if (card) {
        card.classList.toggle('expanded', !isExpanded);
        const expandedEl = card.querySelector('.practice-expanded');
        const indicator = card.querySelector('.practice-expand-indicator');
        if (expandedEl) expandedEl.style.display = isExpanded ? 'none' : 'block';
        if (indicator) indicator.textContent = isExpanded ? '▶' : '▼';
    }
};

window.viewDetails = function(adName) {
    console.log('🎯 VIEW DETAILS CALLED:', adName);
    AppState.selectedAD = adName;
    showView('reviews');
    document.getElementById('ad-select').value = adName;
    renderReviewsForAD(adName);
};

// Test that functions are defined
console.log('✅ window.toggleRow defined:', typeof window.toggleRow);
console.log('✅ window.viewDetails defined:', typeof window.viewDetails);

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

async function loadBestPractices() {
    try {
        // Best practices are now in data.json under bestPractices key
        if (!AppState.data || !AppState.data.bestPractices) {
            console.warn('No best practices data found in data.json');
            return false;
        }
        
        // Transform from {AD_NAME: [...]} to {practices: [...], metadata: {...}}
        const bestPracticesData = AppState.data.bestPractices;
        const practices = [];
        const categories = new Set();
        const replicabilities = new Set();
        const statuses = new Set();
        const verticals = new Set();
        const accounts = new Set();
        
        // Create AD to account and vertical mapping
        const adAccountMap = {};
        const adVerticalMap = {};
        if (AppState.data.accountDirectors) {
            AppState.data.accountDirectors.forEach(ad => {
                adAccountMap[ad.accountDirector] = ad.account || '';
                adVerticalMap[ad.accountDirector] = ad.vertical || 'N/A';
                if (ad.vertical && ad.vertical !== 'N/A') verticals.add(ad.vertical);
                // Extract unique accounts from comma-separated account string
                if (ad.account) {
                    ad.account.split(',').map(a => a.trim()).filter(a => a && a !== 'undefined').forEach(acc => accounts.add(acc));
                }
            });
        }
        
        // Flatten the structure and map fields
        Object.keys(bestPracticesData).forEach(adName => {
            const adPractices = bestPracticesData[adName];
            if (Array.isArray(adPractices)) {
                adPractices.forEach(practice => {
                    const replicable = practice.replicability || 'Medium';
                    const status = practice.status || '';
                    replicabilities.add(replicable);
                    if (status) statuses.add(status);
                    
                    const umbrellaCat = getUmbrellaCategory(practice.category);
                    const umbrellaStat = getUmbrellaStatus(practice.status || '');
                    practices.push({
                        ...practice,
                        adName: adName,
                        account: adAccountMap[adName] || '',
                        vertical: adVerticalMap[adName] || 'N/A',
                        replicable: replicable,
                        replicableDetails: '',
                        quote: practice.leadership_endorsement || '',
                        featured: practice.status === 'Proven & Active' || practice.status === 'Proven & Scalable',
                        metrics: [],
                        umbrellaCategory: umbrellaCat,
                        umbrellaStatus: umbrellaStat
                    });
                    if (practice.category) {
                        categories.add(practice.category);
                    }
                });
            }
        });
        
        // Build the expected structure
        AppState.bestPractices = {
            metadata: {
                totalPractices: practices.length,
                categories: Array.from(categories).sort(),
                umbrellaCategories: UMBRELLA_CATEGORIES.map(u => u.id),
                replicabilities: Array.from(replicabilities).sort(),
                statuses: Array.from(statuses).sort(),
                verticals: Array.from(verticals).sort(),
                accounts: Array.from(accounts).sort(),
                lastUpdated: AppState.data.metadata?.lastUpdated || new Date().toISOString()
            },
            practices: practices
        };
        
        console.log('Best practices loaded:', AppState.bestPractices);
        return true;
    } catch (error) {
        console.error('Error loading best practices:', error);
        return false;
    }
}

// ==================== INITIALIZATION ====================
async function init() {
    const success = await loadData();
    if (!success) return;
    
    // Load best practices (non-blocking)
    await loadBestPractices();
    
    // Initialize UI
    populateFilters();
    populateBestPracticesFilters();
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
    ['rankings-view', 'reviews-view', 'best-practices-view', 'rubric-view', 'atb-view'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.add('hidden');
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
        'best-practices': {
            title: 'Best Practices & Innovation',
            subtitle: 'Showcasing excellence and replicable strategies across our team'
        },
        rubric: {
            title: 'Scoring Rubric & Methodology',
            subtitle: 'Understand how Account Director performance is evaluated'
        },
        atb: {
            title: 'Above the Base (ATB) Leaderboard',
            subtitle: 'ATB by Account Director • Oct 2025 – Jan 2026'
        }
    };
    
    document.getElementById('page-title').textContent = titles[viewName].title;
    document.getElementById('page-subtitle').textContent = titles[viewName].subtitle;
    
    // Render view content
    if (viewName === 'rankings') renderRankings();
    else if (viewName === 'reviews') renderReviews();
    else if (viewName === 'best-practices') renderBestPractices();
    else if (viewName === 'rubric') renderRubric();
    else if (viewName === 'atb') renderATB();
}

// ==================== FILTER MANAGEMENT ====================
function populateFilters() {
    const verticals = new Set();
    const accounts = new Set();
    const tiers = new Set();
    const roles = new Set();
    
    AppState.data.accountDirectors.forEach(ad => {
        if (ad.vertical && ad.vertical !== 'N/A') verticals.add(ad.vertical);
        if (ad.account) accounts.add(ad.account);
        if (ad.tier) {
            tiers.add(ad.tier);
        } else {
            tiers.add('Unassigned');
        }
        if (ad.role) roles.add(ad.role);
    });
    
    // Populate vertical filter (in rankings view)
    const verticalFilterSelect = document.getElementById('vertical-filter');
    if (verticalFilterSelect) {
        Array.from(verticals).sort().forEach(vertical => {
            const option = document.createElement('option');
            option.value = vertical;
            option.textContent = vertical;
            verticalFilterSelect.appendChild(option);
        });
    }
    
    // Populate tier filter (in rankings view)
    const tierFilterSelect = document.getElementById('tier-filter');
    if (tierFilterSelect) {
        Array.from(tiers).sort().forEach(tier => {
            const option = document.createElement('option');
            option.value = tier;
            option.textContent = tier;
            tierFilterSelect.appendChild(option);
        });
    }
    
    // Populate role filter (in rankings view)
    const roleFilterSelect = document.getElementById('role-filter');
    if (roleFilterSelect) {
        Array.from(roles).sort().forEach(role => {
            const option = document.createElement('option');
            option.value = role;
            option.textContent = role;
            roleFilterSelect.appendChild(option);
        });
    }

    // Populate ATB view filters
    ['atb-vertical-filter', 'atb-tier-filter', 'atb-role-filter'].forEach((id, i) => {
        const sel = document.getElementById(id);
        if (!sel) return;
        const source = i === 0 ? verticals : i === 1 ? tiers : roles;
        sel.innerHTML = '<option value="all">' + (i === 0 ? 'All Verticals' : i === 1 ? 'All Tiers' : 'All Roles') + '</option>';
        Array.from(source).sort().forEach(v => {
            const opt = document.createElement('option');
            opt.value = v;
            opt.textContent = v;
            sel.appendChild(opt);
        });
    });
    
    // Populate role filter in sidebar
    const filterRole = document.getElementById('filter-role');
    if (filterRole) {
        Array.from(roles).sort().forEach(role => {
            const option = document.createElement('option');
            option.value = role;
            option.textContent = role;
            filterRole.appendChild(option);
        });
    }
    
    // Populate account filter (for reviews view if it exists)
    const accountSelect = document.getElementById('filter-account');
    if (accountSelect) {
        Array.from(accounts).sort().forEach(account => {
            const option = document.createElement('option');
            option.value = account;
            option.textContent = account;
            accountSelect.appendChild(option);
        });
    }
}

function getFilteredData() {
    let filtered = AppState.data.accountDirectors.filter(ad => {
        if (AppState.filters.vertical !== 'all' && ad.vertical !== AppState.filters.vertical) {
            return false;
        }
        if (AppState.filters.account !== 'all' && ad.account !== AppState.filters.account) {
            return false;
        }
        if (AppState.filters.tier !== 'all') {
            const adTier = ad.tier || 'Unassigned';
            if (adTier !== AppState.filters.tier) {
                return false;
            }
        }
        if (AppState.filters.role !== 'all' && (ad.role || 'Account Director') !== AppState.filters.role) {
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
            return sortOrder === 'desc' ? bVal - aVal : aVal - bVal;
        } else if (sortKey === 'tier') {
            // Sort by tier - handle empty tiers as "Unassigned" (sort to end)
            const aTier = a.tier || 'Unassigned';
            const bTier = b.tier || 'Unassigned';
            
            // Extract tier number for numeric sorting (e.g., "Tier 5" -> 5)
            const aTierNum = aTier.match(/\d+/) ? parseInt(aTier.match(/\d+/)[0]) : 999;
            const bTierNum = bTier.match(/\d+/) ? parseInt(bTier.match(/\d+/)[0]) : 999;
            
            return sortOrder === 'desc' ? bTierNum - aTierNum : aTierNum - bTierNum;
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
            return sortOrder === 'desc' ? bVal - aVal : aVal - bVal;
        }
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
        
        // Get tier badge with color coding
        const getTierBadge = (tier) => {
            if (!tier) return '';
            
            let bgColor, textColor;
            switch(tier) {
                case 'Tier 4':
                    bgColor = '#f97316'; // Orange
                    textColor = 'white';
                    break;
                case 'Tier 5':
                    bgColor = '#6366f1'; // Indigo
                    textColor = 'white';
                    break;
                case 'Tier 6':
                    bgColor = '#10b981'; // Green
                    textColor = 'white';
                    break;
                default: // Unassigned
                    bgColor = '#94a3b8'; // Gray
                    textColor = 'white';
            }
            
            return `<span style="margin-left: 8px; padding: 3px 10px; background: ${bgColor}; color: ${textColor}; border-radius: 12px; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.5px;">${tier}</span>`;
        };
        
        return `
            <div class="leaderboard-row ${cardClass} ${rankCardClass} ${isExpanded ? 'expanded' : ''} fade-in" 
                 data-ad="${ad.accountDirector}"
                 onclick="window.toggleRow('${ad.accountDirector.replace(/'/g, "\\'")}');"
                 style="cursor: pointer;">
                <div class="rank-badge ${rankClass}">${rank}</div>
                <div class="ad-info">
                    <div class="ad-name">${ad.accountDirector}</div>
                    <div class="ad-account">${ad.account}</div>
                </div>
                <div class="ad-vertical">
                    📂 ${ad.vertical || 'N/A'}
                    ${getTierBadge(ad.tier)}
                </div>
                <div class="ad-score-container">
                    <div class="ad-score">${ad.avgTotalScore.toFixed(1)}</div>
                    <div class="ad-score-max">of ${AppState.data.metadata.totalMaxScore}</div>
                    <div class="perf-badge ${perfBadge.class}">${perfBadge.label}</div>
                </div>
                <div class="expand-indicator">${isExpanded ? '▼' : '▶'}</div>
            </div>
            ${isExpanded ? renderExpandedSection(ad) : ''}
        `;
    }).join('');
    
    // Note: Event handlers are inline (onclick) for maximum mobile compatibility
    // The global window.toggleRow and window.viewDetails functions handle all clicks
    // Initial render includes expanded sections; subsequent toggles are DOM-only (no re-render)
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
        <div class="expanded-section">
            <div class="section-scores-grid">
                <div>${leftSections}</div>
                <div>${rightSections}</div>
            </div>
            <button class="view-details-btn" onclick="event.stopPropagation(); window.viewDetails('${ad.accountDirector.replace(/'/g, "\\'")}');">
                View Full Reviews
            </button>
        </div>
    `;
}

function toggleExpandedRow(adName) {
    // Toggle state
    const isExpanded = AppState.expandedRows.has(adName);
    
    if (isExpanded) {
        AppState.expandedRows.delete(adName);
    } else {
        AppState.expandedRows.add(adName);
    }
    
    console.log('🔄 Toggle:', adName, 'Was:', isExpanded, 'Now:', !isExpanded);
    
    // Find the row in DOM
    const row = document.querySelector(`.leaderboard-row[data-ad="${adName}"]`);
    if (!row) {
        console.error('❌ Row not found for:', adName);
        return;
    }
    
    console.log('✓ Row found');
    
    // Toggle expanded class on row
    row.classList.toggle('expanded');
    
    // Update indicator
    const indicator = row.querySelector('.expand-indicator');
    if (indicator) {
        indicator.textContent = isExpanded ? '▶' : '▼';
        console.log('✓ Indicator:', indicator.textContent);
    }
    
    // Find expanded section as SIBLING (not child)
    let expandedSection = row.nextElementSibling;
    
    if (expandedSection && expandedSection.classList.contains('expanded-section')) {
        console.log('✓ Found existing expanded section');
        // Toggle visibility
        if (isExpanded) {
            expandedSection.style.display = 'none';
            console.log('✓ Collapsed');
        } else {
            expandedSection.style.display = 'block';
            console.log('✓ Expanded');
        }
    } else if (!isExpanded) {
        // Need to create expanded section
        console.log('📝 Creating new expanded section');
        const ad = AppState.data.accountDirectors.find(a => a.accountDirector === adName);
        if (ad) {
            const expandedHTML = renderExpandedSection(ad);
            row.insertAdjacentHTML('afterend', expandedHTML);
            console.log('✅ Created and inserted');
            
            // Show it
            expandedSection = row.nextElementSibling;
            if (expandedSection) {
                expandedSection.style.display = 'block';
                console.log('✅ Shown');
            }
        }
    }
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

// ==================== BEST PRACTICES VIEW ====================
// Umbrella categories: group 60+ granular categories into 8 buckets for easier filtering
const UMBRELLA_CATEGORIES = [
    { id: 'Transitions', label: 'Transitions', class: 'cat-transitions', color: '#06b6d4' },
    { id: 'Financial Strategy', label: 'Financial Strategy', class: 'cat-financial', color: '#f59e0b' },
    { id: 'Operational Excellence', label: 'Operational Excellence', class: 'cat-operational', color: '#3b82f6' },
    { id: 'Innovation & Technology', label: 'Innovation & Technology', class: 'cat-innovation', color: '#6366f1' },
    { id: 'Client Relations & Partnership', label: 'Client Relations & Partnership', class: 'cat-client', color: '#10b981' },
    { id: 'Governance & Process', label: 'Governance & Process', class: 'cat-governance', color: '#64748b' },
    { id: 'People & Culture', label: 'People & Culture', class: 'cat-people', color: '#f43f5e' },
    { id: 'Safety & Quality', label: 'Safety & Quality', class: 'cat-safety', color: '#ef4444' }
];

// Umbrella statuses: group granular statuses into broader buckets
const UMBRELLA_STATUSES = [
    { id: 'Proven', label: 'Proven (Active, Scalable, Complete, etc.)' },
    { id: 'In Development', label: 'In Development (2026 goals, pilots, etc.)' },
    { id: 'Active / Expanding', label: 'Active / Expanding' }
];

function getUmbrellaStatus(granularStatus) {
    if (!granularStatus) return 'Proven';
    const s = granularStatus.toLowerCase();
    if (s.includes('development') || s.includes('2026 development') || s.includes('pilot') || s.includes('in progress')) return 'In Development';
    if (s.includes('expanding') || s.includes('converting') || s.includes('phase 2') || (s.startsWith('active (') && (s.includes('2026') || s.includes('growth')))) return 'Active / Expanding';
    return 'Proven';
}

function getUmbrellaCategory(granularCategory) {
    if (!granularCategory) return 'Operational Excellence';
    const c = granularCategory.toLowerCase();
    if (c.includes('transition') || c.includes('turnaround') || c.includes('account recovery')) return 'Transitions';
    if (c.includes('financial') || c.includes('cost savings') || c.includes('cost avoidance') || c.includes('revenue growth') || c.includes('financial excellence') || c.includes('financial optimization') || c.includes('financial recovery') || c.includes('contract management') || c.includes('procurement')) return 'Financial Strategy';
    if (c.includes('operational') || c.includes('process excellence') || c.includes('service excellence') || c.includes('emergency response') || c.includes('labor optimization') || c.includes('standardization') || c.includes('scalability') || c.includes('crisis response') || c.includes('service innovation')) return 'Operational Excellence';
    if (c.includes('innovation') || c.includes('technology') || c.includes('data-driven') || c.includes('product innovation') || c.includes('equipment investment') || c.includes('sustainability')) return 'Innovation & Technology';
    if (c.includes('client') || c.includes('partnership') || c.includes('relationship management') || c.includes('strategic partnership') || c.includes('strategic negotiation') || c.includes('service expansion') || c.includes('business development') || c.includes('strategic thinking')) return 'Client Relations & Partnership';
    if (c.includes('governance') || c.includes('process improvement') || c.includes('communication') || c.includes('strategic communication') || c.includes('data alignment') || c.includes('real-time communication') || c.includes('strategic planning') || c.includes('executive presentation')) return 'Governance & Process';
    if (c.includes('people') || c.includes('team building') || c.includes('staffing') || c.includes('workforce') || c.includes('talent') || c.includes('retention') || c.includes('leadership philosophy')) return 'People & Culture';
    if (c.includes('safety') || c.includes('quality') || c.includes('risk management') || c.includes('compliance') || c.includes('regulatory') || c.includes('accountability')) return 'Safety & Quality';
    return 'Operational Excellence';
}

function populateBestPracticesFilters() {
    if (!AppState.bestPractices) return;
    
    const meta = AppState.bestPractices.metadata;
    
    // Populate AD filter
    const adFilter = document.getElementById('bp-ad-filter');
    const uniqueADs = [...new Set(AppState.bestPractices.practices.map(p => p.adName))].sort();
    uniqueADs.forEach(ad => {
        const option = document.createElement('option');
        option.value = ad;
        option.textContent = ad;
        adFilter.appendChild(option);
    });
    
    // Populate category filter with umbrella categories (dropdown)
    const categoryFilterSelect = document.getElementById('bp-category-filter');
    if (categoryFilterSelect) {
        categoryFilterSelect.innerHTML = '<option value="all">All Categories</option>';
        UMBRELLA_CATEGORIES.forEach(umbrella => {
            const option = document.createElement('option');
            option.value = umbrella.id;
            option.textContent = umbrella.label;
            categoryFilterSelect.appendChild(option);
        });
    }
    
    // Populate replicability filter
    const replicabilityFilter = document.getElementById('bp-replicability-filter');
    if (replicabilityFilter) {
        (meta.replicabilities || []).forEach(r => {
            const option = document.createElement('option');
            option.value = r;
            option.textContent = r;
            replicabilityFilter.appendChild(option);
        });
    }
    
    // Populate status filter with umbrella statuses
    const statusFilter = document.getElementById('bp-status-filter');
    if (statusFilter) {
        statusFilter.innerHTML = '<option value="all">All Status</option>';
        UMBRELLA_STATUSES.forEach(us => {
            const option = document.createElement('option');
            option.value = us.id;
            option.textContent = us.label;
            statusFilter.appendChild(option);
        });
    }
    
    // Populate vertical filter
    const verticalFilter = document.getElementById('bp-vertical-filter');
    if (verticalFilter) {
        (meta.verticals || []).forEach(v => {
            const option = document.createElement('option');
            option.value = v;
            option.textContent = v;
            verticalFilter.appendChild(option);
        });
    }
    
    // Populate account filter
    const accountFilter = document.getElementById('bp-account-filter');
    if (accountFilter) {
        (meta.accounts || []).forEach(a => {
            const option = document.createElement('option');
            option.value = a;
            option.textContent = a;
            accountFilter.appendChild(option);
        });
    }
}

function getCategoryClass(categoryOrUmbrella) {
    const u = UMBRELLA_CATEGORIES.find(x => x.id === categoryOrUmbrella);
    return u ? u.class : 'cat-default';
}

function getCategoryBadge(practice) {
    const umbrella = practice.umbrellaCategory || getUmbrellaCategory(practice.category);
    const categoryClass = getCategoryClass(umbrella);
    return `<span class="category-badge ${categoryClass}">${umbrella.toUpperCase()}</span>`;
}

function getPracticeKey(practice, index) {
    return `bp-${index}-${(practice.title || '').slice(0, 30).replace(/[^a-zA-Z0-9]/g, '-')}`;
}

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function getFilteredPractices() {
    if (!AppState.bestPractices) return [];
    
    const f = AppState.bestPracticesFilters;
    
    return AppState.bestPractices.practices.filter(practice => {
        if (f.adName !== 'all' && practice.adName !== f.adName) return false;
        if (f.category !== 'all' && practice.umbrellaCategory !== f.category) return false;
        if (f.replicability !== 'all' && (practice.replicable || practice.replicability) !== f.replicability) return false;
        if (f.status !== 'all' && practice.umbrellaStatus !== f.status) return false;
        if (f.vertical !== 'all' && practice.vertical !== f.vertical) return false;
        if (f.account !== 'all') {
            const practiceAccounts = (practice.account || '').split(',').map(a => a.trim());
            if (!practiceAccounts.includes(f.account)) return false;
        }
        if (f.featuredOnly && !practice.featured) return false;
        return true;
    });
}

function renderBestPractices() {
    if (!AppState.bestPractices) {
        document.getElementById('featured-practices').innerHTML = 
            '<p style="text-align: center; color: var(--text-secondary); padding: 40px;">Best practices data not available.</p>';
        return;
    }
    
    AppState.expandedPractices.clear();
    const filtered = getFilteredPractices();
    
    // Render featured practices
    const featured = filtered.filter(p => p.featured);
    renderFeaturedPractices(featured);
    
    // Render all practices by category
    renderAllPractices(filtered);
}

function renderFeaturedPractices(practices) {
    const container = document.getElementById('featured-practices');
    
    if (practices.length === 0) {
        container.innerHTML = '';
        return;
    }
    
    const startIdx = 10000; // Offset to avoid collision with all-practices keys
    container.innerHTML = `
        <div class="featured-section-header">
            <div class="featured-badge">FEATURED HIGHLIGHTS</div>
            <div class="featured-subtitle">Strategic initiatives with high impact and replicability • Click to expand</div>
        </div>
        ${practices.map((practice, i) => {
            const key = getPracticeKey(practice, startIdx + i);
            const isExpanded = AppState.expandedPractices.has(key);
            const desc = escapeHtml(practice.description || '');
            const ctx = escapeHtml(practice.context || '');
            const quote = escapeHtml(practice.quote || '');
            return `
            <div class="practice-card featured compact ${isExpanded ? 'expanded' : ''}" data-practice-key="${key}" onclick="event.stopPropagation(); window.togglePracticeExpand('${key}');" style="cursor: pointer;">
                <div class="compact-summary">
                    <div class="practice-header">${getCategoryBadge(practice)}</div>
                    <div class="compact-header">
                        <h3 class="card-title">${practice.title}</h3>
                        <span class="practice-expand-indicator">${isExpanded ? '▼' : '▶'}</span>
                    </div>
                    <div class="card-meta">
                        <span class="ad-name">${practice.adName}</span>
                        <span class="separator">|</span>
                        <span class="account-name">${practice.account}</span>
                    </div>
                    <div class="compact-details">
                        <div class="compact-detail">
                            <span class="compact-label">Impact:</span>
                            <span class="compact-value">${practice.impact}</span>
                        </div>
                        <div class="compact-detail">
                            <span class="compact-label">Replicability:</span>
                            <span class="compact-value">${practice.replicable}</span>
                        </div>
                    </div>
                </div>
                <div class="practice-expanded" style="display: ${isExpanded ? 'block' : 'none'};">
                    ${desc ? `<p class="card-description">${desc}</p>` : ''}
                    ${ctx ? `<div class="detail-item"><span class="detail-label">CONTEXT</span><span class="detail-text">${ctx}</span></div>` : ''}
                    <div class="card-details">
                        <div class="detail-item"><span class="detail-label">IMPACT</span><span class="detail-text">${practice.impact}</span></div>
                        <div class="detail-item"><span class="detail-label">STATUS</span><span class="detail-text">${practice.status || '—'}</span></div>
                    </div>
                    ${quote ? `<blockquote class="practice-quote">"${quote}"</blockquote>` : ''}
                </div>
            </div>
        `}).join('')}
    `;
}

function renderAllPractices(practices) {
    const container = document.getElementById('all-practices');
    
    if (practices.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 40px;">No practices match the current filters.</p>';
        return;
    }
    
    // Group by umbrella category (8 sections instead of 60+)
    const byUmbrella = {};
    practices.forEach(practice => {
        const umbrella = practice.umbrellaCategory || getUmbrellaCategory(practice.category);
        if (!byUmbrella[umbrella]) byUmbrella[umbrella] = [];
        byUmbrella[umbrella].push(practice);
    });
    const umbrellaOrder = UMBRELLA_CATEGORIES.map(u => u.id);
    const sortedUmbrellas = Object.keys(byUmbrella).sort((a, b) => 
        umbrellaOrder.indexOf(a) - umbrellaOrder.indexOf(b));
    
    let practiceIndex = 0;
    
    container.innerHTML = `
        <div class="all-practices-header">
            <h2 class="section-title">ALL BEST PRACTICES</h2>
            <div class="section-divider"></div>
        </div>
        ${sortedUmbrellas.map(umbrella => {
            const umbrellaDef = UMBRELLA_CATEGORIES.find(u => u.id === umbrella);
            const headerClass = umbrellaDef ? umbrellaDef.class : 'cat-default';
            return `
            <div class="category-section fade-in">
                <div class="category-header ${headerClass}" style="${umbrellaDef ? `border-left-color: ${umbrellaDef.color}` : ''}">
                    <span class="category-title">${umbrella.toUpperCase()}</span>
                </div>
                ${byUmbrella[umbrella].map(practice => {
                    const key = getPracticeKey(practice, practiceIndex++);
                    const isExpanded = AppState.expandedPractices.has(key);
                    const desc = escapeHtml(practice.description || '');
                    const ctx = escapeHtml(practice.context || '');
                    const quote = escapeHtml(practice.quote || '');
                    return `
                    <div class="practice-card compact ${isExpanded ? 'expanded' : ''}" data-practice-key="${key}" onclick="event.stopPropagation(); window.togglePracticeExpand('${key}');" style="cursor: pointer;">
                        <div class="compact-summary">
                            <div class="compact-header">
                                <h4 class="compact-title">${practice.title}</h4>
                                <span class="practice-expand-indicator">${isExpanded ? '▼' : '▶'}</span>
                                ${practice.featured ? '<span class="featured-indicator">FEATURED</span>' : ''}
                            </div>
                            <div class="compact-meta">
                                <span class="meta-ad">${practice.adName}</span>
                                <span class="meta-separator">|</span>
                                <span class="meta-account">${practice.account}</span>
                            </div>
                            ${practice.category && practice.category !== umbrella ? `<div class="compact-subcategory">${practice.category}</div>` : ''}
                            <div class="compact-details">
                                <div class="compact-detail">
                                    <span class="compact-label">Impact:</span>
                                    <span class="compact-value">${practice.impact}</span>
                                </div>
                                <div class="compact-detail">
                                    <span class="compact-label">Replicability:</span>
                                    <span class="compact-value">${practice.replicable}</span>
                                </div>
                            </div>
                        </div>
                        <div class="practice-expanded" style="display: ${isExpanded ? 'block' : 'none'};">
                            ${desc ? `<p class="card-description">${desc}</p>` : ''}
                            ${ctx ? `<div class="detail-item"><span class="detail-label">CONTEXT</span><span class="detail-text">${ctx}</span></div>` : ''}
                            <div class="card-details">
                                <div class="detail-item"><span class="detail-label">IMPACT</span><span class="detail-text">${practice.impact}</span></div>
                                <div class="detail-item"><span class="detail-label">STATUS</span><span class="detail-text">${practice.status || '—'}</span></div>
                            </div>
                            ${quote ? `<blockquote class="practice-quote">"${quote}"</blockquote>` : ''}
                        </div>
                    </div>
                `}).join('')}
            </div>
        `}).join('')}
    `;
}

// ==================== ATB VIEW ====================
window.toggleATBRow = function(adName) {
    if (AppState.expandedATBRows.has(adName)) {
        AppState.expandedATBRows.delete(adName);
    } else {
        AppState.expandedATBRows.add(adName);
    }
    const row = document.querySelector(`#atb-leaderboard .leaderboard-row[data-ad="${adName}"]`);
    if (row) {
        row.classList.toggle('expanded', AppState.expandedATBRows.has(adName));
        const indicator = row.querySelector('.expand-indicator');
        if (indicator) indicator.textContent = AppState.expandedATBRows.has(adName) ? '▼' : '▶';
        let section = row.nextElementSibling;
        if (section && section.classList.contains('atb-expanded-section')) {
            section.style.display = AppState.expandedATBRows.has(adName) ? 'block' : 'none';
        } else if (AppState.expandedATBRows.has(adName)) {
            const ad = AppState.data.accountDirectors.find(a => a.accountDirector === adName);
            if (ad) {
                const sectionEl = document.createElement('div');
                sectionEl.className = 'atb-expanded-section expanded-section';
                sectionEl.style.display = 'block';
                sectionEl.innerHTML = renderATBExpandedSection(ad);
                row.insertAdjacentElement('afterend', sectionEl);
                const atb = ad.atbData || { accounts: [] };
                if (atb.accounts && atb.accounts.length > 0) {
                    const oct = atb.accounts.reduce((s, a) => s + (a.october || 0), 0);
                    const nov = atb.accounts.reduce((s, a) => s + (a.november || 0), 0);
                    const dec = atb.accounts.reduce((s, a) => s + (a.december || 0), 0);
                    const jan = atb.accounts.reduce((s, a) => s + (a.january || 0), 0);
                    setTimeout(() => initATBChart('atb-chart-' + ad.accountDirector.replace(/\s/g, '-'), oct, nov, dec, jan), 50);
                }
            }
        }
    }
};

function formatATBValue(val) {
    if (val === null || val === undefined) return '—';
    const n = Number(val);
    if (isNaN(n)) return '—';
    if (n >= 0) return '$' + Math.round(n).toLocaleString();
    return '($' + Math.abs(Math.round(n)).toLocaleString() + ')';
}

function renderATBExpandedSection(ad) {
    const atb = ad.atbData || { accounts: [], totalAtb: 0 };
    const accounts = atb.accounts || [];
    if (accounts.length === 0) {
        return '<div class="atb-expanded-content"><p style="color: var(--text-secondary);">No ATB data for this Account Director.</p></div>';
    }
    const oct = accounts.reduce((s, a) => s + (a.october || 0), 0);
    const nov = accounts.reduce((s, a) => s + (a.november || 0), 0);
    const dec = accounts.reduce((s, a) => s + (a.december || 0), 0);
    const jan = accounts.reduce((s, a) => s + (a.january || 0), 0);
    const chartId = 'atb-chart-' + ad.accountDirector.replace(/\s/g, '-');
    const tableRows = accounts.map(a => `
        <tr>
            <td>${a.account}${a.hasSubcontractedWork ? ' *' : ''}</td>
            <td>${a.october !== null && a.october !== undefined ? formatATBValue(a.october) : '—'}</td>
            <td>${a.november !== null && a.november !== undefined ? formatATBValue(a.november) : '—'}</td>
            <td>${a.december !== null && a.december !== undefined ? formatATBValue(a.december) : '—'}</td>
            <td>${a.january !== null && a.january !== undefined ? formatATBValue(a.january) : '—'}</td>
        </tr>
    `).join('');
    const subNote = accounts.some(a => a.hasSubcontractedWork) ? '<p style="font-size: 0.85em; color: var(--text-secondary); margin-top: 8px;">* Some TB contains subcontracted work (P&G, Merck)</p>' : '';
    return `
        <div class="atb-expanded-content">
            <h4 style="margin-bottom: 12px;">ATB by Month (Aggregate)</h4>
            <div style="height: 200px; margin-bottom: 20px;">
                <canvas id="${chartId}"></canvas>
            </div>
            <h4 style="margin-bottom: 12px;">Per-Account Breakdown</h4>
            <table class="atb-account-table" style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="border-bottom: 2px solid var(--border-color);">
                        <th style="text-align: left; padding: 8px;">Account</th>
                        <th style="text-align: right; padding: 8px;">October</th>
                        <th style="text-align: right; padding: 8px;">November</th>
                        <th style="text-align: right; padding: 8px;">December</th>
                        <th style="text-align: right; padding: 8px;">January</th>
                    </tr>
                </thead>
                <tbody>${tableRows}</tbody>
            </table>
            ${subNote}
        </div>
    `;
}

function initATBChart(canvasId, oct, nov, dec, jan) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || typeof Chart === 'undefined') return;
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['October', 'November', 'December', 'January'],
            datasets: [{
                label: 'ATB ($)',
                data: [oct, nov, dec, jan],
                backgroundColor: ['rgba(30, 64, 175, 0.7)', 'rgba(30, 64, 175, 0.7)', 'rgba(30, 64, 175, 0.7)', 'rgba(30, 64, 175, 0.7)'],
                borderColor: 'rgb(30, 64, 175)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: v => '$' + (v >= 1000 ? (v/1000) + 'K' : v) }
                }
            }
        }
    });
}

function getFilteredATBData() {
    let filtered = AppState.data.accountDirectors.filter(ad => {
        if (AppState.filters.vertical !== 'all' && ad.vertical !== AppState.filters.vertical) return false;
        if (AppState.filters.tier !== 'all') {
            const adTier = ad.tier || 'Unassigned';
            if (adTier !== AppState.filters.tier) return false;
        }
        if (AppState.filters.role !== 'all' && (ad.role || 'Account Director') !== AppState.filters.role) return false;
        return true;
    });
    const sortBy = AppState.atbSort.by;
    const order = AppState.atbSort.order;
    filtered.sort((a, b) => {
        let aVal, bVal;
        if (sortBy === 'totalAtb') {
            aVal = (a.atbData && a.atbData.totalAtb) || 0;
            bVal = (b.atbData && b.atbData.totalAtb) || 0;
        } else {
            aVal = a.avgTotalScore || 0;
            bVal = b.avgTotalScore || 0;
        }
        return order === 'desc' ? bVal - aVal : aVal - bVal;
    });
    return filtered;
}

function renderATB() {
    const filtered = getFilteredATBData();
    const metricsEl = document.getElementById('atb-metrics-grid');
    if (metricsEl) {
        const totalCount = filtered.length;
        const atbValues = filtered.map(ad => (ad.atbData && ad.atbData.totalAtb) || 0).filter(v => v > 0);
        const avgAtb = atbValues.length > 0 ? atbValues.reduce((a, b) => a + b, 0) / atbValues.length : 0;
        const topAtb = atbValues.length > 0 ? Math.max(...atbValues) : 0;
        const lowAtb = atbValues.length > 0 ? Math.min(...atbValues.filter(v => v > 0)) : 0;
        metricsEl.innerHTML = `
            <div class="metric-card fade-in"><div class="metric-label">Total</div><div class="metric-value">${totalCount}</div></div>
            <div class="metric-card fade-in"><div class="metric-label">Avg ATB</div><div class="metric-value">${formatATBValue(avgAtb)}</div></div>
            <div class="metric-card fade-in"><div class="metric-label">Top</div><div class="metric-value">${formatATBValue(topAtb)}</div></div>
            <div class="metric-card fade-in"><div class="metric-label">Low</div><div class="metric-value">${formatATBValue(lowAtb)}</div></div>
        `;
    }
    const container = document.getElementById('atb-leaderboard');
    if (!container) return;
    if (filtered.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 40px;">No Account Directors match the current filters.</p>';
        return;
    }
    const getTierBadge = (tier) => {
        if (!tier) return '';
        let bg = tier === 'Tier 4' ? '#f97316' : tier === 'Tier 5' ? '#6366f1' : tier === 'Tier 6' ? '#10b981' : '#94a3b8';
        return `<span style="margin-left: 8px; padding: 3px 10px; background: ${bg}; color: white; border-radius: 12px; font-size: 0.7rem; font-weight: 600;">${tier}</span>`;
    };
    container.innerHTML = filtered.map((ad, index) => {
        const rank = index + 1;
        const rankClass = rank <= 3 ? `rank-${rank}` : 'rank-other';
        const totalAtb = (ad.atbData && ad.atbData.totalAtb) || 0;
        const isExpanded = AppState.expandedATBRows.has(ad.accountDirector);
        return `
            <div class="leaderboard-row ${isExpanded ? 'expanded' : ''} fade-in" data-ad="${ad.accountDirector}"
                 onclick="window.toggleATBRow('${ad.accountDirector.replace(/'/g, "\\'")}');" style="cursor: pointer;">
                <div class="rank-badge ${rankClass}">${rank}</div>
                <div class="ad-info">
                    <div class="ad-name">${ad.accountDirector}</div>
                    <div class="ad-account">${ad.account}</div>
                </div>
                <div class="ad-vertical">📂 ${ad.vertical || 'N/A'} ${getTierBadge(ad.tier)}</div>
                <div class="ad-score-container">
                    <div class="ad-score">${formatATBValue(totalAtb)}</div>
                    <div class="ad-score-label">ATB (Oct-Jan)</div>
                </div>
                <span class="expand-indicator">${isExpanded ? '▼' : '▶'}</span>
            </div>
        `;
    }).join('');
    AppState.expandedATBRows.forEach(adName => {
        const ad = filtered.find(a => a.accountDirector === adName);
        if (ad) {
            const row = container.querySelector(`.leaderboard-row[data-ad="${adName}"]`);
            if (row && !row.nextElementSibling?.classList?.contains('atb-expanded-section')) {
                const sectionEl = document.createElement('div');
                sectionEl.className = 'atb-expanded-section expanded-section';
                sectionEl.style.display = 'block';
                sectionEl.innerHTML = renderATBExpandedSection(ad);
                row.insertAdjacentElement('afterend', sectionEl);
                const atb = ad.atbData || { accounts: [] };
                if (atb.accounts && atb.accounts.length > 0) {
                    const oct = atb.accounts.reduce((s, a) => s + (a.october || 0), 0);
                    const nov = atb.accounts.reduce((s, a) => s + (a.november || 0), 0);
                    const dec = atb.accounts.reduce((s, a) => s + (a.december || 0), 0);
                    const jan = atb.accounts.reduce((s, a) => s + (a.january || 0), 0);
                    setTimeout(() => initATBChart('atb-chart-' + ad.accountDirector.replace(/\s/g, '-'), oct, nov, dec, jan), 50);
                }
            }
        }
    });
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

    // Close mobile menu when clicking view buttons only (NOT filters)
    sidebar.addEventListener('click', (e) => {
        if (e.target.closest('.view-btn')) {
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
    
    // Vertical filter (in rankings view)
    const verticalFilter = document.getElementById('vertical-filter');
    if (verticalFilter) {
        verticalFilter.addEventListener('change', (e) => {
            AppState.filters.vertical = e.target.value;
            if (AppState.currentView === 'rankings') renderRankings();
        });
    }
    
    // Tier filter (in rankings view)
    const tierFilter = document.getElementById('tier-filter');
    if (tierFilter) {
        tierFilter.addEventListener('change', (e) => {
            AppState.filters.tier = e.target.value;
            if (AppState.currentView === 'rankings') renderRankings();
        });
    }
    
    // Role filter (in rankings view)
    const roleFilter = document.getElementById('role-filter');
    if (roleFilter) {
        roleFilter.addEventListener('change', (e) => {
            AppState.filters.role = e.target.value;
            if (AppState.currentView === 'rankings') renderRankings();
        });
    }
    
    // Old filters for reviews view (if they exist)
    const filterVertical = document.getElementById('filter-vertical');
    const filterAccount = document.getElementById('filter-account');
    const clearFiltersBtn = document.getElementById('clear-filters');
    
    if (filterVertical) {
        filterVertical.addEventListener('change', (e) => {
            AppState.filters.vertical = e.target.value;
            if (AppState.currentView === 'rankings') renderRankings();
        });
    }
    
    if (filterAccount) {
        filterAccount.addEventListener('change', (e) => {
            AppState.filters.account = e.target.value;
            if (AppState.currentView === 'rankings') renderRankings();
        });
    }
    
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', () => {
            AppState.filters.vertical = 'all';
            AppState.filters.account = 'all';
            AppState.filters.tier = 'all';
            AppState.filters.role = 'all';
            if (filterVertical) filterVertical.value = 'all';
            if (filterAccount) filterAccount.value = 'all';
            if (filterRole) filterRole.value = 'all';
            if (tierFilter) tierFilter.value = 'all';
            if (verticalFilter) verticalFilter.value = 'all';
            if (roleFilter) roleFilter.value = 'all';
            const atbV = document.getElementById('atb-vertical-filter');
            const atbT = document.getElementById('atb-tier-filter');
            const atbR = document.getElementById('atb-role-filter');
            if (atbV) atbV.value = 'all';
            if (atbT) atbT.value = 'all';
            if (atbR) atbR.value = 'all';
            if (AppState.currentView === 'rankings') renderRankings();
            if (AppState.currentView === 'atb') renderATB();
        });
    }
    
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

    // ATB view filters and sort
    const atbVertical = document.getElementById('atb-vertical-filter');
    const atbTier = document.getElementById('atb-tier-filter');
    const atbRole = document.getElementById('atb-role-filter');
    const atbSortBy = document.getElementById('atb-sort-by');
    const atbSortOrder = document.getElementById('atb-sort-order');
    if (atbVertical) atbVertical.addEventListener('change', (e) => { AppState.filters.vertical = e.target.value; if (AppState.currentView === 'atb') renderATB(); });
    if (atbTier) atbTier.addEventListener('change', (e) => { AppState.filters.tier = e.target.value; if (AppState.currentView === 'atb') renderATB(); });
    if (atbRole) atbRole.addEventListener('change', (e) => { AppState.filters.role = e.target.value; if (AppState.currentView === 'atb') renderATB(); });
    if (atbSortBy) atbSortBy.addEventListener('change', (e) => { AppState.atbSort.by = e.target.value; AppState.expandedATBRows.clear(); if (AppState.currentView === 'atb') renderATB(); });
    if (atbSortOrder) atbSortOrder.addEventListener('change', (e) => { AppState.atbSort.order = e.target.value; AppState.expandedATBRows.clear(); if (AppState.currentView === 'atb') renderATB(); });
    
    // AD selector in reviews view
    document.getElementById('ad-select').addEventListener('change', (e) => {
        if (e.target.value) {
            AppState.selectedAD = e.target.value;
            renderReviewsForAD(e.target.value);
        }
    });
    
    // Best Practices filters
    const bpAdFilter = document.getElementById('bp-ad-filter');
    const bpCategoryFilter = document.getElementById('bp-category-filter');
    const bpReplicabilityFilter = document.getElementById('bp-replicability-filter');
    const bpStatusFilter = document.getElementById('bp-status-filter');
    const bpVerticalFilter = document.getElementById('bp-vertical-filter');
    const bpAccountFilter = document.getElementById('bp-account-filter');
    const bpFeaturedOnly = document.getElementById('bp-featured-only');
    
    const bpFilterHandler = (e, key) => {
        AppState.bestPracticesFilters[key] = e.target.value;
        if (AppState.currentView === 'best-practices') renderBestPractices();
    };
    
    if (bpAdFilter) bpAdFilter.addEventListener('change', (e) => bpFilterHandler(e, 'adName'));
    if (bpCategoryFilter) bpCategoryFilter.addEventListener('change', (e) => bpFilterHandler(e, 'category'));
    if (bpReplicabilityFilter) bpReplicabilityFilter.addEventListener('change', (e) => bpFilterHandler(e, 'replicability'));
    if (bpStatusFilter) bpStatusFilter.addEventListener('change', (e) => bpFilterHandler(e, 'status'));
    if (bpVerticalFilter) bpVerticalFilter.addEventListener('change', (e) => bpFilterHandler(e, 'vertical'));
    if (bpAccountFilter) bpAccountFilter.addEventListener('change', (e) => bpFilterHandler(e, 'account'));
    
    if (bpFeaturedOnly) {
        bpFeaturedOnly.addEventListener('change', (e) => {
            AppState.bestPracticesFilters.featuredOnly = e.target.checked;
            if (AppState.currentView === 'best-practices') renderBestPractices();
        });
    }
    
    const bpClearFilters = document.getElementById('bp-clear-filters');
    if (bpClearFilters) {
        bpClearFilters.addEventListener('click', () => {
            AppState.bestPracticesFilters = { adName: 'all', category: 'all', replicability: 'all', status: 'all', vertical: 'all', account: 'all', featuredOnly: false };
            if (bpAdFilter) bpAdFilter.value = 'all';
            if (bpCategoryFilter) bpCategoryFilter.value = 'all';
            if (bpReplicabilityFilter) bpReplicabilityFilter.value = 'all';
            if (bpStatusFilter) bpStatusFilter.value = 'all';
            if (bpVerticalFilter) bpVerticalFilter.value = 'all';
            if (bpAccountFilter) bpAccountFilter.value = 'all';
            if (bpFeaturedOnly) bpFeaturedOnly.checked = false;
            if (AppState.currentView === 'best-practices') renderBestPractices();
        });
    }
}

// ==================== START APPLICATION ====================
document.addEventListener('DOMContentLoaded', init);

// DEBUG: Global click listener to see if clicks are registered
document.addEventListener('click', function(e) {
    const row = e.target.closest('.leaderboard-row');
    if (row) {
        console.log('🖱️ CLICK DETECTED on leaderboard row:', row.dataset.ad);
        console.log('🖱️ Click target:', e.target.className);
    }
}, true);

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

