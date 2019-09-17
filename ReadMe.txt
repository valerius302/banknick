This Enron Email summary script has been built using python 3.7

Some data cleaning to remove duplicate emails (based on ID of email) was done.

The data was not changed based on "similar" names like capitalization.

Assumption being that if there is Frank C. Copolla and frank c. copolla as different
senders in the dataset, they represent different people and the dataset is "clean"
for stuff like this.

visualization for Q2 and Q3:
While the visualization was done for daily monthly and weekly only the monthly was saved.
However, by uncommenting plt.show() the remaining two can be seen too (and usd if needed).
