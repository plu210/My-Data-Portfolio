# Jack P. Lu's Data Project Portfolio
Hi, I'm Jack P. Lu, and this repository is a curated collection of my personal data science projects

## Featured Projects

### [VA Helper](./VA-Helper)
_Solo Project_

A Phase 1 RAG prototype assistant combining official VA policy documents with community insights for veterans navigating tinnitus claims.

<table>
  <tr>
    <td><img src="./assets/VAHelper_Diagram.png" width="455"/></td>
    <td><img src="./assets/VAHelper_loaddata.png" width="455"/></td>
    <td><img src="./assets/VAHelper_pipeline.png" width="455"/></td>
    <td><img src="./assets/VAHelper_prompt_eng.png" width="455"/></td>
    
  </tr>
  <tr>
    <td align="center"><b>VA Helper Pipeline Diagram:</b> End-to-end workflow showing how VA Helper processes policy documents and community texts, retrieves relevant context, and generates structured answers to user queries</td>
    <td align="center"><b>Data Loading and Preprocessing:</b> Parsed, cleaned, and segmented source files into 388 document pieces, yielding 887 text chunks ready for vector retrieval </td>
    <td align="center"><b>Retrieval and Generation:</b> Vectorized 1113 text chunks, then retrieved and generated both <i>Official Policy</i> and <i>Community Insights</i> answers for the sample query: “Can I apply for tinnitus benefits without a formal diagnosis?” </td>
    <td align="center"><b>Prompt Engineering Snippet:</b> Example of a structured system prompt directing the LLM to reason step-by-step and format answers into “Official Policy” and “Community Insights,” following custom formatting and tone guidelines.
  </i> </td>
  </tr>
</table>
<p align="center"><i>Click any image to view in full resolution.</i></p>

<p align="center">
  <a href="./VA-Helper">
    <img src="./assets/q1_no_diagnosis.gif" alt="VA Helper Demo" width="500"/>
  </a>
</p>
<p align="center">
  <i>
    <b>Demo:</b> User asks “Can I apply for tinnitus benefits without a formal diagnosis?” and receives a structured answer showing both official VA policy and real-world community insights.
  </i>
</p>

**Tech Stack:** Python · LangChain · Ollama · Streamlit

### Vibe Check (private repo)
_Team project (4)_  **Role:** Project manager and technical contributor — led evaluation design, coordinated team communication, and supported UI development.

Developed a two-tier sentiment analysis pipeline (VADER + Google Cloud NLP) and a personalized venue recommendation engine with interactive “vibe weight” sliders and a map-based UI, achieving 78% Precision@3 in vibe tagging and 62% sentiment classification accuracy on the Yelp Open Dataset.

**[Read the full project report (PDF)](./docs/team020report.pdf)**

<table>
  <tr>
    <td><img src="./assets/vc_pipeline.png" width="455"/></td>
    <td><img src="./assets/list.png" width="455"/></td>
    <td><img src="./assets/map_hover.png" width="455"/></td>
    <td><img src="./assets/map_detail.png" width="455"/></td>
  </tr>
  <tr>
    <td align="center">Vibe Check Pipeline Diagram</td>
    <td align="center">List View (Full App)</td>
    <td align="center">Map View (Pin Hovered)</td>
    <td align="center">Map View (Pin Clicked)</td>
  </tr>
</table>
<p align="center"><i>Click any image to view in full resolution.</i></p>

<p align="center">
  <a href="https://www.youtube.com/watch?v=5-HJOuXxcwE&ab_channel=plu1994" target="_blank">
    <img src="https://img.shields.io/badge/YouTube-VibeCheck_Presentation-red?logo=youtube" alt="Watch the Vibe Check Presentation"/>
  </a>
  <br>
  <i>Watch the Vibe Check project presentation on YouTube</i>
</p>

**Tech Stack:** Python · VADER · Google Cloud NLP · HTML/JavaScript (Leaflet)

**My contributions:**  
- Stepped up as project manager, leading team communication, facilitating meetings, documenting action items, and tracking progress throughout the project
- Took primary responsibility for drafting and assembling the final report and presentation, integrating technical findings with product and design highlights
- Developed the interactive map UI for the front page using Leaflet, including toggle functionality between map and list views  
- Developed the evaluation framework: independently set up the golden dataset labeling process, established the project’s performance metrics (precision@3, tagging accuracy), and document findings 

*Note: This was a collaborative, end-to-end product design and ML project. Repository is private due to course policy

### [San Francisco Traffic Collision Data Analysis](./San%20Francisco%20Traffic%20Collision%20Data%20Analysis)
_Solo project_

Python EDA of San Francisco bicycle & pedestrian collisions (2006–2022) using [SFCTA data](https://safety.sfcta.org/). Investigates **Vision Zero (2014)** trend shifts, **street-level risk**, and **mode severity** (pedestrian vs. bicycle) with static charts and interactive maps.

[Open in Google Colab](./San%20Francisco%20Traffic%20Collision%20Data%20Analysis/SanFranciscoTrafficCollisionDataAnalysis.ipynb)

[View on nbviewer](https://nbviewer.org/github/plu210/My-Data-Portfolio/blob/main/San%20Francisco%20Traffic%20Collision%20Data%20Analysis/SanFranciscoTrafficCollisionDataAnalysis.ipynb)

[View the HTML Version](./San%20Francisco%20Traffic%20Collision%20Data%20Analysis/SanFranciscoTrafficCollisionDataAnalysis.html)

<table>
  <tr>
    <td><img src="./assets/SFTCDA_V0.png" width="455"/></td>
    <td><img src="./assets/Fatalities_per_collision_top5.png" width="455"/></td>
    <td><img src="./assets/Highest_Fatalities_per_collision.png" width="455"/></td>
    <td><img src="./assets/SFTCDA_fatalitiy_rates.png" width="455"/></td>
    <td><img src="./assets/SFTCDA_map_both.png" width="455"/></td>
  </tr>
  <tr>
    <td align="center"><b>Number of Collisions Per Year (Pre vs Post Vision Zero):</b> On average, the change in collision rates is 7.01% from 2008 to 2014, succeeded by a downtrend trend of -5.07% in the change in collision rates from 2014 to 2020. This observation underscores a shift in collision occurrences over the specified period, potentially linked to the introduction of Vision Zero initiatives.</td>
    <td align="center"><b>Fatalities Per Collision on Top 5 Streets:</b> MISSION ST: 3.06%, MARKET ST: 2.44%, GEARY BLVD: 4.64%, FOLSOM ST: 2.37%, POLK ST: 1.49%.</td>
    <td align="center"><b>Streets with Highest Fatalities per Collision:</b> Tennessee St and Tulare St each have a 100% fatalities-per-collision rate due to a single fatality on each street from 2006 to 2022, highlighting the need to consider both total deaths and rate for context.</td>
    <td align="center"><b>Fatality Rates: Pedestrians vs Cyclists:</b> Pedestrian fatality rate 2.38% vs Cyclist 0.44%</td>
    <td align="center"><b>Collision Incidents Map:</b> Interactive OpenStreetMap layer of San Francisco between 2014-2022 for pedestrain (red) and bicycle (teal)</td>
  </tr>
</table>
<p align="center"><i>Click any image to view in full resolution.</i></p>
    
**Tech Stack:** Python · Pandas · NumPy · Matplotlib · Plotly Express

*Note: Originally created as course project for CSE 6040: Computing for Data Analytics and included here as a portfolio piece.

## Legacy Projects

## About

- [LinkedIn](https://linkedin.com/in/jackplu)
