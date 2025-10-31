# 🐦 X Post Automation

AI-powered platform for analyzing, planning, and automatically creating viral posts on X (Twitter).

## ✨ Features

- 🔐 OAuth2 Authentication with JWT tokens
- 📊 Analytics Dashboard with engagement metrics
- 🤖 AI Content Generation with Google Gemini
- 📅 Smart Scheduler for automated posting
- 🎯 Viral Prediction scoring
- 🔄 Auto-posting with Celery workers
- 📈 Campaign Management
- 📉 Engagement Analytics and Trends

## 🏗️ Architecture

### Backend (FastAPI)
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database for storing tweets, metrics, campaigns
- **Redis** - Message broker for Celery
- **Celery** - Task queue for scheduled posting and metrics collection
- **Google Gemini AI** - Free AI for tweet generation
- **SQLAlchemy** - ORM for database operations

### Frontend (React + Vite)
- **React 18** - Modern UI library
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **Vite** - Fast build tool and dev server

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Google Gemini API key (free tier: 15 req/min, 1500/day)
- Optional: X (Twitter) API credentials

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/JKM2828/x-post-automation.git
cd x-post-automation
```

2. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
# Required for AI generation
GEMINI_API_KEY=your_gemini_api_key_here

# Optional for posting to Twitter
X_API_KEY=your_api_key_here
X_API_SECRET=your_api_secret_here

# Application secrets
SECRET_KEY=your-random-secret-key-here
```

3. **Start the application**
```bash
docker-compose up -d
```

This will start:
- Backend API (port 8000)
- Frontend (port 3000)
- PostgreSQL (port 5432)
- Redis (port 6379)
- Celery worker
- Celery beat scheduler

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs
- Backend health: http://localhost:8000/health

## 📖 Usage

### 1. Register/Login
- Navigate to http://localhost:3000
- Create an account with username
- Login to access the dashboard

### 2. Generate AI Tweets
- Go to "AI Generate" page
- Enter a topic (e.g., "AI and future of work")
- Select tone (professional, casual, humorous, inspirational)
- Choose number of variants (1-5)
- Click "Generate Tweets"
- Generated tweets are saved as drafts

### 3. Manage Tweets
- Go to "Tweets" page
- View all tweets (drafts, scheduled, posted)
- Create manual tweets
- Schedule tweets for later
- Post tweets immediately

### 4. Create Campaigns
- Go to "Campaigns" page
- Create recurring tweet campaigns
- Set cron expressions for automation
- Activate/deactivate campaigns

### 5. View Analytics
- Dashboard shows:
  - Total tweets posted
  - Total engagement (likes + retweets + replies)
  - Average engagement rate
  - Best posting hours
  - Recent tweets performance

## 🔧 Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Run Celery Worker Locally
```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

### Run Celery Beat Locally
```bash
cd backend
celery -A app.workers.celery_app beat --loglevel=info
```

## 🧪 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token

#### Tweets
- `GET /api/tweets/` - List all tweets
- `POST /api/tweets/` - Create tweet
- `POST /api/tweets/{id}/post` - Post tweet to Twitter

#### AI Generation
- `POST /api/ai/generate` - Generate tweet variants with AI
- `POST /api/ai/analyze` - Analyze tweet sentiment

#### Analytics
- `GET /api/analytics/summary` - Get analytics summary
- `GET /api/analytics/engagement-trends` - Get engagement over time

#### Campaigns
- `GET /api/campaigns/` - List campaigns
- `POST /api/campaigns/` - Create campaign
- `POST /api/campaigns/{id}/toggle` - Toggle campaign status

## 🔑 Getting API Keys

### Google Gemini API (Free)
1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Add to `.env` as `GEMINI_API_KEY`
4. Free tier: 15 requests/minute, 1500/day

### X (Twitter) API (Optional)
1. Visit https://developer.twitter.com
2. Create a new app
3. Get API keys and tokens
4. Add to `.env`

## 📊 Background Tasks

Celery workers handle:
- **Post Scheduled Tweets** - Every 5 minutes
- **Fetch Tweet Metrics** - Every 15 minutes
- **Retrain Viral Model** - Daily at midnight

## 🐛 Troubleshooting

### Backend won't start
- Check if ports 8000, 5432, 6379 are available
- Verify `.env` file exists and has correct values
- Check logs: `docker-compose logs backend`

### Frontend won't start
- Check if port 3000 is available
- Verify API URL in frontend/.env
- Check logs: `docker-compose logs frontend`

### Can't post to Twitter
- Verify X API credentials in `.env`
- Check user has API key configured in database
- Review backend logs for errors

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Google Gemini for free AI API
- FastAPI for excellent Python framework
- React team for amazing frontend library