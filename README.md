KVStore Errors
==============

The file `kvstore_test.py` produces the errors described below.

You can run this container using:

```
docker run -it dleen/kvstore
```

If you want to make changes and run do:
```
docker build -t dleen/kvstore .
docker run -it dleen/kvstore
```

The base image for this container is found in `docker/Dockerfile` and is just Ubuntu 14.04 with Python 2.7.13 and mxnet built for CPU with distributed kvstore enabled.


Uninitialized values
--------------------
The `kvstore` is initialized using

```
kvstore.init(mx.nd.zeros((100, 100)))
```

method but often when pulling the following can be observed instead of zeros:
```
[04/03/2017 21:33:16 INFO 13 kvstore_test.py:55 __main__] First pull
[[  3.22298647e-44   0.00000000e+00   1.13612347e-38 ...,   4.57874273e-41
    1.40129846e-45   0.00000000e+00]
 [  1.13612347e-38   0.00000000e+00   1.26116862e-44 ...,   0.00000000e+00
    1.13612347e-38   0.00000000e+00]
 [  7.00649232e-45   0.00000000e+00   9.45166471e-13 ...,   0.00000000e+00
    7.00649232e-45   0.00000000e+00]
 ...,
 [  1.23576462e-22   4.57874273e-41              nan ...,   0.00000000e+00
    1.23576462e-22   4.57874273e-41]
 [             nan              nan   1.22984753e-22 ...,   0.00000000e+00
    2.80259693e-44   0.00000000e+00]
 [             nan              nan   0.00000000e+00 ...,   0.00000000e+00
               nan              nan]]
```

Message containing empty data
-----------------------------
Sometimes a message is sent (not sure if it is a worker/server/scheduler sending this) containing empty data which causes CHECK to fail in ZMQ:
```
Assertion failed: data_ != NULL || size_ == 0 (src/msg.cpp:97)
[04/03/2017 21:34:31 INFO 6 kvstore_test.py:103 __main__] Main process...
Traceback (most recent call last):
  File "/kvstore_test.py", line 145, in <module>
    main()
  File "/kvstore_test.py", line 111, in main
    process.exitcode))
Exception: Process was not alive when queried: <Process(Process-1, started)>, pid: 7, exit code: None
```

KVStore hangs due to dead process
---------------------------------
Sometimes a process exits/dies with no apparent error. This causes the script to hang, presumably due to the kvstore waiting for a worker which is never going to respond.

