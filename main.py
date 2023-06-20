import importlib
if __name__ == "__main__":
    task = 'src.scraper'
    
    Task = importlib.import_module(task).Task
    t = Task()
    t.queries.append("Amsterdam, restaurant")
    t.scroll_times = 1
    t.filtered_data = {"min_rating": 3}
    t.begin_task()
