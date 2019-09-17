This Enron Email summary script has been built using python 3.7

Some data cleaning to remove duplicate emails (based on ID of email) was done.

The data was not changed based on "similar" names like capitalization.

Assumption being that if there is Frank C. Copolla and frank c. copolla as different
senders in the dataset, they represent different people and the dataset is "clean"
for stuff like this.

visualization for Q2 and Q3:
While the visualization was done for daily monthly and weekly only the monthly was saved.
However, by uncommenting plt.show() the remaining two can be seen too (and usd if needed).

The visualization is done for the top 8 most prolific senders. But it can be easily extended.
Indeed, I have build it such that we can do it for the entire set of senders pretty easily. 
It will of course have to be done in seperate "sheets" to print out for human consumption.

