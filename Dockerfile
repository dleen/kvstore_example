FROM dleen/mxnet_kvstore

COPY logging_config.yaml /
COPY kvstore_test.py /

CMD python /kvstore_test.py
