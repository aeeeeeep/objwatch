import multiprocessing


def calculate(pid, queue):
    total = pid * 1000
    for step in range(3):
        increment = (pid + 1) * (step + 1)
        total += increment
        queue.put(('intermediate', pid, step, total))
    queue.put(('final', pid, total))


def worker():
    result_queue = multiprocessing.Queue()
    processes = []

    for pid in range(8):
        p = multiprocessing.Process(target=calculate, args=(pid, result_queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    intermediate_values = []
    final_results = {}

    while not result_queue.empty():
        item = result_queue.get()
        if item[0] == 'intermediate':
            _, pid, step, value = item
            intermediate_values.append(value)
        elif item[0] == 'final':
            _, pid, value = item
            final_results[pid] = value


if __name__ == '__main__':
    worker()
