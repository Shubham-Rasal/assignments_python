import time  # to simulate a real time data, time loop

import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development
import matplotlib.pyplot as plt
import pandas as pd
from pybloom_live import BloomFilter
from kafka import KafkaConsumer
# Use a pipeline as a high-level helper
from transformers import pipeline
pipe = pipeline("text-classification", model="IMSyPP/hate_speech_en")


df_speech = pd.read_csv('hurtlex_EN.tsv', sep='\t')

grouped = df_speech.groupby('category')
grouped.head()

# Create a Bloom filter with an appropriate size and false positive rate
bloom_filter = BloomFilter(capacity=df_speech.shape[0], error_rate=0.001)

# Add hate speech terms to the Bloom filter
hate_speech_terms = df_speech["lemma"]
for term in hate_speech_terms:
    bloom_filter.add(term)


def detect_hate_speech(text)-> bool:
    tokens = text.split()
    for token in tokens:
        if token in bloom_filter:
            return True
    return False

# Test the hate speech detection function
text = "I will love you"
if detect_hate_speech(text):
    print("Hate speech detected!")
else:
    print("No hate speech detected.")

def decode_kafka_item(message):
    print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value))
    return message.value.decode('utf-8')


st.set_page_config(
    page_title="Real-Time Hate Speech Detection Dashboard",
    page_icon="✅",
    layout="wide",
    )
# dashboard title
st.title("Real-Time / Live Data Youtube Chat Stream Dashboard")


# [{'label': 'LABEL_2', 'score': 0.6886570453643799}]
#make a mapping
# 0 - acceptable
# 1 - inappropriate
# 2 - offensive
# 3 - violent
# LABEL_0
label_to_category = {
    "LABEL_0": "acceptable",
    "LABEL_1": "inappropriate",
    "LABEL_2": "offensive",
    "LABEL_3": "violent"
}




