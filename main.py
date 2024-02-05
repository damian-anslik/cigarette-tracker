from supabase.client import Client
from functools import lru_cache
import streamlit as st
import pandas as pd


@lru_cache
def get_cigarettes_table():
    db_client = Client(
        supabase_url=st.secrets["SUPABASE_URL"],
        supabase_key=st.secrets["SUPABASE_KEY"],
    )
    return db_client.table("cigarettes")


def track_cigarette() -> dict:
    insert_response = get_cigarettes_table().insert({}).execute()
    return insert_response.data[0]


def get_cigarette_data() -> dict:
    fetch_response = get_cigarettes_table().select("*").execute()
    return fetch_response.data


def prepare_usage_data(usage_data: dict) -> pd.DataFrame:
    if not usage_data:
        return
    usage_df = pd.DataFrame(usage_data)
    datetime_format = "%Y-%m-%dT%H:%M:%S.%f%z"
    usage_df["timestamp"] = pd.to_datetime(
        usage_df["timestamp"],
        format=datetime_format,
    )
    # Aggregate the data by date and count the number of cigarettes smoked
    usage_df["date"] = usage_df["timestamp"].dt.date
    usage_df = usage_df.groupby("date").size().reset_index(name="count")
    usage_df = usage_df.rename(columns={"date": "Date", "count": "Cigarettes Smoked"})
    usage_df = usage_df.sort_values("Date", ascending=True)
    usage_df = usage_df.set_index("Date")
    return usage_df


def main():
    st.title("Cigarette Tracker")
    if not st.session_state.get("data"):
        st.session_state["data"] = get_cigarette_data()
    prepared_data = prepare_usage_data(st.session_state["data"])
    if prepared_data is None:
        st.success("You haven't smoked any cigarettes yet.")
    else:
        NUM_DAYS_TO_SHOW = 14
        st.bar_chart(
            data=prepared_data.tail(NUM_DAYS_TO_SHOW),
            use_container_width=True,
        )
    track_button = st.button("🚬 Track", use_container_width=True)
    if track_button:
        tracked_cigarette_data = track_cigarette()
        st.session_state["data"].append(tracked_cigarette_data)
        st.rerun()


if __name__ == "__main__":
    main()
