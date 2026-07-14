## 1. Nomi unici dei launch site

```sql
SELECT DISTINCT LaunchSite FROM SPACEXTABLE ORDER BY LaunchSite;
```

| LaunchSite   |
|:-------------|
| CCAFS SLC-40 |
| KSC LC-39A   |
| VAFB SLC-4E  |

## 2. 5 record dove il launch site inizia con 'CCA'

```sql
SELECT FlightNumber, DateOnly, LaunchSite, Payload, PayloadMass
        FROM SPACEXTABLE WHERE LaunchSite LIKE 'CCA%' LIMIT 5;
```

|   FlightNumber | DateOnly   | LaunchSite   | Payload                                 |   PayloadMass |
|---------------:|:-----------|:-------------|:----------------------------------------|--------------:|
|              1 | 2010-06-04 | CCAFS SLC-40 | Dragon Spacecraft Qualification Unit    |           nan |
|              2 | 2010-12-08 | CCAFS SLC-40 | SpaceX COTS Demo Flight 1 (Dragon C101) |           nan |
|              3 | 2012-05-22 | CCAFS SLC-40 | SpaceX COTS Demo Flight 2 (Dragon C102) |           525 |
|              4 | 2012-10-08 | CCAFS SLC-40 | SpaceX CRS-1 (Dragon C103)              |          4700 |
|              5 | 2013-03-01 | CCAFS SLC-40 | SpaceX CRS-2 (Dragon C104)              |          4877 |

## 3. Payload totale dei booster per clienti NASA

```sql
SELECT Customer, SUM(PayloadMass) AS TotalPayloadMass
        FROM SPACEXTABLE WHERE Customer LIKE '%NASA%' GROUP BY Customer;
```

| Customer                                                     |   TotalPayloadMass |
|:-------------------------------------------------------------|-------------------:|
| Firefly Aerospace & NASA (CLPS)                              |               2517 |
| Iridium Communications GFZ • NASA                            |               6460 |
| NASA                                                         |               3155 |
| NASA & Various                                               |                325 |
| NASA (CCD)                                                   |              12055 |
| NASA (CCDev)                                                 |              12530 |
| NASA (CCP)                                                   |              38500 |
| NASA (CLPS) / Intuitive Machines                             |               1931 |
| NASA (CLPS) Intuitive Machines AstroForge Epic Aerospace TBD |                nan |
| NASA (COTS)                                                  |                525 |
| NASA (CRS)                                                   |             100759 |
| NASA (CTS)                                                   |             129050 |
| NASA (LSP)                                                   |               3005 |
| NASA (LSP) NOAA CNES                                         |                553 |
| NASA / NOAA / ESA / EUMETSAT                                 |               1192 |
| NASA / NOAA / EUMETSAT / ESA                                 |               1440 |
| NASA/CNES                                                    |               2200 |
| USAF NASA NOAA                                               |                570 |
| ispace MBRSC JAXA  NASA                                      |               1000 |

## 4. Payload medio della Booster Version F9 v1.1

```sql
SELECT AVG(PayloadMass) AS AvgPayloadMass
        FROM SPACEXTABLE WHERE BoosterVersion LIKE 'F9 v1.1%' OR BoosterVersion LIKE '%v1.1%';
```

|   AvgPayloadMass |
|-----------------:|
|          2534.67 |

## 5. Data del primo atterraggio riuscito su ground pad

```sql
SELECT MIN(DateOnly) AS FirstSuccessfulGroundPadLanding
        FROM SPACEXTABLE WHERE LandingType = 'Ground pad' AND LandingSuccess = 1;
```

| FirstSuccessfulGroundPadLanding   |
|:----------------------------------|
| 2015-12-22                        |

## 6. Booster con atterraggio riuscito su drone ship e payload 4000-6000 kg

```sql
SELECT DISTINCT BoosterVersion FROM SPACEXTABLE
        WHERE LandingType = 'Drone ship' AND LandingSuccess = 1
          AND PayloadMass > 4000 AND PayloadMass < 6000
        ORDER BY BoosterVersion;
```

