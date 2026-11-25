
import streamlit as st
import pandas as pd
import plotly.express as px

from algorithms import (
    search_products, near_duplicate_candidates, approximate_unique_count,
    percentile, benchmark_scan, shard_replica_experiment
)
from database import (
    init_db, get_products, add_product, update_stock,
    get_history, add_event, get_events
)

# 1. CONFIGURATION
st.set_page_config(page_title="Marketly | Smart Marketplace", page_icon="🛍️", layout="wide")
init_db()

# 2. STYLING
st.markdown("""
<style>
:root {
    --cream:#F6F2EA; --surface:#FFFEFB; --ink:#302D29;
    --muted:#71695F; --accent:#A47769; --dark:#8E6255;
    --border:#DDD5C9;
}
.stApp {background:var(--cream);color:var(--ink)}
[data-testid="stHeader"] {background:rgba(246,242,234,.96)}
.block-container {padding-top:1.6rem;padding-bottom:3rem;max-width:1440px}
/* Fix common header text clipping */
div[data-testid="stMarkdownContainer"] {
    overflow: visible !important;
}

div[data-testid="stMarkdownContainer"] h5 {
    display: block !important;
    height: auto !important;
    min-height: 30px !important;
    line-height: 1.8 !important;
    overflow: visible !important;
    margin: 0 0 24px 0 !important;
    padding: 8px 0 !important;
    position: relative !important;
    transform: none !important;
    text-shadow: none !important;
}
h1,h2,h3,h4,p,label {color:var(--ink)!important}
[data-testid="stWidgetLabel"] p {color:var(--ink)!important;font-weight:600}
[data-testid="stCaptionContainer"],.stCaption {color:var(--muted)!important}
section[data-testid="stSidebar"] {background:#EFE8DD;border-right:1px solid var(--border)}
section[data-testid="stSidebar"] .block-container {padding-top:2rem}
.market-brand {font:700 2.5rem Georgia;color:var(--accent);letter-spacing:-.04em}
.market-kicker {color:var(--muted)!important;font-size:.72rem;letter-spacing:.14em;font-weight:700}
.market-subtitle {color:var(--muted)!important;margin-top:-.5rem}
section[data-testid="stSidebar"] [role="radiogroup"] {gap:7px}
section[data-testid="stSidebar"] [role="radiogroup"]>label {
    background:transparent;border:1px solid transparent;border-radius:9px;
    padding:9px 12px;transition:background .2s
}
section[data-testid="stSidebar"] [role="radiogroup"]>label:hover {
    background:#E5DACE;border-color:var(--border)
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label>div:first-child {display:none}
section[data-testid="stSidebar"] [data-testid="stRadio"] label p {
    font-size:.95rem;font-weight:550;color:#35332F!important
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background:var(--accent);border:1px solid var(--accent);border-radius:9px
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {
    color:white!important;font-weight:700
}
[data-testid="stMetric"] {
    background:var(--surface);padding:17px 18px;border:1px solid var(--border);
    border-radius:15px;box-shadow:0 2px 10px rgba(65,48,34,.035)
}
[data-testid="stMetricLabel"],[data-testid="stMetricLabel"] p {
    color:var(--muted)!important;font-weight:600!important
}
[data-testid="stMetricValue"],[data-testid="stMetricValue"] div {
    color:var(--ink)!important;font-weight:750!important
}
.stButton>button,.stFormSubmitButton>button {
    width:100%;min-height:42px;border-radius:10px;border:1px solid var(--accent);
    background:var(--accent);color:white!important;font-weight:600
}
.stButton>button:hover,.stFormSubmitButton>button:hover {
    background:var(--dark);border-color:var(--dark);color:white!important
}
.stTextInput input,.stNumberInput input,.stTextArea textarea,
[data-baseweb="select"]>div {
    background:var(--surface)!important;color:var(--ink)!important;
    border-color:var(--border)!important
}
[data-baseweb="select"] * {color:var(--ink)!important}
[data-testid="stDataFrame"],[data-testid="stTable"] {
    background:var(--surface);border-radius:12px
}
[data-testid="stExpander"] {
    background:var(--surface);border:1px solid var(--border);border-radius:12px
}
hr {border-color:var(--border)}
[data-testid="stImage"] img {
    width:100%;height:220px!important;object-fit:cover!important;border-radius:12px
}
.product-title {color:var(--ink)!important;font-weight:700;font-size:1rem;
    line-height:1.45;min-height:48px;margin:10px 0 6px}
.product-meta,.product-stock {color:var(--muted)!important;font-size:.85rem}
.product-meta {min-height:25px}
.product-price {font-weight:750;color:var(--accent)!important;font-size:1.1rem;margin-top:10px}
.product-stock {margin:7px 0 12px}
</style>
""", unsafe_allow_html=True)

