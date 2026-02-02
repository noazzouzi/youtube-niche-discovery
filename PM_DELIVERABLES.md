# PRODUCT MANAGER DELIVERABLES
## YouTube Niche Discovery Engine - Business Requirements & Scoring System

**Date:** February 2, 2026  
**Project:** YouTube Niche Discovery & Validation Engine  
**Product Manager:** PM_Agent_NicheDiscovery  

---

## 📊 YOUTUBE MONETIZATION RESEARCH FINDINGS

### CPM Rates by Niche (2024-2025 Data)
Based on comprehensive analysis of 3,143+ creators and industry reports:

#### **TIER 1: Premium Monetization ($10+ CPM)**
- **Making Money Online:** $13.52 CPM (Affiliate Marketing: $22 CPM)
- **Digital Marketing:** $12.52 CPM  
- **Personal Finance/Investments:** $12.00 CPM
- **Business Strategy:** $4.70 CPM

#### **TIER 2: Strong Monetization ($4-10 CPM)**
- **Education & Science:** $4.90 CPM
- **Tech/Gadgets:** $4.15 CPM
- **Lifestyle:** $3.73 CPM  
- **Health & Sports:** $3.60 CPM
- **ASMR/Oddly Satisfying:** $3.50 CPM

#### **TIER 3: Moderate Monetization ($2-4 CPM)**
- **Fashion/Try-On Hauls:** $3.13 CPM
- **Beauty & Makeup:** $3.00 CPM (Weight Loss: up to $10 CPM)
- **Gaming:** $3.11 CPM
- **Entertainment:** $2.98 CPM
- **Cooking/DIY:** $2.50 CPM
- **Travel:** $2.00+ CPM

#### **TIER 4: Scale-Based Monetization (<$2 CPM)**
- **Fitness/Bodybuilding:** $1.60 CPM
- **Comedy/Pranks:** $1.00 CPM
- **Music/Entertainment:** Variable

### Key Geographic Multipliers
- **USA:** $14.67 CPM baseline
- **Australia:** $13.30 CPM  
- **Switzerland:** $12.98 CPM
- **Germany:** $9.79 CPM
- **UK:** $8.91 CPM

---

## 🎯 100-POINT SCORING ALGORITHM SPECIFICATION

### ALGORITHM BREAKDOWN

#### **1. SEARCH VOLUME (25 Points)**
**Measurement Methodology:**
- **Google Trends Score (0-100):** 15 points
  - 90-100 trending score = 15 points
  - 70-89 trending score = 12 points  
  - 50-69 trending score = 9 points
  - 30-49 trending score = 6 points
  - <30 trending score = 3 points

- **YouTube Search Volume (Monthly):** 10 points
  - 1M+ monthly searches = 10 points
  - 500K-1M searches = 8 points
  - 100K-500K searches = 6 points  
  - 50K-100K searches = 4 points
  - <50K searches = 2 points

**Data Sources:** Google Trends API, YouTube Search Suggest, TubeBuddy/VidIQ data

#### **2. COMPETITION LEVEL (25 Points - Inverse Scoring)**
**Methodology:** Higher competition = Lower score

- **Channel Saturation Analysis (15 points):**
  - Channels per 1M search volume ratio
  - <50 channels per 1M searches = 15 points
  - 50-100 channels = 12 points
  - 100-200 channels = 9 points
  - 200-500 channels = 6 points
  - 500+ channels = 3 points

- **Subscriber Growth Rate (10 points):**
  - Average monthly subscriber growth of top 20 channels
  - <5% monthly growth = 10 points
  - 5-10% growth = 8 points
  - 10-20% growth = 6 points
  - 20-30% growth = 4 points
  - >30% growth = 2 points

**Metrics to Track:**
- View-to-subscriber ratio
- Average video performance 
- Keyword difficulty score
- Top 20 channel analysis

#### **3. MONETIZATION POTENTIAL (20 Points)**
**CPM-Based Scoring:**
- **CPM Rate Tier (15 points):**
  - $10+ CPM = 15 points (Finance, Business)
  - $4-10 CPM = 12 points (Education, Tech)
  - $2-4 CPM = 9 points (Lifestyle, Beauty)
  - $1-2 CPM = 6 points (Gaming, Fitness)
  - <$1 CPM = 3 points (Comedy, Music)

- **Brand Safety Score (5 points):**
  - Family-friendly content = 5 points
  - General audience content = 4 points  
  - Mature content (non-explicit) = 3 points
  - Controversial topics = 2 points
  - Adult/explicit content = 1 point

**Additional Revenue Streams:**
- Affiliate marketing potential
- Sponsorship opportunities
- Product placement viability
- Course/coaching potential

