
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

# ---------------- Free Product Research (no paid API credits) ----------------
st.divider()
st.title("🆓 Free Product Research")
st.caption("Free workflow — no RankHero credits used. Verify demand and competition on the linked sources; this tool does not claim live trend/search-volume data.")

with st.expander("Open Free Product Research menu", expanded=True):
    free_col1, free_col2 = st.columns([2, 1])
    with free_col1:
        free_niche = st.selectbox(
            "Choose a niche",
            ["Artificial flowers & plants", "Jewellery", "Crochet & knitting", "Garden decor", "Home decor", "Personalized gifts", "Pet accessories", "Wedding products", "Other / custom"],
            key="free_research_niche"
        )
        free_seed = st.text_input(
            "Product or seed keyword",
            value="artificial flowers",
            help="Enter the item you want to research. This creates search links and keyword variations; it does not fetch private or paid trend data.",
            key="free_research_seed"
        )
    with free_col2:
        free_market = st.selectbox("Target market", ["United States", "Global", "United Kingdom", "Canada", "Australia"], key="free_research_market")
        free_count = st.slider("Keyword variations", 5, 25, 12, key="free_research_count")

    if st.button("Build free research checklist", type="primary", key="free_research_build"):
        seed = free_seed.strip()
        if not seed:
            st.warning("Pehle product ya keyword likho.")
        else:
            import urllib.parse
            modifiers = [
                "best seller", "trending", "personalized", "custom", "handmade",
                "gift", "wedding", "minimalist", "modern", "rustic", "small", "large",
                "premium", "budget", "for women", "for home", "seasonal", "outdoor",
                "unique", "made to order", "set of", "custom color", "gift for her",
                "gift for mom", "Christmas"
            ]
            variations = [seed] + [f"{m} {seed}" for m in modifiers if m.lower() not in seed.lower()]
            variations = variations[:free_count]
            st.session_state["free_research_terms"] = variations
            st.session_state["free_research_terms"] = variations
            st.session_state["free_research_seed_saved"] = seed
        st.session_state["free_research_market_saved"] = free_market

    free_terms = st.session_state.get("free_research_terms", [])
    if free_terms:
        import urllib.parse
        market_code = {"United States": "US", "Global": "", "United Kingdom": "GB", "Canada": "CA", "Australia": "AU"}.get(st.session_state.get("free_research_market_saved", free_market), "US")
        st.subheader("Keyword ideas and free research links")
        st.caption("Open the links and record what you actually observe. Search-result counts are not search volume, and a trend signal is not proof of sales.")
        rows = []
        for term in free_terms:
            q = urllib.parse.quote_plus(term)
            etsy_url = f"https://www.etsy.com/search?q={q}"
            trends_url = f"https://trends.google.com/trends/explore?geo={market_code}&q={q}"
            google_url = f"https://www.google.com/search?q={q}"
            rows.append({"Keyword idea": term, "Etsy search": etsy_url, "Google Trends": trends_url, "Google search": google_url})
        free_df = pd.DataFrame(rows)
        st.dataframe(
            free_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Etsy search": st.column_config.LinkColumn("Open Etsy", display_text="Search Etsy"),
                "Google Trends": st.column_config.LinkColumn("Open Trends", display_text="Check Trends"),
                "Google search": st.column_config.LinkColumn("Open Google", display_text="Search Google"),
            },
        )
        st.download_button(
            "Download free keyword ideas CSV",
            free_df.to_csv(index=False).encode("utf-8"),
            file_name="free_product_research_keywords.csv",
            mime="text/csv",
            key="free_research_download",
        )

        st.subheader("Record your observations")
        with st.form("free_observation_form"):
            observed_term = st.selectbox("Keyword checked", free_terms, key="free_observed_term")
            competition_note = st.selectbox("Competition you observed", ["Not checked", "Low", "Medium", "High"], key="free_competition_note")
            trend_note = st.selectbox("Google Trends direction", ["Not checked", "Rising", "Stable", "Falling", "Seasonal / mixed"], key="free_trend_note")
            price_note = st.text_input("Typical prices you observed (optional)", placeholder="e.g. $18–$35", key="free_price_note")
            product_note = st.text_area("Product gap / differentiation idea (optional)", placeholder="What could make your offer different?", key="free_product_note")
            save_observation = st.form_submit_button("Save observation")
        if "free_observations" not in st.session_state:
            st.session_state["free_observations"] = []
        if save_observation:
            st.session_state["free_observations"].append({
                "Keyword": observed_term,
                "Competition observed": competition_note,
                "Google Trends direction": trend_note,
                "Price range observed": price_note.strip(),
                "Differentiation idea": product_note.strip(),
                "Market": st.session_state.get("free_research_market_saved", free_market),
            })
            st.success("Observation saved for this session.")
        if st.session_state["free_observations"]:
            observations_df = pd.DataFrame(st.session_state["free_observations"])
            st.dataframe(observations_df, use_container_width=True, hide_index=True)
            st.download_button(
                "Download observations CSV",
                observations_df.to_csv(index=False).encode("utf-8"),
                file_name="free_product_research_observations.csv",
                mime="text/csv",
                key="free_observations_download",
            )

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




