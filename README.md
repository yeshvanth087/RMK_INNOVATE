# 🚍 NeuroNex UrbanSense AI — Mobile Urban Intelligence Platform

### **Smart India Hackathon 2026 | Problem Statement ID: SIH26124**
**Organization:** Bharat Electronics Limited (BEL)  
**Theme:** Fitness & Sports / Software / Intelligent Urban Mobility  
**Team Name:** NeuroNex

---

## 🌟 Executive Overview
In modern smart cities, thousands of public transit buses traverse every major arterial road every day. While these buses carry multiple cameras (front, rear, sides, and cabin), they are traditionally used only for passive incident recording. 

**NeuroNex UrbanSense AI** transforms municipal bus fleets into an **autonomous mobile sensing network**. The platform executes edge computer vision onboard buses to continuously detect:
- 🚧 **Road surface defects & hazards:** Potholes, cracks, waterlogging, damaged road dividers, missing zebra crossings, and obscured traffic signs.
- 🚗 **Traffic density & bottlenecks:** Multi-class vehicle counting and Passenger Car Unit (PCU) congestion estimation.
- 🚸 **Pedestrian & VRU safety:** School children crossing and vulnerable road users in traffic lanes.
- 🚨 **Law enforcement incidents:** Hit-and-run tracking, rash driving detection, and Automatic Number Plate Recognition (ANPR) with confidence scores, GPS coordinates, and timestamped evidence packages.

The **Centralized Platform** aggregates fleet telemetry, performs spatial deduplication (`ST_ClusterDBSCAN`), predicts transit delays using ML models, optimizes bus routes using Google OR-Tools VRP, and provides role-based command centers for **Municipal PWD**, **Traffic Police**, and **Public Transit Operations**.

---

## 🏗️ Architecture & Component Synthesis

```
┌────────────────────────────────────────────────────────────────────────┐
│                   EDGE LAYER (ONBOARD BUS SENSING UNIT)                │
│  • Multi-Camera Feed + GPS/IMU Telemetry                              │
│  • YOLOv8/v11 & ByteTrack Road Hazard, Traffic, VRU & ANPR Detectors  │
│  • Zero-Raw-Video Bandwidth Packager (Compact JSON + Thumbnails)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │  MQTT / 4G / 5G
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│             CENTRAL ANALYTICS & GEOSPATIAL CLOUD (FASTAPI)             │
│  • Spatial Deduplication (ST_ClusterDBSCAN 15m Pothole Merge)          │
│  • ML ETA & Delay Predictor (Random Forest / XGBoost + Weather)        │
│  • Dynamic Hazard Detour Optimizer (Google OR-Tools VRP + NetworkX)    │
│  • GTFS Transit Bottleneck Analyzer (Schedule Variance Index)          │
│  • Urban AI Decision Support Assistant (Conversational NLP)            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│           ROLE-BASED GIS COMMAND CENTER & AUTHORITY PORTALS            │
│  [1] Municipal PWD Portal: Auto Work Orders & AI Repair Verification   │
│  [2] Traffic Police Portal: ANPR Hit-and-Run Interceptor & Evidence    │
│  [3] Transit Ops Portal: Fleet Tracking, Delays & Dynamic Detours      │
│  [4] AI Urban Assistant: Natural Language Plain-English Decision Chat  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🔗 Reference Repositories Synthesized

| Repository | Synthesized Capability in UrbanSense AI |
| :--- | :--- |
| **`chaitanyab24/Smart-Bus-Route-Optimization`** | **DBSCAN POI Clustering & OR-Tools VRP**: Solves dynamic detour routing around high-severity road hazards, potholes, and waterlogging. |
| **`AKHIL-SAURABH/PTOML-public-transport-optimization-ml`** | **ML ETA Prediction & Crowding Classification**: Predicts trip delays conditioned on live traffic density (PCU), weather rainfall, and passenger load. |
| **`Hemamalini-L/Smart-Chennai-Public-Transport-Bottleneck-Analyzer`** | **GTFS Schedule Variance & Weather Impact Analyzer**: Identifies structural corridor bottlenecks across Chennai / metro transit networks. |
| **`MdAshrufali/TransportAi_platform_proj`** | **AI Decision Support Framework**: Conversational NLP assistant answering plain-English queries from municipal and police authorities. |

---

## 🚀 Quickstart Guide

### 1. Installation
```bash
# Clone and navigate to workspace
cd sih

# Install dependencies
python -m pip install -r requirements.txt
```

### 2. Run Automated Verification Tests
```bash
python test_platform.py
```

### 3. Launch Platform & Live Fleet Simulator
```bash
python run_platform.py
```

- Open **Unified Command Center**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Open **Interactive API Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🛡️ Key Features & Authority Workflows

### 🏛️ Municipal Corporation / PWD Workflow
1. **Automated Defect Ticketing:** When 2+ sensing buses detect the same pothole or a CRITICAL waterlogging event, the system deduplicates the coordinates and issues an automated PWD Work Order.
2. **AI Repair Verification:** Once contractors complete repairs, subsequent passes by sensing buses confirm the surface restoration and automatically upgrade ticket status to `AI_VERIFIED`.

### 👮 Traffic Police Workflow
1. **ANPR Alert Stream:** Instant alert on hit-and-run or rash driving with license plate number, OCR confidence (85-98%), vehicle make/color, speed, and GPS timestamp.
2. **Vehicle Search & Interceptor Dispatch:** Search past fleet sightings of any vehicle registration number to reconstruct movement trajectory.

### 🚌 Public Transit Operations Workflow
1. **Real-time Fleet GIS Map:** Live bus tracking with speed, heading, and passenger crowding.
2. **Dynamic Detour Solver:** Recalculates route waypoints using OR-Tools when critical road hazards or flooding obstruct standard corridors, displaying time saved.

---

## 👥 Team NeuroNex
*SIH 2026 | Bharat Electronics Limited (BEL)*