#### **4. CONTENT AVAILABILITY (15 Points)**
**Source Material Abundance:**
- **Reddit Activity Score (5 points):**
  - Active subreddits with 100K+ members = 5 points
  - 50K-100K members = 4 points
  - 10K-50K members = 3 points
  - 1K-10K members = 2 points
  - <1K members = 1 point

- **TikTok Content Volume (5 points):**
  - Hashtag usage >10M posts = 5 points
  - 1-10M posts = 4 points
  - 100K-1M posts = 3 points
  - 10K-100K posts = 2 points
  - <10K posts = 1 point

- **News/Blog Coverage (5 points):**
  - Daily news coverage = 5 points
  - Weekly coverage = 4 points
  - Monthly coverage = 3 points
  - Occasional coverage = 2 points
  - Rare coverage = 1 point

#### **5. TREND MOMENTUM (15 Points)**
**Growth vs. Decline Indicators:**
- **12-Month Trend Analysis (10 points):**
  - 50%+ year-over-year growth = 10 points
  - 20-50% growth = 8 points
  - 0-20% growth = 6 points
  - 0 to -20% decline = 4 points
  - >20% decline = 2 points

- **Social Media Momentum (5 points):**
  - Cross-platform growth (TikTok, Instagram, Twitter)
  - Viral content frequency
  - Influencer adoption rate
  - Celebrity endorsements

**Leading Indicators:**
- Google search trend trajectory
- Social media mention velocity
- New channel creation rate
- Video upload frequency

---

## 📈 DATA SOURCE PRIORITY RANKING

### **PRIORITY 1: CORE PLATFORMS**
1. **YouTube Data API v3** 
   - **Rationale:** Primary platform, official API, comprehensive data
   - **Data:** Search volumes, channel stats, video performance
   - **Cost:** $0.15 per 10,000 quota units
   - **Rate Limits:** 10,000 units/day (free tier)

2. **Google Trends API**
   - **Rationale:** Best trend momentum indicator, free, reliable
   - **Data:** Search interest over time, geographic distribution
   - **Cost:** Free
   - **Rate Limits:** Reasonable for our needs

### **PRIORITY 2: SUPPLEMENTARY PLATFORMS**
3. **Reddit API (PRAW)**
   - **Rationale:** Rich content source indicator, community engagement
   - **Data:** Subreddit activity, post frequency, member counts
   - **Cost:** Free tier available
   - **Rate Limits:** 60 requests/minute

4. **TikTok Research API**
   - **Rationale:** Trend prediction, young demographic insights
   - **Data:** Hashtag volumes, viral content patterns
   - **Cost:** Enterprise pricing required
   - **Rate Limits:** TBD based on tier

### **PRIORITY 3: MARKET INTELLIGENCE**
5. **Twitter/X API v2**
   - **Rationale:** Real-time trend detection, influencer tracking
   - **Data:** Hashtag trends, mention volumes, engagement rates
   - **Cost:** $100/month for Basic tier
   - **Rate Limits:** 10,000 tweets/month (Basic)

### **FALLBACK: WEB SCRAPING**
- **Selenium-based scraping** for platforms without APIs
- **Rate limiting:** 1 request/second minimum
- **Proxy rotation:** Required for scale
- **Legal compliance:** Respect robots.txt, ToS

---

## 👤 MVP USER STORIES

### **Primary Persona: Content Creator "Sarah"**
- 25-35 years old, part-time YouTuber
- 500-10K subscribers
- Looking to optimize niche selection
- Tech-savvy but not data analyst

### **Core User Stories:**

#### **Epic 1: Niche Discovery**
- **US-001:** As Sarah, I want to search for niches by keyword so I can find profitable opportunities in my area of interest
- **US-002:** As Sarah, I want to see a ranked list of niches so I can quickly identify the best opportunities
- **US-003:** As Sarah, I want to filter niches by minimum CPM rate so I only see monetizable options

#### **Epic 2: Niche Analysis**
- **US-004:** As Sarah, I want to see detailed niche metrics so I can understand why a niche scored highly
- **US-005:** As Sarah, I want to compare up to 3 niches side-by-side so I can make informed decisions
- **US-006:** As Sarah, I want to see competitor analysis so I can understand the competitive landscape

#### **Epic 3: Trend Monitoring**
- **US-007:** As Sarah, I want to set up alerts for high-scoring niches so I'm notified of new opportunities
- **US-008:** As Sarah, I want to track niche score changes over time so I can spot declining opportunities
- **US-009:** As Sarah, I want to see trending keywords in my niche so I can create timely content