# ---------------- Listing Creator (URL-based draft) ----------------
def _safe_fetch_product_page(url):
    """Fetch basic public product metadata from a user-supplied HTTP(S) URL."""
    from urllib.parse import urlparse
    import ipaddress
    from html.parser import HTMLParser

    class MetaParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.meta = {}
            self.title_parts = []
            self.in_title = False
            self.images = []
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag.lower() == "title":
                self.in_title = True
            if tag.lower() == "meta":
                key = (attrs.get("property") or attrs.get("name") or "").lower()
                value = attrs.get("content", "").strip()
                if key and value:
                    self.meta[key] = value
            if tag.lower() == "img":
                src = attrs.get("src") or attrs.get("data-src")
                if src and src.startswith(("http://", "https://")):
                    self.images.append(src)
        def handle_endtag(self, tag):
            if tag.lower() == "title":
                self.in_title = False
        def handle_data(self, data):
            if self.in_title and data.strip():
                self.title_parts.append(data.strip())

    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Please enter a complete public http:// or https:// product URL.")
    host = parsed.hostname.lower()
    if host in ("localhost",) or host.endswith(".localhost") or host.endswith(".local"):
        raise ValueError("Local/private URLs are not allowed.")
    try:
        ip = ipaddress.ip_address(host)
        if not ip.is_global:
            raise ValueError("Private or local IP addresses are not allowed.")
    except ValueError as exc:
        if "not allowed" in str(exc):
            raise
        # Host is a domain name rather than an IP address.
        pass

    response = requests.get(
        url.strip(),
        headers={"User-Agent": "Mozilla/5.0 (compatible; EtsyResearchDashboard/1.0)"},
        timeout=20,
        allow_redirects=True,
    )
    response.raise_for_status()
    if len(response.content) > 4_000_000:
        raise ValueError("The page is too large to process (4 MB limit).")
    parser = MetaParser()
    parser.feed(response.text[:4_000_000])
    final_host = urlparse(response.url).hostname or ""
    if final_host.lower() in ("localhost",) or final_host.lower().endswith((".local", ".localhost")):
        raise ValueError("The URL redirected to a local address.")
    title = (
        parser.meta.get("og:title")
        or parser.meta.get("twitter:title")
        or (parser.title_parts[0] if parser.title_parts else "")
    )
    description = (
        parser.meta.get("og:description")
        or parser.meta.get("description")
        or parser.meta.get("twitter:description")
        or ""
    )
    main_image = parser.meta.get("og:image") or parser.meta.get("twitter:image")
    image_urls = []
    if main_image and main_image.startswith(("http://", "https://")):
        image_urls.append(main_image)
    for image_url in parser.images:
        if image_url not in image_urls:
            image_urls.append(image_url)
    return {
        "title": title[:500],
        "description": description[:3000],
        "image_urls": image_urls[:12],
        "final_url": response.url,
    }


