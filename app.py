import streamlit as st # type: ignore
import streamlit.components.v1 as components # type: ignore

# --- Data Configuration ---
ranks = [
    "Grandmaster V", "Grandmaster IV", "Grandmaster III", "Grandmaster II", "Grandmaster I",
    "Epic V", "Epic IV", "Epic III", "Epic II", "Epic I",
    "Legend V", "Legend IV", "Legend III", "Legend II", "Legend I",
    "Mythic"
]

stars_in_rank_default = {"Grandmaster": 5, "Epic": 5, "Legend": 5}
prices_non_mythic = {"Grandmaster": 1.5, "Epic": 2, "Legend": 2.5}

mythic_pricing = [
    (0, 24, 4.5),   # Mythic
    (25, 49, 5.0),  # Mythical Honor
    (50, 99, 6.0),  # Mythical Glory
    (100, 9999, 6.5)# Mythic Immortal
]

def get_tier(rank_name):
    for t in ["Grandmaster", "Epic", "Legend"]:
        if t in rank_name: return t
    return "Mythic"

# --- Streamlit UI Setup ---
st.set_page_config(page_title="MLBB Joki Calculator", page_icon="🎮")
st.title("🎮 MLBB Joki Calculator")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Starting Point")
    start_r = st.selectbox("Starting Rank", options=ranks + ["Mythical Honor", "Mythical Glory", "Mythic Immortal"], index=9)
    current_s = st.number_input("Current Stars in Rank", min_value=0, value=1)

with col2:
    st.subheader("Target Point")
    dropdown_values = ranks + ["Mythical Honor", "Mythical Glory", "Mythic Immortal"]
    end_r = st.selectbox("Target Rank", options=dropdown_values, index=len(dropdown_values)-4)
    target_s_in_rank = st.number_input("Target Total Stars (e.g., 1)", min_value=0, value=1)

if st.button("Calculate Total RM", type="primary", use_container_width=True):
    report_text = ""
    total_stars = 0
    total_price = 0.0

    # 1. Non-Mythic Logic
    is_start_mythic = any(m in start_r for m in ["Mythic", "Honor", "Glory", "Immortal"])
    is_end_mythic = any(m in end_r for m in ["Mythic", "Honor", "Glory", "Immortal"])

    if not is_start_mythic:
        target_for_loop = "Mythic" if is_end_mythic else end_r
        start_idx = ranks.index(start_r)
        end_idx = ranks.index(target_for_loop)

        for i in range(start_idx, end_idx):
            rank = ranks[i]
            tier = get_tier(rank)
            price = prices_non_mythic[tier]
            
            # UPDATED RULE: Only Epic I requires 6 stars to promote to Legend V.
            # Legend I to Mythic and all other tiers use 5 stars.
            if rank == "Epic I":
                max_stars = 6
            else:
                max_stars = 5
            
            if i == start_idx:
                needed = max_stars - current_s
            else:
                needed = max_stars
            
            if not is_end_mythic and rank == end_r:
                needed = target_s_in_rank - (current_s if i == start_idx else 0)

            if needed > 0:
                cost = max(0, float(needed) * price)
                report_text += f"{rank} : {needed} stars x RM{price} = RM{cost:.2f}\\n"
                total_stars += max(0, needed)
                total_price += max(0, cost)
        
        current_s_temp = 0 if is_end_mythic else current_s
    else:
        current_s_temp = current_s

    # 2. Mythic Logic
    if is_end_mythic:
        absolute_target = target_s_in_rank
        absolute_start = 0
        if is_start_mythic:
            start_map = {"Mythic": 0, "Mythical Honor": 25, "Mythical Glory": 50, "Mythic Immortal": 100}
            absolute_start = start_map.get(start_r, 0) + current_s_temp
        
        temp_s = absolute_start
        mythic_segments = {}

        while temp_s < absolute_target:
            for low, high, price in mythic_pricing:
                if low <= temp_s <= high:
                    tier_name = "Mythic"
                    if low == 25: tier_name = "Mythical Honor"
                    elif low == 50: tier_name = "Mythical Glory"
                    elif low >= 100: tier_name = "Mythic Immortal"
                    
                    if tier_name not in mythic_segments:
                        mythic_segments[tier_name] = {"count": 0, "price": price}
                    mythic_segments[tier_name]["count"] += 1
                    total_price += price
                    total_stars += 1
                    temp_s += 1
                    break
        
        for name, data in mythic_segments.items():
            report_text += f"{name} : {data['count']} stars x RM{data['price']} = RM{data['count']*data['price']:.2f}\\n"

    # 3. Final Output
    if not report_text or total_stars <= 0:
        st.warning("No stars needed! Check your inputs.")
    else:
        # Prepare strings
        final_summary = f"{report_text}--------------------------------\\nTotal Price : RM{total_price:.2f}"
        html_display = final_summary.replace("\\n", "<br>")
        js_copy_text = final_summary

        st.subheader("Final Report")
        
        # We wrap the component in a container to help Streamlit manage mobile layering
        report_container = st.container()
        
        with report_container:
            copy_button_html = f"""
            <div id="copy-container" style="
                background-color: #f8f9fa; 
                padding: 15px; 
                border-radius: 12px; 
                border: 1px solid #e0e0e0;
                position: relative;
                font-family: sans-serif;
                white-space: pre-wrap;
                color: #262730;
            ">
                <div id="report-content" style="font-size: 14px; line-height: 1.6; padding-right: 45px;">{html_display}</div>
                <button id="copy-btn" onclick="copyToClipboard()" style="
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    background: #2ecc71;
                    border: none;
                    border-radius: 8px;
                    width: 40px;
                    height: 40px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                ">
                    <span id="icon" style="font-size: 1.2rem;">📋</span>
                </button>
            </div>

            <script>
            function copyToClipboard() {{
                const textToCopy = `{js_copy_text}`.replace(/\\\\n/g, '\\n');
                const textArea = document.createElement("textarea");
                textArea.value = textToCopy;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand("copy");
                document.body.removeChild(textArea);

                const btn = document.getElementById("copy-btn");
                const icon = document.getElementById("icon");
                icon.innerText = "✅";
                btn.style.background = "#3498db";

                setTimeout(() => {{
                    icon.innerText = "📋";
                    btn.style.background = "#2ecc71";
                }}, 2000);
            }}
            </script>
            """
            
            # CRITICAL: Reduced height to 300 so it doesn't overlap the top dropdowns
            # and set scrolling to 'no' to keep it clean on mobile
            components.html(copy_button_html, height=300, scrolling=True)
            
            st.success(f"### Total Price: RM{total_price:.2f}")
