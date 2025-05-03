import streamlit as st
import pdfkit

import datahelper

# check
import base64
from io import BytesIO

def fig_to_base64(fig):
    """
    Converts a matplotlib/seaborn/plotly figure to a base64-encoded PNG image.
    """
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    return img_base64

# check

if "dataload" not in st.session_state:
    st.session_state.dataload = False


def activate_dataload():
    st.session_state.dataload = True


st.set_page_config(page_title="Data Analyzer 🤖", layout="wide")
st.image("./image/banner2.png", use_container_width=True)
st.title("🤖 LLM Agent Data analyzer ")
st.divider()


# Sidebar
st.sidebar.subheader("Load your data")
st.sidebar.divider()

loaded_file = st.sidebar.file_uploader("Chose your csv data", type="csv")
load_data_btn = st.sidebar.button(
    label="Load", on_click=activate_dataload, use_container_width=True
)

# Main

col_prework, col_dummy, col_interaction = st.columns([4, 1, 7])

if st.session_state.dataload:

    @st.cache_data
    def summerize():
        loaded_file.seek(0)
        data_summary = datahelper.summerize_csv(filename=loaded_file)
        return data_summary

    data_summary = summerize()

    with col_prework:
        st.info("Data summary")
        st.subheader("Sample of Data")
        st.write(data_summary["initial_data_sample"])
        st.divider()
        st.subheader("Features of Data")
        st.write(data_summary["column_descriptions"])
        st.divider()
        st.subheader("Missing values of Data")
        st.write(data_summary["missing_values"])
        st.divider()
        st.subheader("Duplicate values of Data")
        st.write(data_summary["duplicate_values"])
        st.divider()
        st.subheader("Summary Statistics of Data")
        st.write(data_summary["essential_metrics"])
        # check
        st.subheader("Data Types Summary")
        st.markdown("This section shows the data types and non-null counts for each column.")
        st.text(data_summary["data_types"])  # Display the captured info





        st.divider()
        st.subheader("WordClouds for Text Columns")

        wordcloud_images = data_summary.get("wordcloud_images", {})

        if wordcloud_images:
            for col_name, img_base64 in wordcloud_images.items():
                st.markdown(f"**WordCloud for column: `{col_name}`**")
                st.image(f"data:image/png;base64,{img_base64}", use_container_width=True)
        else:
            st.warning("No suitable text columns found for WordCloud generation.")


    with col_dummy:
        st.empty()

    with col_interaction:
        st.info("Interaction")
        variable = st.text_input(label="Which feature do you want to analyze?")
        exemine_btn = st.button("Examine")
        st.divider()

        @st.cache_data
        def explore_variable(data_file, variable):
            data_file.seek(0)
            dataframe = datahelper.get_dataframe(filename=data_file)
            st.bar_chart(data=dataframe, y=[variable])
            st.divider()

            data_file.seek(0)
            trend_response = datahelper.analyze_trend(
                filename=loaded_file, variable=variable
            )
            st.success(trend_response)
            return

        if variable or exemine_btn:
            explore_variable(data_file=loaded_file, variable=variable)

        free_question = st.text_input(label="What do you want to know about dataset?")
        ask_btn = st.button(label="Ask Question")
        st.divider()

        @st.cache_data
        def answer_question(data_file, free_question):
            data_file.seek(0)
            AI_response = datahelper.ask_question(
                filename=data_file, question=free_question
            )
            st.success(AI_response)
            return

        if free_question or ask_btn:
            answer_question(data_file=loaded_file, free_question=free_question)

        # Correlation Heatmap
        st.subheader("Correlation Heatmap")

        # Reload dataframe
        loaded_file.seek(0)
        df = datahelper.get_dataframe(filename=loaded_file)

        # Plot heatmap
        import seaborn as sns
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)


                # Path where wkhtmltopdf is installed
        path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
               
          


        def generate_html_report(data_summary, correlation_fig_base64, wordcloud_images):
            wordcloud_html = ""

            if wordcloud_images:
                for col_name, img_base64 in wordcloud_images.items():
                    wordcloud_html += f"""
                    <div class="section">
                        <h3>WordCloud for Column: <code>{col_name}</code></h3>
                        <img src="data:image/png;base64,{img_base64}" alt="WordCloud for {col_name}" />
                    </div>
                    """
            else:
                wordcloud_html = "<p>No suitable text columns found for WordCloud generation.</p>"

            html_content = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; }}
                        h1, h2, h3 {{ color: #4CAF50; }}
                        .section {{ margin-bottom: 30px; }}
                        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
                        img {{ width: 100%; max-width: 600px; }}
                        code {{ background-color: #f2f2f2; padding: 2px 4px; border-radius: 4px; }}
                    </style>
                </head>
                <body>
                    <h1>Data Analysis Report</h1>

                    <div class="section">
                        <h2>Sample Data</h2>
                        <pre>{str(data_summary['initial_data_sample'])}</pre>
                    </div>

                    <div class="section">
                        <h2>Column Descriptions</h2>
                        <pre>{str(data_summary['column_descriptions'])}</pre>
                    </div>

                    <div class="section">
                        <h2>Missing Values</h2>
                        <pre>{str(data_summary['missing_values'])}</pre>
                    </div>

                    <div class="section">
                        <h2>Duplicate Values</h2>
                        <pre>{str(data_summary['duplicate_values'])}</pre>
                    </div>

                    <div class="section">
                        <h2>Summary Statistics</h2>
                        <pre>{str(data_summary['essential_metrics'])}</pre>
                    </div>

                    <div class="section">
                        <h2> Data Types</h2>
                        <pre>{str(data_summary['data_types'])}</pre>
                    </div>

                    <div class="section">
                        <h2> WordClouds for Text Columns</h2>
                        {wordcloud_html}
                    </div>

                    <div class="section">
                        <h2>Correlation Heatmap</h2>
                        <img src="data:image/png;base64,{correlation_fig_base64}" alt="Correlation Heatmap"/>
                    </div>
                </body>
            </html>
            """
            return html_content



            
    correlation_fig_base64 = fig_to_base64(fig)
    wordcloud_images = data_summary.get("wordcloud_images", {})

    # Generate HTML
    html_content = generate_html_report(data_summary, correlation_fig_base64, wordcloud_images)

    # Convert HTML to PDF
    pdf = pdfkit.from_string(html_content, configuration=config)

    # Streamlit download button
    st.download_button(
        label=" Download Full PDF Report",
        data=pdf,
        file_name="data_analysis_report.pdf",
        mime="application/pdf",
    )