def _listing_tags_from_text(title, category, notes, count=13):
    """Simple transparent starter tag builder; does not claim search-volume data."""
    import re
    stop = {"with", "from", "that", "this", "your", "for", "and", "the", "of", "to", "in", "on", "a", "an", "by", "is", "are"}
    phrases = []
    base = f"{title} {category} {notes}".lower()
    words = re.findall(r"[a-z0-9]+", base)
    for n in (3, 2, 1):
        for i in range(max(0, len(words) - n + 1)):
            phrase_words = words[i:i+n]
            phrase = " ".join(phrase_words).strip()
            if not phrase or all(w in stop for w in phrase_words):
                continue
            if len(phrase) <= 20 and phrase not in phrases and any(w not in stop for w in phrase_words):
                phrases.append(phrase)
    # Add relevant category/occasion modifiers, but mark them as suggestions for seller review.
    for extra in [category.lower(), "gift idea", "home decor", "unique gift", "personalized gift"]:
        if extra and len(extra) <= 20 and extra not in phrases:
            phrases.append(extra)
    return phrases[:count]


rh_tab_creator, rh_tab_listing, rh_tab_shop, rh_tab_rank, rh_tab_keywords = st.tabs([
    "🪄 Listing Creator", "🧾 Listing Analyzer", "🏪 Shop Analyzer", "📍 Rank Check", "🌐 Keyword Ideas"
])