def read_from_kafka(topic_name):
    consumer = KafkaConsumer(
        topic_name,
        auto_offset_reset='latest',
        bootstrap_servers=['127.0.0.1:29092'],
        consumer_timeout_ms=10000
    )
    # Continuously listen for messages
    placeholder = st.empty()

    hate_speech_count = 0

    acceptable_count = 0
    inappropriate_count = 0
    offensive_count = 0
    violent_count = 0

    avg_bloom_execution_time = 0
    avg_model_execution_time = 0

    bloom_execution_total_time = 0
    model_execution_total_time = 0

    
  

    plt.style.use('dark_background') 

    fig, ax = plt.subplots()

    x = np.array([time.time()])
    y = np.array([0])
    line, = ax.plot(x, y)


    ax.set_xlim(x[0], x[0] + 600)
    ax.set_ylim(0, 10)

    the_plot = st.pyplot(plt)

    line.set_xdata(x)
    line.set_ydata(y)

    #put titles
    plt.title('Hate Speech Count Over Time')
    plt.xlabel('Time')
    plt.ylabel('Hate Speech Count')

    bloom_count = 0
    model_count = 0


    #diffeent line and and fig and axis for model and bloom
    x_model = np.array([time.time()])
    y_model = np.array([0])
    line_model, = ax.plot(x_model, y_model)

    ax.set_xlim(x_model[0], x_model[0] + 600)
    ax.set_ylim(0, 10)

    from wordcloud import WordCloud

    count = 0
    
    df_speech["hate_speech"] = df_speech["lemma"].apply(detect_hate_speech)
    start_time = time.time()
    while True:

        records = consumer.poll(timeout_ms=2000, max_records=500)
        print("Received {0} messages from topic: {1}".format(len(records), topic_name))
        # Calculate hate speech count per minute
        count += 1
        for record in records:
            for message in records[record]:
                decoded_msg = decode_kafka_item(message)
                
                bloom_start_time = time.time()
                is_hate_speech_bloom = detect_hate_speech(decoded_msg)
                bloom_end_time = time.time()

                print("exe : ", bloom_end_time - bloom_start_time)

                bloom_execution_total_time += bloom_end_time - bloom_start_time


                # model execution
                model_start_time = time.time()
                predicted_category = pipe(decoded_msg)
                label = predicted_category[0]['label']
                score = predicted_category[0]['score']

                if label in label_to_category and score > 0.5 and label != "LABEL_0":
                    model_count += 1
                model_end_time = time.time()

                model_execution_total_time += model_end_time - model_start_time

                # create a dataframe
                # near real-time / live feed simulation
                # creating KPIs
                hate_speech_count += is_hate_speech_bloom
                bloom_count += is_hate_speech_bloom
                avg_bloom_execution_time = bloom_execution_total_time / count
                avg_model_execution_time = model_execution_total_time / count


                #create kpis for all four categories
                if label == "LABEL_0":
                    acceptable_count += 1
                elif label == "LABEL_1":
                    inappropriate_count += 1
                elif label == "LABEL_2":
                    offensive_count += 1
                elif label == "LABEL_3":
                    violent_count += 1

        with placeholder.container():
                        
            # create kpis
            kpi1, accept, inap, off, viol, bloom, model = st.columns(7)

            # fill in those three columns with respective metrics or KPIs
            kpi1.metric(
                label="Hate Speech Count (Bloom)",
                value=round(hate_speech_count),
                delta=round(hate_speech_count) - 10,
            )

            accept.metric(
                label="Acceptable",
                value=round(acceptable_count),
                delta=round(acceptable_count) - 10,
            )

            inap.metric(
                label="Inappropriate",
                value=round(inappropriate_count),
                delta=round(inappropriate_count) - 10,
            )

            off.metric(
                label="Offensive",
                value=round(offensive_count),
                delta=round(offensive_count) - 10,
            )

            viol.metric(
                label="Violent",
                value=round(violent_count),
                delta=round(violent_count) - 10,
            )

            #print in microseconds
            bloom.metric(
                label="Bloom Execution Time (μs)",
                value=round(avg_bloom_execution_time * 1000000, 2),
                delta=round(avg_bloom_execution_time - 10, 2),
            )

            model.metric(
                label="Model Execution Time (ms)",
                value=round(avg_model_execution_time * 1000, 2),
                delta=round(avg_model_execution_time - 10, 2),
            )


            fig_col1, fig_col2 = st.columns(2)
            with fig_col1:
                st.markdown("### Hate Speech Category Distribution")
                fig = px.bar(
                    x=["Acceptable", "Inappropriate", "Offensive", "Violent"],
                    y=[acceptable_count, inappropriate_count, offensive_count, violent_count],
                    labels={"x": "Category", "y": "Count"},
                    title="Hate Speech Category Distribution",
                )
                st.plotly_chart(fig, use_container_width=True)

            with fig_col2:
                #heat map
                st.markdown("### Heat Map of Hate Speech Terms")
                fig = px.density_heatmap(
                    df_speech,
                    x="category",
                    y="lemma",
                    title="Heat Map of Hate Speech Terms",
                )
                st.plotly_chart(fig, use_container_width=True)

            # plot the graph
            current_time = time.time()

            
            if current_time - start_time > 10:
                #convert to normal time
                x = np.append(x, current_time)
                line.set_xdata(x)
                #set hate speech count
                line.set_ydata(np.append(line.get_ydata(), bloom_count))
                the_plot.pyplot(plt)
                start_time = current_time
                bloom_count = 0

            # Create a word cloud
            wordcloud = WordCloud(width=800, height=400, random_state=21, max_font_size=110, background_color="white").generate(' '.join(df_speech['lemma']))

            # Display the word cloud
            st.set_option('deprecation.showPyplotGlobalUse', False)
            st.title("Word Cloud")
            st.image(wordcloud.to_array())
                
            st.markdown("### Detailed Data View")
            st.dataframe(df_speech)
            time.sleep(1)



read_from_kafka('youtube')

