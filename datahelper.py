import io
import sys
import re
import os
import matplotlib.pyplot as plt
from wordcloud import WordCloud 
from io import BytesIO
import base64
import pandas as pd
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_experimental.agents.agent_toolkits.pandas.base import (
    create_pandas_dataframe_agent,    
)
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
# gemini key
google_api_key = os.getenv("GOOGLE_API_KEY")
llm_gemini = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    google_api_key=google_api_key
)
selected_llm = llm_gemini

# summarize data
def summerize_csv(filename):
    df = pd.read_csv(filename, low_memory=False)
    pandas_agent = create_pandas_dataframe_agent(
        llm=selected_llm,
        df=df,
        verbose=False,
        allow_dangerous_code=True,
        agent_executor_kwargs={"handle_parsing_errors": "True"},
    )

    data_summary = {}
    data_summary["initial_data_sample"] = df.head()

    data_summary["column_descriptions"] = pandas_agent.run(
        f"Create a table in for dataset columns. Write a column name and column descriptions as a table format"
    )

    data_summary["missing_values"] = pandas_agent.run(
        "Is there any missing values in dataset and how many? Your response should be like 'There are X number of missing values in this dataset' replace missing values to 'X'"
    )

    data_summary["duplicate_values"] = pandas_agent.run(
        "Is there any duplicate values in dataset and how many? Your response should be like 'There are X number of duplicate values in this dataset' replace missing values to 'X'"
    )

    data_summary["essential_metrics"] = df.describe()
    def capture_df_info(df):
        buf = io.StringIO()
        df.info(buf=buf)
        info_str = buf.getvalue()

        # Keep only the header and rows with column info
        lines = info_str.splitlines()
        column_lines = []
        capture = False
        for line in lines:
            if re.match(r"\s*#\s+Column\s+.*", line):
                capture = True
            if capture:
                if re.match(r"\s*\d+\s+", line) or line.strip().startswith(("#", "---")):
                    column_lines.append(line)

        return "\n".join(column_lines)
    data_summary["data_types"] = capture_df_info(df)
   
    # Generate wordclouds for text columns
    wordcloud_images = {}
    text_columns = df.select_dtypes(include=["object"]).columns

    for col in text_columns:
        text_data = df[col].dropna().astype(str)
        if text_data.str.len().mean() > 3:  
            text = " ".join(text_data)
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

            # Save image as base64 to avoid filesystem dependency
            buffer = BytesIO()
            plt.figure(figsize=(8, 4))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.tight_layout()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            wordcloud_images[col] = image_base64
    data_summary["wordcloud_images"] = wordcloud_images
    return data_summary

# get dataframe
def get_dataframe(filename):

    df = pd.read_csv(filename, low_memory=False)
    return df
# analyze trend
def analyze_trend(filename, variable):
    df = pd.read_csv(filename, low_memory=False)
    pandas_agent = create_pandas_dataframe_agent(
        llm=selected_llm,
        df=df,
        verbose=True,
        agent_executor_kwargs={"handle_parsing_errors": "True"},
        allow_dangerous_code=True,
    )

    trend_response = pandas_agent.run(
        f"Interpret the trend of this shortly: {variable}. Do not reject the interpretation!. The rows of the dataset is historical. So you can do interpreting with looking the rows of dataset"
    )
    return trend_response
#ask question
def ask_question(filename, question):

    df = pd.read_csv(filename, low_memory=False)

    pandas_agent = create_pandas_dataframe_agent(
        llm=selected_llm,
        df=df,
        verbose=True,
        agent_executor_kwargs={"handle_parsing_errors": "True"},
        allow_dangerous_code=True,
    )
    AI_response = pandas_agent.run(question)

    return AI_response