# 3. PRODUCT IMAGES
CATEGORY_IMAGES = {
    "Electronics/Computers":"https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=700&auto=format&fit=crop&q=80",
    "Electronics/Audio":"https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=700&auto=format&fit=crop&q=80",
    "Electronics/Mobile":"https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=700&auto=format&fit=crop&q=80",
    "Electronics/Accessories":"https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=700&auto=format&fit=crop&q=80",
    "Fashion/Footwear":"https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=700&auto=format&fit=crop&q=80",
    "Fashion/Bags":"https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=700&auto=format&fit=crop&q=80",
    "Home/Lighting":"https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=700&auto=format&fit=crop&q=80"
}
DEFAULT_IMAGE = "https://images.unsplash.com/photo-1491553895911-0055eca6402d?w=700&auto=format&fit=crop&q=80"

# 4. DATABASE
products = get_products()
events = get_events()
df, edf = pd.DataFrame(products), pd.DataFrame(events)

# 5. NAVIGATION
pages = ["Home","Shop","Search","Inventory","Duplicates","Analytics","Algorithm Lab","History"]
descriptions = {
    "Home":"A clear snapshot of your marketplace performance.",
    "Shop":"Browse the catalogue with product cards and category filters.",
    "Search":"Explore keyword, vector and hybrid product discovery.",
    "Inventory":"Add catalogue entries and manage available stock.",
    "Duplicates":"Review similar listings before deciding what to do.",
    "Analytics":"Explore event activity and marketplace trends.",
    "Algorithm Lab":"Run local experiments on search and data algorithms.",
    "History":"Track previous product versions and catalogue changes."
}
icons = dict(zip(pages,["⌂","▦","⌕","▤","⧉","▥","⚙","◷"]))

with st.sidebar:
    st.markdown('<div class="market-brand">Marketly</div>',unsafe_allow_html=True)
    st.markdown('<div class="market-kicker">SMART MARKETPLACE ANALYTICS</div>',unsafe_allow_html=True)
    st.divider()
    page = st.radio("WORKSPACE",pages,format_func=lambda x:f"{icons[x]}   {x}")
    st.divider()
    st.caption("Academic prototype · Local SQLite database")
    st.caption(f"{len(df):,} products in catalogue")

# 6. COMMON HEADER
st.markdown(
    '<h5 style="color:#8E6255 !important;'
    'font-size:14px !important;'
    'font-weight:900 !important;'
    'letter-spacing:4px !important;'
    'margin:0 0 24px 0 !important;'
    'padding:8px 0 !important;'
    'line-height:1.8 !important;'
    'display:block !important;'
    'height:auto !important;'
    'overflow:visible !important;">'
    'SMART MARKETPLACE · CONTROL CENTER</h5>',
    unsafe_allow_html=True
)

st.markdown(f"# {page}")
st.markdown(
    f'<p class="market-subtitle">{descriptions[page]}</p>',
    unsafe_allow_html=True
)
st.divider()

