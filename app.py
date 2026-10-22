
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

# Starter niche and sub-niche suggestions. These are dashboard shortcuts,
# not a claim that RankHero has an official complete niche directory.
niche_groups = {
    "Artificial flowers & plants": {
        "Silk flowers": "silk flowers",
        "Artificial wedding bouquets": "artificial wedding bouquet",
        "Artificial trees": "artificial tree",
        "Outdoor UV-resistant flowers": "UV resistant artificial flowers",
        "Hanging flower baskets": "artificial hanging flower basket",
        "Artificial greenery": "artificial greenery",
        "Custom sub-niche": ""
    },
    "Jewellery": {
        "Personalized necklaces": "personalized necklace",
        "Gold necklaces": "gold necklace",
        "Birthstone rings": "birthstone ring",
        "Earrings": "handmade earrings",
        "Jewellery sets": "jewelry set",
        "Custom sub-niche": ""
    },
    "Crochet & knitting": {
        "Baby booties": "crochet baby booties",
        "Crochet bags": "crochet bag",
        "Christmas sweaters": "crochet Christmas sweater",
        "Crochet blankets": "crochet blanket",
        "Amigurumi toys": "crochet amigurumi toy",
        "Custom sub-niche": ""
    },
    "Clothing & accessories": {
        "Crochet sweaters": "crochet sweater",
        "Graphic tees": "graphic tee",
        "Scarves": "handmade scarf",
        "Tote bags": "canvas tote bag",
        "Fashion accessories": "fashion accessories",
        "Custom sub-niche": ""
    },
    "Home decor": {
        "Wall decor": "wall decor",
        "Candle holders": "candle holder",
        "Decorative pillows": "decorative pillow",
        "Vases": "decorative vase",
        "Artificial flower arrangements": "artificial flower arrangement",
        "Custom sub-niche": ""
    },
    "Wedding": {
        "Bridal bouquets": "bridal bouquet",
        "Bridesmaid gifts": "bridesmaid gift",
        "Wedding centerpieces": "wedding centerpiece",
        "Wedding favors": "wedding favor",
        "Personalized wedding signs": "personalized wedding sign",
        "Custom sub-niche": ""
    },
    "Personalized gifts": {
        "Custom name gifts": "custom name gift",
        "Personalized mugs": "personalized mug",
        "Engraved gifts": "engraved gift",
        "Personalized ornaments": "personalized Christmas ornament",
        "Custom sub-niche": ""
    },
    "Pet products": {
        "Dog bandanas": "dog bandana",
        "Pet collars": "personalized dog collar",
        "Pet beds": "dog bed",
        "Pet tags": "personalized pet tag",
        "Custom sub-niche": ""
    },
    "Digital products": {
        "Printable planners": "printable planner",
        "Digital wall art": "digital wall art",
        "Wedding templates": "wedding template",
        "Budget spreadsheets": "budget spreadsheet",
        "Custom sub-niche": ""
    },
    "Craft supplies": {
        "Embroidery supplies": "embroidery supplies",
        "Yarn": "crochet yarn",
        "Beads": "jewelry making beads",
        "Sewing patterns": "sewing pattern",
        "Custom sub-niche": ""
    },
    "Baby & kids": {
        "Baby shower gifts": "baby shower gift",
        "Baby clothes": "handmade baby clothes",
        "Nursery decor": "nursery decor",
        "Kids accessories": "kids hair accessories",
        "Custom sub-niche": ""
    },
    "Seasonal & holiday": {
        "Christmas decor": "Christmas decor",
        "Halloween decor": "Halloween decor",
        "Easter gifts": "Easter gift",
        "Fall decorations": "fall decorations",
        "Custom sub-niche": ""
    },
    "Garden & outdoor": {
        "Garden decor": "garden decor",
        "Planters": "garden planter",
        "Outdoor artificial plants": "outdoor artificial plants",
        "Garden signs": "garden sign",
        "Custom sub-niche": ""
    },
    "Vintage": {
        "Vintage home decor": "vintage home decor",
        "Vintage jewellery": "vintage jewelry",
        "Vintage clothing": "vintage clothing",
        "Vintage collectibles": "vintage collectible",
        "Custom sub-niche": ""
    },
    "Custom niche": {
        "Enter your own keyword": ""
    }
}