```
[04/03/2017 21:41:52 INFO 8 kvstore_test.py:123 __main__] Starting...
[04/03/2017 21:41:52 INFO 9 kvstore_test.py:19 __main__] Subprocess starting with role scheduler
[04/03/2017 21:41:52 INFO 10 kvstore_test.py:19 __main__] Subprocess starting with role server
[04/03/2017 21:41:52 INFO 8 kvstore_test.py:84 __main__] Launched worker process: <Process(Process-5, started)>, pid: 13
[04/03/2017 21:41:52 INFO 8 kvstore_test.py:84 __main__] Launched worker process: <Process(Process-6, started)>, pid: 14
[04/03/2017 21:41:53 INFO 8 kvstore_test.py:84 __main__] Launched worker process: <Process(Process-7, started)>, pid: 15
[04/03/2017 21:41:53 INFO 8 kvstore_test.py:88 __main__] Main process...
[04/03/2017 21:41:53 INFO 14 kvstore_test.py:33 __main__] Worker subprocess starting with pid: 14
[04/03/2017 21:41:53 INFO 11 kvstore_test.py:19 __main__] Subprocess starting with role server
[04/03/2017 21:41:53 INFO 12 kvstore_test.py:19 __main__] Subprocess starting with role server
[04/03/2017 21:41:53 INFO 15 kvstore_test.py:33 __main__] Worker subprocess starting with pid: 15
[04/03/2017 21:41:53 INFO 13 kvstore_test.py:33 __main__] Worker subprocess starting with pid: 13
[21:41:53] src/van.cc:75: Bind to role=scheduler, id=1, ip=0.0.0.0, port=50000, is_recovery=0
[21:41:53] src/van.cc:75: Bind to role=server, ip=172.17.0.2, port=52855, is_recovery=0
[21:41:53] src/van.cc:75: Bind to role=server, ip=172.17.0.2, port=35575, is_recovery=0
[21:41:53] src/van.cc:75: Bind to role=server, ip=172.17.0.2, port=49947, is_recovery=0
[04/03/2017 21:41:53 INFO 14 kvstore_test.py:45 __main__] Starting run...
[04/03/2017 21:41:53 INFO 15 kvstore_test.py:45 __main__] Starting run...
[04/03/2017 21:41:53 INFO 13 kvstore_test.py:45 __main__] Starting run...
[21:41:53] src/van.cc:75: Bind to role=worker, ip=172.17.0.2, port=38107, is_recovery=0
[21:41:53] src/van.cc:75: Bind to role=worker, ip=172.17.0.2, port=55539, is_recovery=0
[21:41:53] src/van.cc:75: Bind to role=worker, ip=172.17.0.2, port=48295, is_recovery=0
[21:41:53] src/van.cc:235: assign rank=8 to node role=server, ip=172.17.0.2, port=35575, is_recovery=0
[21:41:53] src/van.cc:235: assign rank=9 to node role=worker, ip=172.17.0.2, port=38107, is_recovery=0
[21:41:53] src/van.cc:235: assign rank=11 to node role=worker, ip=172.17.0.2, port=48295, is_recovery=0
[21:41:53] src/van.cc:235: assign rank=10 to node role=server, ip=172.17.0.2, port=49947, is_recovery=0
[21:41:53] src/van.cc:235: assign rank=12 to node role=server, ip=172.17.0.2, port=52855, is_recovery=0
[21:41:53] src/van.cc:235: assign rank=13 to node role=worker, ip=172.17.0.2, port=55539, is_recovery=0
[21:41:53] src/van.cc:251: the scheduler is connected to 3 workers and 3 servers
[21:41:53] src/van.cc:281: S[10] is connected to others[21:41:53] src/van.cc:281: W[9] is connected to others
[21:41:53
[21:41:53] src/van.cc:281: S[8] is connected to others
] src/van.cc:281: S[12] is connected to others
[21:41:53] src/van.cc:281: W[13] is connected to others
[21:41:53] src/van.cc:291: Barrier count for 7 : 1
[21:41:53] src/van.cc:291: Barrier count for 7 : 2
[21:41:53] src/van.cc:291: Barrier count for 7 : 3
[21:41:53] src/van.cc:291: Barrier count for 7 : 4
[21:41:53] src/van.cc:291: Barrier count for 7 : 5
[21:41:53] src/van.cc:281: W[11] is connected to others
[21:41:53] src/van.cc:291: Barrier count for 7 : 6
[21:41:53] src/van.cc:291: Barrier count for 7 : 7
[21:41:53] src/van.cc:291: Barrier count for 7 : 1
[21:41:53] src/van.cc:291: Barrier count for 4 : 1
[21:41:53] src/van.cc:291: Barrier count for 4 : 2
[04/03/2017 21:41:54 INFO 8 kvstore_test.py:88 __main__] Main process...
[04/03/2017 21:41:54 ERROR 8 kvstore_test.py:93 __main__] Process was not alive when queried: <Process(Process-6, stopped[SIGSEGV])>, pid: 14, exit code: -11
[04/03/2017 21:41:55 INFO 8 kvstore_test.py:88 __main__] Main process...
[04/03/2017 21:41:55 ERROR 8 kvstore_test.py:93 __main__] Process was not alive when queried: <Process(Process-6, stopped[SIGSEGV])>, pid: 14, exit code: -11
[04/03/2017 21:41:56 INFO 8 kvstore_test.py:88 __main__] Main process...
[04/03/2017 21:41:56 ERROR 8 kvstore_test.py:93 __main__] Process was not alive when queried: <Process(Process-6, stopped[SIGSEGV])>, pid: 14, exit code: -11
[04/03/2017 21:37:11 INFO 11 kvstore_test.py:51 __main__] Initialized
[04/03/2017 21:37:11 INFO 11 kvstore_test.py:55 __main__] First pull
[04/03/2017 21:37:11 INFO 12 kvstore_test.py:51 __main__] Initialized
[04/03/2017 21:37:11 INFO 13 kvstore_test.py:51 __main__] Initialized
[04/03/2017 21:37:11 INFO 13 kvstore_test.py:55 __main__] First pull
[04/03/2017 21:37:11 INFO 12 kvstore_test.py:55 __main__] First pull
[04/03/2017 21:37:11 INFO 6 kvstore_test.py:88 __main__] Main process...
```
