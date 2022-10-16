# Import libraries
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import sqlite3 as sql

# Set dashboard page configuration
st.set_page_config(page_title='Library analysis',page_icon='📚',layout='wide')

# Load Data
@st.cache(allow_output_mutation=True)
def load_data():
    try:
        global conn
        conn = sql.connect('library.db')
        df_lib = pd.read_sql_query('select b.BookID,b.Title,b.Author,b.Published,b.Barcode,l.LoanID,l.PatronID,l.LoanDate,\
                      l.DueDate,l.ReturnedDate,p.FirstName,p.LastName,p.Email\
                      from Books b\
                      inner join Loans l\
                      on b.BookID = l.BookID\
                      inner join Patrons p\
                      on l.PatronID = p.PatronID;',conn)
        df_lib['Reader Name'] = df_lib['FirstName'] + ' ' + df_lib['LastName'] 
        df_lib.drop(columns=['FirstName','LastName'],inplace=True)

        df_not_returned_book = pd.read_sql_query('select b.BookID,b.Title,b.Author,b.Published,b.Barcode,l.LoanID,l.PatronID,\
                                        l.LoanDate,l.DueDate,l.ReturnedDate,p.FirstName,p.LastName,p.Email\
                                        from Books b\
                                        inner join Loans l\
                                        on b.BookID = l.BookID\
                                        inner join Patrons p\
                                        on l.PatronID = p.PatronID\
                                        where l.ReturnedDate is null;',conn)
        df_not_returned_book['Reader Name'] = df_not_returned_book['FirstName'] + ' ' + df_not_returned_book['LastName']
        df_not_returned_book.drop(columns=['FirstName','LastName'],inplace=True)

        df_two_readers = pd.read_sql_query('SELECT * FROM Patrons\
                                               WHERE FirstName IN\
                                               (SELECT FirstName FROM Patrons\
                                               GROUP BY FirstName\
                                               HAVING COUNT(*) > 1);',conn)
        
        return df_lib, df_not_returned_book, df_two_readers

    except Exception as e:
        return e
df_lib, df_not_returned_book, df_two_readers = load_data()

# Checking datatypes
#df_lib.dtypes

# Converting datatypes of date columns to date format
try:
    df_lib['LoanDate'] = pd.to_datetime(df_lib['LoanDate'])
    df_lib['DueDate'] = pd.to_datetime(df_lib['DueDate'])
    df_lib['ReturnedDate'] = pd.to_datetime(df_lib['ReturnedDate'])

except Exception as e:
    print(e)

# Checking missing values, if any
#df_lib.isnull().sum() 

# 22 missing values showed for returned date. There is a possibility some readers hasn't returned book.

# Engineer Data
@st.cache(allow_output_mutation=True)
def engineer_data():
    try:
        df_book_issued = df_lib[['LoanDate']].groupby([df_lib.LoanDate.dt.month,df_lib.LoanDate.dt.year]).count()
        s = df_book_issued.squeeze()
        s.index = ['{}_{}'.format(i,j) for i,j in s.index]
        df_book_issued_new = s.to_frame()
        df_book_issued_new.rename(columns={'LoanDate':'Numbers of books issued'},inplace=True)

        df_book_quarter = df_lib.copy()
        df_book_quarter['LoanDate quarter'] = df_book_quarter['LoanDate'].dt.to_period('Q')
        quarter_book_issued = df_book_quarter[['Title','LoanDate quarter']].groupby(['LoanDate quarter']).count()
        quarter_book_issued.rename(columns={'Title':'Number of books issued'},inplace=True)
        quarter_book_issued.reset_index(inplace=True)
        quarter_book_issued['LoanDate quarter'] = quarter_book_issued['LoanDate quarter'].astype(str)

        df_book_year = df_lib.copy()
        df_book_year['LoanDate year'] = df_book_year['LoanDate'].dt.isocalendar().year
        year_book_issued = df_book_year[['Title','LoanDate year']].groupby(['LoanDate year']).count()
        year_book_issued.rename(columns={'Title':'Number of books issued'},inplace=True)
        year_book_issued.reset_index(inplace=True)
        year_book_issued['LoanDate year'] = year_book_issued['LoanDate year'].astype(str)

        df_reader = df_lib.copy()
        s1 = df_reader.groupby(['PatronID','Reader Name'])['LoanDate'].diff(1).tolist()
        df_reader.insert(12,'Gap between books issued',s1)

        return df_book_issued_new, quarter_book_issued, year_book_issued, df_reader
    
    except Exception as e:
        return e

df_book_issued_new, quarter_book_issued, year_book_issued, df_reader = engineer_data()

# Build dashboard
# Add sidebar
try:
    add_sidebar = st.sidebar.selectbox('Aggregate or Individual reader',('Aggregate metrics', 'Individual reader analysis'))

