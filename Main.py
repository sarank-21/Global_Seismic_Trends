import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
from sqlalchemy import create_engine, text

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Global Seismic Trends",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Global Seismic Trends")

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

# --------------------------------------------------
# MYSQL CONNECTION
# --------------------------------------------------
engine = create_engine("mysql+pymysql://root:0007@localhost")

with engine.connect() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS Earthquake_Database"))
    conn.commit()

db_engine = create_engine(
    "mysql+pymysql://root:0007@localhost/Earthquake_Database"
)

# --------------------------------------------------
# CREATE TABLE
# --------------------------------------------------
with db_engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS Earthquake (
            id VARCHAR(50) PRIMARY KEY,
            mag DECIMAL(4,2),
            place VARCHAR(255),
            Time DATETIME,
            updated DATETIME,
            felt DECIMAL(10,2),
            cdi DECIMAL(10,2),
            mmi DECIMAL(10,2),
            alert VARCHAR(50),
            status VARCHAR(50),
            tsunami INT,
            sig INT,
            net VARCHAR(20),
            code VARCHAR(50),
            ids VARCHAR(255),
            sources VARCHAR(255),
            Types TEXT,
            nst INT,
            dmin DECIMAL(10,4),
            rms DECIMAL(10,4),
            gap DECIMAL(10,2),
            magType VARCHAR(20),
            Type VARCHAR(50),
            latitude DECIMAL(10,6),
            longitude DECIMAL(10,6),
            depth DECIMAL(10,2),
            country VARCHAR(255),
            Earthquake_depth VARCHAR(255),
            mag_flag VARCHAR(255),
            Year INT,
            Month INT,
            Day INT,
            Day_of_week VARCHAR(50)
        )
    """))
    conn.commit()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.header("📅 Data Range")

start_year = st.sidebar.selectbox(
    "From Year",
    list(range(2015, datetime.now().year + 1))
)

end_year = st.sidebar.selectbox(
    "To Year",
    list(range(start_year, datetime.now().year + 1))
)

# 🔑 store in session
st.session_state.start_year = start_year
st.session_state.end_year = end_year

fetch_button = st.sidebar.button("🚀 Fetch Data")

if st.sidebar.button("📊 Analysis"):
    st.session_state.page = "analysis"
    st.rerun()

# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------
if st.session_state.page == "home":

    # ---------------- FETCH DATA ----------------
    if fetch_button:
        st.info(f"Processing data for {start_year} – {end_year}")
        new_records = []
        year_ex = []  # <-- collect all existing years he
        years_fetched = []  # years for which new data was fetched

        for year in range(start_year, end_year + 1):

            # Check if this year already exists in DB
            check_query = """
                SELECT COUNT(*) cnt
                FROM Earthquake
                WHERE Time >= %s AND Time < %s
            """
            start_date_year = f"{year}-01-01"
            end_date_year = f"{year + 1}-01-01"
            
            df_check_year = pd.read_sql(check_query, db_engine, params=(start_date_year, end_date_year))
            existing_count_year = df_check_year['cnt'].iloc[0]
            
            if existing_count_year > 0:
                year_ex.append(year)
                continue  # skip this year

            # ----------------- Fetch missing year data month by month -----------------
            year_had_data = False  # track if any data fetched for this year

            # Fetch missing year data month by month
            for month in range(1, 13):
                start_date = datetime(year, month, 1)
                end_date = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

                params = {
                    "format": "geojson",
                    "starttime": start_date.strftime("%Y-%m-%d"),
                    "endtime": end_date.strftime("%Y-%m-%d"),
                    "minmagnitude": 3.0
                }

                try:
                    r = requests.get(
                        "https://earthquake.usgs.gov/fdsnws/event/1/query",
                        params=params,
                        timeout=30
                    )

                    if r.status_code != 200:
                        continue

                    features = r.json().get("features", [])
                    if not features:
                        continue

                    df_month = pd.DataFrame([
                        {
                            "id": f["id"],
                            **f["properties"],
                            "longitude": f["geometry"]["coordinates"][0],
                            "latitude": f["geometry"]["coordinates"][1],
                            "depth": f["geometry"]["coordinates"][2]
                        }
                        for f in features
                    ])

                    existing_ids = set(
                        pd.read_sql("SELECT id FROM Earthquake", db_engine)["id"])

                    df_month = df_month[~df_month["id"].isin(existing_ids)]

                    if not df_month.empty:
                        new_records.append(df_month)
                        year_had_data = True  # mark that this year got new data


                    time.sleep(1)

                except Exception as e:
                    st.error(f"{year}-{month:02d} failed: {e}")

            if year_had_data:
                years_fetched.append(year)  # add to list of fetched years

        # ---------------- SHOW SKIPPED YEARS ----------------
        if year_ex:
            st.info(f"ℹ️ Data for year(s) already exists: {', '.join(map(str, year_ex))}. These years were skipped.")

        # ---------------- INSERT NEW DATA ----------------
        if new_records:
            df_new = pd.concat(new_records, ignore_index=True)

            df_new["time"] = pd.to_datetime(df_new["time"], unit="ms")
            df_new["updated"] = pd.to_datetime(df_new["updated"], unit="ms")

            # Cleaning
            df_new["time"] = pd.to_datetime(df_new["time"], unit="ms")
            df_new["updated"] = pd.to_datetime(df_new["updated"], unit="ms")
            df_new.drop(columns=["tz", "title", "url", "detail"], inplace=True, errors="ignore")
            df_new["alert"].fillna("green", inplace=True)
            df_new["cdi"].fillna(round(df_new["cdi"].mean(), 1), inplace=True)
            df_new["felt"].fillna(round(df_new["felt"].mean(), 1), inplace=True)
            df_new["mmi"].fillna(round(df_new["mmi"].mean(), 1), inplace=True)
            df_new["nst"].fillna(round(df_new["nst"].mean(), 1), inplace=True)
            df_new["sources"] = df_new["sources"].str.strip(",")
            df_new["types"] = df_new["types"].str.strip(",")
            df_new["ids"] = df_new["ids"].str.strip(",")

            df_new.drop(columns=["tz", "title", "url", "detail"], inplace=True, errors="ignore")

            df_new["country"] = df_new["place"].str.extract(r",\s*(.+)$")
            df_new["Earthquake_depth"] = df_new["depth"].apply(
                lambda x: "Deep Earthquake" if x > 70 else "Shallow Earthquake"
            )
            df_new["mag_flag"] = df_new["mag"].apply(
                lambda x: "Low" if x < 5 else
                "Moderate" if x < 6 else
                "Strong" if x < 7 else
                "Destructive"
            )

            df_new["Year"] = df_new["time"].dt.year
            df_new["Month"] = df_new["time"].dt.month
            df_new["Day"] = df_new["time"].dt.day
            df_new["Day_of_week"] = df_new["time"].dt.day_name()

            df_new.rename(columns={"time": "Time", "types": "Types", "type": "Type"}, inplace=True)

            df_new.dropna(subset=["mag", "latitude", "longitude", "depth", "country"], inplace=True)

            df_new.to_sql("Earthquake", db_engine, if_exists="append", index=False)
            st.success(f"✅ Inserted for year(s): {', '.join(map(str, years_fetched))} and new records fetched is {len(df_new)}")

        else:
            st.info("ℹ️ No new data inserted")


    # ---------------- CHECK MISSING YEARS ----------------
    query_years = """
        SELECT DISTINCT YEAR(Time) AS year
        FROM Earthquake
        WHERE Time IS NOT NULL
    """
    df_years = pd.read_sql(query_years, db_engine)
    fetched_years = set(df_years["year"].dropna().astype(int))

    selected_years = set(range(start_year, end_year + 1))
    missing_years = sorted(selected_years - fetched_years)

    if missing_years:
        st.warning(
            "⚠️ Data not fetched for year(s): "
            + ", ".join(map(str, missing_years))
        )


    # ---------------- SHOW TABLE ----------------
    query_view = """
        SELECT *
        FROM Earthquake
        WHERE Year BETWEEN %s AND %s
        ORDER BY Time
    """
    df_view = pd.read_sql(
        query_view,
        db_engine,
        params=(start_year, end_year)
    )

    st.subheader(f"🗂️ Earthquake Data ({start_year} – {end_year})")
    st.markdown(
    f"<h4 style='color:RED;'>TOTAL RECORDS : {len(df_view)}</h5>",
    unsafe_allow_html=True
)

    st.dataframe(df_view, use_container_width=True)

# --------------------------------------------------
# ANALYSIS PAGE
# --------------------------------------------------
elif st.session_state.page == "analysis":

    st.subheader("📊 Earthquake Analysis")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📈 Magnitude & Depth"):
            st.session_state.page = "Magnitude & Depth"
            st.rerun()
        if st.button("⌛ Time Analysis"):
            st.session_state.page = "Time Analysis"
            st.rerun()
        if st.button("🏆 Event Type & Quality Metrics"):
            st.session_state.page = "Event Type & Quality Metrics"
            st.rerun()
    with col2:
        
        if st.button("🌊 Tsunamis & Alerts"):
            st.session_state.page = "Tsunamis & Alerts"
            st.rerun()
        if st.button("📑 Seismic Pattern & Trends Analysis."):
            st.session_state.page = "Seismic Pattern & Trends Analysis"
            st.rerun()
        if st.button("⚓ Depth, Location & Distance-Based  Analysis"):
            st.session_state.page = "Depth, Location & Distance-Based  Analysis"
            st.rerun()
            
    if st.button("⬅ Go Back"):
        st.session_state.page = "home"
        st.rerun()

# --------------------------------------------------
# MAGNITUDE & DEPTH
# --------------------------------------------------
if st.session_state.page == "Magnitude & Depth":

    st.subheader("📈 Magnitude & Depth")

    topic = st.selectbox(
        "Choose Topic",
        [
            "— Select Topic —",
            "Top 10 Strongest Earthquakes",
            "Top 10 Deepest Earthquakes",
            "Shallow Earthquakes (<50 km & Mag > 7.5)",
            "Average Depth by Country",
            "Average Magnitude by Mag Type"
        ]
    )

    if topic == "— Select Topic —":
        st.info("👆 Please select a topic")
        if st.button("⬅ Go Back"):
            st.session_state.page = "analysis"
            st.rerun()
        st.stop()

    explanation = None   # 👈 important

    if topic == "Top 10 Strongest Earthquakes":
        query = """
        SELECT id, mag
        FROM Earthquake
        WHERE Year BETWEEN %s AND %s
        ORDER BY mag DESC
        LIMIT 10
        """
        explanation = (
            """Earthquakes with higher magnitude represent stronger and 
            more dangerous seismic events, capable of causing severe ground shaking and widespread damage."""
        )

    elif topic == "Top 10 Deepest Earthquakes":
        query = """
        SELECT id, depth
        FROM Earthquake
        WHERE Year BETWEEN %s AND %s
        ORDER BY depth DESC
        LIMIT 10
        """
        explanation = ("""Deepest earthquakes mean how far inside the Earth the earthquake occurs,
                       measured as the depth below the Earth’s surface (in kilometers). So Earthquakes 
                       deeper than (>300 km ) typically have weaker surface impact because seismic 
                       energy dissipates before reaching the ground.""")

    elif topic == "Shallow Earthquakes (<50 km & Mag > 7.5)":
        query = """
        SELECT id, mag, depth
        FROM Earthquake
        WHERE Year BETWEEN %s AND %s
          AND depth < 50 AND mag > 7.5
        """
        explanation = ("""Shallow earthquakes with depths less than 50 km and magnitudes greater than 7.5 
                       are the most destructive because they produce intense ground shaking and experience minimal energy dissipation,
                       resulting in severe damage to the surrounding surface.""")

    elif topic == "Average Depth by Country":
        query = """
        SELECT country, AVG(depth) AS avg_depth
        FROM Earthquake
        WHERE Year BETWEEN %s AND %s
        GROUP BY country
        """

        explanation = ("""“Average earthquake depth by country indicates whether earthquakes in that region are generally shallow or deep. 
                       Shallow earthquakes (depth < 70 km) often cause more surface damage, even if their magnitude is moderate. 
                       Deep earthquakes (depth > 300 km) may have high magnitudes, but their surface impact is usually weaker due to energy dissipation. 
                       While this insight helps assess the potential impact, the likelihood of earthquakes occurring in a country depends on earthquake frequency.""")

    else:
        query = """
        SELECT magType, AVG(mag) AS avg_mag
        FROM Earthquake
        WHERE Year BETWEEN %s AND %s
        GROUP BY magType ORDER BY avg_mag DESC
        """

        explanation = ("""Magnitude (value) tells how strong an earthquake is,Magnitude type (magType) tells how the magnitude was measured.
        If a magType has a higher average magnitude, it means that method is mostly used for strong earthquakes.
        If a magType has a lower average magnitude, it means that method is mostly used for small earthquakes. """)

    df = pd.read_sql(query, db_engine, params=(start_year, end_year))

    # 📊 Table first
    st.dataframe(df, use_container_width=True)

    # 📝 Explanation BELOW the table
    if explanation:
        st.subheader("📝 Insights")
        st.info(explanation)


    if st.button("⬅ Go Back"):
        st.session_state.page = "analysis"
        st.rerun()

# --------------------------------------------------
# TIME ANALYSIS
# --------------------------------------------------
elif st.session_state.page == "Time Analysis":

    st.subheader("⌛ Time Analysis")

    topic = st.selectbox(
        "Choose Topic",
        [
            "— Select Topic —",
            "Year with most earthquakes",
            "Month with highest number of earthquakes",
            "Day of week with most earthquakes",
            "Count of earthquakes per hour",
            "Most active reporting network"
        ]
    )

    if topic == "— Select Topic —":
        st.info("👆 Please select a topic")
        if st.button("⬅ Go Back"):
           st.session_state.page = "analysis"
           st.rerun()
        st.stop()

    elif topic == "Year with most earthquakes":
        query = """
        SELECT Year, COUNT(*) AS total
        FROM Earthquake
        WHERE Year BETWEEN %s AND %s
        GROUP BY Year
        ORDER BY total DESC
        """
        explanation = ("""This analysis tells you how many earthquakes occurred in each year 
        and then identifies which year recorded the highest number of events.""")

    elif topic == "Month with highest number of earthquakes":
        query = """
        SELECT Month, COUNT(*) AS total
        FROM Earthquake
        WHERE Year BETWEEN %s AND %s
        GROUP BY Month
        ORDER BY total DESC
        """
        explanation = ("""This analysis shows how many earthquakes occurred in each month (across all years) 
                       and identifies which month recorded the maximum number of events.""")

    elif topic == "Day of week with most earthquakes":
        query = """
        SELECT Day_of_week, COUNT(*) AS total
        FROM Earthquake
        WHERE Year BETWEEN %s AND %s
        GROUP BY Day_of_week
        ORDER BY total DESC
        """
        explanation =("""This analysis counts how many earthquakes occurred on each day of the week (Monday–Sunday) and 
                      identifies which day recorded the highest number of events.""")

    elif topic == "Count of earthquakes per hour":
        query = """
        SELECT HOUR(Time) AS hour, COUNT(*) AS total
        FROM Earthquake
        WHERE Year BETWEEN %s AND %s
        GROUP BY hour
        ORDER BY hour
        """
        explanation = ("""This analysis shows how many earthquakes occurred in each hour of the day (0–23), 
                       based on the event timestamp.""")

    else:
        query = """
        SELECT net, COUNT(*) AS total
        FROM Earthquake
        WHERE Year BETWEEN %s AND %s
        GROUP BY net
        ORDER BY total DESC
        """
        explanation = ("""This analysis shows which network group has recorded and 
                       reported the highest number of earthquakes.""")

    df = pd.read_sql(query, db_engine, params=(start_year, end_year))
    st.dataframe(df, use_container_width=True)

    # 📝 Explanation BELOW the table
    if explanation:
        st.subheader("📝 Insights")
        st.info(explanation)

    if st.button("⬅ Go Back"):
        st.session_state.page = "analysis"
        st.rerun()

# --------------------------------------------------
# Event Type & Quality Metrics ANALYSIS PAGE
# --------------------------------------------------

elif st.session_state.page == "Event Type & Quality Metrics":

    st.subheader("🏆 Event Type & Quality Metrics")

    topic = st.selectbox(
        "Choose Analysis Topic",
        [
        "— Select Topic —",
        "Count of reviewed vs automatic earthquakes (status)",
        "Count by earthquake type (type)",
        "Number of earthquakes by data type (types)",
        "Average RMS and gap per continent",
        "Events with high station coverage (nst > threshold)"
        ]
    )

    if topic == "— Select Topic —":
        st.info("👆 Please select a topic")
        if st.button("⬅ Go Back"):
           st.session_state.page = "analysis"
           st.rerun()
        st.stop()

    elif topic == "Count of reviewed vs automatic earthquakes (status)":
        query = """SELECT status, COUNT(*) AS total
        FROM earthquake
        WHERE Year BETWEEN %s AND %s
        GROUP BY status"""
        explanation = ("""This analysis shows that earthquakes with a Reviewed status are verified by human experts, 
                       resulting in high data reliability, while Automatic status earthquakes are system-generated and 
                       therefore have lower reliability.""")

    elif topic == "Count by earthquake type (type)":
        query = """SELECT type, COUNT(*) AS total 
        FROM earthquake
        WHERE Year BETWEEN %s AND %s
        GROUP BY type"""
        explanation = ("""This analysis shows how many seismic events occurred for each earthquake type.""")
    
    elif topic == "Number of earthquakes by data type (types)":
        query = """SELECT Types, COUNT(*) AS total
        FROM earthquake
        WHERE Year BETWEEN %s AND %s
        GROUP BY types"""
        explanation = ("""This analysis shows that most recorded seismic events are natural earthquakes, 
                       which are caused by tectonic activity, while other types, such as man-made events, occur less frequently.""")
    
    elif topic == "Average RMS and gap per continent":
        query = """SELECT country ,
        AVG(rms) AS avg_rms,
        AVG(gap) AS avg_gap
        FROM earthquake
        WHERE Year BETWEEN %s AND %s
        GROUP BY country """
        explanation = ("""tThis analysis shows that country with low average RMS and 
                       gap have high-quality earthquake data with good station coverage, 
                       while country with high average RMS and gap have lower data reliability and poorer station coverage.""")
    
    else:
        query = """SELECT id, country, nst
        FROM earthquake
        WHERE nst > 50 AND 
        Year BETWEEN %s AND %s """

        explanation = ("""This shows which earthquakes were reported or detected by the highest number of stations (nst) above a fixed threshold.
                        More stations reporting an event → more accurate location, depth, and magnitude. 
                       Events reported by very few stations may be less certain..""")

    df = pd.read_sql(query, db_engine, params=(start_year, end_year))
    st.dataframe(df, use_container_width=True)

    # 📝 Explanation BELOW the table
    if explanation:
        st.subheader("📝 Insights")
        st.info(explanation)
    
    if st.button("⬅ Go Back"):
        st.session_state.page = "analysis"
        st.rerun()

# --------------------------------------------------
# Tsunamis & Alerts ANALYSIS PAGE
# --------------------------------------------------

elif st.session_state.page == "Tsunamis & Alerts":

    st.subheader("🌊 Tsunamis & Alerts")

    topic = st.selectbox(
        "Choose Analysis Topic",
        [
           "— Select Topic —",
           "Number of tsunamis triggered per year",
           "Count earthquakes by alert levels (red, orange, green , yellow)"
        ])

    if topic == "— Select Topic —":
        st.info("👆 Please select a topic")
        if st.button("⬅ Go Back"):
           st.session_state.page = "analysis"
           st.rerun()
        st.stop()

    elif topic == "Number of tsunamis triggered per year" :
        query = """SELECT Year, COUNT(*) AS tsunami_events
        FROM earthquake
        WHERE tsunami = 1 and Year BETWEEN %s AND %s
        GROUP BY Year"""
        explanation = ("""This analysis counts tells how many earthquake events triggered tsunamis in each year.""")
        explanation1 = ("tsunami = 1 → tsunami triggered")
        explanation2 = ("tsunami = 0 → no tsunami")
    else :
        query = """SELECT alert, COUNT(*) AS total
        FROM earthquake
        WHERE Year BETWEEN %s AND %s
        GROUP BY alert"""
        explanation = ("""This analysis counts tels how many earthquakes fall under each alert level,Where
                       Most earthquakes are usually green or yellow,
                       Red alerts are rare and correspond to very high-magnitude, high-impact events,
                       This helps prioritize risk assessment and emergency response planning.""")
        explanation1 = ("🔴 Red → Severe potential impact (major damage, high losses)")
        explanation2 = ("🟠 Orange → Significant impact possible")
        explanation3 = ("🟢 Green → Minor or no expected impact")
        explanation4 = ("🟡 Yellow → Moderate impact")

    df = pd.read_sql(query, db_engine, params=(start_year, end_year))
    st.dataframe(df, use_container_width=True)

    # 📝 Explanation BELOW the table
    if topic == "Number of tsunamis triggered per year" :
        if explanation:
            st.subheader("📝 Insights")
            st.error(explanation1)
            st.success(explanation2)
            st.info(explanation)
    else : 
         if explanation:
            st.subheader("📝 Insights")
            st.error(explanation1)
            st.info(explanation2)
            st.success(explanation3)
            st.warning(explanation4)
            st.info(explanation)
    if st.button("⬅ Go Back"):
        st.session_state.page = "analysis"
        st.rerun()

# --------------------------------------------------
# Seismic Pattern & Trends Analysis ANALYSIS PAGE
# --------------------------------------------------

elif st.session_state.page == "Seismic Pattern & Trends Analysis":

    st.subheader("📑 Seismic Pattern & Trends Analysis")

    topic = st.selectbox(
        "Choose Analysis Topic",
        [
           "— Select Topic —",
           "Find the top 5 countries with the highest average magnitude of earthquakes in the past 10 years" ,             	
           "Find countries that have experienced both shallow and deep earthquakes within the same month",
           "Compute the year-over-year growth rate in the total number of earthquakes globally",
           "List the 3 most seismically active regions by combining both frequency and average magnitude"

        ]
    )

    if topic == "— Select Topic —":
        st.info("👆 Please select a topic")
        if st.button("⬅ Go Back"):
           st.session_state.page = "analysis"
           st.rerun()
        st.stop()

    elif topic == "Find the top 5 countries with the highest average magnitude of earthquakes in the past 10 years":
        query = """SELECT country, AVG(mag) AS avg_mag
        FROM earthquake
        WHERE Time >= DATE_SUB(CURDATE(), INTERVAL 10 YEAR) AND Year BETWEEN %s AND %s
        GROUP BY country
        ORDER BY avg_mag DESC
        LIMIT 5"""
        explanation = ("""This analysis shows that the Countries with higher average earthquake 
                       magnitudes are likely to face greater damage when earthquakes occur.""")
    
    elif topic == "Find countries that have experienced both shallow and deep earthquakes within the same month":
        query = """SELECT
        country,
        Month,
        COUNT(*) AS total_quakes
        FROM earthquake
        WHERE Earthquake_depth IN ('Shallow earthquake', 'Deep earthquake') AND Year BETWEEN %s AND %s
        GROUP BY country, Month
        HAVING
        COUNT(DISTINCT Earthquake_depth) = 2"""
        explanation = ("""This analysis indicates that certain countries experienced 
                       earthquakes  with different depths in the same month.""")

    elif topic == "Compute the year-over-year growth rate in the total number of earthquakes globally":
        query = """SELECT Year, total_earthquakes,
        LAG(total_earthquakes) OVER (ORDER BY Year) AS prev_year_earthquakes,
        ROUND(
        (total_earthquakes - LAG(total_earthquakes) OVER (ORDER BY Year)) * 100.0
        / LAG(total_earthquakes) OVER (ORDER BY Year),2) AS yoy_growth_percentage
        FROM ( SELECT Year , COUNT(*) AS total_earthquakes FROM earthquake
        GROUP BY Year) t WHERE Year BETWEEN %s AND %s   ORDER BY Year"""
        explanation1 = ("Positive % → increase")
        explanation2 = ("Negative % → decrease")
        explanation3 = ("First year has NULL (no previous year)")
        explanation = ("""This analysis Shows whether global earthquake occurrences are increasing or decreasing year by year""")

    else :
        query = """SELECT 
        country,mag_flag,
        COUNT(*) AS frequency,
        AVG(mag) AS avg_mag,
        COUNT(*) * AVG(mag) AS activity_score
        FROM earthquake
        WHERE mag >= 6 AND Year BETWEEN %s AND %s
        GROUP BY country,mag_flag
        ORDER BY activity_score DESC
        LIMIT 3"""
        explanation = ("""this analysis shows that countries with many earthquakes and 
                       high average magnitudes are the countries which experience most frequent earthquakes 
                       and often strong earthquakes due to tectonic plate movements.""")

    df = pd.read_sql(query, db_engine, params=(start_year, end_year))
    st.dataframe(df, use_container_width=True)

    if topic == "Compute the year-over-year growth rate in the total number of earthquakes globally":
        if explanation:
            st.subheader("📝 Insights")
            st.success(explanation1)
            st.error(explanation2)
            st.warning(explanation3)
            st.info(explanation)
    else : 
        if explanation:
            st.subheader("📝 Insights")
            st.info(explanation)

    if st.button("⬅ Go Back"):
        st.session_state.page = "analysis"
        st.rerun()

# ----------------------------------------------------------
# Depth, Location & Distance-Based  Analysis ANALYSIS PAGE
# ----------------------------------------------------------

elif st.session_state.page == "Depth, Location & Distance-Based  Analysis":

    st.subheader("⚓ Depth, Location & Distance-Based  Analysis")

    topic = st.selectbox(
        "Choose Analysis Topic",
        [
            "— Select Topic —",
            "For each country, calculate the average depth of earthquakes within ±5° latitude range of the equator",
            "Identify countries having the highest ratio of shallow to deep earthquakes",
            "Find the average magnitude difference between earthquakes with tsunami alerts and those without",
            "Using the gap and rms columns, identify events with the lowest data reliability (highest average error margins)",
           " Determine the regions with the highest frequency of deep-focus earthquakes (depth > 300 km)"
        ]
    )



    if topic == "— Select Topic —":
        st.info("👆 Please select a topic")
        if st.button("⬅ Go Back"):
           st.session_state.page = "analysis"
           st.rerun()
        st.stop()

    elif topic == "For each country, calculate the average depth of earthquakes within ±5° latitude range of the equator":
        query = """SELECT country, AVG(depth) AS avg_depth
        FROM earthquake
        WHERE ABS(latitude) <= 5 AND Year BETWEEN %s AND %s
        GROUP BY country"""
        explanation = ("""This analysis identifies how deep earthquakes are, 
                       on average, in each country near the equator (±5° latitude).""")

    elif topic == "Identify countries having the highest ratio of shallow to deep earthquakes":
        query = """SELECT country,
        SUM(depth < 70) / NULLIF(SUM(depth > 300), 0) AS shallow_deep_ratio
        FROM earthquake
        WHERE Year BETWEEN %s AND %s
        GROUP BY country
        ORDER BY shallow_deep_ratio DESC"""
        explanation = ("""Countries with a high shallow-to-deep earthquake ratio generally face greater surface damage risk, as shallow earthquakes generate 
                       stronger ground shaking.Conversely,countries with a low ratio, dominated by deep earthquakes, 
                       often experience less localized damage per event, despite high seismic activity.""")

    elif topic == "Find the average magnitude difference between earthquakes with tsunami alerts and those without":
        query = """SELECT
        AVG(CASE WHEN tsunami = 1 THEN mag END) -
        AVG(CASE WHEN tsunami = 0 THEN mag END) AS mag_difference from  earthquake
        WHERE Year BETWEEN %s AND %s"""
        explanation = ("""If the average magnitude of tsunami-triggering earthquakes is higher than that of non-tsunami earthquakes, 
                       the magnitude difference will be positive, indicating that stronger earthquakes are more likely to generate tsunamis.""")

    elif topic == "Using the gap and rms columns, identify events with the lowest data reliability (highest average error margins)":
        query = """SELECT id, place, rms, gap, (rms + gap) / 2 AS error_score
        FROM earthquake
        WHERE Year BETWEEN %s AND %s
        ORDER BY error_score DESC
        LIMIT 10"""
        explanation = ("""Earthquake events with high gap and high RMS values indicate poor seismic station coverage and 
                       large observational errors, resulting in low data reliability. This means the reported earthquake location,
                        depth, and magnitude are not very accurate and have high uncertainty.""")
    
    else :
        query = """SELECT country, COUNT(*) AS deep_events
        FROM earthquake
        WHERE depth > 300 AND Year BETWEEN %s AND %s
        GROUP BY country
        ORDER BY deep_events DESC"""
        explanation = ("""Regions with the highest frequency of deep-focus earthquakes experience many earthquakes, 
                       but these events usually cause less surface damage because the energy dissipates before reaching the surface.""")

    df = pd.read_sql(query, db_engine, params=(start_year, end_year))
    st.dataframe(df, use_container_width=True)
 
    if explanation:
        st.subheader("📝 Insights")
        st.info(explanation)

    if st.button("⬅ Go Back"):
        st.session_state.page = "analysis"
        st.rerun()

