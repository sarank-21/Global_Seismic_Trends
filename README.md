# **🌍 Global Seismic Trends: Data-Driven Earthquake Insights**
## **📖 About the Project**

Global Seismic Trends is a data-driven web application built using Streamlit, MySQL, and USGS Earthquake APIs to analyze worldwide earthquake activity.
The project focuses on collecting, storing, analyzing, and visualizing seismic data to uncover meaningful earthquake patterns, risks, and trends over time.

This application transforms raw earthquake data into actionable insights for risk assessment, research, and educational purposes.

## **🔨 Development Process**

The Global Seismic Trends project was developed following a structured, step-by-step approach to ensure scalability, data accuracy, and meaningful insights.

### **1️⃣ Requirement Analysis**

* Identified key objectives: earthquake data collection, storage, analysis, and visualization
* Defined analysis dimensions: magnitude, depth, time, location, tsunami impact, and data quality
* Selected appropriate tools: Streamlit, MySQL, Python, USGS API

### **2️⃣ Data Collection**

* Integrated the USGS Earthquake API
* Implemented year-wise and month-wise data fetching
* Applied filters:
     * Minimum magnitude ≥ 3.0
     * User-selected time range
* Introduced rate limiting to avoid API overload

### **3️⃣ Database Design**

* Designed a structured MySQL schema
* Created a normalized Earthquake table
* Implemented:
    * Primary key constraints
    * Duplicate record prevention
    * Efficient time-based querying

### **4️⃣ Data Cleaning & Transformation**

* Converted timestamps to readable datetime formats
* Handled missing values using statistical imputation
* Derived new features:
    * Shallow vs Deep earthquake classification
    * Magnitude severity flags
    * Temporal attributes (Year, Month, Day, Day of Week)
* Extracted country information from location strings

### **5️⃣ Backend Processing**

* Built reusable SQL queries for each analytical question
* Implemented session-based navigation using Streamlit
* Optimized queries for large datasets and time-range filtering

### **6️⃣ Data Analysis**

* Performed multi-level analysis including:
* Magnitude & Depth insights
* Temporal patterns (year, month, hour, weekday)
* Tsunami and alert severity evaluation
* Data quality assessment using RMS, GAP, and NST
* Seismic trend and growth analysis

### **7️⃣ Visualization & UI Design**

* Developed an interactive Streamlit dashboard
* Organized analysis into logical sections
* Enabled dynamic filtering using sidebar controls
* Displayed tabular insights for clarity and interpretability

### **8️⃣ Testing & Validation**

* Verified duplicate handling across multiple runs
* Validated query accuracy against raw data
* Tested different year ranges and edge cases
* Ensured consistent performance for large datasets

### **9️⃣ Documentation & Deployment**

* Created detailed project documentation (README)
* Structured code for readability and maintenance
* Prepared the project for GitHub publication

## **✨ Key Features**
### **📈 Magnitude & Depth Analysis**
  * Identifies strongest and deepest earthquakes, shallow high-risk events, and average depth trends by country.

### **⏳ Time-Based Seismic Trends**
   * Analyzes earthquake frequency by year, month, weekday, and hour to reveal temporal patterns in seismic activity.

### **🏆 Event Type & Data Quality Metrics**
   * Evaluates earthquake types, review status, station coverage (NST), RMS, and GAP to assess data reliability.

### **🌊 Tsunami & Alert Insights**
   * Tracks tsunami-triggering events and analyzes alert levels (Green, Yellow, Orange, Red) for risk prioritization.

### **📑 Advanced Seismic Pattern Analysis**
   * Includes year-over-year growth rates, mixed-depth occurrences, and identification of highly active seismic regions.

### **⚓ Depth, Location & Distance-Based Insights**
   * Examines equatorial earthquake depth patterns, shallow-to-deep ratios, deep-focus hotspots, and reliability errors.

## **⚙️ Tech Stack**
### **🧠 Programming Language**
* Python – Core language for data processing, API integration, database operations, and analytics

### **🌐 Frontend / Web Framework**
* Streamlit – Interactive web application framework used to build dashboards and enable user-driven analysis

### **🗄️ Database**
* MySQL – Relational database for storing structured earthquake data efficiently
* SQLAlchemy – ORM and database connection management

### **🔌 Data Source**

* USGS Earthquake API – Official data source for real-time and historical global earthquake events (GeoJSON format)

### **📊 Data Processing & Analysis**

* Pandas – Data cleaning, transformation, aggregation, and analysis
* Datetime – Time-based feature extraction (year, month, weekday, hour)

### **🌍 Geospatial & Seismic Attributes**

* Latitude, Longitude, Depth
* Magnitude, RMS, GAP, NST
* Tsunami indicators & alert levels

### **🔄 Backend Utilities**

* Requests – API communication and data fetching
* Time – Rate limiting and API call management

### **🛠️ Development & Deployment Tools**

* Git & GitHub – Version control and project hosting
* VS Code / IDE – Development environment
* Localhost Deployment – Streamlit local server

### **📌 Architecture Style**

* API-driven data ingestion
* Relational database-backed analytics
* Modular Streamlit UI design
* Session-based navigation

## **📋 Project Overview**

The project:

   * Fetches real-time and historical earthquake data from the USGS Earthquake API
   * Stores structured data in a MySQL database
   * Performs multi-dimensional seismic analysis
   * Provides an interactive Streamlit dashboard for exploration

## **🎯 Features**
### **📅 Dynamic Year-Based Data Selection**
   * Users can select custom year ranges to fetch and analyze earthquake data interactively.

