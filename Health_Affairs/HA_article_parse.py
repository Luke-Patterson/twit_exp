# take the extracted articles and apply filters to weed out unwanted articles
import pandas as pd
import pycountry
kword_df = pd.read_csv('output/HA_articles.csv')
kword_df['Title'] = kword_df['Title'].str.replace('â€™','')

# filter out the titles of articles from blacklisted categories from grace
blacklist = ['Accountable Care Organizations', 'Affordable Care Act', 'Considering Health Spending',
'Culture of Health', 'Ethics', 'Global Health Policy', 'Government Programs & Policies',
'Health Care Finance', 'Health Law', 'Health Professionals', 'Health Reform',
'Health Services Administration', 'HIV/AIDS', 'Legal & Regulatory Issues',
'Managed Care', 'Markets', 'Medicaid', 'Oral Health', 'Payment', 'Politics',
'Precision Medicine', 'Private Health Insurance', 'Public Opinion', 'State Issues']

kword_df = kword_df.loc[kword_df['Tag'].apply(lambda x: x not in blacklist)]

# also add remove some keywords that were too broad
kword_blacklist = ['cancer', 'diabetes', 'mental health']
kword_df = kword_df.loc[kword_df['Keyword'].apply(lambda x: x not in kword_blacklist)]

# remove some categories that returned too few articles
cat_blacklist = ['NUTRITION','ADMINSTRATIVE BURDEN','EMERGING TECHNOLOGY',
    'PRACTICE TRANSFORMATION']
kword_df = kword_df.loc[kword_df['IMPAQ Category'].apply(lambda x: x not in cat_blacklist)]

# remove some of the unwanted types of articles
type_whitelist = ['RESEARCH ARTICLE','ANALYSIS & COMMENTARY','ANALYSIS','REVIEW ARTICLE']
kword_df = kword_df.loc[kword_df['Type'].apply(lambda x: x in type_whitelist)]

# drop articles mentioning another country
country_names = [i.name for i in pycountry.countries]
country_names.remove('United States')
country_names += ['Africa','South America','Asia','Oceania','Europe','Scotland']
country_names = [i.lower() for i in country_names]
kword_df = kword_df.loc[kword_df['Title'].apply(lambda x: any(i in x.lower() for i in country_names) == False)]

# drop articles related to child care
title_blacklist = ['child', 'pediatric', 'children', 'adolescent', 'maternity','adolescents','pediatrics']
# drop articles related to measurement
title_blacklist += ['measure', 'measurement', 'measurements', 'measures', 'measuring','measured']
# articles about insurance
title_blacklist += ['insurance', 'insured','insuring', 'aca','aco']
# articles about cost
title_blacklist += ['cost', 'costing', 'costs','costed', 'spending','spend',
    'finance', 'financial','financing', 'payment', ' pay ','payer']

kword_df = kword_df.loc[kword_df['Title'].apply(lambda x: any(i in x.lower() for i in title_blacklist) == False)]

try:
    kword_df = kword_df.drop('Unnamed: 0', axis = 1)
except:
    pass

kword_df.reset_index(inplace = True, drop=True)
kword_df.to_csv('output/HA_articles_parsed.csv', encoding = 'utf-8')
