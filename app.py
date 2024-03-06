from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import Ollama
import streamlit as st
import time
import sqlite3
from datetime import datetime, timedelta

# Connect to the SQLite database
conn = sqlite3.connect('user-data.db')
c = conn.cursor()

# Create a table to store responses if it doesn't exist already
c.execute('''CREATE TABLE IF NOT EXISTS history
             (id INTEGER PRIMARY KEY, question TEXT, response TEXT, model TEXT, date_saved TEXT)''')
conn.commit()

# various functions
def process_prompt():
    # global response
    response = llm(prompt)
    st.success(response)
    save_response(prompt, response)

# Function to save response to the database
def save_response(question,response):
    date_saved = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO history (question, response, model, date_saved) VALUES (?, ?, ?, ?)",
              (question, response, model, date_saved))
    conn.commit()
    # st.info('Response added to history!')
    
# Function to retrieve responses from the last 7 days
def get_recent_responses():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    c.execute("")
    c.execute("SELECT date_saved, id FROM history WHERE date_saved BETWEEN ? AND ? limit 100", (start_date, end_date))
    recent_responses = c.fetchall()
    return recent_responses

def measure_execution_time(task_function):
    """
    Measures the execution time of a given task function.

    Args:
    task_function (function): A function representing the task whose execution time is to be measured.

    Returns:
    float: Execution time in seconds.
    """
    start_time = time.time()
    task_function()
    end_time = time.time()
    return round(end_time - start_time, 2)

# Define a sample task function
def sample_task():
    # Simulate a task by sleeping for 2 seconds
    time.sleep(2)

# Streamlit interface
st.title('Ask Anything')
model= st.sidebar.selectbox('Select a model', options=['llama2', 'mistral', 'orca-mini'])
# Text box for user input
prompt = st.text_area("Enter your prompt:")
# Sidebar to display recent descriptions
st.sidebar.subheader('Chat History')
recent_responses = get_recent_responses()
selected_date = st.sidebar.radio('Last 7 days', [date_saved[0] for date_saved in recent_responses])

# model definition
llm = Ollama(
    model=model, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)



if st.button('Send'):
    # Using threading to handle the request without blocking the Streamlit interface
    # threading.Thread(target=send_request, args=(prompt,)).start()
    with st.spinner("Processing your request using model: " + model):
        if not prompt:
            st.warning("Please enter a prompt.")
        # elif not labels:
        #     st.warning("Please enter at least one label for classification.")
        else:
            # process_prompt
            # Measure and print the execution time of the sample task
            
            execution_time = measure_execution_time(process_prompt)
            st.caption(f"Task execution time: {execution_time} seconds")
 

st.markdown('---')      
# Display details for the selected record
if selected_date:
    c.execute("SELECT * FROM history WHERE date_saved=?", (selected_date,))
    selected_record = c.fetchone()
    # st.subheader('Chat detail for: ' + {selected_record[4]})
    st.caption('Chat detail for: ' + ', '.join({selected_record[4]}))

    st.write(f"Question: {selected_record[1]}")
    st.caption(f" {selected_record[2]}")
    st.write(f"Model: {selected_record[3]}")

# Close the database connection when Streamlit app closes
conn.close()

  