# 7. HOME
if page == "Home":
    if df.empty:
        st.info("Your catalogue is empty. Add products in Inventory.")
    else:
        cols = st.columns(4)
        metrics = [
            ("Total products",len(df)),
            ("In-stock products",int((df.stock>0).sum())),
            ("Recorded events",len(edf)),
            ("Categories",df.category.nunique())
        ]
        for col,(label,value) in zip(cols,metrics):
            col.metric(label,f"{value:,}")

        left,right = st.columns(2)
        with left:
            cat = df.groupby("category",as_index=False).size().sort_values("size",ascending=False)
            st.plotly_chart(px.bar(cat,x="category",y="size",title="Catalogue by category",
                labels={"size":"Products","category":"Category"},color_discrete_sequence=["#A47769"]),
                use_container_width=True)
        with right:
            if not edf.empty:
                ev = edf.groupby("event_type",as_index=False).size()
                st.plotly_chart(px.pie(ev,names="event_type",values="size",
                    title="Event distribution",color_discrete_sequence=["#A47769","#C8A994","#D9CDBD"]),
                    use_container_width=True)
            else:
                st.info("No events have been recorded yet.")

        st.subheader("Recently updated products")
        st.dataframe(df.sort_values("updated_at",ascending=False).head(6)[
            ["id","title","category","price","stock","updated_at"]],
            use_container_width=True,hide_index=True)