#### **Epic 4: Content Planning**
- **US-010:** As Sarah, I want to see content gap analysis so I can identify underserved topics
- **US-011:** As Sarah, I want export functionality so I can share findings with collaborators
- **US-012:** As Sarah, I want to bookmark promising niches so I can research them later

### **MVP Feature Requirements:**
1. **Niche Search & Discovery Engine**
2. **Real-time Scoring Dashboard**  
3. **Basic Competitor Analysis**
4. **Trend Visualization (30-day)**
5. **Export to CSV/PDF**
6. **Email Alerts (90+ score threshold)**

### **Phase 2 Features:**
- Advanced competitor intelligence
- Content gap analysis
- Multi-platform trend correlation
- API access for power users
- White-label solutions

---

## ⚖️ LEGAL COMPLIANCE CHECKLIST

### **MANDATORY COMPLIANCE REQUIREMENTS**

#### **1. Data Protection (GDPR/CCPA)**
- [ ] **No Personal Data Collection** without explicit consent
- [ ] **Privacy Policy** clearly stating data usage
- [ ] **Data Minimization** - collect only necessary public metrics
- [ ] **Right to Erasure** implementation for any user data
- [ ] **Data Processing Agreement** for EU users

#### **2. Platform Terms of Service**

##### **YouTube API Compliance:**
- [ ] Use **official YouTube Data API v3** only
- [ ] Respect **API quotas and rate limits**
- [ ] **No scraped YouTube data** (per Developer Policies)
- [ ] **Attribution requirements** met
- [ ] **No video downloading** or unauthorized access

##### **General Web Scraping:**
- [ ] **Respect robots.txt** files on all platforms
- [ ] **Rate limiting:** Maximum 1 request/second per domain
- [ ] **User-Agent identification** with contact information
- [ ] **No authentication bypass** or login-protected content
- [ ] **Public data only** - no paywall circumvention

#### **3. Technical Compliance**
- [ ] **Proxy rotation** to distribute load
- [ ] **Error handling** to avoid aggressive retry patterns
- [ ] **Monitoring system** to detect blocking
- [ ] **Graceful degradation** when APIs unavailable
- [ ] **Data retention policy** (max 90 days for trend analysis)

#### **4. Business Protection**
- [ ] **Terms of Service** for our platform
- [ ] **Acceptable Use Policy** 
- [ ] **Disclaimer** about data accuracy and investment advice
- [ ] **Rate limiting** on our own API (prevent abuse)
- [ ] **Usage monitoring** and abuse detection

### **LEGAL RISK MITIGATION**
- **Low Risk:** Google Trends, Reddit public data, YouTube API
- **Medium Risk:** TikTok scraping, Twitter API (paid tier)
- **High Risk:** Any authentication bypass, personal data collection

### **RECOMMENDED ACTIONS**
1. **Legal Review** before production deployment
2. **Insurance Coverage** for technology E&O
3. **Incident Response Plan** for platform blocking
4. **Regular Compliance Audits** (quarterly)

---

## 📋 IMPLEMENTATION ROADMAP

### **Week 1: Foundation (Current)**
- Business requirements finalization ✓
- Technical architecture design
- Legal compliance framework
- MVP feature specification

### **Week 2: Core Development**
- Scoring algorithm implementation
- Primary data source integration
- Basic dashboard development
- Testing framework setup

### **Week 3: Enhancement & Launch**
- Advanced features implementation
- Performance optimization
- Security review and compliance audit
- Beta testing and feedback integration

### **Success Metrics:**
- **Business:** 80% scoring accuracy vs. known profitable niches
- **Technical:** <30s response time, 99% uptime
- **User:** 70% user engagement rate, <5% churn

---

## 🔬 VALIDATION METHODOLOGY

### **Algorithm Accuracy Testing:**
1. **Control Group:** 50 known profitable niches (Mr Beast, Ali Abdaal, etc.)
2. **Test Score:** Our algorithm should score them 80+ points
3. **Benchmark Comparison:** Against existing tools (TubeBuddy, VidIQ)
4. **A/B Testing:** Different scoring weights to optimize accuracy

### **Business Validation:**
- **Creator Interviews:** 10+ established YouTubers for feedback
- **Market Research:** Competitive analysis vs. existing solutions
- **Financial Modeling:** Unit economics and pricing strategy

This comprehensive business requirements document provides the foundation for building a data-driven, legally compliant, and commercially viable YouTube Niche Discovery Engine. The 100-point scoring algorithm balances multiple factors to identify genuinely profitable opportunities while our phased approach ensures rapid time-to-market with iterative improvements.