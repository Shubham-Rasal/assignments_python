import pytchat


def error_callback(exc):
    raise Exception('Error while sending data to kafka: {0}'.format(str(exc)))


def write_to_kafka(topic_name, items):
    count = 0
    producer = KafkaProducer(bootstrap_servers=['127.0.0.1:9092'])
    for message, key in items:
        print(message.encode('utf-8'))
        producer.send(topic_name,
                      key=key.encode('utf-8'),
                      value=message.encode('utf-8')).add_errback(error_callback)
        count += 1
    producer.flush()
    print("Wrote {0} messages into topic: {1}".format(count, topic_name))


def decode_kafka_item(message):
    print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value))
    return message.value.decode('utf-8')


def read_from_kafka(topic_name):
    consumer = KafkaConsumer(
        topic_name,
        auto_offset_reset='earliest',
        bootstrap_servers=['127.0.0.1:29092'],
        consumer_timeout_ms=10000
    )
    
    records = consumer.poll(timeout_ms=1000, max_records=500)
    print("Received {0} messages from topic: {1}".format(len(records), topic_name))
    for record in records:
        for message in records[record]:
            decoded_msg = decode_kafka_item(message)
            print(decoded_msg)
    # consumer.close()
    



chat = pytchat.create(video_id="uIx8l2xlYVY")
while chat.is_alive():
    for c in chat.get().sync_items():
        print(f"{c.datetime} [{c.author.name}]- {c.message}")
        write_to_kafka('youtube', [(c.message, c.author.name)])
