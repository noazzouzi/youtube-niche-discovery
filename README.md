# 🚀 YouTube Niche Discovery Engine

**Discover profitable YouTube niches using PM Agent's research-backed 100-point scoring algorithm + LIVE YouTube data**

![Version](https://img.shields.io/badge/version-4.0.0-blue.svg)
![Data Source](https://img.shields.io/badge/yt--dlp-LIVE-red.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🔴 yt-dlp Powered (No API Keys Required!)

This tool uses **yt-dlp** for direct YouTube data extraction - **no API keys needed**:

- **🔴 yt-dlp** - Direct YouTube data extraction, no quotas, no API keys
- **📈 Google Trends** - Real-time trend analysis and momentum scoring  
- **💰 PM Agent Research** - Actual CPM data from 3,143+ creators
- **🆓 Completely FREE** - No API costs, no rate limits, no setup

## 📊 What It Analyzes

**100-point scoring algorithm based on:**

- **Search Volume (25 pts)** - Real YouTube search results + Google Trends score
- **Competition Level (25 pts)** - Actual channel counts + growth analysis  
- **Monetization Potential (20 pts)** - PM Agent's real CPM data from 3,143+ creators
- **Content Availability (15 pts)** - Social media volume estimates
- **Trend Momentum (15 pts)** - Live Google Trends + YouTube growth patterns

## ⚡ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/youtube-niche-discovery.git
cd youtube-niche-discovery

# 2. Install dependencies
pip install pytrends yt-dlp

# 3. Run the server
python3 enhanced_ui_server.py
```

**Access at:** `http://localhost:8080`

That's it! No API keys, no configuration, no quotas.

## 🏗️ Architecture

```
enhanced_ui_server.py    # Main server (all-in-one)
├── YtDlpDataSource      # Primary data source via yt-dlp
├── TrendsAPI            # Google Trends integration
├── NicheScorer          # 100-point scoring algorithm
├── ChannelDiscovery     # Rising star channel finder
└── RecommendationEngine # Related niche suggestions

ytdlp_data_source.py     # yt-dlp wrapper (imported by server)
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `enhanced_ui_server.py` | Main HTTP server with embedded UI |
| `ytdlp_data_source.py` | yt-dlp data extraction wrapper |
| `frontend/` | React frontend (optional) |
| `tests/` | Test suite |

## 📋 API Endpoints

### Analyze a Niche
```bash
GET /api/analyze?niche=your+niche+here
```

### Get Suggestions
```bash
GET /api/suggestions
```

### Discover Rising Star Channels
```bash
GET /api/channels?niche=your+niche+here
```

### Status Check
```bash
GET /api/status
```

## 🏆 Example Analysis

**"Japanese TV Show"** analysis:

```json
{
  "niche_name": "Japanese tv show", 
  "total_score": 73.7,
  "grade": "B+",
  "recommendation": "👍 GOOD: Solid potential with real YouTube metrics",
  "breakdown": {
    "search_volume": {
      "score": 19.0,
      "details": "Strong search presence, 68/100 trend score",
      "data_source": "yt-dlp + Google Trends"
    },
    "competition": {
      "score": 21.0, 
      "details": "Medium competition, growing niche",
      "data_source": "yt-dlp channel analysis"
    },
    "monetization": {
      "score": 13.0,
      "details": "$2.80 estimated CPM (Entertainment/International)",
      "data_source": "PM Research: 3,143+ creators"
    }
  }
}
```

## 💰 PM Agent Research Credits

Built on **real research** from PM Agent's analysis:

- **3,143+ creators** analyzed across 15+ niches
- **Geographic data** with US baseline $14.67 CPM vs global $2.80
- **Tier system:** Premium ($10+), Strong ($4-10), Moderate ($2-4)

**Key CPM Findings:**
| Category | CPM Rate | Source |
|----------|----------|--------|
| Making Money Online | $13.52 | PM Research: Highest tier |
| AI/Tech Premium | $8.00+ | PM Research: Tech + AI premium |
| Finance | $12.00 | PM Research: Tier 1 Premium |
| Entertainment | $2.80 | PM Research: International content |
| Gaming | $3.11 | PM Research: Gaming category |

## 🚀 Deployment

### Local Development  
```bash
python3 enhanced_ui_server.py
# Access: http://localhost:8080
```

### Docker Deployment
```bash
docker build -t niche-discovery .
docker run -p 8080:8080 niche-discovery
```

### Background/Production
```bash
nohup python3 enhanced_ui_server.py > server.log 2>&1 &
```

## 🔧 Requirements

- Python 3.7+
- yt-dlp (`pip install yt-dlp`)
- pytrends (`pip install pytrends`)

## 📁 Project Structure

```
youtube-niche-discovery/
├── enhanced_ui_server.py     # Main server (run this!)
├── ytdlp_data_source.py      # yt-dlp data extraction
├── requirements.txt          # Python dependencies
├── frontend/                 # React frontend
├── tests/                    # Test suite
├── docs/                     # Documentation
└── deprecated/               # Old/unused files
```

## 🤝 Contributing

1. Fork the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run locally: `python3 enhanced_ui_server.py`
4. Create feature branch: `git checkout -b feature/amazing-feature`
5. Submit Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Credits

- **PM Agent:** Original 100-point algorithm + CPM research (3,143+ creators)
- **yt-dlp:** YouTube data extraction
- **pytrends:** Google Trends integration

---

**Start analyzing in seconds - no API keys needed!**

```bash
pip install pytrends yt-dlp && python3 enhanced_ui_server.py
```
