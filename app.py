
import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Etsy Research Dashboard",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 Etsy AI Research Dashboard")
st.caption("Listing research + keyword insights | Free starter version")

# Get API key from Streamlit Secrets, if configured.
try:
    api_key = st.secrets.get("ETSY_API_KEY", "")
except Exception:
    api_key = ""

with st.sidebar:
    st.header("Settings")
    st.write("Etsy API listing research")
    if not api_key:
        api_key = st.text_input(
            "Etsy API key",
            type="password",
            help="Enter keystring:shared_secret. "
                 "Do not paste it into GitHub code."
        )
    st.caption("Search demand is not supplied by this listing search.")

tab1, tab2, tab3 = st.tabs([
    "🛍️ Product Hunter",
    "🔑 Keyword Insights",
    "📁 Export"
])

if "results" not in st.session_state:
    st.session_state.results = pd.DataFrame()

if "total_count" not in st.session_state:
    st.session_state.total_count = None

with tab1:
    st.subheader("Search Etsy active listings")
    keyword = st.text_input(
        "Product or keyword",
        value="artificial wedding bouquet",
        key="listing_keyword"
    )
    limit = st.selectbox("Listings to retrieve", [10, 25, 50, 100], index=1)

    if st.button("Search real listings", type="primary"):
        if not api_key.strip():
            st.warning(
                "API key missing. Register an Etsy developer app "
                "and enter its key to try this feature."
            )
        elif not keyword.strip():
            st.warning("Enter a keyword first.")
        else:
            try:
                response = requests.get(
                    "https://api.etsy.com/v3/application/listings/active",
                    headers={"x-api-key": api_key.strip()},
                    params={
                        "keywords": keyword.strip(),
                        "limit": limit,
                        "sort_on": "score"
                    },
                    timeout=25
                )

                if response.status_code != 200:
                    st.error(
                        f"Etsy API returned HTTP {response.status_code}. "
                        "Check your API credentials, access and API limits."
                    )
                    st.code(response.text[:1200])
                else:
                    payload = response.json()
                    rows = []

                    for item in payload.get("results", []):
                        price = item.get("price") or {}
                        amount = price.get("amount")
                        divisor = price.get("divisor") or 100
                        price_value = (
                            amount / divisor
                            if amount is not None else None
                        )

                        rows.append({
                            "Title": item.get("title", ""),
                            "Price": price_value,
                            "Currency": price.get("currency_code", ""),
                            "Listing ID": item.get("listing_id", ""),
                            "URL": item.get("url", ""),
                            "Created": item.get(
                                "creation_timestamp", ""
                            )
                        })

                    st.session_state.results = pd.DataFrame(rows)
                    st.session_state.total_count = payload.get("count")
                    st.success(f"Retrieved {len(rows)} listings.")

            except requests.RequestException as exc:
                st.error(f"Network error: {exc}")
            except (ValueError, TypeError, KeyError) as exc:
                st.error(f"Could not read the API response: {exc}")

    if st.session_state.total_count is not None:
        st.metric(
            "API-reported matching listings",
            f"{st.session_state.total_count:,}"
        )
        st.caption(
            "This is a listing count, not keyword search volume or sales."
        )

    if not st.session_state.results.empty:
        df = st.session_state.results
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "URL": st.column_config.LinkColumn("Open listing")
            }
        )

        prices = pd.to_numeric(df["Price"], errors="coerce").dropna()
        if not prices.empty:
            a, b = st.columns(2)
            a.metric("Average listed price", f"{prices.mean():.2f}")
            b.metric("Median listed price", f"{prices.median():.2f}")

        st.download_button(
            "Download listing CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="etsy_listings.csv",
            mime="text/csv"
        )

with tab2:
    st.subheader("Record verified keyword data")
    st.write(
        "Etsy Marketplace Insights se values manually enter karo. "
        "Dashboard inhein Etsy listing search se alag rakhega."
    )

    with st.form("keyword_form"):
        term = st.text_input("Keyword")
        searches = st.number_input(
            "Etsy searches in last 30 days",
            min_value=0,
            step=1
        )
        competing = st.number_input(
            "Etsy listings shown by Marketplace Insights",
            min_value=0,
            step=1
        )
        source = st.selectbox(
            "Data source",
            ["Etsy Marketplace Insights", "Google Trends", "Other"]
        )
        submitted = st.form_submit_button("Add keyword record")

    if "keyword_records" not in st.session_state:
        st.session_state.keyword_records = []

    if submitted:
        if term.strip():
            st.session_state.keyword_records.append({
                "Keyword": term.strip(),
                "Searches (30 days)": int(searches),
                "Listings": int(competing),
                "Source": source
            })
            st.success("Keyword record added.")
        else:
            st.warning("Enter a keyword.")

    if st.session_state.keyword_records:
        kdf = pd.DataFrame(st.session_state.keyword_records)
        st.dataframe(kdf, use_container_width=True, hide_index=True)
        st.download_button(
            "Download keyword CSV",
            kdf.to_csv(index=False).encode("utf-8"),
            file_name="etsy_keyword_research.csv",
            mime="text/csv",
            key="keyword_csv"
        )
        st.caption(
            "Records are held in the current app session. "
            "Download the CSV to keep them."
        )

    st.info(
        "Google Trends values are relative interest scores, "
        "not actual Etsy searches. Label them accordingly."
    )

with tab3:
    st.subheader("Export your research")
    st.write("Download listing and keyword CSV files from their respective tabs.")
    st.write(
        "The app does not estimate sales, profit, or exact search volume "
        "unless a verified data source provides those values."
    )

st.divider()
st.caption(
    "Independent research tool. Not affiliated with or endorsed by Etsy. "
    "Use the Etsy API in accordance with its terms and access permissions."
)