### **🔄 Automated Data Ingestion**
   * Automatically retrieves earthquake data from the USGS API and avoids duplicate entries using database checks.

### **🧹 Data Cleaning & Feature Engineering**
  * Handles missing values, converts timestamps, extracts countries, and creates derived fields such as:
     * Earthquake depth category (Shallow / Deep)
     * Magnitude severity flags
     * Temporal attributes (Year, Month, Day, Weekday)

### **🗄️ Persistent Database Storage**
   * Stores processed data in a MySQL database for fast querying and repeated analysis without re-fetching.

### **📊 Comprehensive Seismic Analysis Modules**
  Includes:
    * Magnitude & Depth Analysis
    * Time-Based Trends
    * Event Type & Data Quality Metrics
    * Tsunami & Alert Analysis
    * Seismic Patterns & Growth Trends
    * Depth, Location & Distance-Based Insights

### **🌊 Tsunami & Alert Monitoring**
   * Identifies tsunami-triggering earthquakes and classifies events by alert severity (Green, Yellow, Orange, Red).

### **🏆 Data Quality Evaluation**
   * Uses RMS, GAP, and station count (NST) to assess the reliability of earthquake records.

### **📈 Trend & Growth Analysis**
   * Computes year-over-year earthquake growth rates and identifies highly active seismic regions.

### **🎛️ Interactive Streamlit Interface**
   * Clean UI with buttons, dropdowns, and session-based navigation for smooth user experience.

### **🚀 Scalable & Extensible Design**
   * Modular code structure allows easy integration of new analytics, visualizations, or machine learning models.

## **⚙️ Setup & Installation**
### **1️⃣ Prerequisites**

Ensure you have the following installed:

   * Python 3.9+
   * MySQL Server
   * Git

### **2️⃣ Clone the Repository**
```
git clone https://github.com/your-username/global-seismic-trends.git
cd global-seismic-trends
```

### **3️⃣ Create a Virtual Environment & Activate**
```
python -m venv GST
# Activate environment
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)

#Install packages
pip install -r requirements.txt
```
requirements.txt:

    * streamlit
    * pandas
    * sqlalchemy
    * pymysql
    * requests

### **4️⃣ MySQL Configuration**

`create_engine("mysql+pymysql://root:password@localhost")`

### **5️⃣ Run the Application**

`streamlit run app.py`

## **📊 Dataset**
   * Source: USGS Earthquake API
   * Format: GeoJSON → Structured MySQL tables
   * Magnitude Filter: ≥ 3.0
   * Time Range: User-selectable (2015 – Present)

**Key Attributes:**
    * Magnitude, Depth, Location
    * Earthquake Type & Status
    * RMS, GAP, Station Count (NST)
    * Tsunami Indicators
    * Alert Levels
    * Temporal Features (Year, Month, Day, Hour)

## **🔄 How It Works**
   * User selects a year range
   * API fetches earthquake data month-wise
   * Duplicate records are skipped
   * Data is cleaned and enriched
   * Depth classification (Shallow / Deep)
   * Magnitude severity flags
   * Time-based features
   * Processed data is stored in MySQL
   * Interactive analysis dashboards are generated

### **Workflow Diagram (Conceptual Flow)**
```
┌──────────────────────────┐
│   User Selects Year      │
│   Range (Streamlit UI)   │
└─────────────┬────────────┘
              │
              ▼
┌──────────────────────────┐
│   Fetch Earthquake Data  │
│   from USGS API          │
└─────────────┬────────────┘
              │
              ▼
┌──────────────────────────┐
│   Check Existing Data    │
│   in MySQL Database      │
└─────────────┬────────────┘
        Yes ───┘            └─── No
      (Skip Year)            (Fetch Data)
                                │
                                ▼
┌──────────────────────────┐
│ Data Cleaning &          │
│ Transformation           │
│ - Handle nulls           │
│ - Convert timestamps     │
│ - Feature engineering    │
└─────────────┬────────────┘
              │
              ▼
┌──────────────────────────┐
│ Store Processed Data     │
│ in MySQL Database        │
└─────────────┬────────────┘
              │
              ▼
┌──────────────────────────┐
│ User Selects Analysis    │
│ Module (UI Buttons)     │
└─────────────┬────────────┘
              │
              ▼
┌──────────────────────────┐
│ SQL Queries & Analysis   │
│ - Magnitude & Depth      │
│ - Time Trends            │
│ - Tsunami & Alerts       │
│ - Data Quality           │
└─────────────┬────────────┘
              │
              ▼
┌──────────────────────────┐
│ Display Insights &       │
│ Results (Streamlit)      │
└──────────────────────────┘
```

## **🎯 Use Case**
This project can be used for:

   * 🌋 Seismic Risk Analysis
   * 📈 Earthquake Trend Monitoring
   * 🚨 Disaster Preparedness Insights
   * 🧪 Academic & Research Projects
   *  📚 Learning Data Visualization & SQL Analytics
   * 🌍 Geospatial & Temporal Pattern Detection

## **🚀 Future Enhancements**
Planned improvements include:
   * 🌐 Interactive map-based visualizations
   * 📉 Advanced time-series forecasting
   * 🧠 Machine Learning models for risk prediction
   * 🗺️ Continent-level & plate-boundary analysis
   * 🔔 Real-time alert notifications
   * 📊 Exportable reports (PDF / CSV)

## 📌 Author
```
Saran K
Data Analytics & Visualization Enthusiast
Capstone Project – Global Health Data Analysis
```
## ⭐ If You Like This Project

```
Give it a ⭐ on GitHub and feel free to fork it!
```
