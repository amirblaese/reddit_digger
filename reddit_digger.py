def digC(start,end,sub,keywords):
  """
  Searches for comments within a subreddit given a keyword and date range.

  start: start date in the format: (2011,8,1), i.e. (Y,M,D)

  end: end date in the format: (2011,8,1), i.e. (Y,M,D)

  sub: the subreddit or subreddits to search for. Must be formatted as ['news',
        'askreddit']

  keywords: keyword to search for. If you are searching for the keyword in more
            than one subreddit, be sure to repeat the subreddit entry in the
            sub entry. For inexact phrases write ['elon musk']. For exact phrase
            you must put double quotes inside the single quote ['"elon musk"'].
            for or conditions (multiple words) use ['Laptop|PC']
  """

  print('Sit tight, this could take a while...')

  num_search_terms=len(keywords)

  dataframes=[None]*num_search_terms
  print('You have entered '+str(num_search_terms)+' search term(s):')
  start_epoch=int(dt.datetime(start[0],start[1],start[2]).timestamp())
  end_epoch=int(dt.datetime(end[0],end[1],end[2]).timestamp())
  search_results=[None]*num_search_terms
  body=[None]*num_search_terms
  dates=[None]*num_search_terms
  scores=[None]*num_search_terms

  
  n_tot=0


  for i in range (num_search_terms):
    print(keywords[i])
    print('Digging for comments containing containing <' +keywords[i]+'> in <'+sub[i]+'>...')
    #here we search for the comments using PSAW and PRAW
    search_results[i]=list(api.search_comments(q=keywords[i],
                        after=start_epoch,
                        before=end_epoch,
                        subreddit=sub[i]))
    print('Found '+str(len(search_results[i]))+' comments containing <' +keywords[i]+'>...')
    dates[i]=[None]*len(search_results[i])
    body[i]=[None]*len(search_results[i])
    scores[i]=[None]*len(search_results[i])

    n_tot=n_tot+len(search_results[i])
    #pull the date,body and score of the comments
    for j in range (len(search_results[i])):
      dates[i][j]=search_results[i][j].created_utc
      body[i][j]=search_results[i][j].body
      if body[i][j]=='':
        body[i][j]='empty'
      scores[i][j]=search_results[i][j].score
    #here we save the files to .csv file to save memory
    print('Saving data to .csv file...')
    dataframes[i]=pd.DataFrame({"Dates": dates[i],
                                "Body": body[i],
                                "Scores": scores[i]})
                               
    dataframes[i].to_csv(sub[i]+'_'+keywords[i]+'_comments'+'.csv', index=False)
  print('Found a total of '+str(n_tot)+' comments...')
  print('Saving successful!')
  return dataframes

