# 📖 Advanced Football Analytics & Statistics Guide

This document provides a comprehensive guide to the advanced metrics and expected data models included in the **Liverpool & Premier League Analysis Datasets**.

---

## 📋 Table of Contents
1. [Expected Goals (xG) & Variants](#1-expected-goals-xg--variants)
2. [Passes Per Defensive Action (PPDA) & Pressing](#2-passes-per-defensive-action-ppda--pressing)
3. [Deep Zone Invasions (Deep Completions)](#3-deep-zone-invasions-deep-completions)
4. [Expected Points (xPTS)](#4-expected-points-xpts)
5. [Player Possession & Build-Up Metrics (xA, xGChain, xGBuildup)](#5-player-possession--build-up-metrics-xa-xgchain-xgbuildup)
6. [Post-Shot xG (PSxG / xGOT)](#6-post-shot-xg-psxg--xgot)
7. [Glossary & Summary Table](#7-glossary--summary-table)

---

## 1. Expected Goals (xG) & Variants

### What is xG?
**Expected Goals (`xG`)** measures the quality of a goal-scoring opportunity. Every shot is assigned a probability between `0.00` (impossible to score) and `1.00` (certain goal) based on thousands of historical shots with similar characteristics:
- **Distance & Angle**: Proximity to the goal line and horizontal angle relative to the posts.
- **Shot Type**: Foot vs. Header vs. Other body part.
- **Assist / Creation Method**: Through-ball, cross, cut-back, rebound, counter-attack, or solo dribble.
- **Game State & Pressure**: Defender positioning, goalkeeper stance, and open-play vs. set-piece.

### Key Variants:
* **`xGA` (Expected Goals Against)**: The total xG conceded from opponent shots. Evaluates underlying defensive solidity independent of luck or goalkeeper saves.
* **`xGD` (Expected Goal Difference)**: 
  $$\text{xGD} = \text{xG} - \text{xGA}$$
  The truest indicator of overall team dominance over a season.
* **`npxG` (Non-Penalty Expected Goals)**: Total xG excluding penalty kicks (which have a fixed ~0.76–0.79 xG). Useful because penalties can artificially inflate a player or team's attacking output.
* **`npxGA` / `npxGD`**: Non-penalty expected goals against and goal difference.
* **Finishing Efficiency (`Goals - xG`)**:
  - **Positive (`Goals > xG`)**: Clinical finishing or hot streak (e.g. Son Heung-min, Mohamed Salah in peak seasons).
  - **Negative (`Goals < xG`)**: Unlucky finishing, poor shot placement, or facing elite goalkeeping.

---

## 2. Passes Per Defensive Action (PPDA) & Pressing

### What is PPDA?
**PPDA (`ppda`)** quantifies the intensity and aggression of a team's high-pressing system in the opponent's defensive half.

$$\text{PPDA} = \frac{\text{Opponent Passes allowed in their defensive 60\% of the pitch}}{\text{Defensive Actions (Tackles + Interceptions + Challenges + Fouls) in that zone}}$$

### How to Interpret PPDA:
> [!NOTE]
> **Inverse Scale**: A **LOWER** PPDA number indicates **MORE AGGRESSIVE** and intense pressing, because the team allows fewer opponent passes before making a defensive challenge.

* **`< 8.5 (Elite High Pressing)`**: Peak Jürgen Klopp (*Gegenpressing*) or Pep Guardiola sides. Relentless high turnover hunting.
* **`8.5 – 11.5 (Active Pressing / Mid-High Block)`**: Modern balanced European style with structured pressing triggers.
* **`> 13.0 – 16.0+ (Low Block / Passive)`**: Deep-sitting defensive teams that concede possession and defend their own penalty box (e.g. historic Sean Dyche Burnley or Roy Hodgson sides).

### `ppda_allowed` (Opponent Pressing against the Team)
Measures the PPDA of opponents when playing against this team.
- **Higher `ppda_allowed`**: Opponents struggle to press this team; the team easily passes through the opponent's press.

---

## 3. Deep Zone Invasions (Deep Completions)

* **`deep_completions`**: Targeted passes completed within **20 yards of the opponent's goal line** (excluding crosses).
* **`deep_allowed`**: Number of deep completions the team conceded to opponents.

### Why is this important?
While possession percentage can be inflated by harmless passes between center-backs in one's own half, **Deep Completions** strictly measure penalty-box penetration and dangerous zone control.

---

## 4. Expected Points (xPTS)

### What is xPTS?
**`xPTS` (Expected Points)** simulates the outcome of every match hundreds of times based on the xG value of every shot taken and conceded.
- A match where Team A generated 3.2 xG and Team B generated 0.4 xG will award Team A nearly **2.85 xPTS** (close to 3 points).
- A tight 1.1 xG vs 1.0 xG game yields ~1.3 xPTS to each side.

### Interpreting League Tables:
Comparing actual **`points`** vs. **`xPTS`**:
- **`Points > xPTS`**: Overperforming underlying numbers (frequently driven by elite goalkeeping, lucky bounces, or late game-winners).
- **`Points < xPTS`**: Underperforming underlying numbers (suggesting bad variance or poor finishing that often mean-reverts).

---

## 5. Player Possession & Build-Up Metrics (xA, xGChain, xGBuildup)

Traditional stats only reward the player who scores (Goal) and the player who passes directly to the scorer (Assist). Advanced analytics evaluate every link in the attacking chain:

```
[Centre-Back] ──(Pass)──> [Deep Midfielder] ──(Through-Ball)──> [Winger] ──(Cross)──> [Striker] ──(Shot / Goal)
     │                           │                                 │                    │
 xGBuildup                   xGBuildup                            xA                   xG
     │                           │                                 │                    │
 └───────────────────────────────┴───────────────┬─────────────────┴────────────────────┘
                                            xGChain
```

### Metrics Breakdown:
1. **`xA` (Expected Assists)**: The xG of the shot resulting from a pass. Evaluates passing creativity and chance creation regardless of whether the striker scores.
2. **`key_passes`**: Total passes that directly lead to an attempt on goal.
3. **`xGChain`**: Total xG of every possession sequence a player participated in. If a player touches the ball at any point in a move that ends in a 0.50 xG chance, they receive 0.50 xGChain.
4. **`xGBuildup`**: Total xG of attacking sequences in which the player was involved **excluding** the shot itself and the key pass. Perfect for evaluating defensive midfielders (e.g. Rodri, Fabinho) and ball-playing center-backs (e.g. Virgil van Dijk).

---

## 6. Post-Shot xG (PSxG / xGOT)

* **`xG` (Pre-Shot)**: Evaluates the chance **before** the shot is struck (location, angle).
* **`PSxG / xGOT` (Post-Shot Expected Goals)**: Evaluates the chance **after** the ball leaves the boot, incorporating:
  - **Trajectory & Placement**: Top corner vs. center of goal.
  - **Shot Speed & Curve**: Difficult dipping shots vs. slow rollers.

### Goalkeeper Evaluation:
$$\text{Goals Prevented} = \text{PSxG Conceded} - \text{Actual Goals Conceded}$$
- **Positive**: Goalkeeper is an elite shot-stopper (saving difficult shots).
- **Negative**: Goalkeeper is conceding shots that an average keeper would save.

---

## 7. Glossary & Summary Table

| Metric | Full Name | Domain | Ideal Target | Description |
| :--- | :--- | :---: | :---: | :--- |
| **`xG`** | Expected Goals | Attack | **High** | Shot quality generated based on location & assist type |
| **`xGA`** | Expected Goals Against | Defense | **Low** | Shot quality conceded to opponents |
| **`xGD`** | Expected Goal Difference | Overall | **High (+)** | Net underlying team quality ($xG - xGA$) |
| **`npxG`** | Non-Penalty xG | Attack | **High** | Open-play and set-piece shot quality without penalty kicks |
| **`ppda`** | Passes Per Defensive Action | Pressing | **Low** | Defensive aggression; lower value = higher pressing tempo |
| **`ppda_allowed`** | Opponent PPDA | Build-Up | **High** | Team's ability to resist and play through opponent press |
| **`deep`** | Deep Completions | Attack | **High** | Completed passes within 20 yards of opponent goal |
| **`xPTS`** | Expected Points | Standings | **High** | Simulated points earned based on match xG profiles |
| **`xA`** | Expected Assists | Player Creation| **High** | Expected goals resulting from a player's key passes |
| **`xGChain`** | xG Chain | Player Impact | **High** | Total xG of all possession sequences involved in |
| **`xGBuildup`** | xG Build-Up | Playmaking | **High** | Build-up contribution excluding the shot and final assist |
