FROM 763725063017.dkr.ecr.us-east-1.amazonaws.com/davileen/mxnet_kvstore:latest

COPY logging_config.yaml /
COPY kvstore_test.py /

CMD python /kvstore_test.py
