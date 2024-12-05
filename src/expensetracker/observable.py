class Observer:
   def update(self):
      pass


class ExpenseTrackerObservable:
    def __init__(self, expense_tracker):
        self.expense_tracker = expense_tracker
        self.observers = []

    def add_observer(self, observer):
        if isinstance(observer, Observer):
            self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer.update()