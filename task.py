from function import *
task1 = crawler('crawler1',[(2016,'01',1)])
task2 = crawler('crawler2',[(2016,'02',1)])
task3 = crawler('crawler3',[(2016,'03',1)])
task4 = crawler('crawler4',[(2016,'04',1)])
a = threading.Thread(target=task1.scrapy)
a.start()
b = threading.Thread(target=task2.scrapy)
b.start()
c = threading.Thread(target=task3.scrapy)
c.start()
d = threading.Thread(target=task4.scrapy)
d.start()

