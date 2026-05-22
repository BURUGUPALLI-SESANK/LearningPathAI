# AI-Powered Personalized Learning Path Generator - Backend

A Flask-based REST API backend for the AI-Powered Personalized Learning Path Generator system with **Machine Learning** and **Adaptive Learning** capabilities.

## 🚀 New Features (v2.0)

### 1. **ML-Based Course Recommendations**
- Uses TF-IDF vectorization and cosine similarity
- Combines machine learning (70%) with rule-based scoring (30%)
- Provides relevance scores for each recommended course

### 2. **Employability Score System**
- Comprehensive job readiness assessment (0-100 scale)
- Three-factor scoring:
  - Skills Mastery (40 points)
  - Course Completion (30 points)
  - Industry Alignment (30 points)
- Real-time readiness level classification

### 3. **Adaptive Learning Engine**
- Analyzes learner performance automatically
- Tracks learning velocity (Fast/Steady/Slow)
- Provides personalized recommendations
- Auto-suggests path regeneration when needed

### 4. **Enhanced Intelligent Tutoring**
- Context-aware chatbot responses
- Employability score queries
- Performance analytics integration
- Adaptive learning insights

## Features

- Learner profile registration with Gmail authentication
- Skill assessment submission with 1-5 level proficiency
- AI-powered learning path generation with skill gap analysis
- **ML-based course recommendation system**
- **Employability scoring and job readiness assessment**
- **Adaptive learning with performance tracking**
- Progress tracking and dashboard data
- Feedback collection and sentiment analysis
- Customer behavior analytics

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**New Dependencies:**
- `scikit-learn` - For ML-based recommendations
- `numpy` - For numerical computations

### 2. Prepare Data Files

Ensure the following CSV files exist in the `data/` directory:
- `students.csv` - Sample student data
- `courses.csv` - Course catalog with metadata
- `feedbacks.csv` - User feedback data (auto-generated)

### 3. Run the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Core Endpoints

**POST** `/register` - Register learner profile  
**POST** `/assessment` - Submit skill assessment  
**POST** `/generate-path` - Generate personalized learning path (now with ML recommendations)  
**GET** `/dashboard/<user_id>` - Get dashboard data  
**POST** `/update-progress` - Update progress (now with adaptive learning)

### New Endpoints (v2.0)

**GET** `/employability/<user_id>` - Get employability score  
**GET** `/adaptive-insights/<user_id>` - Get adaptive learning insights  
**POST** `/chat` - Enhanced intelligent tutoring chatbot

### Analytics Endpoints

**POST** `/submit-feedback` - Submit user feedback  
**GET** `/feedbacks` - Get feedback analytics with sentiment analysis  
**GET** `/analytics-data` - Get customer behavior analytics

## Machine Learning Features

### TF-IDF Course Recommendation
The system uses Term Frequency-Inverse Document Frequency (TF-IDF) to match learner skills with course content:

1. Creates a skill profile from learner's assessment
2. Vectorizes course descriptions and skills
3. Calculates cosine similarity between learner and courses
4. Combines ML scores with rule-based factors
5. Returns top 10 most relevant courses

### Employability Scoring Algorithm

```
Overall Score = Skills Score + Completion Score + Industry Score

Skills Score (40 pts):
- Based on average skill level (1-5 scale)
- Penalty for skill gaps
- Max: 40 points

Completion Score (30 pts):
- Based on course completion percentage
- Weighted by total courses
- Max: 30 points

Industry Score (30 pts):
- Experience level bonus (5-25 pts)
- Domain demand multiplier (1.0-1.2x)
- Course relevance score (0-10 pts)
- Max: 30 points
```

### Adaptive Learning Engine

Tracks and analyzes:
- Total study sessions
- Average completion rate
- Learning velocity classification
- Performance-based recommendations
- Auto-regeneration triggers

## Readiness Levels

| Score Range | Level | Description |
|-------------|-------|-------------|
| 80-100 | Job Ready | Highly employable, ready to apply |
| 60-79 | Nearly Ready | Complete 2-3 more courses |
| 40-59 | Developing | Focus on completing learning path |
| 0-39 | Early Stage | Foundation building phase |

## Project Structure

```
.
├── app.py                 # Main Flask application with ML features
├── requirements.txt       # Python dependencies (includes scikit-learn)
├── README.md             # This file
├── employability.html    # New employability score page
└── data/
    ├── students.csv      # Student dataset
    ├── courses.csv       # Course catalog
    └── feedbacks.csv     # Feedback data
```

## Technologies Used

- **Flask** - Web framework
- **Flask-CORS** - Cross-Origin Resource Sharing
- **Pandas** - CSV data processing
- **NumPy** - Numerical computations
- **scikit-learn** - Machine learning (TF-IDF, cosine similarity)
- **Python** - Programming language

## Notes

- Data is stored in-memory (suitable for development/demo)
- For production, consider using a database (SQLite, PostgreSQL, etc.)
- CSV files are loaded at startup
- CORS is enabled for frontend integration
- ML models are lightweight and run in real-time

## Testing

Example cURL command for employability score:
```bash
curl http://localhost:5000/employability/user_20241201120000
```

Example cURL command for adaptive insights:
```bash
curl http://localhost:5000/adaptive-insights/user_20241201120000
```

## Performance Metrics

- ML recommendation processing: ~50-100ms per request
- Employability calculation: ~10-20ms per request
- Adaptive analysis: ~5-10ms per request

## Future Enhancements

- Integration with real course APIs (Coursera, Udemy, edX)
- Deep learning models for advanced recommendations
- Real-time skill demand tracking from job markets
- Predictive analytics for career trajectory
- National skill framework integration (NSQF, NQF)

