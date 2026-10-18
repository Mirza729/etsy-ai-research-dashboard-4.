
import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(
    page_title="Etsy AI Research Dashboard",
    page_icon="🌿",
    layout="wide"
)

st.title("🔎 Etsy AI Research Dashboard")
st.caption("Product Hunting | Keyword Research | Competition | SEO")

# Demo data — real Etsy data abhi connected nahi hai
DATA = [
    {"Product": "Personalized Necklace", "Niche": "Jewellery", "Price": 25.99, "Competition": "High"},
    {"Product": "Custom Birthstone Ring", "Niche": "Jewellery", "Price": 32.00, "Competition": "Medium"},
    {"Product": "Artificial Flower Arrangement", "Niche": "Garden", "Price": 45.00, "Competition": "Medium"},
    {"Product": "Crochet Christmas Sweater", "Niche": "Crochet", "Price": 48.00, "Competition": "High"},
    {"Product": "Personalized Garden Sign", "Niche": "Garden", "Price": 42.00, "Competition": "Low"},
    {"Product": "Crochet Baby Booties", "Niche": "Crochet", "Price": 24.00, "Competition": "Medium"},
    {"Product": "Minimalist Gold Necklace", "Niche": "Jewellery", "Price": 39.00, "Competition": "High"},
    {"Product": "Artificial Wedding Bouquet", "Niche": "Garden", "Price": 55.00, "Competition": "Medium"},
]

df = pd.DataFrame(DATA)

# Sidebar
st.sidebar.header("⚙️ Research Filters")
niche = st.sidebar.selectbox(
    "Choose niche",
    ["All", "Jewellery", "Garden", "Crochet"]
)
min_price = st.sidebar.number_input(
    "Minimum price ($)", min_value=0.0, value=0.0
)
max_price = st.sidebar.number_input(
    "Maximum price ($)", min_value=0.0, value=1000.0
)
competition = st.sidebar.selectbox(
    "Competition", ["All", "Low", "Medium", "High"]
)

filtered = df.copy()

if niche != "All":
    filtered = filtered[filtered["Niche"] == niche]

filtered = filtered[
    (filtered["Price"] >= min_price)
    & (filtered["Price"] <= max_price)
]

if competition != "All":
    filtered = filtered[filtered["Competition"] == competition]

# Summary
c1, c2, c3 = st.columns(3)
c1.metric("Products Found", len(filtered))
c2.metric(
    "Average Price",
    f"${filtered['Price'].mean():.2f}" if len(filtered) else "$0.00"
)
c3.metric(
    "Low Competition",
    int((filtered["Competition"] == "Low").sum())
)

st.divider()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🛍️ Product Hunter",
    "🔑 Keyword Research",
    "📊 Competition",
    "✍️ SEO Generator"
])

with tab1:
    st.subheader("Product Ideas")
    st.info("Demo dataset — products aur metrics live Etsy research nahi hain.")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Products CSV",
        data=csv,
        file_name="etsy_product_research.csv",
        mime="text/csv"
    )

with tab2:
    st.subheader("Keyword Idea Generator")
    product = st.text_input(
        "Product or niche",
        placeholder="e.g. artificial wedding bouquet"
    )
    if st.button("Generate Keyword Ideas"):
        if product.strip():
            base = product.strip().lower()
            keywords = [
                base,
                f"personalized {base}",
                f"handmade {base}",
                f"{base} gift",
                f"{base} for wedding",
                f"custom {base}",
                f"{base} home decor",
                f"unique {base}",
                f"{base} gift idea",
                f"premium {base}",
                f"{base} for her",
                f"modern {base}",
                f"custom made {base}",
            ]
            st.write("Suggested keyword ideas:")
            for i, keyword in enumerate(keywords, start=1):
                st.write(f"{i}. {keyword}")
            st.caption(
                "These are AI-free keyword suggestions, not verified "
                "search-volume or ranking data."
            )
        else:
            st.warning("Pehle product ya niche enter karo.")

with tab3:
    st.subheader("Competition Overview")
    st.caption("Sample records only — actual market competition nahi.")
    if len(filtered):
        counts = (
            filtered["Competition"]
            .value_counts()
            .reindex(["Low", "Medium", "High"], fill_value=0)
        )
        st.bar_chart(counts)
        st.dataframe(filtered, use_container_width=True, hide_index=True)
    else:
        st.warning("Filters ke mutabiq koi product nahi mila.")

with tab4:
    st.subheader("Etsy SEO Draft Generator")
    seo_product = st.text_input(
        "Product name",
        placeholder="e.g. personalized birthstone necklace",
        key="seo_product"
    )
    audience = st.text_input(
        "Target audience or occasion",
        placeholder="e.g. birthday gift"
    )
    material = st.text_input(
        "Material or key feature (optional)",
        placeholder="e.g. sterling silver"
    )

    if st.button("Create SEO Draft"):
        if seo_product.strip():
            name = seo_product.strip()
            title = f"{name.title()} - Custom Gift"
            if material.strip():
                title = f"{name.title()} - {material.strip().title()}"

            words = [
                name.lower(),
                f"personalized {name.lower()}",
                f"custom {name.lower()}",
                f"{name.lower()} gift",
                f"unique {name.lower()}",
                f"{name.lower()} for her",
                f"handmade {name.lower()}",
                f"{name.lower()} gift idea",
                f"modern {name.lower()}",
                f"special {name.lower()}",
                f"{name.lower()} for {audience.lower()}" if audience.strip()
                else f"premium {name.lower()}",
                f"custom made {name.lower()}",
                f"personalized gift for {audience.lower()}" if audience.strip()
                else f"unique personalized gift",
            ]

            tags = list(dict.fromkeys(words))[:13]

            description = (
                f"Discover this {name}. "
                f"{'Designed with ' + material.strip() + '. ' if material.strip() else ''}"
                f"{'A thoughtful choice for ' + audience.strip() + '. ' if audience.strip() else ''}"
                "Please review the actual product details, materials, "
                "dimensions, processing time and shipping information "
                "before publishing. Update this draft to match the real item."
            )

            st.markdown("**Suggested title**")
            st.write(title)
            st.caption("Review Etsy's current title guidance before publishing.")

            st.markdown("**13 suggested tags**")
            st.write(", ".join(tags))
            st.caption("Check Etsy tag length limits and relevance before publishing.")

            st.markdown("**Description draft**")
            st.write(description)

            output = (
                "TITLE\n" + title
                + "\n\nTAGS\n" + ", ".join(tags)
                + "\n\nDESCRIPTION\n" + description
            )
            st.download_button(
                "⬇️ Download SEO Draft",
                data=output,
                file_name="etsy_seo_draft.txt",
                mime="text/plain"
            )
        else:
            st.warning("Pehle product name enter karo.")

st.divider()
st.caption(
    "Etsy AI Research Dashboard MVP | Demo mode — "
    "no live Etsy data or external AI API connected."
)