with rh_tab_creator:
    st.write("Paste a public product-page URL to build an editable Etsy listing draft. Some sites block automated fetching; if that happens, paste the product title and details manually.")
    st.info("Free-first version: it fetches public page metadata and creates a draft plus six separate image prompts. It does not publish to Etsy or generate image files by itself. Actual AI image generation needs an image-generation service/API.")
    with st.form("rh_listing_creator_form"):
        creator_url = st.text_input("Product URL (any public website)", placeholder="https://example.com/product-page")
        creator_category = st.selectbox(
            "Etsy category / product niche",
            ["Artificial flowers & plants", "Jewellery", "Crochet & knitting", "Clothing & accessories",
             "Home decor", "Wedding", "Personalized gifts", "Garden decor", "Other"]
        )
        creator_notes = st.text_area(
            "Extra product facts (optional but recommended)",
            placeholder="Materials, dimensions, colors, what's included, customization, who it's for, shipping/production facts..."
        )
        creator_market = st.selectbox("Target market", ["United States", "Global", "United Kingdom", "Canada", "Australia"])
        creator_use_rankhero = st.checkbox("Also fetch RankHero Etsy tag research (uses 1 API credit)", value=False)
        run_creator = st.form_submit_button("Fetch product & create listing draft")

    if run_creator:
        if not creator_url.strip():
            st.warning("Please enter a product URL.")
        else:
            try:
                product_data = _safe_fetch_product_page(creator_url.strip())
                st.session_state["listing_creator_product"] = product_data
                st.session_state["listing_creator_notes"] = creator_notes.strip()
                st.session_state["listing_creator_category"] = creator_category
                st.session_state["listing_creator_market"] = creator_market
                st.session_state["listing_creator_use_rankhero"] = creator_use_rankhero
            except Exception as exc:
                st.error(f"Could not fetch that page: {exc}")
                st.info("Some websites block automated requests. Copy the product title, details, and image URLs into the fields below and try again with a publicly accessible page.")

    if st.session_state.get("listing_creator_product"):
        product_data = st.session_state["listing_creator_product"]
        st.subheader("Fetched product information")
        st.write("**Source page:**", product_data.get("final_url", ""))
        fetched_title = product_data.get("title") or "Product title not found"
        st.write("**Fetched title:**", fetched_title)
        if product_data.get("description"):
            with st.expander("Fetched source description"):
                st.write(product_data["description"])
        image_urls = product_data.get("image_urls", [])
        st.caption(f"Found {len(image_urls)} possible product image URL(s). Some may not be product photos.")
        if image_urls:
            cols = st.columns(min(3, len(image_urls)))
            for i, image_url in enumerate(image_urls[:6]):
                with cols[i % len(cols)]:
                    st.image(image_url, caption=f"Source image {i+1}", use_container_width=True)

        notes_value = st.session_state.get("listing_creator_notes", "")
        category_value = st.session_state.get("listing_creator_category", "Other")
        market_value = st.session_state.get("listing_creator_market", "United States")
        st.subheader("Edit your Etsy listing draft")
        draft_title = st.text_input("SEO title (editable)", value=(fetched_title if fetched_title != "Product title not found" else ""), max_chars=140, key="creator_edit_title")
        draft_tags = _listing_tags_from_text(draft_title, category_value, notes_value)
        draft_tags = [tag[:20] for tag in draft_tags if tag.strip()]
        draft_description = st.text_area(
            "Product description (editable)",
            value=(
                f"{draft_title}\n\n"
                f"PRODUCT DETAILS\n{notes_value or 'Add verified materials, dimensions, colors, included items, and customization details here.'}\n\n"
                f"WHY YOU MAY LOVE IT\nDescribe the product's real features, intended use, and gifting occasions without making unverified claims.\n\n"
                f"IMPORTANT DETAILS\n- Materials: add confirmed materials\n- Size/dimensions: add exact measurements\n- What's included: list every included item\n- Processing/shipping: add accurate shop-specific details\n\n"
                f"Please review all details before publishing. This draft was prepared for the {market_value} market."
            ),
            height=280,
            key="creator_edit_description"
        )
        st.write("**Suggested tags** (starter suggestions only; check relevance and Etsy's 20-character limit):")
        st.write(", ".join(draft_tags))
        st.caption("These draft tags are generated from page text and your notes, not from measured Etsy search volume. For real keyword/competition metrics, use the Keyword Research tab or optionally run RankHero below.")
        tag_text = st.text_area("Edit tags (one per line; max 20 characters each)", value="\n".join(draft_tags), key="creator_edit_tags")
        valid_tags = list(dict.fromkeys([x.strip() for x in tag_text.splitlines() if x.strip()]))
        invalid_tags = [tag for tag in valid_tags if len(tag) > 20]
        if invalid_tags:
            st.warning("These tags exceed 20 characters: " + ", ".join(invalid_tags))
        st.caption(f"{len(valid_tags)} non-empty tags entered. Etsy currently allows up to 13 tags per listing; use no more than 13 relevant tags.")

        st.subheader("Six separate image concepts")
        image_prompts = [
            f"Main Etsy product photo of {draft_title}, centered, clear details, clean uncluttered background, natural realistic lighting, square composition. Preserve the actual product design and do not add features not shown.",
            f"Second product angle of {draft_title}, showing a different realistic viewing angle, accurate proportions, neutral background, professional ecommerce photography.",
            f"Close-up detail photo of {draft_title}, highlighting real texture, stitching, finish, or craftsmanship visible on the actual product; do not invent materials.",
            f"Lifestyle scene featuring {draft_title} in a relevant everyday setting for {category_value}, realistic scale, product clearly visible, natural light.",
            f"Size and scale presentation for {draft_title}, with clean layout and space to add verified dimensions later; do not invent measurements or text.",
            f"Gift-ready or alternate-use scene for {draft_title}, tasteful styling, product remains the main focus, realistic details and no misleading accessories."
        ]
        prompt_cols = st.columns(2)
        for idx, prompt in enumerate(image_prompts):
            with prompt_cols[idx % 2]:
                st.markdown(f"**Image {idx+1}**")
                st.text_area(f"Prompt {idx+1}", value=prompt, height=105, key=f"creator_img_prompt_{idx}")
        st.caption("Etsy listing-photo guidance changes over time; use clear, accurate product photos and check the current Etsy Seller Handbook before publishing. Do not use supplier/competitor images unless you have permission and they accurately represent what you sell.")

        listing_export = {
            "source_url": product_data.get("final_url", ""),
            "target_market": market_value,
            "category": category_value,
            "title": draft_title,
            "tags": valid_tags[:13],
            "description": draft_description,
            "source_image_urls": image_urls[:6],
            "image_prompts": image_prompts,
            "notes": notes_value,
        }
        st.download_button(
            "Download listing draft (JSON)",
            data=__import__("json").dumps(listing_export, ensure_ascii=False, indent=2),
            file_name="etsy_listing_draft.json",
            mime="application/json",
            key="creator_download_json",
        )
        st.download_button(
            "Download listing text (TXT)",
            data=f"TITLE\n{draft_title}\n\nTAGS\n{', '.join(valid_tags[:13])}\n\nDESCRIPTION\n{draft_description}\n\nSIX IMAGE PROMPTS\n" + "\n\n".join(f"{i+1}. {p}" for i, p in enumerate(image_prompts)),
            file_name="etsy_listing_draft.txt",
            mime="text/plain",
            key="creator_download_txt",
        )
        if st.session_state.get("listing_creator_use_rankhero"):
            if st.button("Run RankHero Etsy tag research (1 credit)", key="creator_rankhero_tags"):
                rank_result = _rh_post("etsy/tags", {
                    "search_term": draft_title[:140],
                    "location": market_value,
                    "limit": 75,
                    "include_listings": False,
                })
                if rank_result:
                    st.success("RankHero tag research completed.")
                    _rh_show_usage(rank_result)
                    _rh_table(rank_result, "tags", "RankHero Etsy tag research")


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


