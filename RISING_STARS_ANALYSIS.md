# Rising Stars Detection Analysis

## Current Implementation

**Location:** `/root/clawd/youtube-niche-discovery/app/discovery.py` (lines 36-240)

### What It Does:
```python
def _calculate_rising_star_score_from_aggregated_data(self, channel: dict) -> float:
    # Views per subscriber (viral potential) - max 40 points
    # Low subscriber bonus (opportunity) - max 30 points  
    # Activity score (videos in search results) - max 30 points
```

### Problems:
1. **No actual growth rate** - Just scores current state, not trajectory
2. **Sorts by video count** - Activity ≠ growth
3. **No historical comparison** - Can't calculate "growing 200% month-over-month"
4. **`avg_growth` is random!** - Line 153 in `scorer.py`: `'avg_growth': random.uniform(0.08, 0.18)`

---

## Data Availability Research

### YouTube Data API v3
- ❌ **No historical data** - Only provides current snapshots
- ❌ **No subscriber history** - Can't see last month's count
- ✅ Provides: current subscribers, views, video count

### yt-dlp (Current Data Source)
Available per video:
```
channel_follower_count: 4450000
view_count: 1739469704  
upload_date: '20091025'
like_count: 18775988
comment_count: 2400000
```
- ❌ **No historical channel stats**
- ✅ **Video upload dates** - Can calculate upload frequency
- ✅ **View/like/comment counts per video** - Can calculate engagement velocity

### Social Blade API
- ✅ **Has historical data** (30-day subscriber gains)
- ❌ **Requires paid API key** ($5/month minimum)
- ❌ **Rate limited** (varies by plan)
- ❌ **No free tier for commercial use**

---

## Practical Growth Indicators (No Historical Data Required)

### 1. **View Velocity** (Best Option)
Compare views on recent videos vs older videos:
```python
def calculate_view_velocity(videos):
    """Calculate growth by comparing recent vs older video performance"""
    recent = [v for v in videos if uploaded_within_days(v, 30)]
    older = [v for v in videos if uploaded_between_days(v, 60, 180)]
    
    avg_recent_views = mean([v['view_count'] for v in recent])
    avg_older_views = mean([v['view_count'] for v in older])
    
    if avg_older_views > 0:
        velocity = (avg_recent_views - avg_older_views) / avg_older_views
        return velocity  # 0.5 = 50% growth
```

### 2. **Upload Acceleration**
Channels posting more frequently = growing:
```python
def upload_acceleration(videos):
    """Detect if upload frequency is increasing"""
    last_30_days = count_videos_in_period(videos, 30)
    prev_30_days = count_videos_in_period(videos, 60, 30)
    
    if prev_30_days > 0:
        return last_30_days / prev_30_days
```

### 3. **Engagement Ratio Trend**
Compare engagement (likes+comments/views) on new vs old videos:
```python
def engagement_trend(videos):
    recent_engagement = calculate_engagement_ratio(recent_videos)
    older_engagement = calculate_engagement_ratio(older_videos)
    return recent_engagement / older_engagement  # >1 = improving
```

### 4. **Views Per Subscriber Ratio**
High ratio = viral potential = likely growing:
```python
def viral_potential(channel):
    recent_avg_views = mean(recent_video_views)
    subscribers = channel['subscribers']
    return recent_avg_views / subscribers  # >1 = each video reaches beyond subs
```

### 5. **Channel Age vs Size Ratio**
Small channels with high views = fast growth:
```python
def growth_efficiency(channel):
    age_days = days_since(channel['created_at'])
    subscribers_per_day = channel['subscribers'] / age_days
    return subscribers_per_day  # Higher = faster growth
```

---

## Proposed Solution

### Phase 1: Improved Scoring (No API Changes)

