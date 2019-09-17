#!/usr/bin/python

# Code for summarizing enron email event csv file
# and related visualizations
import time
t_start = time.time()

import os
import sys
import pandas as pd
from pandas.tseries.offsets import MonthEnd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import itertools

t1 =time.time()
print(f'Time to import modules: {t1-t_start:.2f} seconds')
t0 = time.time()

raw_data_dir =r"..\raw_data"
staging_area_dir = r"..\staging_area"
output_dir = r"..\output_dir"

q1_output_fname = 'q1_person_send_received.csv'
q1_output_file = os.path.join(output_dir,q1_output_fname)
q2_output_fname = 'q2_most_prolific_emailers.png'
q2_output_file = os.path.join(output_dir,q2_output_fname)
q3_output_fname = 'q3_unique_contacts_by_prolific_emailers.png'
q3_output_file = os.path.join(output_dir,q3_output_fname)

raw_data_file_name = sys.argv[1]

fname = os.path.join(raw_data_dir,raw_data_file_name)

print("READING FILE...")
header_row = ['time','mess_identifier','sender','recipients','topic','mode']
df_in = pd.read_csv(fname,header=None,names=header_row)

t1 =time.time()
print(f'Time to read in file: {t1-t0:.2f} seconds')
t0=time.time()
print(df_in.shape)


# drop the 'topic' and 'mode' column as not relevant to the problem
print("Processing file...")
df_in.drop(columns=['topic','mode'],inplace=True)

# convert 'time' column to datetime format
df_in['time'] = pd.to_datetime(df_in['time'],unit='ms')

df_in.to_csv(os.path.join(staging_area_dir,'enron_all_with_datetime.csv'))
df_1 =df_in.copy()

t1 =time.time()
print(f'Time to prepare file for Questions: {t1-t0:.2f} seconds')
t0 =time.time()

# Drop the duplicated messages (identified by mess_identifier being same)
print("Dropping duplicates...")
df_2 = df_1.drop_duplicates(subset="mess_identifier",keep="first",inplace=False)

t1 =time.time()
print(f'Time to drop duplicate emails: {t1-t0:.2f} seconds')
t0 =time.time()

# # Q1 START
# # SOLVING FOR QUESTION 1 TO GENERATE SEND RECEIVED SUMMARY FILE
# # split out the pipe seperated recipient column to get a separate row for each
# # recipient. This will increase the number of rows substantially
t_start_Q1 = time.time()

df_a = df_2.recipients.str.split('|',expand=True).stack().reset_index()\
    .merge(df_2.reset_index(),left_on ='level_0',right_on='index')\
    .drop(['level_0','level_1','index','recipients'],1)

df_a.rename(columns={0:'recipients'},inplace=True)

# Generate a count of emails send by a person and received, based on unique emails
df_c = (pd.merge(df_a.groupby('sender').mess_identifier.nunique(),
            df_a.groupby('recipients').mess_identifier.nunique(),
            left_index=True,
            right_index=True,
            how='outer').fillna(0).rename(columns={'mess_identifier_x':'send','mess_identifier_y':'received'}))

# sort the summary count file into descending order by number send
df_d = df_c.sort_values('send',ascending=False)

t0 =time.time()
df_d.to_csv(q1_output_file,index=True)
t1=time.time()
print(f'Time to write out file to disk: {t1-t0:.2f} seconds')
t0 =time.time()

t_end_Q1 =time.time()
print(f'Total time to run for Q1 alone: {t_end_Q1-t_start_Q1:.2f} seconds')
print("waiting...")

# END OF QUESTION 1

# START QUESTION 2: VISUALIZATION OF EMAILS SENT BY
# MOST PROLIFIC SENDERS
t_start_Q2 = time.time()
print('Working on Question 2...')

df_3 = df_2.drop(columns=['recipients','mess_identifier'],inplace=False)

df_3['date'] = df_3['time'].dt.normalize()

t1 =time.time()
print(f'Time to drop unnecessary columns and add month end column: {t1-t_start_Q2:.2f} seconds')
t0 =time.time()

# Generating list of top senders to keep for visualization
print("Generating list of top senders to keep for visualization...")

df_grp_1 = df_3.groupby(['sender']).count()

df_grp_1.sort_values(by=['time'],ascending=False,inplace=True)

toppers = list(df_grp_1.index.array)

toppers_to_keep =toppers[:10] #keeping 10, this can be changed to higher or lower depending on how many you want to plot


t1 =time.time()
print(f'Time to generate list of top senders to keep: {t1-t_start_Q2:.2f} seconds')
print(f'Total time thus far: {t1-t_start:.2f} seconds')

