import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Netflix Data Explorer", page_icon="🎬", layout="wide")


@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/netflix_titles.csv")
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier: {e}")
        return None


st.title("🎬 Netflix Data Explorer")
st.markdown("Exploration et analyse des données Netflix (films et séries TV)")

with st.spinner("Chargement des données en cours..."):
    df = load_data()

if df is not None:
    st.subheader("Aperçu des données")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Aperçu général",
            "Visualisations",
            "Recherche avancée",
            "Analyses temporelles",
        ]
    )

    with tab1:
        col1, col2 = st.columns([1, 1])

        with col1:
            total_items = len(df)
            movies_count = df[df["type"] == "Movie"].shape[0]
            tvshows_count = df[df["type"] == "TV Show"].shape[0]

            fig = px.pie(
                names=["Films", "Séries TV"],
                values=[movies_count, tvshows_count],
                title="Répartition Films / Séries TV",
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.4,
            )
            fig.update_traces(textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Statistiques générales")
            st.write(f"**Nombre total d'éléments:** {total_items}")
            st.write(f"**Nombre de films:** {movies_count}")
            st.write(f"**Nombre de séries TV:** {tvshows_count}")

            countries = []
            for c in df["country"].dropna().str.split(", "):
                if isinstance(c, list):
                    countries.extend(c)
                else:
                    countries.append(c)
            unique_countries = len(set(countries))
            st.write(f"**Nombre de pays d'origine:** {unique_countries}")

            min_year = df["release_year"].min()
            max_year = df["release_year"].max()
            st.write(f"**Période couverte:** {min_year} - {max_year}")

        with st.expander("Afficher un échantillon des données"):
            st.dataframe(df.head(10))

    with tab2:
        st.subheader("Visualisations")

        viz_col1, viz_col2 = st.columns([1, 1])

        with viz_col1:
            st.subheader("Top 10 des pays producteurs")

            all_countries = []
            for countries in df["country"].dropna():
                if isinstance(countries, str):
                    all_countries.extend([c.strip() for c in countries.split(",")])

            country_counts = pd.Series(all_countries).value_counts().reset_index()
            country_counts.columns = ["country", "count"]
            country_counts = country_counts.head(10)

            fig = px.bar(
                country_counts,
                x="count",
                y="country",
                orientation="h",
                title="Top 10 des pays producteurs",
                color="count",
                color_continuous_scale="Viridis",
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

        with viz_col2:
            st.subheader("Distribution des années de sortie")

            year_counts = df["release_year"].value_counts().reset_index()
            year_counts.columns = ["release_year", "count"]
            year_counts = year_counts.sort_values("release_year")

            fig = px.line(
                year_counts,
                x="release_year",
                y="count",
                title="Évolution du nombre de sorties par année",
                markers=True,
            )
            st.plotly_chart(fig, use_container_width=True)

        viz_col3, viz_col4 = st.columns([1, 1])

        with viz_col3:
            st.subheader("Distribution des évaluations")

            rating_counts = df["rating"].value_counts().reset_index()
            rating_counts.columns = ["rating", "count"]
            rating_counts = rating_counts.sort_values("count", ascending=False)

            fig = px.bar(
                rating_counts,
                x="rating",
                y="count",
                title="Répartition des évaluations",
                color="count",
                color_continuous_scale="Viridis",
            )
            st.plotly_chart(fig, use_container_width=True)

        with viz_col4:
            st.subheader("Catégories les plus fréquentes")

            all_genres = []
            for genres in df["listed_in"].dropna():
                if isinstance(genres, str):
                    all_genres.extend([g.strip() for g in genres.split(",")])

            genre_counts = pd.Series(all_genres).value_counts().reset_index()
            genre_counts.columns = ["genre", "count"]
            genre_counts = genre_counts.head(10)

            fig = px.pie(
                genre_counts,
                names="genre",
                values="count",
                title="Top 10 des catégories",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.4,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Recherche avancée")

        search_col1, search_col2, search_col3 = st.columns([1, 1, 1])

        with search_col1:
            search_type = st.selectbox("Type", ["Tous", "Movie", "TV Show"])

        with search_col2:
            years = ["Toutes"] + sorted(
                df["release_year"].unique().tolist(), reverse=True
            )
            search_year = st.selectbox("Année de sortie", years)

        with search_col3:
            all_categories = []
            for categories in df["listed_in"].dropna():
                if isinstance(categories, str):
                    all_categories.extend([c.strip() for c in categories.split(",")])
            unique_categories = ["Toutes"] + sorted(list(set(all_categories)))
            search_category = st.selectbox("Catégorie", unique_categories)

        search_text = st.text_input(
            "Rechercher par titre, directeur, acteurs ou description:", ""
        )

        filtered_df = df.copy()

        if search_type != "Tous":
            filtered_df = filtered_df[filtered_df["type"] == search_type]

        if search_year != "Toutes":
            filtered_df = filtered_df[filtered_df["release_year"] == search_year]

        if search_category != "Toutes":
            filtered_df = filtered_df[
                filtered_df["listed_in"].str.contains(search_category, na=False)
            ]

        if search_text:
            text_columns = ["title", "director", "cast", "description"]
            text_filter = filtered_df[text_columns].apply(
                lambda row: row.astype(str).str.contains(search_text, case=False).any(),
                axis=1,
            )
            filtered_df = filtered_df[text_filter]

        st.subheader("Résultats de la recherche")
        st.write(f"{len(filtered_df)} élément(s) trouvé(s)")

        if len(filtered_df) > 0:
            display_df = filtered_df[
                [
                    "show_id",
                    "type",
                    "title",
                    "director",
                    "country",
                    "release_year",
                    "rating",
                    "duration",
                ]
            ]
            st.dataframe(display_df, use_container_width=True)

            selected_show_id = st.selectbox(
                "Sélectionner un élément pour voir les détails:",
                display_df["show_id"].tolist(),
            )

            if selected_show_id:
                show_details = filtered_df[
                    filtered_df["show_id"] == selected_show_id
                ].iloc[0]

                st.markdown("### Détails")
                st.markdown(f"**Titre:** {show_details['title']}")
                st.markdown(f"**Type:** {show_details['type']}")

                if pd.notna(show_details["director"]):
                    st.markdown(f"**Réalisateur:** {show_details['director']}")

                if pd.notna(show_details["cast"]):
                    st.markdown(f"**Casting:** {show_details['cast']}")

                if pd.notna(show_details["country"]):
                    st.markdown(f"**Pays:** {show_details['country']}")

                st.markdown(f"**Année de sortie:** {show_details['release_year']}")

                if pd.notna(show_details["rating"]):
                    st.markdown(f"**Évaluation:** {show_details['rating']}")

                if pd.notna(show_details["duration"]):
                    st.markdown(f"**Durée:** {show_details['duration']}")

                if pd.notna(show_details["listed_in"]):
                    st.markdown(f"**Catégories:** {show_details['listed_in']}")

                if pd.notna(show_details["description"]):
                    st.markdown(f"**Description:** {show_details['description']}")

    with tab4:
        st.subheader("Analyses temporelles")

        df_year_type = (
            df.groupby(["release_year", "type"]).size().reset_index(name="count")
        )

        fig = px.line(
            df_year_type,
            x="release_year",
            y="count",
            color="type",
            title="Évolution des sorties par année et par type",
            markers=True,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Évolution des catégories populaires")

        time_col1, time_col2 = st.columns([1, 1])

        with time_col1:
            start_year = st.selectbox(
                "Année de début", sorted(df["release_year"].unique().tolist()), index=0
            )

        with time_col2:
            end_year = st.selectbox(
                "Année de fin",
                sorted(df["release_year"].unique().tolist()),
                index=len(df["release_year"].unique()) - 1,
            )

        if start_year <= end_year:
            period_df = df[
                (df["release_year"] >= start_year) & (df["release_year"] <= end_year)
            ]

            period_genres = []
            for genres in period_df["listed_in"].dropna():
                if isinstance(genres, str):
                    period_genres.extend([g.strip() for g in genres.split(",")])

            period_genre_counts = (
                pd.Series(period_genres).value_counts().head(10).reset_index()
            )
            period_genre_counts.columns = ["genre", "count"]

            fig = px.bar(
                period_genre_counts,
                x="genre",
                y="count",
                title=f"Top 10 des catégories ({start_year}-{end_year})",
                color="count",
                color_continuous_scale="Viridis",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("L'année de début doit être inférieure ou égale à l'année de fin")

        st.subheader("Évolution de la durée des films")

        movies_df = df[df["type"] == "Movie"].copy()

        movies_df["duration_minutes"] = (
            movies_df["duration"].str.extract(r"(\d+)").astype(float)
        )

        duration_by_year = (
            movies_df.groupby("release_year")["duration_minutes"].mean().reset_index()
        )

        fig = px.line(
            duration_by_year,
            x="release_year",
            y="duration_minutes",
            title="Durée moyenne des films par année",
            markers=True,
        )
        fig.update_layout(yaxis_title="Durée moyenne (minutes)")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.error(
        "Impossible de charger les données. Veuillez vérifier que le fichier CSV est présent et correctement formaté."
    )

st.markdown("---")
st.markdown("Développé avec Streamlit • Netflix Data Explorer")
