from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "stree_secret_key"

# ------------------ FILE UPLOAD CONFIG ------------------
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024   # 5 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ------------------ DATABASE INIT ------------------
def init_db():
    conn = sqlite3.connect("stree.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cycle_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            start_date TEXT,
            end_date TEXT,
            cycle_length INTEGER,
            period_length INTEGER,
            symptoms TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

init_db()


# ------------------ ROOT ------------------
@app.route('/')
def index():
    return redirect('/login')


# ------------------ SIGNUP ------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("stree.db")
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (name, age, email, password)
                VALUES (?, ?, ?, ?)
            """, (name, age, email, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('signup.html', error="This email is already registered. Please login.")

        conn.close()
        return redirect('/login')

    return render_template('signup.html')


# ------------------ LOGIN ------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect("stree.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[4], password):
            session['user'] = user[1]
            session['email'] = user[3]
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Invalid email or password. Please try again.")

    return render_template('login.html')


# ------------------ DASHBOARD ------------------
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', username=session['user'])
    return redirect('/login')


# ------------------ PCOS ANALYZER ------------------
def get_exercise_plan(risk_level, exercise_minutes, living):
    """
    Returns a personalized exercise plan list based on:
    - risk_level : 'low' | 'medium' | 'high'
    - exercise_minutes : int (15, 30, 45, 60, 90)
    - living : 'hostel' | 'home'
    """
    minutes = int(exercise_minutes)

    # ---- Base exercise banks ----
    hostel_exercises = {
        15: [
            {"name": "Brisk Walk",       "desc": "Walk around your hostel campus at a fast pace.", "duration": "10 min"},
            {"name": "Stretching",        "desc": "Full-body stretch routine to improve flexibility.", "duration": "5 min"},
        ],
        30: [
            {"name": "Brisk Walk / Jog", "desc": "Alternate between walking and jogging on campus.", "duration": "15 min"},
            {"name": "Bodyweight HIIT",   "desc": "Jumping jacks, high knees, squats — no equipment needed.", "duration": "10 min"},
            {"name": "Cool-down Stretch", "desc": "Ease your muscles and improve circulation.", "duration": "5 min"},
        ],
        45: [
            {"name": "Jog / Run",         "desc": "Moderate-paced outdoor jog.", "duration": "20 min"},
            {"name": "Bodyweight Circuit","desc": "Squats, lunges, push-ups, plank — 3 rounds.", "duration": "15 min"},
            {"name": "Yoga / Stretch",    "desc": "Focus on lower abdomen and hip openers.", "duration": "10 min"},
        ],
        60: [
            {"name": "Outdoor Run",       "desc": "Steady-state run at a comfortable pace.", "duration": "25 min"},
            {"name": "Strength Circuit",  "desc": "Bodyweight squats, glute bridges, push-ups, mountain climbers.", "duration": "20 min"},
            {"name": "Yoga Flow",         "desc": "Sun salutations and hip-opening poses.", "duration": "15 min"},
        ],
        90: [
            {"name": "Run / Cycle",       "desc": "Sustained cardio — run or rent a bicycle.", "duration": "35 min"},
            {"name": "Core & Strength",   "desc": "Full bodyweight workout: squats, deadlifts (bodyweight), planks.", "duration": "30 min"},
            {"name": "Yoga & Meditation", "desc": "Hormone-balancing yoga poses + 5 min breathing.", "duration": "25 min"},
        ],
    }

    home_exercises = {
        15: [
            {"name": "Yoga Warm-up",      "desc": "Child's pose, cat-cow, and gentle twists.", "duration": "10 min"},
            {"name": "Breathing Exercise","desc": "Anulom Vilom pranayama to balance hormones.", "duration": "5 min"},
        ],
        30: [
            {"name": "Yoga Flow",         "desc": "Sun salutations, warrior poses, hip openers.", "duration": "20 min"},
            {"name": "Strength Training", "desc": "Squats, glute bridges, and household-weight exercises.", "duration": "10 min"},
        ],
        45: [
            {"name": "Yoga & Pilates",    "desc": "Combine yoga poses with pilates core moves.", "duration": "25 min"},
            {"name": "Home Cardio",       "desc": "Dance, skipping rope, or aerobics video.", "duration": "15 min"},
            {"name": "Meditation",        "desc": "Guided meditation to reduce cortisol.", "duration": "5 min"},
        ],
        60: [
            {"name": "Dance / Zumba",     "desc": "High-energy fun cardio — 30-min online video.", "duration": "30 min"},
            {"name": "Strength & Yoga",   "desc": "Light dumbbells + hormone-balance asanas.", "duration": "20 min"},
            {"name": "Breathing & Relax", "desc": "Pranayama and body scan relaxation.", "duration": "10 min"},
        ],
        90: [
            {"name": "Cardio Workout",    "desc": "Dance, aerobics, or treadmill (if available).", "duration": "35 min"},
            {"name": "Weight Training",   "desc": "Dumbbells or resistance bands — full body routine.", "duration": "30 min"},
            {"name": "Yoga Nidra",        "desc": "Deep relaxation yoga to reduce androgens.", "duration": "25 min"},
        ],
    }

    # Normalise minutes to nearest key
    time_keys = [15, 30, 45, 60, 90]
    closest = min(time_keys, key=lambda k: abs(k - minutes))

    exercises = (hostel_exercises if living == 'hostel' else home_exercises).get(closest, [])

    # ---- Risk-specific tips ----
    tips = {
        'low': (
            "Great news! Keep maintaining an active lifestyle. "
            "Even light daily exercise significantly helps hormonal balance."
        ),
        'medium': (
            "Consistency is key! Aim for at least 5 days a week. "
            "Reduce refined sugar and processed foods alongside exercise."
        ),
        'high': (
            "Please consult a gynecologist soon. In the meantime, low-impact exercises "
            "like yoga and walking are highly effective for PCOS management. "
            "Avoid high-stress workouts and prioritize sleep."
        ),
    }

    return exercises, tips[risk_level]


def get_diet_chart(risk_level, living):
    hostel_meals = [
        {
            "time": "7:00 – 8:00 AM", "label": "Breakfast", "emoji": "🌅",
            "foods": [
                "Oats porridge with banana slices & 5 almonds",
                "OR Poha (less oil, no potato) with peanuts",
                "OR 2 boiled eggs + 1 multigrain bread slice",
                "Warm lemon water (1 glass before eating)",
            ]
        },
        {
            "time": "10:30 AM", "label": "Mid-Morning Snack", "emoji": "🍎",
            "foods": [
                "1 apple / guava / papaya / pear",
                "OR Roasted chana (handful) from canteen",
                "OR Makhana (fox nuts) — 1 small pack",
            ]
        },
        {
            "time": "1:00 – 2:00 PM", "label": "Lunch (Mess)", "emoji": "🍱",
            "foods": [
                "2 rotis + moong dal / chana dal / rajma",
                "Green sabzi: palak, methi, lauki, tinda (choose from mess)",
                "1 bowl cucumber + carrot + onion salad",
                "1 small bowl low-fat curd / buttermilk",
            ]
        },
        {
            "time": "4:30 – 5:00 PM", "label": "Evening Snack", "emoji": "🫖",
            "foods": [
                "Green tea / spearmint tea (no sugar)",
                "5–6 walnuts + 5 almonds",
                "OR 1 banana / guava",
            ]
        },
        {
            "time": "8:00 – 9:00 PM", "label": "Dinner (Mess)", "emoji": "🌙",
            "foods": [
                "1–2 rotis + dal (moong/masoor/chana)",
                "Any green vegetable sabzi from mess",
                "Skip rice & fried items at night",
                "1 glass warm turmeric milk at bedtime",
            ]
        },
    ]

    home_meals = [
        {
            "time": "7:00 – 8:00 AM", "label": "Breakfast", "emoji": "🌅",
            "foods": [
                "Vegetable oats upma with broccoli, spinach & flaxseeds",
                "OR Moong dal chilla (2 pieces) with green chutney",
                "OR 2 egg white omelette with onion, tomato & sprouts",
                "1 glass methi seed water (soaked overnight)",
            ]
        },
        {
            "time": "10:30 AM", "label": "Mid-Morning Snack", "emoji": "🍎",
            "foods": [
                "Coconut water (1 glass)",
                "1 bowl papaya / strawberries / blueberries / apple",
                "8–10 soaked almonds + 4 walnut halves",
            ]
        },
        {
            "time": "1:00 – 2:00 PM", "label": "Lunch", "emoji": "🍱",
            "foods": [
                "Brown rice (½ cup) OR jowar / bajra / quinoa roti (2)",
                "Palak dal / rajma / chana / soybean curry",
                "Stir-fried or steamed sabzi: broccoli, beans, carrots",
                "Salad: cucumber, tomato, sprouts, lemon + olive oil dressing",
                "Low-fat curd / raita (1 bowl)",
            ]
        },
        {
            "time": "4:30 – 5:00 PM", "label": "Evening Snack", "emoji": "🫖",
            "foods": [
                "Spearmint / green tea or black coffee (no sugar)",
                "Roasted pumpkin seeds + sunflower seeds + flax seeds (2 tbsp)",
                "OR 1 small bowl mixed sprouts chaat with lemon",
            ]
        },
        {
            "time": "8:00 – 9:00 PM", "label": "Dinner", "emoji": "🌙",
            "foods": [
                "2 jowar / wheat rotis with ghee (½ tsp)",
                "Dal palak / mixed vegetable curry / tofu stir-fry",
                "OR Vegetable khichdi (moong dal + rice 1:2 ratio)",
                "Salad: cucumber + tomato + beetroot",
                "Finish dinner by 8 PM — no eating after",
            ]
        },
    ]

    high_risk_extra = {
        "time": "All Day", "label": "Anti-Inflammatory Boost", "emoji": "💊",
        "foods": [
            "Cinnamon powder (½ tsp) in oats or warm water — reduces insulin resistance",
            "Turmeric (haldi) in dal / sabzi / milk daily",
            "Spearmint tea (2 cups/day) — lowers excess androgens",
            "2.5–3 litres plain water throughout the day",
            "Avoid ALL refined sugar, maida, packaged biscuits & chips",
        ]
    }

    avoid = [
        "White bread, maida rotis & noodles",
        "Sugary drinks — cold drinks, packaged juices, energy drinks",
        "Deep-fried snacks — samosa, pakoda, french fries",
        "Excess full-fat dairy — paneer, butter, cream",
        "Processed foods — Maggi, chips, biscuits, cookies",
        "Skipping meals — especially breakfast",
        "Late-night eating (after 9 PM)",
    ]

    diet_tip_map = {
        "low": "Your diet looks manageable! Focus on consistency — eat at regular times and stay hydrated.",
        "medium": "Reducing sugar and refined carbs will make a noticeable difference within 4–6 weeks.",
        "high": "Diet is the most powerful tool for managing PCOS. Combine this plan with your doctor's advice for best results.",
    }

    meals = home_meals if living == "home" else hostel_meals
    if risk_level == "high":
        meals = meals + [high_risk_extra]

    return meals, avoid, diet_tip_map[risk_level]



@app.route('/pcos', methods=['GET', 'POST'])
def pcos():

    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        # ---- New Metrics fields ----
        age           = int(request.form['age'])
        height_cm     = float(request.form['height'])
        weight_kg     = float(request.form['weight'])
        
        # Calculate BMI
        height_m = height_cm / 100
        bmi = round(weight_kg / (height_m ** 2), 1)
        
        bmi_cat = "Normal"
        bmi_score = 0
        if bmi < 18.5:
            bmi_cat = "Underweight"
        elif 18.5 <= bmi < 25:
            bmi_cat = "Healthy Weight"
        elif 25 <= bmi < 30:
            bmi_cat = "Overweight"
            bmi_score = 1
        else:
            bmi_cat = "Obese"
            bmi_score = 2

        # ---- Symptom scores ----
        # Weighting primary symptoms heavier
        # Values from Form: 0=No, 1=Sometimes, 2=Yes
        irregular     = int(request.form['irregular']) * 2      # 0, 2, 4
        acne          = int(request.form['acne']) * 0.5         # 0, 0.5, 1
        hair_growth   = int(request.form['hair_growth']) * 1.5  # 0, 1.5, 3
        weight_gain   = int(request.form['weight_gain']) * 0.5  # 0, 0.5, 1
        family_history= int(request.form['family_history'])     # 0, 1, 2

        # ---- Lifestyle fields ----
        living        = request.form['living']          # 'hostel' or 'home'
        exercise_time = request.form['exercise_time']   # minutes string

        # ---- Risk calculation ----
        score     = irregular + acne + hair_growth + weight_gain + family_history + bmi_score
        max_score = 13  # 4 + 1 + 3 + 1 + 2 + 2
        percentage = int((score / max_score) * 100)

        if percentage < 35:
            result     = "Low Risk of PCOS / PCOD 🌿"
            risk_class = "low"
        elif 35 <= percentage < 65:
            result     = "Moderate Risk of PCOS / PCOD ⚠️"
            risk_class = "medium"
        else:
            result     = "High Risk of PCOS / PCOD 🚨 Please Consult a Doctor"
            risk_class = "high"

        # ---- Exercise plan ----
        exercises, tip = get_exercise_plan(risk_class, exercise_time, living)

        # ---- Diet chart ----
        diet_meals, diet_avoid, diet_tip = get_diet_chart(risk_class, living)

        # ---- File upload ----
        report_uploaded = False
        report_filename = None
        file = request.files.get('report')
        if file and file.filename and allowed_file(file.filename):
            report_filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], report_filename))
            report_uploaded = True

        return render_template(
            'pcos.html',
            result=result,
            percentage=percentage,
            risk_class=risk_class,
            bmi=bmi,
            bmi_cat=bmi_cat,
            exercise_time=exercise_time,
            exercises=exercises,
            tip=tip,
            diet_meals=diet_meals,
            diet_avoid=diet_avoid,
            diet_tip=diet_tip,
            living=living,
            report_uploaded=report_uploaded,
            report_filename=report_filename,
        )

    return render_template('pcos.html')


# ------------------ CYCLE TRACKER HELPERS ------------------
def calculate_cycle_predictions(logs, pcos_risk_class):
    """
    Takes a list of cycle logs (from oldest to newest) and calculates:
    - Average cycle length
    - Next expected period date
    - Next fertile window
    - Red flags / alerts (e.g. >35 days indicates PCOS risk)
    - Current phase (approx based on days since last period)
    """
    if not logs:
        return None

    # Sort logs by start date ascending just in case
    logs = sorted(logs, key=lambda x: datetime.strptime(x[2], '%Y-%m-%d'))
    
    # Calculate average cycle length from valid previous cycle_lengths
    cycle_lengths = [log[4] for log in logs if log[4] is not None and log[4] > 0]
    avg_cycle = sum(cycle_lengths) // len(cycle_lengths) if cycle_lengths else 28
    
    # Get the most recent period start date
    latest_start_str = logs[-1][2]
    latest_start = datetime.strptime(latest_start_str, '%Y-%m-%d').date()
    today = datetime.now().date()
    
    # Predict next period start
    next_period_date = latest_start + timedelta(days=avg_cycle)
    days_to_next = (next_period_date - today).days

    # Predict fertile window (roughly 14 days before next period)
    ovulation_date = next_period_date - timedelta(days=14)
    fertile_start = ovulation_date - timedelta(days=4)
    fertile_end = ovulation_date + timedelta(days=1)

    # Determine approximate current phase
    days_since_start = (today - latest_start).days
    current_phase = ""
    # Assuming average period is 5 days
    if days_since_start < 6:
        current_phase = "Menstrual"
    elif today < fertile_start:
        current_phase = "Follicular"
    elif fertile_start <= today <= fertile_end:
        current_phase = "Ovulation"
    else:
        current_phase = "Luteal"

    # Red Flags & Alerts
    alerts = []
    if cycle_lengths:
        recent_cycle = cycle_lengths[-1]
        if recent_cycle > 35:
            alerts.append(f"Your last cycle was {recent_cycle} days (longer than usual 35 days). This is a common PCOS symptom.")
        elif recent_cycle < 21:
            alerts.append(f"Your last cycle was very short ({recent_cycle} days). Frequent periods can cause anemia.")
        
        # Fluctuation check
        if len(cycle_lengths) >= 2:
            diff = abs(cycle_lengths[-1] - cycle_lengths[-2])
            if diff > 7:
                alerts.append("High cycle fluctuation detected (>7 days difference). This irregularity is a key red flag for PCOD.")
                
    if pcos_risk_class == "high":
        alerts.append("Based on your PCOS analyzer result, you are at HIGH risk. Please consult a doctor regarding your cycle health.")

    return {
        "avg_cycle": avg_cycle,
        "next_period": next_period_date.strftime('%d %b %Y'),
        "days_to_next": days_to_next,
        "fertile_window": f"{fertile_start.strftime('%d %b')} - {fertile_end.strftime('%d %b')}",
        "current_phase": current_phase,
        "alerts": alerts
    }

def get_tracker_tips(living, current_phase):
    """Returns tips based on Hostel/Home living and current phase."""
    tips = {
        "Menstrual": {
            "hostel": [
                "Drink warm water from the mess/canteen dispenser.",
                "Use a hot water bag for cramps (borrow from warden/friends if needed).",
                "Eat iron-rich snacks: dates, jaggery, or roasted chana.",
                "Avoid heavy mess food; stick to dal/roti or khichdi."
            ],
            "home": [
                "Drink homemade ginger-ajwain tea for cramps.",
                "Use a heating pad and take adequate rest.",
                "Eat palak (spinach) or beetroot to replenish iron.",
                "Practice restorative yoga (Balasana/Child's pose)."
            ]
        },
        "Follicular": {
            "hostel": [
                "Energy is high! Do a 20-min HIIT workout in your room.",
                "Grab fresh fruits from the local vendor/canteen.",
                "Include soaked almonds/walnuts in your morning routine."
            ],
            "home": [
                "Great time for intense workouts or joining a gym class.",
                "Incorporate flaxseeds and pumpkin seeds into your diet.",
                "Eat fresh salads with lunch."
            ]
        },
        "Ovulation": {
            "hostel": [
                "Stay hydrated! Keep a 1L bottle on your desk.",
                "Mess food can be oily—try to eat early and avoid fried snacks.",
                "Engage in group sports or evening walks with hostellers."
            ],
            "home": [
                "Perfect time for social events and high-energy tasks.",
                "Focus on cruciferous veggies like broccoli and cauliflower.",
                "Drink fresh coconut water."
            ]
        },
        "Luteal": {
            "hostel": [
                "PMS starting? Switch from coffee to green tea.",
                "Cravings hitting? Keep dark chocolate or roasted makhana handy.",
                "Prioritize sleep; wear an eye mask if your roommate studies late."
            ],
            "home": [
                "Reduce salt intake to minimize bloating.",
                "Drink chamomile or peppermint tea before bed.",
                "Do light exercises like walking or gentle stretching."
            ]
        }
    }
    
    # Default to Menstrual if phase is unknown
    phase = current_phase if current_phase in tips else "Menstrual"
    return tips[phase].get(living, tips[phase]["home"])


# ------------------ CYCLE TRACKER ROUTES ------------------
@app.route('/tracker', methods=['GET', 'POST'])
def tracker():
    if 'user' not in session:
        return redirect('/login')

    user_email = session['email']
    conn = sqlite3.connect("stree.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (user_email,))
    user_id = cursor.fetchone()[0]

    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        symptoms_list = request.form.getlist('symptoms')
        symptoms = ", ".join(symptoms_list)
        living = request.form.get('living', 'home')
        
        # Save living situation in session for tips
        session['living'] = living

        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') if end_date else start_dt
        period_length = (end_dt - start_dt).days + 1

        # Calculate cycle length (from previous period start to this start)
        cursor.execute("SELECT start_date FROM cycle_logs WHERE user_id = ? ORDER BY start_date DESC LIMIT 1", (user_id,))
        last_log = cursor.fetchone()
        cycle_length = None
        if last_log:
            last_start_dt = datetime.strptime(last_log[0], '%Y-%m-%d')
            cycle_length = (start_dt - last_start_dt).days
            # Prevent negative cycles if logging back in time (simple safeguard)
            if cycle_length < 0: cycle_length = None

        cursor.execute("""
            INSERT INTO cycle_logs (user_id, start_date, end_date, cycle_length, period_length, symptoms)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, start_date, end_date, cycle_length, period_length, symptoms))
        
        conn.commit()
        conn.close()
        return redirect('/tracker')

    # GET Request Processing
    cursor.execute("SELECT * FROM cycle_logs WHERE user_id = ? ORDER BY start_date ASC", (user_id,))
    logs = cursor.fetchall()
    
    # We need to know previous PCOS risk if any to pass to predictions. 
    # Since we didn't save PCOS risk to DB, we'll assume "unknown" unless we want to extend the schema.
    # For now, we'll pass "unknown"
    pcos_risk = "unknown"
    
    predictions = calculate_cycle_predictions(logs, pcos_risk)
    
    # Get living situation from session, default to home
    living = session.get('living', 'home')
    
    tips = []
    if predictions:
        tips = get_tracker_tips(living, predictions['current_phase'])

    # Format data for Chart.js
    chart_labels = []
    chart_data = []
    for log in logs[-6:]: # Last 6 cycles
        if log[4]: # If cycle_length exists
            dt = datetime.strptime(log[2], '%Y-%m-%d')
            chart_labels.append(dt.strftime('%b'))
            chart_data.append(log[4])

    conn.close()
    
    # Reverse logs for displaying history (newest first)
    history_logs = list(reversed(logs))

    return render_template('tracker.html', 
                           logs=history_logs, 
                           predictions=predictions, 
                           tips=tips,
                           living=living,
                           chart_labels=chart_labels,
                           chart_data=chart_data)