# 8. SHOP
elif page == "Shop":
    if df.empty:
        st.info("No products available in the catalogue.")
    else:
        f1,f2 = st.columns([2,1])
        category = f1.selectbox("Browse category",["All categories"]+sorted(df.category.dropna().unique().tolist()))
        order = f2.selectbox("Sort products",["Recommended (newest ID)","Price: low to high","Price: high to low"])
        shown = df.copy()
        if category != "All categories":
            shown = shown[shown.category==category]
        shown = shown.sort_values("price" if order!="Recommended (newest ID)" else "id",
                                  ascending=order!="Price: high to low" if order!="Recommended (newest ID)" else False)
        st.caption(f"Showing {len(shown):,} products · Product photography is representative by category.")
        per_page = 12
        total_pages = max(1,(len(shown)+per_page-1)//per_page)
        current = st.number_input("Page",1,total_pages,1,1,key="shop_page")
        rows = shown.iloc[(int(current)-1)*per_page:int(current)*per_page].to_dict("records")

        for offset in range(0,len(rows),3):
            for col,item in zip(st.columns(3,gap="large"),rows[offset:offset+3]):
                with col:
                    with st.container(border=True):
                        st.image(CATEGORY_IMAGES.get(item["category"],DEFAULT_IMAGE),use_container_width=True)
                        st.markdown(f'<div class="product-title">{item["title"]}</div>',unsafe_allow_html=True)
                        st.markdown(f'<div class="product-meta">{item["category"]}</div>',unsafe_allow_html=True)
                        st.markdown(f'<div class="product-price">₹{item["price"]:,.2f}</div>',unsafe_allow_html=True)
                        stock = f'{item["stock"]} available' if item["stock"]>0 else "Out of stock"
                        st.markdown(f'<div class="product-stock">{stock}</div>',unsafe_allow_html=True)
                        if st.button("Record product view",key=f'shop_view_{item["id"]}',disabled=item["stock"]<=0):
                            add_event(int(item["id"]),"view","demo_visitor")
                            st.toast("Product view recorded")

# 9. SEARCH
elif page == "Search":
    query = st.text_input("What are you looking for?","lightweight laptop for programming")
    c1,c2,c3 = st.columns(3)
    price = c1.number_input("Maximum price (INR)",min_value=0,value=60000,step=1000)
    roots = ["All"]+sorted({p["category"].split("/")[0] for p in products})
    category = c2.selectbox("Category",roots)
    mode = c3.selectbox("Search method",["Hybrid","Keyword","Vector"])
    in_stock = st.checkbox("Only show in-stock products",True)
    limit = st.slider("Maximum results",5,100,25)

    if st.button("Search products",type="primary"):
        matches = search_products(products,query,price,category,in_stock,mode,limit)
        if query.strip():
            add_event(None,"search","demo_visitor")
        st.session_state["last_search"] = matches
        st.session_state["last_query"] = query

    matches = st.session_state.get("last_search",[])
    if matches:
        st.success(f"Found {len(matches)} ranked results")
        st.dataframe(pd.DataFrame(matches)[
            ["id","title","category","price","stock","keyword_score","vector_score","rank_score"]],
            use_container_width=True,hide_index=True)
        st.caption("Hybrid score = 55% keyword + 45% deterministic feature-hash vector similarity, with a small reranking boost.")
        selected = st.selectbox("Select a product to record a view",[x["id"] for x in matches])
        if st.button("Record product view"):
            add_event(int(selected),"view","demo_visitor")
            st.toast("View event recorded")
    else:
        st.info("Enter a query and select Search products to see ranked results.")

# 10. INVENTORY
elif page == "Inventory":
    with st.expander("＋ Add a new product",expanded=True):
        with st.form("add_product_form"):
            title = st.text_input("Product title")
            desc = st.text_area("Description")
            categories = sorted(df.category.dropna().unique().tolist()) if not df.empty else [
                "Electronics/Computers","Electronics/Mobile","Electronics/Audio",
                "Electronics/Accessories","Fashion/Footwear","Fashion/Bags","Home/Lighting"
            ]
            category = st.selectbox("Category",categories)
            price = st.number_input("Price (INR)",min_value=1.0,value=10000.0)
            stock = st.number_input("Initial stock",min_value=0,value=10,step=1)
            submitted = st.form_submit_button("Add product")
            if submitted:
                if title.strip() and desc.strip():
                    add_product(title.strip(),desc.strip(),category,price,stock)
                    st.success("Product added to catalogue.")
                    st.rerun()
                else:
                    st.error("Title and description are required.")

    if not df.empty:
        st.subheader("Update stock")
        ids = df.id.tolist()
        pid = st.selectbox("Choose product",ids,
            format_func=lambda x:f"#{x} · {df.loc[df.id==x,'title'].iloc[0]}")
        current = int(df.loc[df.id==pid,"stock"].iloc[0])
        new_stock = st.number_input("New stock quantity",min_value=0,value=current,step=1)
        if st.button("Save inventory update",type="primary"):
            update_stock(pid,new_stock)
            st.success("Stock updated. Previous version saved to history.")
            st.rerun()
        st.subheader("Current catalogue")
        st.dataframe(df[["id","title","category","price","stock","version"]],
                     use_container_width=True,hide_index=True)

# 11. DUPLICATES
elif page == "Duplicates":
    st.write("Candidate generation uses token-set Jaccard similarity. Candidates are not auto-merged; exact text is checked separately.")
    threshold = st.slider("Similarity threshold",0.4,1.0,0.82,0.02)
    if st.button("Find similar products",type="primary"):
        st.session_state["dupes"] = near_duplicate_candidates(products,threshold)
    dupes = st.session_state.get("dupes",[])
    if dupes:
        st.success(f"Found {len(dupes)} candidate pairs")
        st.dataframe(pd.DataFrame(dupes),use_container_width=True,hide_index=True)
    elif "dupes" in st.session_state:
        st.info("No candidates found at this threshold. Try lowering the threshold.")
    else:
        st.info("Choose a similarity threshold and run duplicate detection.")

# 12. ANALYTICS
elif page == "Analytics":
    if edf.empty:
        st.info("No events recorded yet. Search or browse products to create demo events.")
    else:
        edf["time"] = pd.to_datetime(edf["occurred_at"],utc=True,errors="coerce")
        edf = edf.dropna(subset=["time"])
        window = st.selectbox("Time window",["Last 1 hour","Last 24 hours","Last 7 days","All events"])
        now = pd.Timestamp.now(tz="UTC")
        cutoffs = {
            "Last 1 hour":now-pd.Timedelta(hours=1),
            "Last 24 hours":now-pd.Timedelta(days=1),
            "Last 7 days":now-pd.Timedelta(days=7),
            "All events":pd.Timestamp.min.tz_localize("UTC")
        }
        recent = edf[edf.time>=cutoffs[window]].copy()
        a,b,c = st.columns(3)
        a.metric("Events in window",f"{len(recent):,}")
        b.metric("Exact unique visitors",f"{recent.anonymous_user_id.nunique():,}")
        c.metric("Approx. unique visitors",f"{approximate_unique_count(recent.anonymous_user_id.tolist()):,}")

        if not recent.empty:
            recent["bucket"] = recent.time.dt.floor("h")
            timeline = recent.groupby(["bucket","event_type"],as_index=False).size()
            st.plotly_chart(px.line(timeline,x="bucket",y="size",color="event_type",
                markers=True,title="Events over time"),use_container_width=True)
            counts = recent.groupby("event_type",as_index=False).size()
            st.plotly_chart(px.bar(counts,x="event_type",y="size",
                title="Events by type",color_discrete_sequence=["#A47769"]),
                use_container_width=True)
            st.dataframe(recent.groupby("event_type").size().rename("count").reset_index(),
                         use_container_width=True,hide_index=True)
        st.caption("This prototype processes seeded/recent events from SQLite; it does not connect to real users.")

# 13. ALGORITHM LAB
elif page == "Algorithm Lab":
    st.markdown("**1. Baseline exact scan and performance measurement**")
    sizes = st.multiselect("Catalogue sizes",[20,100,500,1000],default=[20,100,500,1000])
    rows = [{"catalogue_size":n,"matches":count,"elapsed_ms":round(ms,4),"records_examined":ops}
            for n in sizes for count,ms,ops in [benchmark_scan(products[:n])]]
    if rows:
        result = pd.DataFrame(rows)
        st.dataframe(result,use_container_width=True,hide_index=True)
        st.plotly_chart(px.line(result,x="catalogue_size",y="elapsed_ms",markers=True,
            title="Linear scan time (single local run)"),use_container_width=True)

    st.divider()
    st.markdown("**2. Approximate count and response-time percentiles**")
    exact = df.category.nunique() if not df.empty else 0
    approx = approximate_unique_count(df.category.tolist()) if not df.empty else 0
    st.write(f"Distinct categories — exact: **{exact}**, approximate estimator: **{approx}** (small-cardinality estimates may vary).")
    latencies = [0.4,0.7,0.8,1.0,1.2,1.5,2.1,3.0,5.5,8.0]
    p1,p2 = st.columns(2)
    p1.metric("p50 demo latency",f"{percentile(latencies,50):.2f} ms")
    p2.metric("p95 demo latency",f"{percentile(latencies,95):.2f} ms")
    st.caption("Latency values above are illustrative demo measurements, not live request timings.")

    st.divider()
    st.markdown("**3. Local shard / replica illustration**")
    shards = st.slider("Number of local shards",2,8,4)
    st.dataframe(pd.DataFrame(shard_replica_experiment(products,shards)),
                 use_container_width=True,hide_index=True)
    st.caption("Shard assignment uses product_id modulo shard count. Replica rows illustrate local copies; this is a simulation, not a networked distributed database.")

# 14. HISTORY
elif page == "History":
    history = get_history()
    if history:
        hist_df = pd.DataFrame(history)
        st.metric("Saved product versions",f"{len(hist_df):,}")
        st.dataframe(hist_df,use_container_width=True,hide_index=True)
    else:
        st.info("No edits yet. Update stock in Inventory to create a historical version.")

    st.subheader("Cache demonstration")
    st.write("Search results are kept in the Streamlit session for responsiveness. Inventory edits increment the product version; rerun a search after edits to use the current catalogue data.")