t0 =time.time()

print("Curtailing the dataset to only retain those senders we will need for visualization...")

df_4 = df_3[df_3['sender'].isin(toppers_to_keep)]

# Q2 BEGIN DAILY/WEEKLY/MONTHLY

agg_df_send_daily_1 = df_4.pivot_table(index='date',columns = 'sender',values='time',aggfunc='count')

agg_df_send_weekly = agg_df_send_daily_1[toppers_to_keep].resample('W').sum()

agg_df_send_monthly = agg_df_send_daily_1[toppers_to_keep].resample('M').sum()


topper_case =[x.title() for x in toppers_to_keep]
start, end = '1998-05-01','2002-12-31'
plt.rcParams["figure.figsize"] = (10.0,7.5)  #set figure size
marker = itertools.cycle(('*','o','+',','))
years = mdates.YearLocator()
quarters = mdates.MonthLocator(3,6,9,12)
months = mdates.MonthLocator()
weekly = mdates.WeekdayLocator(byweekday=(1),interval=1)

# PLOT DAILY
fig = plt.figure()
st = fig.suptitle("Number of Emails Sent Over Time By 8 Most Prolific Senders DAILY", fontsize="x-large")

ax1 = plt.subplot(2,1,1)
for i in range(0,4):
    ax1.plot(agg_df_send_daily_1.loc[start:end,toppers[i]],label=topper_case[i],marker='.')
ax1.xaxis.set_major_locator(quarters)
ax1.xaxis.set_minor_locator(months)
ax1.legend()
ax1.set_title("Top 4 Most Prolific Emailers")
plt.grid(True,linestyle='--')
plt.ylabel('Number of Emails Send per Day')

ax2 = plt.subplot(2,1,2,sharex=ax1)
for i in range(4,8):
    plt.plot(agg_df_send_daily_1.loc[start:end,toppers[i]],label=topper_case[i])
ax2.legend()
ax2.set_title("Next 4 Most Prolific Emailers")
plt.grid(True,linestyle='--')
plt.ylabel('Number of Emails Send per Day')
plt.xlabel('Day')

# MONTHLY PLOT
fig = plt.figure()
st = fig.suptitle("Number of Emails Sent Over Time By 8 Most Prolific Senders MONTHLY", fontsize="x-large")

ax1 = plt.subplot(2,1,1)
for i in range(0,4):
    plt.plot(agg_df_send_monthly.loc[start:end,toppers[i]],label=topper_case[i],marker='o')
ax1.xaxis.set_major_locator(quarters)
ax1.xaxis.set_minor_locator(months)
ax1.legend()
ax1.set_title("Top 4 Most Prolific Emailers")
plt.grid(True,linestyle='--')
plt.ylabel('Number of Emails Send per Month')

ax2 = plt.subplot(2,1,2,sharex=ax1)
for i in range(4,8):
    plt.plot(agg_df_send_monthly.loc[start:end,toppers[i]],label=topper_case[i],marker='o')
ax2.legend()
ax2.set_title("Next 4 Most Prolific Emailers")
plt.grid(True,linestyle='--')
plt.ylabel('Number of Emails Send per Month')
plt.xlabel('Month')
plt.savefig(q2_output_file)

# plotting for Q2 weekly
fig = plt.figure()
st = fig.suptitle("Number of Emails Sent Over Time By 8 Most Prolific Senders WEEKLY", fontsize="x-large")

ax1 = plt.subplot(2,1,1)
ax2 = plt.subplot(2,1,2,sharex=ax1)
for i in range(0,4):
    ax1.plot(agg_df_send_weekly.loc[start:end,toppers[i]],label=topper_case[i],marker='.')
ax1.xaxis.set_major_locator(months)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('\n\n\n%b\n%Y'))
ax1.xaxis.set_minor_locator(weekly)
ax1.legend()
ax1.set_title("Top 4 Most Prolific Emailers")
plt.grid(True,linestyle='--')
plt.ylabel('Number of Emails Send per Week')

for i in range(4,8):
    plt.plot(agg_df_send_monthly.loc[start:end,toppers[i]],label=topper_case[i],marker='.')
ax2.legend()
ax2.set_title("Next 4 Most Prolific Emailers")
plt.grid(True,linestyle='--')
plt.ylabel('Number of Emails Send per Week')
plt.xlabel('Month')


# Q2 END DAILY/WEEKLY/MONTHLY

# Q3 BEGIN
# number of unique people contacting prolific
# senders per time period
# DAILY/WEEKLY/MONTHLY