st.subheader("Choose a niche and sub-niche")
niche_group = st.selectbox(
    "Niche group",
    list(niche_groups.keys()),
    help="These are editable starter suggestions, not a complete official RankHero niche list."
)
sub_niche = st.selectbox("Sub-niche", list(niche_groups[niche_group].keys()))
seed_keyword = niche_groups[niche_group][sub_niche]
search_term = st.text_input(
    "Exact product or seed keyword",
    value=seed_keyword,
    max_chars=140,
    key=f"rankhero_seed_{niche_group}_{sub_niche}",
    help="Edit this suggested keyword or enter your own product phrase."
)

with st.form("rankhero_keyword_form"):
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

    run_research = st.form_submit_button("Run Keyword Research")

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

# ---------------- RankHero additional tools ----------------
st.divider()
st.title("🧰 More RankHero Tools")
st.caption("Optional tools use API credits. Run only the tool you need.")

try:
    _rh_key = st.secrets.get("RANKHERO_API_KEY", "")
except Exception:
    _rh_key = ""

RH_BASE = "https://www.rankhero.com/v1"

def _rh_post(endpoint, payload):
    """Call a documented RankHero endpoint and show useful API errors."""
    if not _rh_key:
        st.error("RANKHERO_API_KEY missing from Streamlit Secrets.")
        return None
    try:
        with st.spinner("RankHero is processing your request..."):
            r = requests.post(
                f"{RH_BASE}/{endpoint}",
                headers={
                    "Authorization": f"Bearer {_rh_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=90,
            )
        try:
            body = r.json()
        except ValueError:
            body = {"message": r.text[:2000]}
        if not r.ok:
            error = body.get("error", body) if isinstance(body, dict) else body
            message = error.get("message", str(error)) if isinstance(error, dict) else str(error)
            st.error(f"RankHero API error (HTTP {r.status_code}): {message}")
            if r.status_code == 402:
                st.warning("API credits may be insufficient. Check your RankHero Credits page before retrying.")
            elif r.status_code == 422:
                st.caption("One or more fields may be invalid. Review the input values below.")
            with st.expander("Technical response"):
                st.json(body)
            return None
        return body
    except requests.RequestException as exc:
        st.error(f"Network request failed: {exc}")
        return None


def _rh_show_usage(data):
    usage = data.get("usage") if isinstance(data, dict) else None
    if isinstance(usage, dict):
        cols = st.columns(3)
        if usage.get("credits_charged") is not None:
            cols[0].metric("Credits charged", usage.get("credits_charged"))
        if usage.get("credits_remaining") is not None:
            cols[1].metric("Credits remaining", usage.get("credits_remaining"))
        if usage.get("funded_by"):
            cols[2].metric("Paid by", str(usage.get("funded_by")))


def _rh_table(data, key, title=None):
    rows = data.get(key) if isinstance(data, dict) else None
    if isinstance(rows, list) and rows:
        st.subheader(title or key.replace("_", " ").title())
        df = pd.json_normalize(rows, sep=".")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            f"Download {key.replace('_', ' ')} CSV",
            df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"rankhero_{key}.csv",
            mime="text/csv",
            key=f"rh_extra_{key}_{len(df)}",
        )
    elif rows == []:
        st.info(f"No {title or key.replace('_', ' ')} returned.")


rh_tab_listing, rh_tab_shop, rh_tab_rank, rh_tab_keywords = st.tabs([
    "🧾 Listing Analyzer", "🏪 Shop Analyzer", "📍 Rank Check", "🌐 Keyword Ideas"
])

