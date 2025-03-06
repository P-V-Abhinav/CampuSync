import streamlit as st
import pandas as pd
import replicate

# Student Authentication
def student_login():
    st.sidebar.title("Student Login")
    user_id = st.sidebar.text_input("Enter your university ID")
    password = st.sidebar.text_input("Enter your password", type="password")
    if user_id and password:
        # For demo purposes, accept any password. Replace with real authentication if needed.
        return user_id
    else:
        return None
    
def canteen_owner_login():
    st.title("Canteen Owner Login")
    owner_id = st.text_input("Enter your owner ID")
    password = st.text_input("Enter your password", type="password")
    if owner_id == "CUSATCANTEEN1" and password == "123":  # Replace with your actual password
        st.success("Logged in as Canteen Owner")
        canteen_owner_management()
    elif owner_id or password:
        st.error("Invalid Owner ID or Password")



# Save request to CSV
def save_request(filename, data):
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        df = pd.DataFrame()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(filename, index=False)

# Save item to marketplace CSV
def save_marketplace_item(data):
    try:
        df = pd.read_csv("marketplace_items.csv")
    except FileNotFoundError:
        df = pd.DataFrame()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv("marketplace_items.csv", index=False)

# Delete item from marketplace CSV
def delete_marketplace_item(user_id, item_name):
    try:
        df = pd.read_csv("marketplace_items.csv")
        df = df[~((df['user_id'] == user_id) & (df['item'] == item_name))]
        df.to_csv("marketplace_items.csv", index=False)
    except FileNotFoundError:
        pass