| BoosterVersion   |
|:-----------------|
| F9 B5 B1048-3    |
| F9 B5 B1058-5    |
| F9 B5 B1060-1    |
| F9 B5 B1062-1    |
| F9 B5 B1062-2    |
| F9 B5 B1062-7    |
| F9 B5 B1067-3    |
| F9 B5 B1067-7    |
| F9 B5 B1067-8    |
| F9 B5 B1069-3    |
| F9 FT B1022      |
| F9 FT B1026      |
| F9 FT B1031-2    |
| F9 B5 B1046-2    |
| F9 B5 B1047-2    |
| F9 B5 B1062-14   |
| F9 B5 B1067-12   |
| F9 B5 B1073-19   |
| F9 B5 B1073-20   |
| F9 B5 B1073-6    |
| F9 B5 B1076-12   |
| F9 B5 B1076-15   |
| F9 B5 B1076-4    |
| F9 B5 B1076-9    |
| F9 B5 B1077-2    |
| F9 B5 B1077-3    |
| F9 B5 B1077-6    |
| F9 B5 B1078-2    |
| F9 B5 B1080-9    |
| F9 B5 B1085-4    |
| F9 B5 B1092-4    |
| F9 B5 B1095-7    |
| F9 B5 B1096-5    |
| F9 FT B1021-2    |

## 7. Numero totale di esiti di missione riusciti e falliti

```sql
SELECT LaunchOutcome, COUNT(*) AS N FROM SPACEXTABLE GROUP BY LaunchOutcome;
```

| LaunchOutcome   |   N |
|:----------------|----:|
| Failure         |   2 |
| Success         | 661 |

## 8. Booster che hanno trasportato il payload massimo

```sql
SELECT BoosterVersion, PayloadMass FROM SPACEXTABLE
        WHERE PayloadMass = (SELECT MAX(PayloadMass) FROM SPACEXTABLE)
        ORDER BY BoosterVersion;
```

| BoosterVersion   |   PayloadMass |
|:-----------------|--------------:|
| F9 B5 B1067-24   |         17500 |
| F9 B5 B1069-13   |         17500 |
| F9 B5 B1069-20   |         17500 |
| F9 B5 B1071-28   |         17500 |
| F9 B5 B1075-19   |         17500 |
| F9 B5 B1075-20   |         17500 |
| F9 B5 B1076-18   |         17500 |
| F9 B5 B1077-17   |         17500 |
| F9 B5 B1078-15   |         17500 |
| F9 B5 B1080-12   |         17500 |
| F9 B5 B1081-17   |         17500 |
| F9 B5 B1082-13   |         17500 |
| F9 B5 B1082-14   |         17500 |
| F9 B5 B1082-15   |         17500 |
| F9 B5 B1082-16   |         17500 |
| F9 B5 B1083-6    |         17500 |
| F9 B5 B1088-10   |         17500 |
| F9 B5 B1088-9    |         17500 |
| F9 B5 B1093-5    |         17500 |
| F9 B5 B1097-1    |         17500 |

## 9. Atterraggi falliti su drone ship nel 2015, per booster e sito

```sql
SELECT FlightNumber, DateOnly, BoosterVersion, LaunchSite
        FROM SPACEXTABLE
        WHERE LandingType = 'Drone ship' AND LandingSuccess = 0
          AND DateOnly LIKE '2015%';
```

|   FlightNumber | DateOnly   | BoosterVersion   | LaunchSite   |
|---------------:|:-----------|:-----------------|:-------------|
|             14 | 2015-01-10 | F9 v1.1 B1012    | CCAFS SLC-40 |
|             17 | 2015-04-14 | F9 v1.1 B1015    | CCAFS SLC-40 |
|             19 | 2015-06-28 | F9 v1.1 B1018    | CCAFS SLC-40 |

## 10. Ranking degli esiti di atterraggio tra 2010-06-04 e 2017-03-20 (decrescente)

```sql
SELECT
          CASE WHEN LandingSuccess = 1 THEN 'Success (' || LandingType || ')'
               WHEN LandingSuccess = 0 THEN 'Failure (' || LandingType || ')'
               ELSE LandingType END AS LandingOutcome,
          COUNT(*) AS N
        FROM SPACEXTABLE
        WHERE DateOnly BETWEEN '2010-06-04' AND '2017-03-20'
        GROUP BY LandingOutcome
        ORDER BY N DESC;
```

| LandingOutcome       |   N |
|:---------------------|----:|
| Failure (Other)      |   9 |
| Failure (Drone ship) |   6 |
| Success (Drone ship) |   5 |
| Failure (Ocean)      |   5 |
| Success (Ground pad) |   3 |
| Failure (Parachute)  |   2 |
| No attempt           |   1 |

