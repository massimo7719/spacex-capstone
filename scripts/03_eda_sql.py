#!/usr/bin/env python3
"""EDA with SQL - runs the 10 queries requested by the capstone template
(slides 24-33) against the real dataset loaded into SQLite."""
import sqlite3
import pandas as pd

DB = "/home/claude/spacex_capstone/data/spacex.db"
OUT = "/home/claude/spacex_capstone/data/sql_results.md"

df = pd.read_csv("/home/claude/spacex_capstone/data/spacex_launches.csv")
df["Date"] = pd.to_datetime(df["Date"])
df["DateOnly"] = df["Date"].dt.date.astype(str)

con = sqlite3.connect(DB)
df.to_sql("SPACEXTABLE", con, if_exists="replace", index=False)

queries = {
    "1. Nomi unici dei launch site": """
        SELECT DISTINCT LaunchSite FROM SPACEXTABLE ORDER BY LaunchSite;
    """,
    "2. 5 record dove il launch site inizia con 'CCA'": """
        SELECT FlightNumber, DateOnly, LaunchSite, Payload, PayloadMass
        FROM SPACEXTABLE WHERE LaunchSite LIKE 'CCA%' LIMIT 5;
    """,
    "3. Payload totale dei booster per clienti NASA": """
        SELECT Customer, SUM(PayloadMass) AS TotalPayloadMass
        FROM SPACEXTABLE WHERE Customer LIKE '%NASA%' GROUP BY Customer;
    """,
    "4. Payload medio della Booster Version F9 v1.1": """
        SELECT AVG(PayloadMass) AS AvgPayloadMass
        FROM SPACEXTABLE WHERE BoosterVersion LIKE 'F9 v1.1%' OR BoosterVersion LIKE '%v1.1%';
    """,
    "5. Data del primo atterraggio riuscito su ground pad": """
        SELECT MIN(DateOnly) AS FirstSuccessfulGroundPadLanding
        FROM SPACEXTABLE WHERE LandingType = 'Ground pad' AND LandingSuccess = 1;
    """,
    "6. Booster con atterraggio riuscito su drone ship e payload 4000-6000 kg": """
        SELECT DISTINCT BoosterVersion FROM SPACEXTABLE
        WHERE LandingType = 'Drone ship' AND LandingSuccess = 1
          AND PayloadMass > 4000 AND PayloadMass < 6000
        ORDER BY BoosterVersion;
    """,
    "7. Numero totale di esiti di missione riusciti e falliti": """
        SELECT LaunchOutcome, COUNT(*) AS N FROM SPACEXTABLE GROUP BY LaunchOutcome;
    """,
    "8. Booster che hanno trasportato il payload massimo": """
        SELECT BoosterVersion, PayloadMass FROM SPACEXTABLE
        WHERE PayloadMass = (SELECT MAX(PayloadMass) FROM SPACEXTABLE)
        ORDER BY BoosterVersion;
    """,
    "9. Atterraggi falliti su drone ship nel 2015, per booster e sito": """
        SELECT FlightNumber, DateOnly, BoosterVersion, LaunchSite
        FROM SPACEXTABLE
        WHERE LandingType = 'Drone ship' AND LandingSuccess = 0
          AND DateOnly LIKE '2015%';
    """,
    "10. Ranking degli esiti di atterraggio tra 2010-06-04 e 2017-03-20 (decrescente)": """
        SELECT
          CASE WHEN LandingSuccess = 1 THEN 'Success (' || LandingType || ')'
               WHEN LandingSuccess = 0 THEN 'Failure (' || LandingType || ')'
               ELSE LandingType END AS LandingOutcome,
          COUNT(*) AS N
        FROM SPACEXTABLE
        WHERE DateOnly BETWEEN '2010-06-04' AND '2017-03-20'
        GROUP BY LandingOutcome
        ORDER BY N DESC;
    """,
}

with open(OUT, "w", encoding="utf-8") as f:
    for title, q in queries.items():
        result = pd.read_sql_query(q, con)
        print(f"=== {title} ===")
        print(result.to_string(index=False))
        print()
        f.write(f"## {title}\n\n")
        f.write("```sql\n" + q.strip() + "\n```\n\n")
        f.write(result.to_markdown(index=False) if hasattr(result, "to_markdown") else result.to_string(index=False))
        f.write("\n\n")

con.close()
print(f"Risultati salvati in {OUT}")
