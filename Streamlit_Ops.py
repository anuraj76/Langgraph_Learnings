import time
from operator import index

import st
import streamlit as st
import pandas as pd
from streamlit import camera_input

#Display data on the screen:

# 1. st.write()
# 2. Magic


st.write('Hello, Streamlit!')

l1 = [1, 2, 3, 4, 5]
st.write(l1)

l2 = ['apple', 'banana', 'cherry']
st.write(l2)

d1 = dict(zip(l1, l2))

st.write(d1)


#Using Magic

'Display using magic:smile:'

# df = pd.DataFrame({
#     'A': [1, 2, 3, 4, 5],
#     'B': [10, 20, 30, 40, 50]
# })



#Text Input

name = st.text_input('Enter your name:')

if name:
    st.write('Hello,', name)

#Numeric Input


number = st.number_input('Enter a number:')

st.write('The number is:', number)

st.divider()

clicked = st.button('Click me!')

if clicked:
    st.write('You clicked the button!')

#Checkbox

agree = st.checkbox('I Agree!')

if agree:
    'Great!! You agreed!'
    #st.write('You agreed!')

checked = st.checkbox('Continue', value=True)

if checked:
    st.write('You continued!')

df = pd.DataFrame({name: ['Alice', 'Bob', 'Charlie'], 'Age': [25, 30, 35]})

if st.checkbox('Show DataFrame'):
    st.write(df)
st.divider()
#Radio Buttons

color = st.radio('Select a color:', ['Red', 'Green', 'Blue'], index=1, key='color_radio')
st.write('You selected:', color)
st.write('The selected color is', color, {st.session_state.color_radio: color})


st.divider()
#Selectbox

cities = ['New York', 'London', 'Tokyo', 'Paris']
city = st.selectbox('Select a city:', cities, index=2, key='city_select')
st.write('You selected:', city)

st.divider()

#Slider
x = st.slider('X-axis:', value=15, min_value=12, max_value= 70, step=3,  key='slider')
st.write('X-axis value:', x)

st.divider()

#File uploader

uploaded_file = st.file_uploader('Upload a CSV file', type=['csv'])

if uploaded_file:
    st.write('File uploaded:', uploaded_file.name)
    if uploaded_file.name.endswith('.csv'):
        from io import StringIO
        stringio = StringIO(uploaded_file.read().decode('utf-8'))
        string_data = stringio.read()


st.divider()

# #Camera Input
#
# camera_photo = st.camera_input('Camera')
# if camera_photo:
#     st.image(camera_photo, use_column_width=True)

#Sidebar


my_side_bar = st.sidebar.selectbox('Select country:', ['US', 'UK', 'DE', 'FR', 'JP'])

my_slider = st.sidebar.slider('Temperature C')

#Columns

left_column, right_column = st.columns(2)

import random
data = {random.randint(1, 100) for _ in range(10)}
with left_column:
    st.write('Left Column')
    st.subheader('A line chart')
    st.line_chart(data)

right_column.subheader('DATA')
# right_column.write(data[:20])

column1, column2, column3 = st.columns([1, 1, 0.5])
column1.markdown('### Column 1')
# column2.write(data[:20])

with column3:
    st.subheader('An image')
    st.image('https://picsum.photos/200', use_column_width=True)


#Expander

with st.expander('Expand me'):
    st.bar_chart({'A': 10, 'B': 20, 'C': 30})
    st.write('This is an image of a dog')
    st.image('https://picsum.photos/200', use_column_width=True)

#Progress Bar

import time
st.write('Starting execution...')
latest_iteration = st.empty()

progress_text = 'Ops in Progress...'
my_bar = st.progress(0, text=progress_text)
time.sleep(3)

for i in range(100):
    latest_iteration.text(f'Iteration {i+1}')
    my_bar.progress(i + 1)
    time.sleep(0.2)

st.write('Execution completed! :+1:')