with rh_tab_listing:
    st.write("Analyze a public Etsy listing URL or numeric listing ID. This call costs API credits.")
    with st.form("rh_listing_analysis_form"):
        listing_input = st.text_input("Etsy listing URL or listing ID", placeholder="https://www.etsy.com/listing/1234567890/... ")
        listing_tag_metrics = st.checkbox("Include tag search/competition metrics", value=True)
        listing_images = st.checkbox("Include image checks", value=False)
        listing_description = st.checkbox("Include full description text", value=False)
        run_listing_analysis = st.form_submit_button("Analyze listing")
    if run_listing_analysis:
        if not listing_input.strip():
            st.warning("Enter a listing URL or numeric ID first.")
        else:
            result = _rh_post("etsy/listing-analysis", {
                "listing": listing_input.strip(),
                "include_tag_metrics": listing_tag_metrics,
                "include_images": listing_images,
                "include_description": listing_description,
            })
            if result:
                st.success("Listing analysis completed.")
                _rh_show_usage(result)
                summary = result.get("listing", {})
                score = result.get("score", {})
                stats = result.get("stats", {})
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Listing score", score.get("value", "N/A"))
                c2.metric("Grade", score.get("grade", "N/A"))
                c3.metric("Views", stats.get("views", "N/A"))
                c4.metric("Favorites", stats.get("favorites", "N/A"))
                st.write("**Title:**", summary.get("title", "Not provided"))
                if summary.get("url"):
                    st.markdown(f"[Open Etsy listing]({summary['url']})")
                sections = result.get("sections", {})
                for section_name, section in sections.items():
                    with st.expander(section_name.replace("_", " ").title()):
                        st.json(section)
                _rh_table(result, "tag_metrics", "Tag Search & Competition Metrics")
                st.subheader("Listing tags")
                st.write(", ".join(result.get("tags", [])) or "No tags returned")
                if listing_images and result.get("images") is not None:
                    _rh_table(result, "images", "Image Checks")
                if listing_description and result.get("description"):
                    with st.expander("Full listing description"):
                        st.write(result["description"])

with rh_tab_shop:
    st.write("Analyze any public Etsy shop, including competitors. Sales and revenue figures are estimates, not exact shop accounts.")
    with st.form("rh_shop_analysis_form"):
        shop_input = st.text_input("Etsy shop name", placeholder="ShopName (not a full Etsy URL)")
        shop_max_listings = st.selectbox("Listings to analyze", [25, 50, 100, 200], index=2)
        shop_tag_metrics = st.checkbox("Include tag search/competition metrics", value=True)
        shop_include_listings = st.checkbox("Include all analyzed listings in results", value=False)
        shop_include_about = st.checkbox("Include shop announcement and policies", value=False)
        run_shop_analysis = st.form_submit_button("Analyze shop")
    if run_shop_analysis:
        if not shop_input.strip():
            st.warning("Enter an Etsy shop name first.")
        else:
            result = _rh_post("etsy/shop-analysis", {
                "shop_name": shop_input.strip(),
                "max_listings": shop_max_listings,
                "include_tag_metrics": shop_tag_metrics,
                "include_listings": shop_include_listings,
                "include_about": shop_include_about,
            })
            if result:
                st.success("Shop analysis completed.")
                _rh_show_usage(result)
                shop = result.get("shop", {})
                perf = result.get("performance", {})
                grade = result.get("grade", {})
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Active listings", shop.get("active_listings", "N/A"))
                c2.metric("Lifetime sales (Etsy count)", shop.get("sales", "N/A"))
                c3.metric("Estimated monthly sales", perf.get("monthly_sales_estimate", "N/A"))
                c4.metric("Average listing grade", grade.get("average_grade", "N/A"))
                st.write("**Shop:**", shop.get("name", shop_input.strip()))
                if shop.get("url"):
                    st.markdown(f"[Open Etsy shop]({shop['url']})")
                st.write("**Shop performance:**")
                st.json(perf)
                if result.get("rank"):
                    st.write("**RankHero shop index:**")
                    st.json(result["rank"])
                _rh_table(result, "top_tags", "Most-used Tags")
                _rh_table(result, "categories", "Shop Categories")
                _rh_table(result, "top_listings", "Top Listings")
                if shop_include_listings:
                    _rh_table(result, "listings", "All Analyzed Listings")
                if shop_include_about and result.get("about"):
                    with st.expander("Shop announcement and policies"):
                        st.json(result["about"])