# ------------------ HEALTH TIPS ------------------
def get_dynamic_tips(feeling_text, living):
    """
    Analyzes the user's feeling text and returns contextual health tips.
    Categories: pain, mood, fatigue, diet
    """
    feeling_text = feeling_text.lower()
    
    # Keywords
    pain_keywords = ['pain', 'cramp', 'ache', 'sore', 'back', 'hurt', 'stomachache']
    mood_keywords = ['sad', 'angry', 'mood', 'cry', 'stress', 'anxi', 'depress', 'irritab', 'overwhelm']
    fatigue_keywords = ['tired', 'sleep', 'exhaust', 'fatigue', 'lazy', 'low energy', 'drain']
    diet_keywords = ['bloat', 'hungry', 'crav', 'nausea', 'food', 'sweet', 'chocolate', 'heavy']
    
    matched_categories = []
    
    if any(word in feeling_text for word in pain_keywords):
        matched_categories.append('pain')
    if any(word in feeling_text for word in mood_keywords):
        matched_categories.append('mood')
    if any(word in feeling_text for word in fatigue_keywords):
        matched_categories.append('fatigue')
    if any(word in feeling_text for word in diet_keywords):
        matched_categories.append('diet')
        
    # Standard responses from our database
    responses = {
        'pain': {
            'home': [
                "**The Classic Heating Pad:** Use a proper hot water bag or an electric heating pad on your lower abdomen to soothe muscle cramps and improve blood flow.",
                "**Soothing Teas:** Brew a fresh cup of warm ginger or chamomile tea to reduce inflammation and relax the body.",
                "**Gentle Movement:** Practice light, restorative yoga poses, such as Child’s Pose or a gentle reclining twist, on your bed or an exercise mat."
            ],
            'hostel': [
                "**DIY Heating Pad:** Fill a sturdy water bottle with hot water, wrap it in a towel or thick t-shirt, and place it on your stomach.",
                "**Quick Herbal Fix:** Keep peppermint or ginger tea bags in your room. Use warm water from the kettle, dispenser, or canteen.",
                "**Dress for Comfort:** Change out of jeans or tight clothes into the loosest, most comfortable pajamas as soon as you return to your room."
            ]
        },
        'mood': {
            'home': [
                "**Sensory Break:** Step into a quiet, dimly lit room for 15 minutes. Close your eyes and listen to calming music or guided meditation.",
                "**Creative Outlet:** Engage in a relaxing hobby you enjoy—like reading, sketching, or gardening—to gently distract and center your mind.",
                "**Fresh Air:** Step out onto your balcony or take a short, slow walk in your garden for a change of scenery."
            ],
            'hostel': [
                "**Create a 'Bubble':** Put on noise-canceling headphones (or regular earphones) and play your favorite podcast to block out hostel noise.",
                "**Brain Dump:** Keep a journal on your desk. Write down your thoughts or doodle when feeling overwhelmed.",
                "**Change Scenery:** Leave your room and take a short walk on the hostel terrace or campus grounds to reset."
            ]
        },
        'fatigue': {
            'home': [
                "**The Power Nap:** Take a strict 20 to 30-minute power nap setting an alarm to avoid grogginess.",
                "**Fresh Energy Snacks:** Grab a sustaining snack from the kitchen, like an apple with peanut butter or fresh yogurt with berries.",
                "**Light Stretching:** Full-body stretching for 5 minutes. Reaching for the ceiling and touching toes can quickly improve blood circulation."
            ],
            'hostel': [
                "**Legs Up:** Lie on your bed and prop your legs up against the wall for 10-15 minutes to return blood flow to heart and brain.",
                "**Smart Stash:** Keep non-perishable, energy-boosting snacks in your cupboard like roasted makhana or mixed seeds.",
                "**The Cold Splash:** Splash cold water on your face, followed by deliberate neck rolls and shoulder shrugs at your desk."
            ]
        },
        'diet': {
            'home': [
                "**Infused Hydration:** Make 'spa water' adding cucumber, lemon, and mint leaves to your water to encourage drinking and reduce bloating.",
                "**Smart Sweets:** Satisfy sugar cravings with natural options like dark chocolate (70%+), dates, or grapes.",
                "**Controlled Cooking:** Prepare meals with fresh, fiber-rich vegetables and lean proteins, keeping processed ingredients to a minimum."
            ],
            'hostel': [
                "**The Visual Reminder:** Keep a large, transparent water bottle on your desk as a reminder to drink consistently.",
                "**Mess Hacks:** Build a balanced plate prioritizing salads, plain curd, and protein sources, while limiting heavy, oily gravies.",
                "**Midnight Craving Kit:** Keep healthier alternatives for late-night hunger like plain rolled oats or a small packet of dark chocolate."
            ]
        }
    }
    
    selected_tips = []
    
    if not matched_categories:
        # Generic comforting response
        selected_tips.append({
            'title': '🤍 A Gentle Reminder',
            'tips_list': [
                "Take a deep breath. Whatever you're feeling right now is completely okay and valid.",
                "Ensure you're drinking enough water today. It's a small step that makes a big difference.",
                "Take 5 minutes to step away from screens and rest your eyes.",
                "Be kind to yourself today. You are doing the best you can."
            ]
        })
    else:
        # Compile tips for matched categories
        category_titles = {
            'pain': '⚡ Easing Your Discomfort',
            'mood': '🎭 Supporting Your Mood',
            'fatigue': '🥱 Restoring Your Energy',
            'diet': '🥗 Nourishing Your Body'
        }
        
        for cat in matched_categories:
            selected_tips.append({
                'title': category_titles[cat],
                'tips_list': responses[cat][living]
            })
            
    return selected_tips


@app.route('/tips', methods=['GET', 'POST'])
def tips():
    if 'user' not in session:
        return redirect('/login')
    
    living = session.get('living', 'home')
    dynamic_tips = None
    user_feeling = ""
    
    if request.method == 'POST':
        user_feeling = request.form.get('feeling', '')
        # Allow user to update their living situation from the tips page if desired
        living_toggle = request.form.get('living_env')
        if living_toggle in ['home', 'hostel']:
            living = living_toggle
            session['living'] = living
            
        if user_feeling.strip():
            dynamic_tips = get_dynamic_tips(user_feeling, living)

    return render_template('tips.html', default_living=living, dynamic_tips=dynamic_tips, user_feeling=user_feeling)


# ------------------ LOGOUT ------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)
