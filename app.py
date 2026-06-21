"""
SIERRA LEONE HEALTH EMERGENCIES DASHBOARD
===========================================
MSBA382 - Healthcare Analytics Individual Project
A decade of health emergencies in Sierra Leone (2014-2024):
Ebola, COVID-19, and the everyday disease burden.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ============================================================
# PAGE CONFIG (must be first Streamlit command)
# ============================================================
st.set_page_config(
    page_title="Sierra Leone Health Emergencies Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# PASSWORD PROTECTION
# ============================================================
PASSWORD = "sierraleone2026"

def check_password():
    """Returns True if the user entered the correct password."""

    def password_entered():
        if st.session_state["password"] == PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First visit - show password input
        st.markdown("## 🏥 Sierra Leone Health Emergencies Dashboard")
        st.text_input(
            "Enter password to access the dashboard",
            type="password",
            on_change=password_entered,
            key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Wrong password entered
        st.markdown("## 🏥 Sierra Leone Health Emergencies Dashboard")
        st.text_input(
            "Enter password to access the dashboard",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.error("😕 Incorrect password")
        return False
    else:
        # Correct password
        return True


if not check_password():
    st.stop()


# ============================================================
# LOAD DATA (cached so it only loads once per session)
# ============================================================
@st.cache_data
def load_data():
    covid = pd.read_csv("data/covid_sierra_leone_clean.csv", parse_dates=["date"])
    ebola = pd.read_csv("data/ebola_sierra_leone_clean.csv", parse_dates=["report_date"])
    ebola_subtypes = pd.read_csv("data/ebola_sierra_leone_subtypes.csv")
    causes = pd.read_csv("data/causes_of_death_sierra_leone.csv")
    return covid, ebola, ebola_subtypes, causes

covid_sl_clean, ebola_sl_all, ebola_sl_subtypes, top15 = load_data()

# Category mapping for causes of death (recreated here for the pie chart)
category_map = {
    'Malaria': 'Infectious Disease',
    'Lower respiratory infections': 'Infectious Disease',
    'Diarrhoeal diseases': 'Infectious Disease',
    'Tuberculosis': 'Infectious Disease',
    'HIV/AIDS': 'Infectious Disease',
    'Meningitis': 'Infectious Disease',
    'Stroke': 'Non-Communicable Disease',
    'Ischaemic heart disease': 'Non-Communicable Disease',
    'Cirrhosis of the liver': 'Non-Communicable Disease',
    'Diabetes mellitus': 'Non-Communicable Disease',
    'Preterm birth complications': 'Maternal & Child Health',
    'Birth asphyxia and birth trauma': 'Maternal & Child Health',
    'Protein-energy malnutrition': 'Maternal & Child Health',
    'Congenital anomalies': 'Maternal & Child Health',
    'Road injury': 'Injury'
}
top15['Category'] = top15['Cause'].map(category_map)
category_summary = top15.groupby('Category')['Death_Rate_per_100k'].sum().reset_index()
category_summary = category_summary.sort_values('Death_Rate_per_100k', ascending=False)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
st.sidebar.title("🏥 Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Overview", "Ebola (2014-2016)", "COVID-19 (2020-2024)",
     "Everyday Disease Burden", "Compare Emergencies"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**About this dashboard**")
st.sidebar.markdown(
    "Built for MSBA382 Healthcare Analytics. "
    "Data sourced from WHO, Our World in Data, and WHO Global Health Estimates."
)


# ============================================================
# PAGE: OVERVIEW
# ============================================================
if page == "Overview":
    st.title("Sierra Leone Health Emergencies Dashboard")
    st.markdown("### A decade of crisis and resilience (2014-2024)")
    st.markdown(
        "This dashboard analyzes Sierra Leone's two major health emergencies "
        "of the past decade — the 2014-2016 Ebola epidemic and the COVID-19 "
        "pandemic — and places them in context against the country's "
        "everyday infectious disease burden."
    )

    st.markdown("---")

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)

    ebola_total_cases = int(ebola_sl_all['Total cases'].max())
    ebola_total_deaths = int(ebola_sl_all['Total deaths'].max())
    covid_total_cases = int(covid_sl_clean['total_cases'].max())
    covid_total_deaths = int(covid_sl_clean['total_deaths'].max())

    with col1:
        st.metric("Ebola Total Cases", f"{ebola_total_cases:,}")
    with col2:
        st.metric("Ebola Total Deaths", f"{ebola_total_deaths:,}",
                   delta=f"{ebola_total_deaths/ebola_total_cases*100:.1f}% CFR",
                   delta_color="off")
    with col3:
        st.metric("COVID-19 Total Cases", f"{covid_total_cases:,}")
    with col4:
        st.metric("COVID-19 Total Deaths", f"{covid_total_deaths:,}",
                   delta=f"{covid_total_deaths/covid_total_cases*100:.1f}% CFR",
                   delta_color="off")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Leading cause of death (2021)")
        top_cause = top15.iloc[0]
        st.markdown(f"**{top_cause['Cause']}** — {top_cause['Death_Rate_per_100k']:.1f} per 100,000")
        st.caption(
            "Malaria remains Sierra Leone's leading cause of death, "
            "exceeding the peak annual toll of either Ebola or COVID-19."
        )

    with col2:
        st.subheader("Disease burden mix")
        fig_mini_pie = px.pie(
            category_summary, values='Death_Rate_per_100k', names='Category',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_mini_pie.update_layout(height=250, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_mini_pie, use_container_width=True)

    st.markdown("---")
    st.markdown(
        "**Navigate using the sidebar** to explore each emergency in detail, "
        "see the everyday disease burden, and compare the two crises side by side."
    )


# ============================================================
# PAGE: EBOLA
# ============================================================
elif page == "Ebola (2014-2016)":
    st.title("Ebola Virus Disease Outbreak (2014-2016)")
    st.markdown(
        "Sierra Leone was one of three West African countries at the center "
        "of the largest Ebola outbreak in history."
    )

    # KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Cases", f"{int(ebola_sl_all['Total cases'].max()):,}")
    with col2:
        st.metric("Total Deaths", f"{int(ebola_sl_all['Total deaths'].max()):,}")
    with col3:
        final_cfr = ebola_sl_all['CFR_percent'].iloc[-1]
        st.metric("Final Case Fatality Rate", f"{final_cfr:.1f}%")

    st.markdown("---")

    # Cases & Deaths chart
    st.subheader("Cumulative cases and deaths over time")
    fig_ebola = go.Figure()
    fig_ebola.add_trace(go.Scatter(
        x=ebola_sl_all['report_date'], y=ebola_sl_all['Total cases'],
        mode='lines', name='Total Cases',
        line=dict(color='darkred', width=3),
        fill='tozeroy', fillcolor='rgba(139,0,0,0.1)'
    ))
    fig_ebola.add_trace(go.Scatter(
        x=ebola_sl_all['report_date'], y=ebola_sl_all['Total deaths'],
        mode='lines', name='Total Deaths',
        line=dict(color='black', width=3, dash='dash')
    ))
    fig_ebola.update_layout(
        xaxis_title='Report Date', yaxis_title='Cumulative Count',
        hovermode='x unified', template='plotly_white', height=450
    )
    st.plotly_chart(fig_ebola, use_container_width=True)

    st.caption(
        "Note: Two minor downward revisions in WHO's original reporting "
        "(Nov 2014 and Aug 2015, reflecting case reclassification) were "
        "smoothed using cumulative maximum methodology for clean trend "
        "visualization."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Case fatality rate over time")
        fig_cfr = px.line(
            ebola_sl_all, x='report_date', y='CFR_percent',
            labels={'report_date': 'Date', 'CFR_percent': 'CFR (%)'}
        )
        fig_cfr.update_traces(line=dict(color='darkorange', width=3))
        fig_cfr.update_layout(template='plotly_white', height=400)
        st.plotly_chart(fig_cfr, use_container_width=True)
        st.caption(
            "CFR started near 41% in the earliest, most chaotic phase, "
            "dropped as case detection improved, then rose again during "
            "the peak caseload of spring 2015 before declining as "
            "treatment capacity expanded."
        )

    with col2:
        st.subheader("Cases by classification (final report)")
        fig_subtypes = px.bar(
            ebola_sl_subtypes, x='Case def.', y='Total cases',
            color='Case def.',
            color_discrete_map={'Confirmed': 'darkred', 'Probable': 'orange', 'Suspected': 'gold'},
            text='Total cases'
        )
        fig_subtypes.update_traces(textposition='outside')
        fig_subtypes.update_layout(template='plotly_white', height=400, showlegend=False)
        st.plotly_chart(fig_subtypes, use_container_width=True)
        st.caption(
            "Confirmed cases (lab-verified) made up the majority of the "
            "total caseload, with suspected cases representing a "
            "significant secondary category."
        )


# ============================================================
# PAGE: COVID-19
# ============================================================
elif page == "COVID-19 (2020-2024)":
    st.title("COVID-19 Pandemic (2020-2024)")
    st.markdown(
        "Sierra Leone experienced four distinct waves of COVID-19 infection "
        "between 2020 and 2024."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Cases", f"{int(covid_sl_clean['total_cases'].max()):,}")
    with col2:
        st.metric("Total Deaths", f"{int(covid_sl_clean['total_deaths'].max()):,}")
    with col3:
        final_cfr_covid = (covid_sl_clean['total_deaths'].max() /
                            covid_sl_clean['total_cases'].max() * 100)
        st.metric("Overall Case Fatality Rate", f"{final_cfr_covid:.1f}%")

    st.markdown("---")

    # Date range filter
    min_date = covid_sl_clean['date'].min()
    max_date = covid_sl_clean['date'].max()
    date_range = st.slider(
        "Select date range",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=(min_date.to_pydatetime(), max_date.to_pydatetime())
    )

    filtered_covid = covid_sl_clean[
        (covid_sl_clean['date'] >= date_range[0]) &
        (covid_sl_clean['date'] <= date_range[1])
    ]

    st.subheader("Daily new cases (7-day smoothed) — shows pandemic waves")
    fig_waves = px.area(
        filtered_covid, x='date', y='new_cases_smoothed',
        labels={'date': 'Date', 'new_cases_smoothed': 'New Cases (smoothed)'}
    )
    fig_waves.update_traces(line=dict(color='steelblue', width=2),
                              fillcolor='rgba(70,130,180,0.3)')
    fig_waves.update_layout(template='plotly_white', height=450)
    st.plotly_chart(fig_waves, use_container_width=True)
    st.caption(
        "Four distinct waves are visible, with the largest occurring in "
        "mid-2021, consistent with the global Delta variant wave."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Cumulative cases and deaths")
        fig_covid = go.Figure()
        fig_covid.add_trace(go.Scatter(
            x=filtered_covid['date'], y=filtered_covid['total_cases'],
            mode='lines', name='Total Cases',
            line=dict(color='steelblue', width=3),
            fill='tozeroy', fillcolor='rgba(70,130,180,0.1)'
        ))
        fig_covid.add_trace(go.Scatter(
            x=filtered_covid['date'], y=filtered_covid['total_deaths'],
            mode='lines', name='Total Deaths',
            line=dict(color='black', width=3, dash='dash'),
            yaxis='y2'
        ))
        fig_covid.update_layout(
            yaxis=dict(title='Total Cases'),
            yaxis2=dict(title='Total Deaths', overlaying='y', side='right'),
            hovermode='x unified', template='plotly_white', height=400
        )
        st.plotly_chart(fig_covid, use_container_width=True)

    with col2:
        st.subheader("Vaccination rollout")
        covid_vax_only = covid_sl_clean[
            covid_sl_clean['people_fully_vaccinated_per_hundred'].notnull()
        ]
        fig_vax = px.line(
            covid_vax_only, x='date', y='people_fully_vaccinated_per_hundred',
            labels={'date': 'Date', 'people_fully_vaccinated_per_hundred': '% Fully Vaccinated'},
            markers=True
        )
        fig_vax.update_traces(line=dict(color='seagreen', width=3), marker=dict(size=5))
        fig_vax.update_layout(template='plotly_white', height=400)
        st.plotly_chart(fig_vax, use_container_width=True)
        st.caption(
            "Vaccination rollout began around April 2021, with slow initial "
            "uptake followed by accelerating coverage through 2022-2023."
        )


# ============================================================
# PAGE: EVERYDAY DISEASE BURDEN
# ============================================================
elif page == "Everyday Disease Burden":
    st.title("Everyday Disease Burden (2021)")
    st.markdown(
        "Beyond emergency outbreaks, Sierra Leone faces a sustained burden "
        "of infectious and chronic disease. This data provides essential "
        "context for healthcare resource allocation."
    )

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("Top 15 causes of death")
        fig_causes = px.bar(
            top15.sort_values('Death_Rate_per_100k', ascending=True),
            x='Death_Rate_per_100k', y='Cause', orientation='h',
            labels={'Death_Rate_per_100k': 'Death Rate (per 100,000)', 'Cause': ''},
            text='Death_Rate_per_100k', color='Death_Rate_per_100k',
            color_continuous_scale='Reds'
        )
        fig_causes.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_causes.update_layout(template='plotly_white', height=600, coloraxis_showscale=False)
        st.plotly_chart(fig_causes, use_container_width=True)

    with col2:
        st.subheader("Burden by category")
        fig_category = px.pie(
            category_summary, values='Death_Rate_per_100k', names='Category',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_category.update_traces(textposition='inside', textinfo='percent+label')
        fig_category.update_layout(template='plotly_white', height=500)
        st.plotly_chart(fig_category, use_container_width=True)

        st.markdown(
            "**Key insight:** Infectious disease accounts for over half "
            "of Sierra Leone's top-15 death burden — more than double the "
            "share of non-communicable disease. This underscores that "
            "routine infectious disease control delivers more lives saved "
            "per dollar than emergency-only response capacity."
        )

    st.caption(
        "Source: WHO Global Health Estimates (GHE), 2021 — the most recent "
        "year available for Sierra Leone at time of analysis."
    )


# ============================================================
# PAGE: COMPARE EMERGENCIES
# ============================================================
elif page == "Compare Emergencies":
    st.title("Comparing Ebola and COVID-19")
    st.markdown(
        "A side-by-side comparison of Sierra Leone's two major health "
        "emergencies of the past decade."
    )

    ebola_cases = int(ebola_sl_all['Total cases'].max())
    ebola_deaths = int(ebola_sl_all['Total deaths'].max())
    ebola_cfr = ebola_sl_all['CFR_percent'].iloc[-1]
    ebola_duration_days = (ebola_sl_all['report_date'].max() -
                            ebola_sl_all['report_date'].min()).days

    covid_cases = int(covid_sl_clean['total_cases'].max())
    covid_deaths = int(covid_sl_clean['total_deaths'].max())
    covid_cfr = covid_deaths / covid_cases * 100
    covid_duration_days = (covid_sl_clean['date'].max() -
                            covid_sl_clean['date'].min()).days

    comparison_df = pd.DataFrame({
        'Metric': ['Total Cases', 'Total Deaths', 'Case Fatality Rate (%)', 'Duration (days)'],
        'Ebola (2014-2016)': [ebola_cases, ebola_deaths, f"{ebola_cfr:.1f}%", ebola_duration_days],
        'COVID-19 (2020-2024)': [covid_cases, covid_deaths, f"{covid_cfr:.1f}%", covid_duration_days]
    })

    st.table(comparison_df.set_index('Metric'))

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Ebola CFR", f"{ebola_cfr:.1f}%",
                   help="Of those infected with Ebola, this percentage died")
    with col2:
        st.metric("COVID-19 CFR", f"{covid_cfr:.1f}%",
                   help="Of those infected with COVID-19, this percentage died")

    st.markdown(
        f"**Key finding:** While COVID-19 produced far more confirmed cases "
        f"({covid_cases:,} vs {ebola_cases:,}), Ebola's case fatality rate "
        f"of {ebola_cfr:.1f}% was dramatically higher than COVID-19's "
        f"{covid_cfr:.1f}%, reflecting Ebola's severity as a disease "
        f"despite its smaller total case count. This has direct implications "
        f"for emergency preparedness: Sierra Leone's health system must "
        f"prepare for both high-volume, lower-severity emergencies (like "
        f"COVID-19) and lower-volume, high-severity emergencies (like Ebola) "
        f"with very different resource and containment strategies."
    )

    st.markdown("---")
    st.subheader("Normalized timeline comparison")
    st.markdown(
        "Both outbreaks shown from their respective start dates, "
        "normalized to days since outbreak began."
    )

    ebola_norm = ebola_sl_all.copy()
    ebola_norm['days_since_start'] = (
        ebola_norm['report_date'] - ebola_norm['report_date'].min()
    ).dt.days
    ebola_norm['outbreak'] = 'Ebola'
    ebola_norm = ebola_norm.rename(columns={'Total cases': 'cases'})

    covid_norm = covid_sl_clean.copy()
    covid_norm['days_since_start'] = (
        covid_norm['date'] - covid_norm['date'].min()
    ).dt.days
    covid_norm['outbreak'] = 'COVID-19'
    covid_norm = covid_norm.rename(columns={'total_cases': 'cases'})

    combined = pd.concat([
        ebola_norm[['days_since_start', 'cases', 'outbreak']],
        covid_norm[['days_since_start', 'cases', 'outbreak']]
    ])

    fig_compare = px.line(
        combined, x='days_since_start', y='cases', color='outbreak',
        labels={'days_since_start': 'Days since outbreak start', 'cases': 'Cumulative cases'},
        color_discrete_map={'Ebola': 'darkred', 'COVID-19': 'steelblue'}
    )
    fig_compare.update_layout(template='plotly_white', height=450, hovermode='x unified')
    st.plotly_chart(fig_compare, use_container_width=True)