def analyseC(sub,keywords,rs='W',roll=4,normalize=True):
  """
  Analyses the comments you have previously searched for and saved to .csv file

  sub: the subreddit or subreddits you have saved. Must be formatted as ['news',
        'askreddit']

  keywords: keyword that has been saved. If you are searching for the keyword in 
           more than one subreddit, be sure to repeat the subreddit entry in the
            sub entry. For inexact phrases write ['elon musk']. For exact phrase
            you must put double quotes inside the single quote ['"elon musk"']

  rs: string optional, the resampling period. Default is 'W' for week but if it's 
      too noisy, you can upgrade this to 'M' (month) or 'Q' (quarterly) or 'Y'.

  roll: int optional, the rolling average window. Default is 4, increase to 
        reduce noise, decrease to restore details. 

  normalize: Boolean optional, option to normalize all data to the subreddit's
              current number of subscribers. Default is TRUE.
  """
  pd.set_option('mode.chained_assignment', None)

  num_search_terms=len(keywords)
  seaborn.set(style='darkgrid', palette='bright')
  #prepare graphics
  fig, ((ax3, ax2), (ax1, ax4), (ax5, ax8)) = py.subplots(3,2, sharey=False)
  print('Initializing')
  dataframes=[None]*num_search_terms
  dataframes_sorted=[None]*num_search_terms
  dataframes_filtered=[None]*num_search_terms
  dataframes_binned=[None]*num_search_terms
  dataframes_binned_sum=[None]*num_search_terms

  sid = SentimentIntensityAnalyzer()
  an=[None]*num_search_terms
  neg=[None]*num_search_terms
  pos=[None]*num_search_terms
  neut=[None]*num_search_terms
  comp=[None]*num_search_terms
  lbl=[None]*num_search_terms
  num_subs=[None]*num_search_terms
  dates_arrowed=[None]*num_search_terms

  #search for the .csv files in the directory.
  print('Searching for .csv files in directory...')
  try:
    for i in range (num_search_terms):
      dataframes[i]=pd.read_csv(sub[i]+'_'+keywords[i]+'_comments'+'.csv')
      if sub[i]==sub[i-1]:
        lbl[i]=keywords[i]
      else:
        lbl[i]=sub[i]
  except:
    raise ('Files were not found.')
  print('Files found!')
  n_tot=0
  

  #initialize arrays
  for i in range (num_search_terms):
    dates_arrowed[i]=[None]*len(dataframes[i])
    an[i]=[None]*len(dataframes[i])  
    pos[i]=np.zeros(len(dataframes[i]))  
    neg[i]=np.zeros(len(dataframes[i]))  
    neut[i]=np.zeros(len(dataframes[i]))  
    comp[i]=np.zeros(len(dataframes[i]))  
    n_tot=n_tot+len(dataframes[i])
    if normalize==True:
      num_subs[i]=r.subreddit(sub[i]).subscribers
    if normalize==False:
      num_subs[i]=1
    #dataframes[i] = dataframes[i].drop(dataframes[i][dataframes[i]['Dates'] == str].index)
    #df = df.drop(df[df.score < 50].index)



  print('Total of '+str(n_tot)+' submissions')
  for i in range (num_search_terms):
    print('Analysing '+sub[i]+'...')
    for j in range (len(dataframes[i])):
      #print(j)
      #print(dataframes[i]['Body'][j])
      #if type(dataframes[i]['Dates'][j])==str:
       # dataframes[i].drop(dataframes[i].index[j])
      #I had to add this try except in this section to avoid a bug with pandas
      #where it puts the second column into fthe first. This leads to an HUGE
      #slowdown. For large files this is necessary to keep the files going as it
      #deletes the problematic row, but it has to go through a lot of rows to 
      #check the condition, and it's slow! I hope someone can help me with this.
      if dataframes[i]['Body'][j]=='':
        dataframes[i]['Body'][j]='Comment removed'
      #retrieve sentiment scores and 
      #convert UTC dates to datetimes, this part was a huge pain to
      #get working!
      try:
        an[i][j]=sid.polarity_scores(dataframes[i]['Body'][j])
        neg[i][j]=list(an[i][j].values())[0]
        neut[i][j]=list(an[i][j].values())[1]
        pos[i][j]=list(an[i][j].values())[2]
        comp[i][j]=list(an[i][j].values())[3]
        dates_arrowed[i][j]=arrow.get(float(dataframes[i]['Dates'][j])).format()
      except:
        dataframes[i].drop(dataframes[i].index[j])
      #print(str(j)+'analysed')
    print('Processing '+keywords[i]+'...')
    dataframes_sorted[i]=pd.DataFrame({"Dates": dates_arrowed[i], 
                               "Body": dataframes[i]['Body'],
                              "Scores": dataframes[i]['Scores'],
                               "Positive": pos[i],
                               "Negative": neg[i],
                               "Neutral": neut[i],
                               "Compound": comp[i]})
    dataframes_sorted[i]=dataframes_sorted[i].sort_values(by=["Dates"])

    #remove data with low compound scores (this means they were difficult to
    #analyse.)
    dataframes_filtered[i]=dataframes_sorted[i].query('Compound > 0.05 or Compound <-0.05')
    
    dataframes_filtered[i].index=dataframes_filtered[i]['Dates']
    
    dataframes_filtered[i].index=pd.to_datetime(dataframes_filtered[i].index)
    
    dataframes_binned[i]=dataframes_filtered[i].resample(rs).mean()
    dataframes_binned_sum[i]=dataframes_filtered[i].resample(rs).sum()

    print('Plotting '+sub[i]+'...')


    #ANALYSIS HERE

  

    #dataframes_binned_sum[i]['Compound'].rolling(roll,center=True).sum().plot(label=lbl[i],legend=True,ax=ax6)


    #Average sentiment
    dataframes_binned[i]['Compound'].resample(rs).mean().rolling(roll,center=True).mean().plot(label=lbl[i],ax=ax5,legend=False)
    dataframes_filtered[i]['Comp x Votes']=dataframes_filtered[i]['Compound']*dataframes_filtered[i]['Scores']
    dataframes_filtered[i].is_copy = False
    #dataframes_filtered[i]['Comp x Votes'].resample(rs).sum().rolling(roll,center=True).mean().plot(label=lbl[i],ax=ax7,legend=True)

    dataframes_sorted[i].index=dataframes_sorted[i]['Dates']
    dataframes_sorted[i].index=pd.to_datetime(dataframes_sorted[i].index)


    #Bar graph of total comments
    ax8.bar(sub[i],len(dataframes[i])/num_subs[i])

    dataframes_sorted[i]['day']=dataframes_sorted[i]['Dates'].astype("datetime64").dt.day
    dataframes_sorted[i]['week']=dataframes_sorted[i]['Dates'].astype("datetime64").dt.week
    dataframes_sorted[i]['month']=dataframes_sorted[i]['Dates'].astype("datetime64").dt.month
    dataframes_sorted[i]['year']=dataframes_sorted[i]['Dates'].astype("datetime64").dt.year

    #dataframes_sorted[i]=dataframes_sorted[i].groupby(by=['week','month', 'year']).count()#.rolling(5,center=True).mean()
    #dataframes_sorted[i]=dataframes_sorted[i].pivot(index='Dates', columns='V', values='value')
    #dataframes_sorted[i].plot(ax=ax[0],legend=False,label=keywords[i])
    #dataframes_sorted[i].plot.hist(by=['Dates'],bins=50,ax=ax[0])

    #Comments per user
    dataframes_sorted[i].resample(rs).size().div(num_subs[i]).rolling(roll,center=True).mean().plot(ax=ax1,label=lbl[i],figsize=(7,9))


    #Total comments per user
    dataframes_sorted[i].resample('D').size().cumsum().div(num_subs[i]).rolling(roll,center=True).mean().plot(ax=ax4,label=lbl[i])


    #Upvotes per user
    dataframes_sorted[i]["Scores"].resample(rs).sum().div(num_subs[i]).rolling(roll,center=True).mean().plot(ax=ax3,label=lbl[i],legend=True)

    #Total upvotes per user
    dataframes_sorted[i]["Scores"].resample('D').sum().cumsum().div(num_subs[i]).plot(ax=ax2,label=lbl[i])
    #dataframes_sorted[i]["Num Comments"].cumsum().plot(ax=ax4,label=keywords[i])




  print('Designing plot...')
  ax1.set_xlabel("")
  ax2.set_xlabel("")
  ax3.set_xlabel("")
  ax4.set_xlabel("")
  ax5.set_xlabel("")
  #ax6.set_xlabel("")
  #ax7.set_xlabel("")



  ax1.legend(frameon=False,fontsize='x-small')
  ax2.legend(frameon=False,fontsize='small')
  ax3.legend(frameon=False,fontsize='small')
  ax4.legend(frameon=False,fontsize='small')
  ax5.legend(frameon=False,fontsize='x-small')
  #ax6.legend(frameon=False,fontsize='small')
  #ax7.legend(frameon=False,fontsize='small')


  if normalize==True:
    ax1.set_ylabel('Comments per user')
    ax2.set_ylabel('Total upvotes per user')  
    ax3.set_ylabel('Upvotes per user')
    ax4.set_ylabel("Total comments per user")
    ax5.set_ylabel("Average sentiment")
    #ax6.set_ylabel("(Comments x Sentiment)")
    #ax7.set_ylabel("(Votes x Sentiment)")
    ax8.set_ylabel("Comments per user")
  if normalize==False:
    ax1.set_ylabel('Comments')
    ax2.set_ylabel('Total upvotes')  
    ax3.set_ylabel('Upvotes')
    ax4.set_ylabel("Total comments")
    ax5.set_ylabel("Average sentiment")
    #ax6.set_ylabel("(Comments x Sentiment)")
    #ax7.set_ylabel("(Votes x Sentiment)")
    ax8.set_ylabel("Comments")





  ax1.tick_params(axis='x', labelrotation= 45)
  ax2.tick_params(axis='x', labelrotation= 45)
  ax3.tick_params(axis='x', labelrotation= 45)
  ax4.tick_params(axis='x', labelrotation= 45)
  ax5.tick_params(axis='x', labelrotation= 45)
  #ax6.tick_params(axis='x', labelrotation= 45)
  #ax7.tick_params(axis='x', labelrotation= 45)
  ax8.tick_params(axis='x', labelrotation= 90)



  print('Saving...')
  py.tight_layout()
  py.savefig('figure.svg',dpi=300)

  # ax[0].tick_params(
  #   axis='x',          # changes apply to the x-axis
  #   which='both',      # both major and minor ticks are affected
  #   bottom=False,      # ticks along the bottom edge are off
  #   top=False,         # ticks along the top edge are off
  #   labelbottom=False) # labels along the bottom edge are off
  print('Done!')
  return dataframes_sorted

      