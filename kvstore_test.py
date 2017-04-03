import itertools
import logging
from multiprocessing import Pipe, Process
import os
import sys
import time
import yaml


NUM_WORKERS = 3
none_tuple = (None, None)
logger = logging.getLogger(__name__)


def mxnet_process(role, conn):
    logger.info("Subprocess starting with role %s", role)

    os.environ['DMLC_PS_ROOT_URI'] = '0.0.0.0'
    os.environ['DMLC_PS_ROOT_PORT'] = '50000'
    os.environ['DMLC_ROLE'] = role
    os.environ['DMLC_NUM_WORKER'] = str(NUM_WORKERS)
    os.environ['DMLC_NUM_SERVER'] = str(NUM_WORKERS)
    os.environ['PS_VERBOSE'] = '1'
    os.environ['PS_RESEND'] = '1'

    import mxnet


def mxnet_process_worker(role, conn):
    logger.info("Worker subprocess starting with pid: %s", os.getpid())

    os.environ['DMLC_PS_ROOT_URI'] = '0.0.0.0'
    os.environ['DMLC_PS_ROOT_PORT'] = '50000'
    os.environ['DMLC_ROLE'] = 'worker'
    os.environ['DMLC_NUM_WORKER'] = str(NUM_WORKERS)
    os.environ['DMLC_NUM_SERVER'] = str(NUM_WORKERS)
    os.environ['PS_VERBOSE'] = '1'
    os.environ['PS_RESEND'] = '1'

    import mxnet as mx

    logger.info("Starting run...")
    kv = mx.kvstore.create('dist')

    kv.init(2, mx.nd.zeros((50, 50)))
    # Errors still occur with this uncommented.
    # kv.push(2, mx.nd.zeros((50, 50)))

    logger.info("Initialized")

    a = mx.nd.zeros((50, 50))

    logger.info("First pull")
    kv.pull(2, a)
    print a.asnumpy()

    a += mx.nd.ones((50, 50))

    # Report to main process that this process is finished. Main process will
    # not send kill message until all other processes have reported as
    # finished.
    conn.send({'finished': kv.rank})
    logger.info("Put finished msg on queue.")
    # Keep this process alive until main process sends a message to kill.
    conn.recv()  # blocks until message is received
    logger.info("Received kill signal.")
    sys.exit(0)


def main():
    pipes = []
    processes = []

    process_parameters = itertools.chain(
        [('scheduler', mxnet_process, none_tuple)],
        [('server', mxnet_process, none_tuple)] * NUM_WORKERS,
        [('worker', mxnet_process_worker, Pipe()) for _ in range(NUM_WORKERS)]
    )

    for type, func, (paren_conn, child_conn) in process_parameters:
        p = Process(target=func, args=(type, child_conn,))
        p.start()
        processes.append(p)
        if paren_conn:
            pipes.append(paren_conn)
            logger.info("Launched %s process: %s, pid: %s", type, p, p.pid)

    finished = {}
    while True:
        logger.info("Main process...")
        for i, process in enumerate(processes):
            if not process.is_alive():
                logger.error(
                    "Process was not alive when queried: %s, pid: %s, exit"
                    " code: %s", process, process.pid, process.exitcode)

        for pipe in pipes:
            if pipe.poll(0.1):
                msg = pipe.recv()
                logger.info("Received msg: %s", msg)
                if msg and msg['finished'] is not None:
                    finished[msg['finished']] = True

        if sorted(finished.keys()) == range(NUM_WORKERS):
            logger.info("All workers finished, sending kill signals.")
            for pipe in pipes:
                pipe.send({'ok': 'go'})

            for process in processes:
                logger.info("Joining %s", process)
                process.join()

            return True

        time.sleep(1)


if __name__ == '__main__':
    import logging.config
    file_path = os.path.realpath(__file__)
    dirname = os.path.dirname(os.path.realpath(__file__))
    with open(dirname + '/logging_config.yaml', 'r') as f:
        logging.config.dictConfig(yaml.load(f))

    logger.info("Starting...")
    main()