# ---------------- AUTOMATED MULTI-NICHE PRODUCT HUNTER ----------------
st.divider()
st.title("🚀 Automated Multi-Niche Product Hunter")
st.caption("Collects real active Etsy listings across starter niches, then creates clearly-labelled screening scores and SEO suggestions.")

with st.expander("How this research works — read before running", expanded=False):
    st.markdown(
        "- **Real Etsy fields:** listing title, listing ID, URL, listed price, currency and creation date when returned by Etsy.\n"
        "- **30-day filter:** only listings with a verifiable creation timestamp within the selected window are included.\n"
        "- **Estimated fields:** screening score, suggested SEO title and tags are generated by this dashboard; they are not Etsy search-volume, sales or ranking data.\n"
        "- **Un-hunted does not mean proven low competition:** a listing found here is a candidate for further research, not proof that few sellers offer it.\n"
        "- This first version runs when you press the button. Daily unattended execution needs a separate scheduler (for example GitHub Actions) and will be added after this test works."
    )

# Broad starter seeds across Etsy categories. These are discovery queries, not a complete Etsy taxonomy.
HUNT_SEEDS = {
    "Artificial flowers & plants": ["artificial flower arrangement", "silk wedding bouquet"],
    "Jewellery": ["personalized necklace", "handmade earrings"],
    "Crochet & knitting": ["crochet baby booties", "crochet bag"],
    "Clothing & accessories": ["crochet clothing", "handmade fashion accessories"],
    "Home decor": ["handmade wall decor", "decorative home accessories"],
    "Wedding": ["personalized wedding decor", "bridal bouquet"],
    "Personalized gifts": ["custom personalized gift", "engraved keepsake"],
    "Pet products": ["personalized pet accessory", "handmade dog bandana"],
    "Digital products": ["printable planner", "digital wall art"],
    "Craft supplies": ["jewelry making supplies", "embroidery supplies"],
    "Baby & kids": ["handmade baby gift", "nursery decor"],
    "Seasonal & holiday": ["Christmas handmade decor", "Halloween decorations"],
    "Garden & outdoor": ["garden decor", "outdoor planter"],
    "Vintage": ["vintage home decor", "vintage jewelry"],
    "Art & collectibles": ["original art print", "handmade collectible"]
}