print("Curtailing the dataset to only retain those RECIPIENTS who were TOP SENDERS for Q3...")

df_b = df_a[df_a['recipients'].isin(toppers_to_keep)]
df_b['date'] = df_b['time'].dt.normalize()

agg_df_rcv_daily = df_b.pivot_table(index='date',columns = 'recipients',values='sender',aggfunc='nunique')
agg_df_rcv_daily =agg_df_rcv_daily[toppers_to_keep]

agg_df_rcv_weekly = agg_df_rcv_daily[toppers_to_keep].resample('W').sum()

agg_df_rcv_monthly = agg_df_rcv_daily[toppers_to_keep].resample('M').sum()

# Plotting for Q3 DAILY
fig = plt.figure()
st = fig.suptitle("Number of Unique Email Addrsses Contacting the 8 Most Prolific Senders DAILY", fontsize="x-large")

ax1 = plt.subplot(2,1,1)
ax2 = plt.subplot(2,1,2,sharex=ax1)
for i in range(0,4):
    ax1.plot(agg_df_rcv_daily.loc[start:end,toppers[i]],label=topper_case[i],marker='o')
ax1.xaxis.set_major_locator(quarters)
ax1.xaxis.set_minor_locator(months)
ax1.legend()
ax1.set_title("Top 4 Most Prolific Emailers")
plt.grid(True,linestyle='--')
plt.ylabel('Number of Unique Email Addrsses\nContacting Person per Day',multialignment='center')

for i in range(4,8):
    plt.plot(agg_df_rcv_daily.loc[start:end,toppers[i]],label=topper_case[i],marker='.')
ax2.legend()
ax2.set_title("Next 4 Most Prolific Emailers")
plt.grid(True,linestyle='--')
plt.ylabel('Number of Unique Email Addrsses\nContacting Person per Day',multialignment='center')
plt.xlabel('Day')


# Plotting for Q3 MONTHLY
fig = plt.figure()
st = fig.suptitle("Number of Unique Email Addrsses Contacting the 8 Most Prolific Senders MONTHLY", fontsize="x-large")

ax1 = plt.subplot(2,1,1)
for i in range(0,4):
    ax1.plot(agg_df_rcv_monthly.loc[start:end,toppers[i]],label=topper_case[i],marker='o')
ax1.xaxis.set_major_locator(quarters)
ax1.xaxis.set_minor_locator(months)
ax1.legend()
ax1.set_title("Top 4 Most Prolific Emailers")
plt.grid(True,linestyle='--')
plt.ylabel('Number of Unique Email Addrsses\ncontacting Person per Month',multialignment='center')

ax2 = plt.subplot(2,1,2,sharex=ax1)
for i in range(4,8):
    plt.plot(agg_df_rcv_monthly.loc[start:end,toppers[i]],label=topper_case[i],marker='o')
ax2.legend()
ax2.set_title("Next 4 Most Prolific Emailers")
plt.grid(True,linestyle='--')
plt.ylabel('Number of Unique Email Addrsses\ncontacting Person per Month',multialignment='center')
plt.xlabel('Month')

plt.savefig(q3_output_file)

# Plotting for Q3 WEEKLY
fig = plt.figure()
st = fig.suptitle("Number of Unique Email Addrsses Contacting the 8 Most Prolific Senders WEEKLY", fontsize="x-large")

ax1 = plt.subplot(2,1,1)
for i in range(0,4):
    ax1.plot(agg_df_rcv_weekly.loc[start:end,toppers[i]],label=topper_case[i],marker='.')
ax1.xaxis.set_major_locator(quarters)
ax1.xaxis.set_minor_locator(months)
ax1.legend()
ax1.set_title("Top 4 Most Prolific Emailers")
plt.grid(True,linestyle='--')
plt.ylabel('Number of Unique Email Addrsses\nContacting Person per Week',multialignment='center')

ax2 = plt.subplot(2,1,2,sharex=ax1)
for i in range(4,8):
    plt.plot(agg_df_rcv_weekly.loc[start:end,toppers[i]],label=topper_case[i])
ax2.legend()
ax2.set_title("Next 4 Most Prolific Emailers")
plt.grid(True,linestyle='--')
plt.ylabel('Number of Unique Email Addrsses\nContacting Person per Week',multialignment='center')
plt.xlabel('Week')



# plt.show()
# Q3 END DAILY/WEEKLY/MONTHLY

t_end =time.time()
print(f'Total time to run for program: {t_end-t_start:.2f} seconds')
