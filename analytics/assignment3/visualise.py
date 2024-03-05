import time  # to simulate a real time data, time loop

import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development

import pandas as pd
from pybloom_live import BloomFilter

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


from kafka import KafkaConsumer

def read_from_kafka(topic_name):
    consumer = KafkaConsumer(
        topic_name,
        auto_offset_reset='earliest',
        bootstrap_servers=['127.0.0.1:29092'],
        consumer_timeout_ms=10000
    )
    # Continuously listen for messages
    placeholder = st.empty()

    hate_speech_count = 0
    non_hate_speech_count = 0
    
    df_speech["hate_speech"] = df_speech["lemma"].apply(detect_hate_speech)
    while True:
        records = consumer.poll(timeout_ms=2000, max_records=500)
        print("Received {0} messages from topic: {1}".format(len(records), topic_name))
        for record in records:
            for message in records[record]:
                decoded_msg = decode_kafka_item(message)
                is_hate_speech = detect_hate_speech(decoded_msg)
                # create a dataframe
                # near real-time / live feed simulation
                # creating KPIs
                hate_speech_count += is_hate_speech 
                non_hate_speech_count += not is_hate_speech


        with placeholder.container():
                        
            # create three columns
            kpi1, kpi2 = st.columns(2)

            # fill in those three columns with respective metrics or KPIs
            kpi1, kpi2 = st.columns(2)

            # fill in those three columns with respective metrics or KPIs
            kpi1.metric(
                label="Hate Speech Count",
                value=round(hate_speech_count),
                delta=round(hate_speech_count) - 10,
            )

            kpi2.metric(
                label="Non-Hate Speech Count",
                value=round(non_hate_speech_count),
                delta=round(non_hate_speech_count) - 100,
            )
            
            
            st.markdown("### Detailed Data View")
            st.dataframe(df_speech)
            time.sleep(1)



read_from_kafka('youtube')