except Exception as e:
    print(e)

try:
    if add_sidebar == 'Aggregate metrics':
        tab1, tab2, tab3, tab4 = st.tabs(['Basic Insights', 'Monthly Insights', 'Quarterly Insights', 'Yearly Insights'])
        
        with tab1:
            most_read_book = df_lib[['Title']].mode().iloc[0].values.tolist()
            most_read_book.append(df_lib['Title'].value_counts()[0])
            most_read_author = df_lib[['Author']].mode().iloc[0].values.tolist()
            most_read_author.append(df_lib['Author'].value_counts()[0])
            max_book_issued = [df_lib[['Reader Name','PatronID']].value_counts()[:1].index[0][0]]
            max_book_issued.append(df_lib[['Reader Name','PatronID']].value_counts()[:1].values[0])
            most_read = most_read_book + most_read_author + max_book_issued
            most_read_book_author_reader = pd.Series(most_read,index=['Most read book','Number of times read','Most read author','Frequency',\
                                                     'Maximum books issued by reader', 'Number of times issued'])

            col1, col2 = st.columns(2)
            columns = [col1, col2]

            count = 0
            for i in most_read_book_author_reader.index:
                with columns[count]:
                    st.metric(label=i,value=most_read_book_author_reader[i])
                    count += 1
                    if count == 2:
                        count = 0
                        

            fig1 = px.scatter(x=df_lib['LoanDate'],y=df_lib['Published'],labels={'x':'Loan Date','y':'Publication Year'},\
                              title='Most read book based on publication year',width=800,height=600)
            st.plotly_chart(figure_or_data=fig1)

            fig2 = px.bar(x=df_not_returned_book['Reader Name'].value_counts().index,y=df_not_returned_book['Reader Name'].value_counts().values,\
                         labels={'x':'Reader Name','y':'Number of times books are not returned'},\
                         title='Number of times reader has not returned a book',width=800,height=400)
            st.plotly_chart(figure_or_data=fig2)

            st.markdown('Details for books that are not returned:')
            df_not_returned_book_details = df_not_returned_book[['Title', 'Published','PatronID','Reader Name', 'LoanDate', 'DueDate',\
                                                                 'ReturnedDate']]
            st.table(df_not_returned_book_details)

            st.markdown('Two readers with same name:')
            st.table(df_two_readers)
            
        
        with tab2:
            col1, col2, col3 = st.columns(3)

            with col1:
                median_books_issued_monthly = int(df_book_issued_new['Numbers of books issued'].median())
                st.metric(label='Median books issued',value=median_books_issued_monthly)

            with col2:
                number_of_months_below_median = len(df_book_issued_new[df_book_issued_new['Numbers of books issued'] < df_book_issued_new\
                                                    ['Numbers of books issued'].median()])
                st.metric(label='Number of months having books issued below median value',value=number_of_months_below_median)

            with col3:
                number_of_months_above_median = len(df_book_issued_new[df_book_issued_new['Numbers of books issued'] >\
                                                                df_book_issued_new['Numbers of books issued'].median()])
                st.metric(label='Number of months having books issued above median value',\
                          value=number_of_months_above_median)
            df_book_issued_new['Percent change in books issued'] = df_book_issued_new['Numbers of books issued'].pct_change()
            fig3 = px.line(x=df_book_issued_new.index,y=df_book_issued_new['Numbers of books issued'],\
                           labels={'x':'Month_year','y':'Number of books issued'},title='Month vs Number of books issued',width=900,height=700)
            st.plotly_chart(figure_or_data=fig3)

            fig4 = px.line(x=df_book_issued_new.index,y=df_book_issued_new['Percent change in books issued'],\
                           labels={'x':'Month_Year','y':'Percent change in books issued'},title='Month vs Percent change in books issued',\
                           width=900,height=700)
            st.plotly_chart(figure_or_data=fig4)

        with tab3:
            col1, col2, col3 = st.columns(3)

            with col1:
                median_books_issued_quarterly = int(quarter_book_issued['Number of books issued'].median())
                st.metric(label='Median books issued',value=median_books_issued_quarterly)

            with col2:
                number_of_quarters_below_median = len(quarter_book_issued[quarter_book_issued['Number of books issued'] < quarter_book_issued\
                                                    ['Number of books issued'].median()])
                st.metric(label='Number of quarters having books issued below median value',value=number_of_quarters_below_median)

            with col3:
                number_of_quarters_above_median = len(quarter_book_issued[quarter_book_issued['Number of books issued'] >\
                                                                  quarter_book_issued['Number of books issued'].median()])
                st.metric(label='Number of quarters having books issued above median value',\
                          value=number_of_quarters_above_median)
                
            quarter_book_issued['Percent change in books issued'] = quarter_book_issued['Number of books issued'].pct_change()
             
            fig5 = px.line(x=quarter_book_issued['LoanDate quarter'],y=quarter_book_issued['Number of books issued'],\
                           labels={'x':'Quarter','y':'Number of books issued'},title='Quarter vs Number of books issued',width=900,height=700)
            st.plotly_chart(figure_or_data=fig5)

            fig6 = px.line(x=quarter_book_issued['LoanDate quarter'],y=quarter_book_issued['Percent change in books issued'],\
                           labels={'x':'Quarter','y':'Percent change in books issued'},title='Quarter vs Percent change in books issued',\
                           width=900,height=700)
            st.plotly_chart(figure_or_data=fig6)

        with tab4:
            col1, col2, col3 = st.columns(3)

            with col1:
                median_books_issued_yearly = int(year_book_issued['Number of books issued'].median())
                st.metric(label='Median books issued',value=median_books_issued_yearly)

            with col2:
                number_of_years_below_median = len(year_book_issued[year_book_issued['Number of books issued'] < year_book_issued\
                                                    ['Number of books issued'].median()])
                st.metric(label='Number of years having books issued below median value',value=number_of_years_below_median)

            with col3:
                number_of_years_above_median = len(year_book_issued[year_book_issued['Number of books issued'] >\
                                                                  year_book_issued['Number of books issued'].median()])
                st.metric(label='Number of years having books issued above median value',\
                          value=number_of_years_above_median)
            
            year_book_issued['Percent change in books issued'] = year_book_issued['Number of books issued'].pct_change()

            fig7 = px.line(x=year_book_issued['LoanDate year'],y=year_book_issued['Number of books issued'],\
                           labels={'x':'Year','y':'Number of books issued'},title='Year vs Number of books issued',width=900,height=700)
            st.plotly_chart(figure_or_data=fig7)

            fig8 = px.line(x=year_book_issued['LoanDate year'],y=year_book_issued['Percent change in books issued'],\
                           labels={'x':'Year','y':'Percent change in books issued'},title='Year vs Percent change in books issued',\
                           width=900,height=700)
            st.plotly_chart(figure_or_data=fig8)

        
    elif add_sidebar == 'Individual reader analysis':
        select_reader = st.number_input('Pick a reader:',1,100)
        
        
        df_reader_select = df_reader[df_reader['PatronID'] == select_reader]
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            reader_name = df_reader_select['Reader Name'].unique()[0]
            st.metric(label='Reader name',value=reader_name) 
        
        with col2:
            min_loandate = df_reader_select['LoanDate'].min().strftime('%Y-%m-%d')
            st.metric(label='Date of first issued book',value=min_loandate)

        with col3:
            max_loandate = df_reader_select['LoanDate'].max().strftime('%Y-%m-%d')
            st.metric(label='Date of latest issued book',value=max_loandate)

        with col4:
            most_read_auth = df_reader_select['Author'].mode().values[0]
            st.metric(label='Most read author',value=most_read_auth)

        with col5:
            min_gap = str(df_reader_select['Gap between books issued'].min(skipna=True)).rstrip('0:')
            st.metric(label='Minimum gap between books issued',value=min_gap)

        with col6:
            max_gap = str(df_reader_select['Gap between books issued'].max(skipna=True)).rstrip('0:')
            st.metric(label='Maximum gap between books issued',value=max_gap)

        avg_dur_bet_books_issued = df_reader['Gap between books issued'].mean()
        avg_dur_bet_cust_issued_books = df_reader_select['Gap between books issued'].mean()

        if avg_dur_bet_cust_issued_books <= avg_dur_bet_books_issued:
            frequent = 'Yes'

        else:
            frequent = 'No'
        
        with col1:
            st.metric(label='Frequent reader or not',value=frequent)    

        
        df_reader_select['LoanDate'] = df_reader_select['LoanDate'].apply(lambda x: x.date())
        df_reader_select['DueDate'] = df_reader_select['DueDate'].apply(lambda x: x.date())
        df_reader_select['ReturnedDate'] = df_reader_select['ReturnedDate'].apply(lambda x: x.date())
        df_reader_select['Gap between books issued'] = df_reader_select['Gap between books issued'].astype(str)
        df_reader_select['Gap between books issued'] = df_reader_select['Gap between books issued'].apply(lambda x: x.rstrip('0:'))
        df_reader_select_new = df_reader_select[['Title','Author','Published','PatronID','LoanDate','DueDate','ReturnedDate',\
                                                 'Gap between books issued']]
        
        st.markdown('Some useful details of reader:')
        st.table(df_reader_select_new)            


except Exception as e:
    print(e)