hunt_c1, hunt_c2, hunt_c3 = st.columns(3)
with hunt_c1:
    hunt_target = st.number_input("Unique products to collect", min_value=10, max_value=50, value=50, step=10)
with hunt_c2:
    hunt_days = st.selectbox("Listing age window", [7, 14, 30, 90], index=2, format_func=lambda x: f"Last {x} days")
with hunt_c3:
    hunt_market = st.selectbox("Marketplace query region", ["United States", "United Kingdom", "Canada", "Australia", "Global"], index=0, key="multi_hunt_market")

selected_hunt_niches = st.multiselect(
    "Niches to include",
    list(HUNT_SEEDS.keys()),
    default=list(HUNT_SEEDS.keys()),
    help="All niches are selected by default. You can narrow the hunt if needed."
)

st.caption("The API key is read from your existing ETSY_API_KEY setting. This feature does not call RankHero and does not spend RankHero credits.")
run_multi_hunt = st.button("🔎 Start product hunting", type="primary", key="run_multi_niche_hunt")


def _hunt_seo_suggestions(source_title, niche_name):
    import re
    import itertools
    clean = re.sub(r"[^A-Za-z0-9 ]+", " ", str(source_title or ""))
    words = [w.lower() for w in clean.split() if len(w) > 2]
    stop_words = {"the", "and", "for", "with", "from", "this", "that", "your", "new", "set", "item"}
    useful = [w for w in words if w not in stop_words]
    title = " ".join(str(source_title or "").split())[:140]
    candidates = []
    for n in (3, 2, 1):
        for i in range(max(0, len(useful) - n + 1)):
            phrase = " ".join(useful[i:i+n])
            if 2 <= len(phrase) <= 20 and phrase not in candidates:
                candidates.append(phrase)
    niche_tag = re.sub(r"[^a-z0-9 ]", "", niche_name.lower()).strip()
    if niche_tag and len(niche_tag) <= 20 and niche_tag not in candidates:
        candidates.append(niche_tag)
    tags = candidates[:13]
    return title, tags