with rh_tab_rank:
    st.write("Check whether a shop or listing appears in Etsy's top 100 results for up to five phrases. Each distinct keyword costs 1 API credit.")
    with st.form("rh_rank_check_form"):
        rank_target_type = st.radio("What do you want to check?", ["Shop name", "Listing ID"], horizontal=True)
        rank_target = st.text_input("Etsy shop name" if rank_target_type == "Shop name" else "Numeric Etsy listing ID")
        rank_keywords_text = st.text_area("Keywords (one per line, maximum 5)", placeholder="artificial wedding bouquet\nsilk flowers\noutdoor artificial flowers")
        rank_location = st.selectbox("Rank marketplace", ["United States", "Global", "United Kingdom", "Canada", "Australia", "India", "European Union"], key="rh_rank_location")
        run_rank_check = st.form_submit_button("Check Etsy rank")
    if run_rank_check:
        rank_keywords = list(dict.fromkeys([x.strip() for x in rank_keywords_text.splitlines() if x.strip()]))
        if not rank_target.strip():
            st.warning("Enter the shop name or listing ID.")
        elif not rank_keywords:
            st.warning("Enter at least one keyword.")
        elif len(rank_keywords) > 5:
            st.warning("Use no more than five unique keywords per request to control credit use.")
        elif rank_target_type == "Listing ID" and not rank_target.strip().isdigit():
            st.warning("Listing ID must contain digits only.")
        else:
            payload = {"keywords": rank_keywords, "location": rank_location}
            if rank_target_type == "Shop name":
                payload["shop_name"] = rank_target.strip()
            else:
                payload["listing_id"] = int(rank_target.strip())
            result = _rh_post("etsy/rank", payload)
            if result:
                st.success("Rank check completed.")
                _rh_show_usage(result)
                st.write("**Target:**", result.get("target", {}))
                st.write("**Marketplace:**", result.get("location", rank_location))
                _rh_table(result, "results", "Keyword Rank Results")

with rh_tab_keywords:
    st.write("Find related web-search keyword ideas. Important: this endpoint is general web SEO data, not Etsy-specific search volume.")
    with st.form("rh_web_keywords_form"):
        seed_terms_text = st.text_area("Seed terms (one per line, maximum 20)", placeholder="artificial flowers\nsilk wedding bouquet")
        keyword_location = st.selectbox("Search-volume country", ["United States", "Global", "United Kingdom", "Canada", "Australia", "India", "New Zealand", "South Africa", "Poland", "Germany", "France", "Italy", "Spain", "Turkey"], key="rh_keyword_location")
        keyword_limit = st.slider("Maximum keyword ideas", 10, 100, 30)
        include_keyword_ideas = st.checkbox("Find related keyword ideas", value=True)
        include_keyword_trend = st.checkbox("Include 12-month search trend", value=False)
        run_web_keywords = st.form_submit_button("Find keyword ideas")
    if run_web_keywords:
        seed_terms = list(dict.fromkeys([x.strip() for x in seed_terms_text.splitlines() if x.strip()]))
        if not seed_terms:
            st.warning("Enter at least one seed term.")
        elif len(seed_terms) > 20:
            st.warning("Use no more than 20 seed terms.")
        elif any(len(x) > 79 or "," in x for x in seed_terms):
            st.warning("Each seed term must be 1–79 characters and must not contain a comma.")
        else:
            result = _rh_post("keywords", {
                "search_terms": seed_terms,
                "location": keyword_location,
                "limit": keyword_limit,
                "include_ideas": include_keyword_ideas,
                "include_trend": include_keyword_trend,
            })
            if result:
                st.success("Keyword ideas loaded.")
                _rh_show_usage(result)
                st.write("**Data source:**", result.get("source", "Not provided"))
                st.write("**Total ideas found:**", result.get("total_ideas", 0))
                _rh_table(result, "keywords", "Keyword Ideas")
                if include_keyword_trend:
                    st.caption("Trend values, when returned, are general web search estimates—not Etsy search volume.")