```python
def calculate_true_rising_star_score(channel: dict, videos: list) -> dict:
    """Enhanced rising star detection using available data"""
    
    scores = {}
    
    # 1. View Velocity (30 points max)
    recent_videos = [v for v in videos if is_recent(v, 30)]
    older_videos = [v for v in videos if is_older(v, 60, 180)]
    
    if recent_videos and older_videos:
        velocity = avg_views(recent_videos) / avg_views(older_videos)
        scores['velocity'] = min(velocity * 15, 30)
    else:
        scores['velocity'] = 15  # Unknown
    
    # 2. Upload Frequency Trend (20 points max)
    last_month_count = count_uploads(videos, 30)
    prev_month_count = count_uploads(videos, 60, 30)
    if prev_month_count > 0:
        upload_trend = last_month_count / prev_month_count
        scores['upload_trend'] = min(upload_trend * 10, 20)
    else:
        scores['upload_trend'] = 10
    
    # 3. Viral Potential (25 points max)
    views_per_sub = avg_views(recent_videos) / max(channel['subscribers'], 1)
    if views_per_sub >= 1.0:
        scores['viral'] = 25
    elif views_per_sub >= 0.5:
        scores['viral'] = 20
    elif views_per_sub >= 0.2:
        scores['viral'] = 15
    else:
        scores['viral'] = 10
    
    # 4. Engagement Quality (15 points max)
    engagement = calculate_engagement(recent_videos)
    scores['engagement'] = min(engagement * 100, 15)
    
    # 5. Sweet Spot Size (10 points max)
    subs = channel['subscribers']
    if 1000 <= subs <= 50000:
        scores['size_opportunity'] = 10
    elif 50000 <= subs <= 200000:
        scores['size_opportunity'] = 7
    else:
        scores['size_opportunity'] = 3
    
    total = sum(scores.values())
    
    return {
        'score': total,
        'breakdown': scores,
        'growth_indicators': {
            'view_velocity': f'{(scores["velocity"]/15 - 1)*100:.0f}%' if scores['velocity'] > 15 else 'stable',
            'upload_trend': 'accelerating' if scores['upload_trend'] > 12 else 'stable',
            'viral_potential': 'high' if scores['viral'] >= 20 else 'moderate'
        }
    }
```

### Phase 2: Local Historical Tracking (Future)

Store snapshots in SQLite:
```python
class ChannelTracker:
    def record_snapshot(self, channel_id, subscribers, views):
        """Store daily/weekly snapshots"""
        db.insert('channel_history', {
            'channel_id': channel_id,
            'date': today(),
            'subscribers': subscribers,
            'total_views': views
        })
    
    def calculate_actual_growth(self, channel_id, days=30):
        """Compare current vs historical snapshot"""
        old = db.get_snapshot(channel_id, days_ago=days)
        current = db.get_latest(channel_id)
        
        if old:
            sub_growth = (current.subs - old.subs) / old.subs
            view_growth = (current.views - old.views) / old.views
            return {'subscriber_growth': sub_growth, 'view_growth': view_growth}
```

### Phase 3: Social Blade Integration (Optional)

If API budget available:
```python
class SocialBladeClient:
    def get_30_day_growth(self, channel_id):
        response = requests.get(
            f'https://api.socialblade.com/youtube/channel/{channel_id}',
            headers={'Authorization': f'Bearer {API_KEY}'}
        )
        data = response.json()
        return {
            'subscriber_gain_30d': data['subscribers_30d'],
            'view_gain_30d': data['views_30d'],
            'estimated_monthly_earnings': data['earnings']
        }
```

---

## Implementation Priority

| Priority | Approach | Effort | Accuracy |
|----------|----------|--------|----------|
| 1 | View Velocity from video dates | Low | Medium |
| 2 | Upload Frequency Trend | Low | Medium |
| 3 | Local SQLite Tracking | Medium | High (over time) |
| 4 | Social Blade API | Low | High |

---

## Key Data Requirements

To implement Phase 1, need to fetch **multiple videos per channel**:

```python
# Current: Only gets 1 video per channel
# Needed: Get 5-10 recent videos with full metadata

def get_channel_video_history(channel_id, limit=10):
    """Fetch recent videos with view counts for velocity calculation"""
    # Use yt-dlp to get channel's recent uploads
    cmd = ['yt-dlp', '--dump-json', '--no-download', 
           '--playlist-items', '1:10',
           f'https://www.youtube.com/channel/{channel_id}/videos']
```

This adds ~1-2 seconds per channel but enables real growth calculation.

---

## Summary

**Root Cause:** YouTube doesn't expose historical data. Current "growth" metrics are random numbers.

**Best Solution:** Calculate **View Velocity** by comparing recent video performance to older videos. This is a reliable proxy for channel growth without requiring external APIs or historical tracking.

**Quick Win:** Replace `random.uniform(0.08, 0.18)` with actual view velocity calculation.
