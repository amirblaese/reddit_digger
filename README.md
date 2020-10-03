# The Reddit Digger



## ABOUT 

Easily dig through as many reddit comments as you like and discover trends and details with automatic intelligent analysis.

## Dependencies

PRAW, PSAW, Pushshift API, reddit API, numpy, pandas, vaderSentiments, seaborn, matplotlib, arrow, datetime

## Example

Let's say we want to see how comments and sentiments regarding "china" or "chinese" have evolved over time in the 'vancouver','seattle','toronto','nyc','canada' subreddits from late 2011 until now.

Before using the functions we must first log in to use the API, do this as follows:

    r = praw.Reddit(client_id='',
                client_secret='',
                user_agent='')


    api = PushshiftAPI(r)

Now we can search and analyse.

    a=digC((2011,8,1),(2020,9,1),['vancouver','seattle','toronto','nyc','canada'],['china|chinese','china|chinese','china|chinese','china|chinese','china|chinese'])
    b=analyseC(['vancouver','seattle','toronto','nyc','canada'],['china|chinese','china|chinese','china|chinese','china|chinese','china|chinese'],rs='Q')

This produces the following analysis:

![Alt text](China_Chinese_N.PNG?raw=true "the raging demon.")
