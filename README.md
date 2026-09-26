# Self-Ratings and Preferences

- Python: 4
- Pandas: 4
- Scikit-learn: 3
- Tree-based Models: 3
- SQL: 3
- Feature Engineering: 4
- Model Evaluation and Validation: 5
- Working with Time-Series or Sequential Data: 2
- Taking a Model into Production: 4
- Experiment Tracking: 5

## What kind of modelling problem are you strongest with?
Computer vision is my strongest areas. I have extnsive experience building and deploying models for image classification  and object detection.
I have also worked on problems with structured data by extracting features from images and treating those features as structured data that I use to build models.

## What would be the steepest learning curve for you here?
Understanding the business context and domain knowledge of the problems we are trying to solve. While I have strong technical skills, I recognize that applying those skills effectively requires a deep understanding of the specific challenges and goals of the business.
On the technical side, I would also need to get up to speed with the specific tools and frameworks used in the company, and improve my skills in working with time-series or sequential data, as that is an area where I have less experience.


# My thought process step by step
## Understanding the data and the problem
- I used Claude to help me understand the meaning of the columns in the dataset and to provide a glossary of terms. Then, I started reading the data.
- I found there are some accounts with zero fills, and how I can associate a trader with an account and with its fills.

- Then, started to understand the problem. As I see it, this is kind of a mass balance problem. I decided to make this instruments and fills dataset a dataset about money. My steps were:
    1. Used the fills data (price x quantity * point_value_usd) to convert to actual money
    2. Dissaggregated the data into buys and sells keeping the comission costs for each instrument
    3. Used the dates to re-create the sessions and tagged each transaction with the session it belongs to
    4. Created two versions of my actual dataset:
        a. Fills aggregated by account / session / instrument - This way I could get to know the profits and loss by instrument each day and in each account
        b. Fills aggregated by account / session - Understand the behavior of each account.
    
    5. Merged the account and traders data to actually perform the requested task: Understand if someone is having a bad session
    I used most of the time in the assessment to build these datasets which would help me reach the final solution.

    6. I created a rule based on the history for each trader: I used a typical definition of anomaly: mean(u) + n * std(u). The mean and std were based on days in which the trader lose money. mean and std were based on their own data (not shared data). The data can be sorted based on how far they are from their mean to get the ones that are having the worse day

## What I'd have done with extra time
If I would have more time I would:
1) Look to gain deeper understanding of the historical behavior of the traders. I couldn't really analyze it as most of my time went in trying to understand the raw data and building the datasets I'd need to analyze.

2) Propose a better rule: 
    - Finding how many stds is the data from its mean has the coldstart problem (what to do with a trader that doesn't have enough trading sessions) 
    - This is also biased to only use days in which the trader didn't get profit, but a bad day for a trader can also mean less profits than usual.
    - Look if the instrument traded is somehow significant for the rule.

3) Answer the other questions asked