import importlib
if __name__ == "__main__":
    task = 'src.scraper'
    
    Task = importlib.import_module(task).Task
    t = Task()
    t.queries.append("Amsterdam, restaurant")
    t.scroll_times = 2

    t.begin_task()