import streamlit as st
import requests

st.subheader("RankHero API Connection Test")

if st.button("Test RankHero API"):
    try:
        api_key = st.secrets["RANKHERO_API_KEY"]

        response = requests.get(
            "https://www.rankhero.com/v1/me",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )

        if response.ok:
            data = response.json()
            st.success("RankHero API connected successfully!")
            st.json(data)
        else:
            st.error(f"API error: HTTP {response.status_code}")
            st.json(response.json())

    except Exception as e:
        st.error(f"Connection test failed: {e}")

import pandas as pd

st.divider()
st.title("Etsy Keyword Research")
st.caption("Powered by RankHero API")

# Broad starter groups are shortcuts; the seed keyword remains editable so
# users can research any niche supported by RankHero's Etsy tags endpoint.
niche_groups = {
    "Artificial flowers & plants": "artificial flowers",
    "Jewellery": "personalized necklace",
    "Crochet & knitting": "crochet baby booties",
    "Clothing & accessories": "crochet sweater",
    "Home decor": "wall decor",
    "Wedding": "wedding bouquet",
    "Personalized gifts": "personalized gift",
    "Pet products": "dog bandana",
    "Digital products": "printable planner",
    "Craft supplies": "embroidery supplies",
    "Baby & kids": "baby shower gift",
    "Seasonal & holiday": "Christmas decor",
    "Garden & outdoor": "garden decor",
    "Vintage": "vintage home decor",
    "Custom niche": ""
}

with st.form("rankhero_keyword_form"):
    niche_group = st.selectbox(
        "Choose a niche group",
        list(niche_groups.keys()),
        help="These are starter shortcuts, not a complete RankHero niche database."
    )
    search_term = st.text_input(
        "Exact product or seed keyword",
        value=niche_groups[niche_group],
        max_chars=140,
        key=f"rankhero_seed_{niche_group}",
        help="You can edit this or enter any niche, for example: artificial flowers, crochet baby booties, birthstone ring."
    )

    location = st.selectbox(
        "Etsy marketplace",
        [
            "United States",
            "Global",
            "United Kingdom",
            "Canada",
            "Australia",
            "India",
            "European Union"
        ]
    )

    limit = st.slider("Maximum tags", 1, 75, 30)

    include_listings = st.checkbox(
        "Include Etsy listings (no extra endpoint charge)",
        value=True
    )

    max_listings = st.slider(
        "Maximum listings",
        1, 60, 20,
        disabled=not include_listings
    )

    run_research = st.form_submit_button(
        "Run Keyword Research"
    )

if run_research:
    if not search_term.strip():
        st.warning("Please enter a product or niche.")
    else:
        try:
            api_key = st.secrets["RANKHERO_API_KEY"]

            payload = {
                "search_term": search_term.strip(),
                "location": location,
                "limit": limit,
                "include_listings": include_listings,
                "max_listings": max_listings
            }

            with st.spinner("Fetching RankHero research data..."):
                response = requests.post(
                    "https://www.rankhero.com/v1/etsy/tags",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=90
                )

            if response.ok:
                data = response.json()

                st.success("Keyword research completed!")

                st.write("**Search term:**", data.get("search_term"))
                st.write("**Marketplace:**", data.get("location"))
                st.write("**Data source:**", data.get("source", "Not provided"))
                st.write("**Generated at (UTC):**", data.get("generated_at", "Not provided"))

                usage = data.get("usage")
                if usage:
                    st.write("**Credits charged:**", usage.get("credits_charged"))
                    st.write("**Credits remaining:**", usage.get("credits_remaining"))

                prices = data.get("prices")
                if prices:
                    st.subheader("Seller Price Bands")
                    st.json(prices)

                for category in ["tags", "materials", "styles"]:
                    rows = data.get(category) or []
                    st.subheader(category.replace("_", " ").title())

                    if rows:
                        df = pd.DataFrame(rows)

                        # Put stronger search-demand tags first when the API
                        # returns a numeric monthly-search estimate.
                        if category == "tags" and "avg_monthly_searches" in df.columns:
                            df["avg_monthly_searches"] = pd.to_numeric(
                                df["avg_monthly_searches"], errors="coerce"
                            )
                            df = df.sort_values(
                                "avg_monthly_searches", ascending=False, na_position="last"
                            )

                        st.dataframe(df, use_container_width=True, hide_index=True)

                        st.download_button(
                            f"Download {category} CSV",
                            data=df.to_csv(index=False).encode("utf-8-sig"),
                            file_name=f"etsy_{category}.csv",
                            mime="text/csv",
                            key=f"download_{category}"
                        )
                    else:
                        st.info(f"No {category} returned for this search.")

                listings = data.get("listings")
                if listings is not None:
                    st.subheader("Etsy Listings")
                    if listings:
                        listing_df = pd.DataFrame(listings)
                        st.dataframe(listing_df, use_container_width=True)

                        st.download_button(
                            "Download listings CSV",
                            data=listing_df.to_csv(index=False).encode("utf-8-sig"),
                            file_name="etsy_listings.csv",
                            mime="text/csv",
                            key="download_listings"
                        )
                    else:
                        st.info("No listings were returned for this search.")

                st.caption(
                    f"Listings available: {data.get('listings_available', 0)}"
                )

            else:
                st.error(f"RankHero API error: HTTP {response.status_code}")
                try:
                    st.json(response.json())
                except ValueError:
                    st.code(response.text[:2000])

        except KeyError:
            st.error("RANKHERO_API_KEY missing from Streamlit Secrets.")
        except requests.RequestException as e:
            st.error(f"Network request failed: {e}")
        except Exception as e:
            st.error(f"Something went wrong: {e}")
