import streamlit as st # type: ignore
import streamlit.components.v1 as components # type: ignore

# --- Data Configuration ---
ranks = [
    "Grandmaster V", "Grandmaster IV", "Grandmaster III", "Grandmaster II", "Grandmaster I",
    "Epic V", "Epic IV", "Epic III", "Epic II", "Epic I",
    "Legend V", "Legend IV", "Legend III", "Legend II", "Legend I",
    "Mythic"
]

prices_non_mythic = {"Grandmaster": 1.5, "Epic": 2.0, "Legend": 2.5}

mythic_pricing = [
    (0, 24, 5.0, "Mythic"),   
    (25, 49, 5.5, "Mythical Honor"),  
    (50, 99, 6.5, "Mythical Glory"),  
    (100, 9999, 7.0, "Mythic Immortal")
]

def get_tier(rank_name):
    for t in ["Grandmaster", "Epic", "Legend"]:
        if t in rank_name: return t
    return "Mythic"

# --- Streamlit UI Setup ---
st.set_page_config(page_title="MLBB Joki Calculator", page_icon="🎮")
st.title("🎮 MLBB Joki Calculator")

st.subheader("Starting Point")
start_r = st.selectbox("Current Rank", options=ranks + ["Mythical Honor", "Mythical Glory", "Mythic Immortal"], index=9)
current_s = st.number_input("Current Stars", min_value=0, value=1)

st.markdown("---")

st.subheader("Target Point")
dropdown_values = ranks + ["Mythical Honor", "Mythical Glory", "Mythic Immortal"]
end_r = st.selectbox("Target Rank", options=dropdown_values, index=15) 
target_s_in_rank = st.number_input("Target Total Stars", min_value=0, value=1)

st.write("") 

if st.button("Calculate Total RM", type="primary", use_container_width=True):
    grouped_report = {}
    total_price = 0.0
    actual_total_stars = 0

    is_start_mythic = any(m in start_r for m in ["Mythic", "Honor", "Glory", "Immortal"])
    is_end_mythic = any(m in end_r for m in ["Mythic", "Honor", "Glory", "Immortal"])

    # 1. Non-Mythic Logic
    if not is_start_mythic:
        start_idx = ranks.index(start_r)
        end_idx = ranks.index("Mythic") if is_end_mythic else ranks.index(end_r) + 1

        for i in range(start_idx, end_idx):
            rank = ranks[i]
            if rank == "Mythic": continue 
            
            tier = get_tier(rank)
            price = prices_non_mythic[tier]
            max_stars = 6 if rank == "Epic I" else 5
            
            # --- Logic fix for same rank or cross-rank calculation ---
            if start_r == end_r:
                needed = target_s_in_rank - current_s
            elif i == start_idx:
                needed = max_stars - current_s
            elif not is_end_mythic and rank == end_r:
                needed = target_s_in_rank
            else:
                needed = max_stars

            if needed > 0:
                if tier not in grouped_report:
                    grouped_report[tier] = {"stars": 0, "price": price}
                grouped_report[tier]["stars"] += needed
                total_price += float(needed) * price
                actual_total_stars += needed
        
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
        while temp_s < absolute_target:
            for low, high, price, tier_name in mythic_pricing:
                if low <= temp_s <= high:
                    if tier_name not in grouped_report:
                        grouped_report[tier_name] = {"stars": 0, "price": price}
                    grouped_report[tier_name]["stars"] += 1
                    total_price += price
                    actual_total_stars += 1
                    temp_s += 1
                    break

    # 3. Final Output
    if not grouped_report or actual_total_stars <= 0:
        st.warning("No stars needed! Check your inputs.")
    else:
        header = f"{start_r} {current_s}⭐️ to {end_r} {target_s_in_rank}⭐️\\n\\n"
        body = ""
        for tier, data in grouped_report.items():
            cost = data["stars"] * data["price"]
            body += f"{tier} : {data['stars']}⭐️ x RM{data['price']:.2f} = RM{cost:.2f}\\n"
        
        final_summary = f"{header}{body}\\nTotal : RM{total_price:.2f}"
        html_display = final_summary.replace("\\n", "<br>")
        js_copy_text = final_summary

        st.subheader("Final Report")
        
        copy_button_html = f"""
        <div id="wrapper" style="font-family: sans-serif; color: #262730;">
            <div id="copy-container" style="
                background-color: #f8f9fa; 
                padding: 15px; 
                border-radius: 12px; 
                border: 1px solid #e0e0e0;
                position: relative;
                min-height: 100px;
                max-height: 250px;
                overflow-y: auto;
            ">
                <button id="copy-btn" onclick="copyToClipboard()" style="
                    position: sticky;
                    float: right;
                    top: 0;
                    right: 0;
                    background: #2ecc71;
                    border: none;
                    border-radius: 8px;
                    width: 36px;
                    height: 36px;
                    cursor: pointer;
                    z-index: 10;
                    margin-left: 10px;
                ">
                    <span id="icon" style="font-size: 1.1rem;">📋</span>
                </button>
                <div id="report-content" style="font-size: 14px; line-height: 1.6; white-space: pre-wrap;">{html_display}</div>
            </div>
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
        components.html(copy_button_html, height=320)
        st.success(f"### Total Price: RM{total_price:.2f}")