# Add feedback saving function
def save_feedback(user_id, hostel_name, rating):
    try:
        df = pd.read_csv("feedback.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["user_id", "hostel_name", "rating"])
    df = pd.concat([df, pd.DataFrame([{"user_id": user_id, "hostel_name": hostel_name, "rating": rating}])], ignore_index=True)
    df.to_csv("feedback.csv", index=False)

# Add average feedback display
def display_average_feedback(hostel_name):
    try:
        df = pd.read_csv("feedback.csv")
        hostel_feedback = df[df["hostel_name"] == hostel_name]
        if not hostel_feedback.empty:
            avg_rating = hostel_feedback["rating"].mean() * 5  # Scale to 5-star system
            st.write(f"⭐ Average Rating: {avg_rating:.1f}/5")
        else:
            st.write("No feedback yet.")
    except FileNotFoundError:
        st.write("No feedback available.")

# Updated Hostel Listing Section
def hostel_listing(user_id):
    st.write("## 🏠 Hostel Listings")
    hostels = [
        {"name": "Michael Hostel", "room_type": "Single", "rent": 5000},
        {"name": "BoyZone", "room_type": "Single", "rent": 3000}
    ]
    for hostel in hostels:
        st.write(f"### {hostel['name']}")
        st.write(f"Room Type: {hostel['room_type']}")
        st.write(f"Rent: ₹{hostel['rent']}")
        if st.button(f"Request {hostel['name']}"):
            save_request("hostel_requests.csv", {"user_id": user_id, "hostel": hostel['name'], "room_type": hostel['room_type'], "rent": hostel['rent']})
            st.success("Request saved!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"👍 Thumbs Up ({hostel['name']})"):
                save_feedback(user_id, hostel['name'], 1)
                st.success("Thanks for your positive feedback!")
        with col2:
            if st.button(f"👎 Thumbs Down ({hostel['name']})"):
                save_feedback(user_id, hostel['name'], 0)
                st.success("Thanks for your feedback!")
        display_average_feedback(hostel['name'])

# Marketplace Section
def marketplace(user_id):
    st.write("## 🛒 Student Marketplace")

    action = st.radio("Select Action", ["Add Item", "Browse Items"])

    if action == "Add Item":
        st.write("### Add Item for Sale")
        item_name = st.text_input("Item Name")
        item_price = st.number_input("Price", min_value=0)
        if st.button("Add Item"):
            save_marketplace_item({"user_id": user_id, "item": item_name, "price": item_price})
            st.success("Item added to marketplace!")

    elif action == "Browse Items":
        st.write("### Browse Items")
        try:
            items = pd.read_csv("marketplace_items.csv")
        except FileNotFoundError:
            items = pd.DataFrame()

        search_query = st.text_input("Search items")
        min_price = st.number_input("Min Price", min_value=0, value=0)
        max_price = st.number_input("Max Price", min_value=0, value=100000)

        if not items.empty:
            filtered_items = items[(items['price'] >= min_price) & (items['price'] <= max_price)]
            for _, item in filtered_items.iterrows():
                if search_query.lower() in item['item'].lower() or not search_query:
                    st.write(f"### {item['item']}")
                    st.write(f"Price: ₹{item['price']}")
                    if st.button(f"Request {item['item']} ({item['user_id']})"):
                        save_request("marketplace_requests.csv", {"user_id": user_id, "item": item['item'], "price": item['price']})
                        st.success("Request saved!")
                    if item['user_id'] == user_id:
                        if st.button(f"Delete {item['item']}"):
                            delete_marketplace_item(user_id, item['item'])
                            st.success("Item deleted!")
        else:
            st.write("No items available.")

# Requests Dashboard
def requests_dashboard(user_id):
    st.write("## 📋 Your Requests")
    for filename, title in [("hostel_requests.csv", "Hostel Requests"), ("marketplace_requests.csv", "Marketplace Requests")]:
        try:
            df = pd.read_csv(filename)
            user_requests = df[df['user_id'] == user_id]
            st.write(f"### {title}")
            if not user_requests.empty:
                st.dataframe(user_requests)
            else:
                st.write("No requests yet.")
        except FileNotFoundError:
            st.write(f"### {title}")
            st.write("No requests yet.")
# Load or initialize data
def load_data(filename):
    try:
        return pd.read_csv(filename)
    except FileNotFoundError:
        if "attendance" in filename:
            return pd.DataFrame(columns=["user_id", "total_classes", "attended", "leaves_taken", "fines_paid", "chances_used"])
        elif "canteen" in filename:
            return pd.DataFrame(columns=["user_id", "meal_type", "option", "date"])
        elif "wait_times" in filename:
            return pd.DataFrame(columns=["user_id", "wait_time", "date"])

# Save data
def save_data(df, filename):
    df.to_csv(filename, index=False)

# Canteen menu
menu = {
    "breakfast": {
        "Option 1": "Iddiappam (50gm) + Kadala Curry (150 ml)",
        "Option 2": "Puttu (100gm) + Green Peas (150 ml)",
        "Option 3": "Chappati (3) + Egg Curry (150 ml)"
    },
    "lunch": {
        "Option 1": "Rice (50gm) + Sambhar Curry (150 ml)"
    }
}

# Ingredient requirements
ingredient_requirements = {
    "Iddiappam (50gm) + Kadala Curry (150 ml)": {"Iddiappam": 50, "Kadala Curry": 150},
    "Puttu (100gm) + Green Peas (150 ml)": {"Puttu": 100, "Green Peas": 150},
    "Chappati (3) + Egg Curry (150 ml)": {"Chappati": 3, "Egg Curry": 150},
    "Rice (50gm) + Sambhar Curry (150 ml)": {"Rice": 50, "Sambhar Curry": 150}
}

# Calculate ingredients needed
def calculate_ingredients(demand):
    ingredients = {}
    for _, row in demand.iterrows():
        option = row["option"]
        count = row["count"]
        for item, quantity in ingredient_requirements[option].items():
            ingredients[item] = ingredients.get(item, 0) + quantity * count
    return ingredients

# Attendance calculation
def calculate_attendance(user_id, tech_fest_days=0):
    df = load_data("attendance.csv")
    user = df[df['user_id'] == user_id].iloc[0]
    
    # Adjust attended days for tech fest participation
    user['attended'] += tech_fest_days
    
    current_percentage = (user['attended'] / user['total_classes']) * 100
    max_allowed_leaves = int(0.25 * user['total_classes'])  # 75% threshold
    
    leaves_remaining = max_allowed_leaves - user['leaves_taken']
    return current_percentage, leaves_remaining, user['chances_used']

# Generate LLM response using Replicate
def generate_llm_response(prompt):
    response = replicate.run(
        "meta/llama-2-7b-chat",  # Replace with your preferred model
        input={"prompt": prompt}
    )
    return "".join(response)

def attendance_management(user_id):
    st.write("## 📅 Attendance Management")

    df = load_data("attendance.csv")
    user = df[df['user_id'] == user_id].iloc[0]

    current_percent = (user['attended'] / user['total_classes']) * 100
    max_allowed_leaves = int(0.25 * user['total_classes'])
    leaves_remaining = max_allowed_leaves - user['leaves_taken']

    st.progress(current_percent / 100)
    st.write(f"Attendance: {current_percent:.1f}% | Leaves Left: {leaves_remaining} | Chances Used: {user['chances_used']}/2")

    if current_percent < 75:
        if user['chances_used'] < 2:
            st.error(f"ALERT: Your attendance is below 75%. You have {2 - user['chances_used']} chance(s) left to pay ₹5000 fine.")
            if st.button("Pay ₹5000 Now (Use 1 Chance)"):
                df.loc[df['user_id'] == user_id, 'chances_used'] += 1
                save_data(df, "attendance.csv")
                st.success("Fine paid! Your attendance has been adjusted.")
        else:
            st.error("BLOCKED: No chances remaining. Contact administration.")

    st.write("## 📩 Raise a Concern")
    concern_text = st.text_area("Describe your concern about your attendance or related parameters")
    if st.button("Submit Concern"):
        save_request("attendance_concerns.csv", {"user_id": user_id, "concern": concern_text, "date": pd.Timestamp.now().date()})
        st.success("Your concern has been submitted. Administration will review it.")

# Updated Requests Dashboard
def requests_dashboard(user_id):
    st.write("## 📋 Your Requests")
    for filename, title in [("hostel_requests.csv", "Hostel Requests"), ("marketplace_requests.csv", "Marketplace Requests")]:
        try:
            df = pd.read_csv(filename)
            user_requests = df[df['user_id'] == user_id]
            st.write(f"### {title}")
            if not user_requests.empty:
                st.dataframe(user_requests)
            else:
                st.write("No requests yet.")
        except FileNotFoundError:
            st.write(f"### {title}")
            st.write("No requests yet.")

    st.write("### Attendance Concerns")
    try:
        df = pd.read_csv("attendance_concerns.csv")
        user_concerns = df[df['user_id'] == user_id]
        if not user_concerns.empty:
            st.dataframe(user_concerns)
        else:
            st.write("No concerns submitted yet.")
    except FileNotFoundError:
        st.write("No concerns submitted yet.")

# Canteen Management Section for Students
def canteen_management(user_id):
    st.write("## 🍽️ Canteen Pre-Registration")
    
    # Meal selection
    meal_type = st.radio("Select Meal Type", ["Breakfast", "Lunch"])
    selected_option = st.selectbox(f"Choose {meal_type} Option", list(menu[meal_type.lower()].values()))
    
    # Submit pre-registration
    if st.button("Submit Meal Pre-Registration"):
        df = load_data("canteen.csv")
        new_entry = {"user_id": user_id, "meal_type": meal_type, "option": selected_option, "date": pd.Timestamp.now().date()}
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        save_data(df, "canteen.csv")
        st.success("Meal pre-registered! Thank you for reducing waste.")
    
    # Wait time crowdsourcing
    st.write("## ⏳ Canteen Wait Time")
    wait_time = st.slider("Current Wait Time (mins)", 0, 30, 5)
    if st.button("Submit Wait Time"):
        df = load_data("wait_times.csv")
        new_entry = {"user_id": user_id, "wait_time": wait_time, "date": pd.Timestamp.now().date()}
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        save_data(df, "wait_times.csv")
        st.success("Thanks for helping others!")
    
    # Display average wait time
    avg_wait = load_data("wait_times.csv")["wait_time"].mean()
    if not pd.isna(avg_wait):
        st.write(f"Average Wait Time: {avg_wait:.1f} mins")
    
    # # LLM Integration (Replicate)
    # st.write("## 🤖 Meal Suggestion")
    # prompt = f"Suggest a meal plan for tomorrow based on current demand: {demand.to_dict()}"
    # if st.button("Generate Suggestion"):
    #     suggestion = generate_llm_response(prompt)
    #     st.write(suggestion)

# Canteen Management Section for Canteen Owner
def canteen_owner_management():
    st.write("## 🍽️ Canteen Owner Dashboard")
    
    # Demand prediction
    st.write("## 📊 Predicted Demand")
    demand = load_data("canteen.csv").groupby(["meal_type", "option"]).size().reset_index(name="count")
    if not demand.empty:
        st.bar_chart(demand.set_index("option")["count"])
        
        # Ingredients needed
        st.write("## 🛒 Ingredients Needed")
        ingredients_needed = calculate_ingredients(demand)
        st.write(ingredients_needed)
    else:
        st.write("No pre-registrations yet.")

def canteen_owner_login():
    st.title("Canteen Owner Login")
    owner_id = st.text_input("Enter your owner ID")
    password = st.text_input("Enter your password", type="password")
    if owner_id == "CUSATCANTEEN1" and password == "canteenpass":  # Replace "canteenpass" with your desired password
        st.success("Logged in as Canteen Owner")
        canteen_owner_management()
    elif owner_id or password:
        st.error("Invalid Owner ID or Password")

# Main App
def main():
    st.title("CampuSync 🏫")

    user_type = st.sidebar.radio("Login as:", ["Student", "Canteen Owner"])  # Removed Admin

    if user_type == "Student":
        user_id = student_login()
        if user_id:
            section = st.sidebar.radio("Select Section", ["Attendance Management", "Canteen Management", "Hostel Listings", "Marketplace", "Your Requests"])

            if section == "Attendance Management":
                attendance_management(user_id)
            elif section == "Canteen Management":
                canteen_management(user_id)
            elif section == "Hostel Listings":
                hostel_listing(user_id)
            elif section == "Marketplace":
                marketplace(user_id)
            elif section == "Your Requests":
                requests_dashboard(user_id)


    elif user_type == "Canteen Owner":
        canteen_owner_login()

# Run the app
if __name__ == "__main__":
    main()