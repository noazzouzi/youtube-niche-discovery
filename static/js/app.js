// YouTube Niche Discovery - Main Application Logic

// Load initial suggestions when page loads
loadSuggestions();

/**
 * Load niche suggestions from the API
 */
async function loadSuggestions() {
    const btn = document.getElementById('suggestBtn');
    btn.disabled = true;
    btn.innerHTML = '⏳ Loading...';
    
    try {
        const res = await fetch('/api/suggestions');
        const data = await res.json();
        
        const grid = document.getElementById('suggestionsGrid');
        grid.innerHTML = data.suggestions.map(cat => `
            <div class="suggestion-category">
                <h4>${cat.category}</h4>
                ${cat.niches.map(n => `
                    <span class="suggestion-tag" onclick="selectNiche('${n}')">${n}</span>
                `).join('')}
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
    }
    
    btn.disabled = false;
    btn.innerHTML = '🎲 More Ideas';
}

/**
 * Select a niche and trigger analysis
 */
function selectNiche(niche) {
    document.getElementById('nicheInput').value = niche;
    analyzeNiche();
}

/**
 * Analyze the selected niche
 */
async function analyzeNiche() {
    const input = document.getElementById('nicheInput');
    const niche = input.value.trim();
    
    if (!niche) {
        alert('Please enter a niche to analyze');
        return;
    }
    
    const btn = document.getElementById('analyzeBtn');
    const resultCard = document.getElementById('resultCard');
    const resultContent = document.getElementById('resultContent');
    
    btn.disabled = true;
    btn.innerHTML = '⏳ Analyzing...';
    
    resultCard.classList.add('visible');
    resultContent.innerHTML = `
        <div class="loading">
            <div class="loading-spinner"></div>
            <p>Analyzing <strong>"${niche}"</strong></p>
            <p style="font-size: 0.85em; color: #888; margin-top: 8px;">This may take 10-20 seconds</p>
        </div>
    `;
    
    // Scroll to results on mobile
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    try {
        const res = await fetch('/api/analyze?niche=' + encodeURIComponent(niche));
        const data = await res.json();
        
        if (data.error) {
            resultContent.innerHTML = `
                <div class="error">
                    <div class="error-title">⚠️ Analysis Failed</div>
                    <p>${data.error}</p>
                </div>
            `;
            return;
        }
        
        const scoreColor = data.total_score >= 75 ? '#16a34a' : 
                           data.total_score >= 60 ? '#d97706' : '#dc2626';
        const recBg = data.total_score >= 75 ? '#dcfce7' : 
                      data.total_score >= 60 ? '#fef3c7' : '#fee2e2';
        
        resultContent.innerHTML = `
            <div class="score-display">
                <div class="score-circle" style="background: ${scoreColor}">
                    <span class="score">${data.total_score}</span>
                    <span class="grade">${data.grade}</span>
                </div>
                <div class="score-info">
                    <h2>${data.niche_name}</h2>
                    <div class="recommendation" style="background: ${recBg}">
                        ${data.recommendation}
                    </div>
                </div>
            </div>
            
            <div class="breakdown">
                ${renderBreakdown('Search Volume', data.breakdown.search_volume, 25, '#667eea')}
                ${renderBreakdown('Competition', data.breakdown.competition, 25, '#764ba2')}
                ${renderBreakdown('Monetization', data.breakdown.monetization, 20, '#16a34a')}
                ${renderBreakdown('Content', data.breakdown.content_availability, 15, '#d97706')}
                ${renderBreakdown('Trends', data.breakdown.trend_momentum, 15, '#0ea5e9')}
            </div>
            
            ${renderRisingStarChannels(data.rising_star_channels)}
            
            <div id="competitorAnalysis" class="analysis-section">
                <div class="section-header">
                    <h3>🎯 Competitor Analysis</h3>
                    <button class="btn-secondary" onclick="loadCompetitorAnalysis('${niche}')">
                        Analyze Competition
                    </button>
                </div>
                <div id="competitorContent">
                    <p style="color: #666; font-style: italic;">Click "Analyze Competition" to see market saturation and top competitors</p>
                </div>
            </div>
            
            ${renderRecommendations(data.recommendations, data.total_score)}
        `;
    } catch (err) {
        resultContent.innerHTML = `
            <div class="error">
                <div class="error-title">⚠️ Something went wrong</div>
                <p>Please try again. If the problem persists, try a different niche.</p>
            </div>
        `;
    }
    
    btn.disabled = false;
    btn.innerHTML = '🔍 Analyze';
}

/**
 * Render breakdown item with score bar
 */
function renderBreakdown(label, data, max, color) {
    const pct = (data.score / max) * 100;
    return `
        <div class="breakdown-item">
            <div class="breakdown-label">${label}</div>
            <div class="breakdown-bar">
                <div class="breakdown-fill" style="width: ${pct}%; background: ${color}"></div>
            </div>
            <div class="breakdown-value">${data.score}/${max}</div>
        </div>
    `;
}

/**
 * Render rising star channels section
 */
function renderRisingStarChannels(channelData) {
    if (!channelData || !channelData.success || !channelData.channels || channelData.channels.length === 0) {
        return '';
    }
    
    const channels = channelData.channels || [];
    
    return `
        <div class="rising-stars-section">
            <div class="rising-stars-header">
                <div class="rising-stars-title">🌟 Rising Star Channels</div>
                <div class="rising-stars-subtitle">Growing channels in this niche worth checking out</div>
            </div>
            <div class="filter-section">
                <div class="filter-label">🔍 Filter Channels:</div>
                <div class="filter-controls">
                    <label class="filter-checkbox">
                        <input type="checkbox" id="facelessFilter" onchange="filterChannels()">
                        <span>🎭 Faceless Only (50%+)</span>
                    </label>
                    <label class="filter-checkbox">
                        <input type="checkbox" id="compilationFilter" onchange="filterChannels()">
                        <span>📋 Compilations</span>
                    </label>
                    <label class="filter-checkbox">
                        <input type="checkbox" id="voiceoverFilter" onchange="filterChannels()">
                        <span>🗣️ Voice-over</span>
                    </label>
                    <label class="filter-checkbox">
                        <input type="checkbox" id="screenRecordingFilter" onchange="filterChannels()">
                        <span>🖥️ Screen Recording</span>
                    </label>
                    <label class="filter-checkbox">
                        <input type="checkbox" id="longVideoFilter" onchange="filterChannels()">
                        <span>⏱️ Long Videos (20+ min)</span>
                    </label>
                </div>
            </div>
            <div class="channel-grid" id="channelGrid">
                ${channels.map(channel => `
                    <div class="channel-card" onclick="window.open('${channel.url}', '_blank')" data-content-type="${channel.content_type || 'unknown'}" data-faceless-score="${channel.faceless_score || 0}" data-has-long-videos="${channel.has_long_videos || false}" data-avg-duration="${channel.avg_duration_minutes || 0}">
                        <div class="channel-header">
                            <a href="${channel.url}" target="_blank" class="channel-name" onclick="event.stopPropagation()">
                                ${channel.name}
                            </a>
                            <div class="rising-star-score">
                                ⭐ ${Math.round(channel.rising_star_score)}
                            </div>
                        </div>
                        <div class="channel-badges">
                            <div class="content-type-badge content-type-${channel.content_type || 'unknown'}">
                                ${getContentTypeLabel(channel.content_type)}
                                ${channel.faceless_score >= 50 ? `<span class="faceless-score">(${channel.faceless_score}%)</span>` : ''}
                            </div>
                            ${channel.avg_duration_minutes && channel.avg_duration_minutes > 0 ? `
                                <div class="duration-badge ${channel.has_long_videos ? 'long-duration' : ''}">
                                    ⏱️ Avg: ${Math.round(channel.avg_duration_minutes)}m
                                </div>
                            ` : ''}
                        </div>
                        <div class="channel-stats">
                            <div class="channel-stat">
                                <span class="stat-value">${formatNumber(channel.subscribers)}</span>
                                <div class="stat-label">Subscribers</div>
                            </div>
                            <div class="channel-stat">
                                <span class="stat-value">${formatNumber(channel.total_views)}</span>
                                <div class="stat-label">Total Views</div>
                            </div>
                            <div class="channel-stat">
                                <span class="stat-value">${channel.video_count || '—'}</span>
                                <div class="stat-label">Videos</div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

/**
 * Format numbers for display (1K, 1M, etc.)
 */
function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toLocaleString();
}

/**
 * Get content type label for display
 */
function getContentTypeLabel(contentType) {
    const labels = {
        'faceless_voiceover': '🎭 Faceless',
        'compilation': '📋 Compilation', 
        'screen_recording': '🖥️ Screen Rec',
        'tutorial': '📚 Tutorial',
        'possibly_faceless': '🤔 Maybe Faceless',
        'unknown': '❓ Unknown'
    };
    return labels[contentType] || '❓ Unknown';
}

/**
 * Filter channels based on selected criteria
 */
function filterChannels() {
    const facelessFilter = document.getElementById('facelessFilter').checked;
    const compilationFilter = document.getElementById('compilationFilter').checked;
    const voiceoverFilter = document.getElementById('voiceoverFilter').checked;
    const screenRecordingFilter = document.getElementById('screenRecordingFilter').checked;
    const longVideoFilter = document.getElementById('longVideoFilter').checked;
    
    const channelCards = document.querySelectorAll('.channel-card');
    
    channelCards.forEach(card => {
        const contentType = card.dataset.contentType;
        const facelessScore = parseInt(card.dataset.facelessScore) || 0;
        const hasLongVideos = card.dataset.hasLongVideos === 'true';
        
        let show = true;
        
        // If any filter is active, start with hide
        if (facelessFilter || compilationFilter || voiceoverFilter || screenRecordingFilter || longVideoFilter) {
            show = false;
            
            // Check faceless filter
            if (facelessFilter && facelessScore >= 50) {
                show = true;
            }
            
            // Check compilation filter
            if (compilationFilter && contentType === 'compilation') {
                show = true;
            }
            
            // Check voiceover filter
            if (voiceoverFilter && contentType === 'faceless_voiceover') {
                show = true;
            }
            
            // Check screen recording filter
            if (screenRecordingFilter && contentType === 'screen_recording') {
                show = true;
            }
            
            // Check long video filter
            if (longVideoFilter && hasLongVideos) {
                show = true;
            }
        }
        
        card.style.display = show ? 'block' : 'none';
    });
}

/**
 * Render recommendations section
 */
function renderRecommendations(recommendations, originalScore) {
    if (!recommendations || recommendations.length === 0) {
        return '';
    }
    
    const betterCount = recommendations.filter(r => r.better).length;
    
    return `
        <div class="recommendations-section">
            <div class="recommendations-header">
                💡 Related Niches to Explore
                ${betterCount > 0 ? `<div class="recommendations-subtext">${betterCount} scored higher—worth checking out!</div>` : ''}
            </div>
            <div class="recommendations-grid">
                ${recommendations.map(rec => `
                    <div class="recommendation-item" onclick="selectNiche('${rec.niche}')">
                        <div class="recommendation-niche">
                            ${rec.niche}
                        </div>
                        <div class="recommendation-score">
                            <span>${rec.score}</span>
                            <span class="${rec.better ? 'recommendation-better' : 'recommendation-worse'}">
                                ${rec.better ? '↑' : '↓'}
                            </span>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

/**
 * Load competitor analysis for a niche
 */
async function loadCompetitorAnalysis(niche) {
    const content = document.getElementById('competitorContent');
    const btn = event.target;
    
    btn.disabled = true;
    btn.innerHTML = '⏳ Loading...';
    
    content.innerHTML = `
        <div class="loading">
            <div class="loading-spinner"></div>
            <p>Analyzing competitors for <strong>"${niche}"</strong></p>
        </div>
    `;
    
    try {
        const res = await fetch('/api/competitors?niche=' + encodeURIComponent(niche));
        const data = await res.json();
        
        if (data.error) {
            content.innerHTML = `
                <div class="error">
                    <div class="error-title">⚠️ Analysis Failed</div>
                    <p>${data.error}</p>
                </div>
            `;
            return;
        }
        
        content.innerHTML = renderCompetitorAnalysis(data);
        
    } catch (err) {
        content.innerHTML = `
            <div class="error">
                <div class="error-title">⚠️ Something went wrong</div>
                <p>Unable to load competitor analysis. Please try again.</p>
            </div>
        `;
    }
    
    btn.disabled = false;
    btn.innerHTML = 'Refresh Analysis';
}

/**
 * Render competitor analysis results
 */
function renderCompetitorAnalysis(data) {
    if (!data || !data.success) {
        return `
            <div class="error">
                <p>${data.error_reason || 'No competitor data available'}</p>
            </div>
        `;
    }
    
    const saturationColor = data.saturation_level === 'low' ? '#16a34a' : 
                            data.saturation_level === 'medium' ? '#d97706' : '#dc2626';
    const saturationIcon = data.saturation_level === 'low' ? '🟢' : 
                           data.saturation_level === 'medium' ? '🟡' : '🔴';
    
    return `
        <div class="competitor-analysis">
            <div class="saturation-meter">
                <div class="saturation-header">
                    <div class="saturation-level" style="color: ${saturationColor}">
                        ${saturationIcon} ${data.saturation_level.toUpperCase()} Saturation
                    </div>
                    <div class="saturation-score">${data.channel_count} active channels</div>
                </div>
                
                <div class="tier-breakdown">
                    <h4>Channel Distribution by Size</h4>
                    <div class="tier-grid">
                        <div class="tier-item">
                            <div class="tier-label">Large (100K+)</div>
                            <div class="tier-count">${data.tier_breakdown.large}</div>
                        </div>
                        <div class="tier-item">
                            <div class="tier-label">Medium (10K-100K)</div>
                            <div class="tier-count">${data.tier_breakdown.medium}</div>
                        </div>
                        <div class="tier-item">
                            <div class="tier-label">Small (1K-10K)</div>
                            <div class="tier-count">${data.tier_breakdown.small}</div>
                        </div>
                        <div class="tier-item">
                            <div class="tier-label">Micro (<1K)</div>
                            <div class="tier-count">${data.tier_breakdown.micro}</div>
                        </div>
                    </div>
                </div>
            </div>
            
            ${data.top_competitors.length > 0 ? `
                <div class="top-competitors">
                    <h4>🏆 Top Competitors to Study</h4>
                    <div class="competitors-list">
                        ${data.top_competitors.map(channel => `
                            <div class="competitor-item">
                                <div class="competitor-info">
                                    <div class="competitor-name">${channel.name}</div>
                                    <div class="competitor-stats">
                                        ${formatNumber(channel.subscribers)} subscribers • ${formatNumber(channel.avg_views)} avg views
                                    </div>
                                </div>
                                <div class="competitor-tier tier-${channel.subscriber_tier}">
                                    ${channel.subscriber_tier}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
}