<p align="center">
  <img src="./img.png" alt="Project Banner" width="100%">
</p>

# STREE 🎯

## Basic Details

### Team Name: SHE TECH

### Team Members
- Member 1: Revathy Krishna - College of Engineering Attingal
- Member 2: Krishna R S - College of Engineering Attingal

### Hosted Project Link
[Tink-Her-Hack Stree](https://github.com/RevathyKrishna06/tink-her-hack-stree)

### Project Description
Our project is a women’s health web application that focuses on PCOS/PCOD analysis, personalized cycle tracking, and daily health tips. It helps users monitor their symptoms, track menstrual cycles, and receive guidance on managing pain, mood swings, and overall well-being both at home and in hostels.

### The Problem statement
Many women, especially those with PCOS or PCOD, struggle to track their menstrual cycles, understand their symptoms, and manage associated health issues like pain, mood swings, and hormonal imbalances. Existing apps often lack personalized guidance and practical tips for day-to-day management, especially for users living away from home, such as in hostels.

### The Solution
Our application provides an all-in-one solution by offering PCOS/PCOD analysis, personalized cycle tracking, and health tips tailored to the user’s symptoms. It helps users monitor their menstrual health, manage pain and mood swings effectively, and receive actionable guidance both at home and in hostel environments.

---

## Technical Details

### Technologies/Components Used

**For Software:**
- Languages used: JavaScript, Python (Flask), HTML5, CSS3, SQLite
- Frameworks used: Flask
- Libraries used: werkzeug, sqlite3
- Tools used: VS Code, GitHub, Git

---

## Features

List the key features of your project:
- Feature 1: AI Based PCOD/PCOS risk prediction
- Feature 2: Comprehensive health analysis report
- Feature 3: Personalized diet plan (hostel/home)
- Feature 4: Time based exercise routine generator
- Feature 5: Dynamic Cycle Tracker with phase-aware tips
- Feature 6: Feeling-based health guidance system

---

## Implementation

### For Software:

#### Installation
```bash
[Installation commands - pip install flask ]
```

#### Run
```bash
[Run commands - python app.py]
```



---

## Project Documentation

### For Software:

#### Screenshots (Add at least 3)

![Login Page](./static/screenshots/login.png)
*Login page of our website*

![Dashboard](./static/screenshots/dashboard.png)
*Dashboard of our website*

![PCOS Analyzer](./static/screenshots/pcos.png)
*PCOS/PCOD risk prediction page of our website*

#### Diagrams

**System Architecture:**

![Architecture Diagram](docs/architecture.png)
*The application follow a Flask MVC patterns. Users interact with a responsive HTML/CSS/JS frontend, which communicates with a Python/Flask backend and an SQLite database.*

**Application Workflow:**

![Workflow](docs/workflow.png)
*User registers/logs in -> Dashboard -> Access PCOS Analyzer, Tracker, or Tips -> View personalized results based on environment.*

---


#### Build Photos

![Team](Add photo of your team here)

![Components](Add photo of your components here)
*List out all components shown*

![Build](Add photos of build process here)
*Explain the build steps*

![Final](Add photo of final product here)
*Explain the final build*

---

## Additional Documentation

### For Web Projects with Backend:

#### API Documentation

**Base URL:** `http://127.0.0.1:5000`

##### Endpoints

**POST /login**
- **Description:** Authenticates the user and starts a session.
- **Form Data:**
  - `email` (string): User email
  - `password` (string): User password

**POST /pcos**
- **Description:** Analyzes PCOS risk and provides recommendations.
- **Form Data:**
  - `age`, `height`, `weight`, `irregular`, `acne`, `hair_growth`, `weight_gain`, `family_history`, `living`, `exercise_time`

**POST /tracker**
- **Description:** Logs menstrual cycle data.
- **Form Data:**
  - `start_date`, `end_date`, `symptoms`, `living`

---

## Project Demo

### Video
[STREE Project Demo](https://youtu.be/example)

*Our video demonstrates the user journey: from secure login, through the PCOS risk assessment, tracking menstrual cycles, and receiving personalized health tips based on current feelings and living situation.*

### Additional Demos
[Add any extra demo materials/links - Live site, APK download, online demo, etc.]

---

## AI Tools Used (Optional - For Transparency Bonus)

If you used AI tools during development, document them here for transparency:

**Tool Used:** Antigravity (Advanced Agentic Coding AI)

**Purpose:** 
- Generating and refining the PCOS analysis logic and diet/exercise plans.
- Implementing the cycle tracker predictions and phase-awareness.
- Designing the responsive UI and adding interactive features like the password toggle.
- Assisting in the creation of comprehensive project documentation.

**Key Prompts Used:**
- "Add show password(eye) on password in login page and signup page and also include * for mandatory fields"
- "Add 'sometimes' option into sympton analyzer along with yes and no . Also add * in sympton analyzer mandatory field"
- "Fill the remaining details in README.md according to my project"

**Percentage of AI-generated code:** Approximately 80%

**Human Contributions:**
- Project vision and requirement planning.
- Healthcare logic verification and diet/exercise curation.
- Integration testing and local environment setup.
- Final UI/UX review and documentation approval.

---

## Team Contributions

- Revathy Krishna: Backend development, PCOS analysis algorithm, and Database design.
- Krishna R S: Frontend UI/UX, Cycle tracker logic, and Health tips system.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Common License Options:**
- MIT License (Permissive, widely used)
- Apache 2.0 (Permissive with patent grant)
- GPL v3 (Copyleft, requires derivative works to be open source)

---

Made with ❤️ at TinkerHub