if run_multi_hunt:
    if not api_key or not str(api_key).strip():
        st.error("ETSY_API_KEY missing. Is feature ke liye Etsy API key configured honi chahiye.")
    elif not selected_hunt_niches:
        st.warning("Kam az kam ek niche select karo.")
    else:
        import time
        from datetime import datetime, timezone
        from collections import Counter

        cutoff = datetime.now(timezone.utc).timestamp() - int(hunt_days) * 86400
        found = {}
        query_errors = []
        query_count = 0
        progress = st.progress(0, text="Preparing niche searches...")
        total_queries = sum(len(HUNT_SEEDS[n]) for n in selected_hunt_niches)

        for niche_index, niche_name in enumerate(selected_hunt_niches):
            for seed in HUNT_SEEDS[niche_name]:
                query_count += 1
                progress.progress(min(query_count / max(total_queries, 1), 1.0), text=f"Searching {niche_name}: {seed}")
                try:
                    resp = requests.get(
                        "https://api.etsy.com/v3/application/listings/active",
                        headers={"x-api-key": str(api_key).strip()},
                        params={"keywords": seed, "limit": 50, "sort_on": "score"},
                        timeout=25,
                    )
                    if not resp.ok:
                        query_errors.append(f"{seed}: HTTP {resp.status_code}")
                        time.sleep(0.26)
                        continue
                    payload = resp.json()
                    for item in payload.get("results", []):
                        listing_id = str(item.get("listing_id", "")).strip()
                        if not listing_id or listing_id in found:
                            continue
                        created = item.get("creation_timestamp")
                        try:
                            created_num = float(created)
                        except (TypeError, ValueError):
                            continue
                        if created_num < cutoff:
                            continue
                        price_obj = item.get("price") or {}
                        amount = price_obj.get("amount")
                        divisor = price_obj.get("divisor") or 100
                        try:
                            price_value = float(amount) / float(divisor) if amount is not None else None
                        except (TypeError, ValueError, ZeroDivisionError):
                            price_value = None
                        title = str(item.get("title") or "").strip()
                        if not title:
                            continue
                        age_days = max(0, int((datetime.now(timezone.utc).timestamp() - created_num) / 86400))
                        # Transparent screening heuristic; deliberately not called demand or sales score.
                        freshness_points = max(0, 50 - (age_days / max(int(hunt_days), 1)) * 50)
                        title_points = min(25, len(set(title.lower().split())) * 2)
                        price_points = 10 if price_value is not None else 0
                        distinct_points = min(15, len(set(title.lower().split())) * 1.5)
                        screening_score = round(freshness_points + title_points + price_points + distinct_points, 1)
                        suggested_title, suggested_tags = _hunt_seo_suggestions(title, niche_name)
                        found[listing_id] = {
                            "Niche": niche_name,
                            "Search phrase": seed,
                            "Original Etsy title": title,
                            "Suggested SEO title": suggested_title,
                            "Suggested tags (draft)": ", ".join(suggested_tags),
                            "Screening score (estimated)": screening_score,
                            "Listing age (days)": age_days,
                            "Listed price": price_value,
                            "Currency": price_obj.get("currency_code", ""),
                            "Listing ID": listing_id,
                            "Etsy URL": item.get("url", ""),
                            "Data created timestamp": created_num,
                            "Metric type": "Real listing fields + estimated screening score / SEO suggestions",
                        }
                except requests.RequestException as exc:
                    query_errors.append(f"{seed}: {exc}")
                except (ValueError, TypeError) as exc:
                    query_errors.append(f"{seed}: response parse error ({exc})")
                # Stay comfortably below the commonly encountered per-second request rate.
                time.sleep(0.26)
                if len(found) >= int(hunt_target):
                    break
            if len(found) >= int(hunt_target):
                break

        progress.empty()
        if found:
            hunt_df = pd.DataFrame(list(found.values()))
            hunt_df = hunt_df.sort_values("Screening score (estimated)", ascending=False).head(int(hunt_target)).reset_index(drop=True)
            st.session_state["multi_hunt_results"] = hunt_df
            st.session_state["multi_hunt_run_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            st.success(f"Hunting complete: {len(hunt_df)} unique Etsy listings found inside the {hunt_days}-day listing-age window.")
        else:
            st.session_state["multi_hunt_results"] = pd.DataFrame()
            st.warning("Is run mein selected time window ke andar koi verifiable listing nahi mili. API access, search phrases aur date fields check karo.")
        if query_errors:
            with st.expander(f"Search warnings ({len(query_errors)})"):
                st.write("\n".join(query_errors[:30]))

if isinstance(st.session_state.get("multi_hunt_results"), pd.DataFrame) and not st.session_state["multi_hunt_results"].empty:
    result_df = st.session_state["multi_hunt_results"]
    st.subheader("Product hunting results")
    st.caption(f"Last run: {st.session_state.get('multi_hunt_run_at', 'Not recorded')} · {len(result_df)} unique listings")
    st.dataframe(
        result_df.drop(columns=["Data created timestamp"], errors="ignore"),
        use_container_width=True,
        hide_index=True,
        column_config={"Etsy URL": st.column_config.LinkColumn("Open Etsy listing")},
    )
    st.download_button(
        "Download 50-product hunting report (CSV)",
        result_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="etsy_multi_niche_product_hunt.csv",
        mime="text/csv",
        key="download_multi_hunt_csv",
    )
    st.info("Score sirf recency/title/price completeness ka screening heuristic hai. Ye demand, sales, profit, search volume ya low competition ka proof nahi hai. SEO title aur tags draft suggestions hain; publish karne se pehle verify/edit karein.")
