#openaidemo3

import sys
import time
sys.path.append('..')

import os
import streamlit as st
from datetime import datetime
from modules.utilities import *
import pathlib
from uuid import uuid4
import asyncio

import streamlit as st
import streamlit.components.v1 as components

import base64

st.set_page_config(page_title='Azure OpenAI Powered Curriculum Management System', layout='wide', page_icon='../images/uni_logo.png')

#------------------------------------------------------------------

# Will need commenting when deploying the app
load_dotenv()
setEnv() #AOAI

#------------------------------------------------------------------
#Demo Configuration

pdf_path = '../documents/Introduction-to-Engineering-Thermodynamics_1.pdf' #1 chapter only
# pdf_path = '../documents/Easy_recipes_Boston_University.pdf'
# pdf_page_nos = [9,10,11,12,13,14] #Pages to generate lecture script for
pdf_page_nos = [9,10]
# pdf_page_nos = [9]

aoai_chat_model = 'gpt-35-turbo' 
aoai_chat_model_version = '0301'
aoai_chat_model_temperature = 0.6
aoai_chat_model_max_tokens = 2000
aoai_chat_model_top_p = 0.5
aoai_chat_model_max_conversations = 1
system_init_text = '''
You are a senior university professor who teaches the many subjects to Engineering students. 
Generate a lecture script based on the textbook content provided to you as input one page at a time.
Do not conclude the lecture at the end of script by saying thank you. The lecture you generate will be linked with other lectures to form a talk on single chapter of the book.
'''
#The lecture should be divided into sections - "Introduction", "Core topic", "Short summary"

aoai_chat_model_deployment = aoai_deployed_models[aoai_chat_model]["version"][aoai_chat_model_version]["deployment_name"] #Azure OpenAI chat completion deployment name

#Speech to text
first_n_chars_to_speech = 600 #Approx 100 chars per line
#------------------------------------------------------------------

# pdfPages = readPDF(source_url=pdf_path)
# print(pdfPages[10])

# Initialization of session vars
if 'chapters' not in st.session_state:
    st.session_state['chapters'] = []
if 'refbooksclicked' not in st.session_state:
    st.session_state['refbooksclicked'] = False
if 'curriculumclicked' not in st.session_state:
    st.session_state['curriculumclicked'] = False
if 'generatescriptclicked' not in st.session_state:
    st.session_state['generatescriptclicked'] = False
if 'pdfPages' not in st.session_state:
    st.session_state['pdfPages'] = []    
if 'lecturescript' not in st.session_state:
    st.session_state['lecturescript'] = ''    
    
#------------------------------------------------------------------

#Added to remove extra space at the top
st.markdown("""
        <style>
               .block-container {
                    padding-top: 2rem;
                    padding-bottom: 1rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)



#------------------------------------------------------------------

with st.container():

    top_col1,top_col2 = st.columns([80,20])
    top_col1.write(f'<div style="font-size:24px;"><b>NextGen</b> Institute of Engineering</div>',unsafe_allow_html=True) 
    top_col2.write(f'<div style="font-size:16px;" align="right"><a href="https://github.com/MaheshSQL/openai-cognitive-semantic-search">Github Repo (TBA)</a></div>',unsafe_allow_html=True)     
    st.image(image='../images/uni_1.png', use_column_width = 'always')

    top_bar_content = 'Welcome <b>Professor James T.</b>'
    st.write(f'<div style="font-size:16px; color:black;background-color:#3498db;border:1px solid #93bfe6;border-bottom-left-radius:5px;border-bottom-right-radius:5px;border-top-right-radius:5px;border-top-left-radius:5px;padding-left:5px;padding-right:5px;padding-top:5px;padding-bottom:5px">{top_bar_content}</div>',unsafe_allow_html=True) 
    st.write('###')
    col1, col2, col3 = st.columns([20,40,40])
    
    selectbox_modules = col1.selectbox('Select module',
                   ('Admissions', 'Student Management', 'Financial Reports', 'Curriculum Management'),
                   key='selectbox_modules'
                   )
    
    if selectbox_modules =='Curriculum Management':
        # col1.write(selectbox_modules)
        selectbox_engineering_courses = col1.selectbox('Select engineering course',
                   ('Bachelor of Civil Engineering','Bachelor of Electrical Engineering', 'Bachelor of Mechanical Engineering', 'Bachelor of Computer Science', 'Bachelor of Data Science', 'Bachelor of Chemical Engineering'),
                   key='selectbox_engineering_courses'
                   )
        
        if selectbox_engineering_courses =='Bachelor of Mechanical Engineering':        
            selectbox_mech_units = col1.selectbox('Select unit',
                    ('1004 Engineering Materials', '3405 Numerical Methods and Modelling', '3023 Advanced Mathematics Applications',
                     '3424 Measurement and Instrumentation', '3024 Engineering Thermodynamics'),
                    key='selectbox_mech_units'
                    )
            
            if selectbox_mech_units =='3024 Engineering Thermodynamics':
                
                col1.write('###')

                col1_1, col1_2 = col1.columns([50,50])

                col1_1.write('Curriculum details')
                btn_load_curriculum_details = col1_2.button(label='Load', key='btn_load_curriculum_details')
                col1_1.write('Reference books')
                btn_load_reference_books = col1_2.button(label='Load', key='btn_load_reference_books')
                
                if btn_load_curriculum_details or st.session_state['curriculumclicked']:
                    description  = getUnitCurriculum(id=3024)[0]
                    outcome = getUnitCurriculum(id=3024)[1]
                    col2.write(f'<div style="font-size:16px; color:black;background-color:#e6eaed;border:1px solid #3498db;border-bottom-left-radius:5px;border-bottom-right-radius:5px;border-top-right-radius:5px;border-top-left-radius:5px;padding-left:5px;padding-right:5px;padding-top:5px;padding-bottom:5px">{description}</div>',unsafe_allow_html=True) 
                    col2.write('###')
                    #e6eaed
                    col2.write(f'<div style="font-size:16px; color:black;background-color:#e6eaed;border:1px solid #3498db;border-bottom-left-radius:5px;border-bottom-right-radius:5px;border-top-right-radius:5px;border-top-left-radius:5px;padding-left:5px;padding-right:5px;padding-top:5px;padding-bottom:5px">{outcome}</div>',unsafe_allow_html=True) 

                    st.session_state['curriculumclicked'] = True

                if btn_load_reference_books or st.session_state['refbooksclicked']:

                    pdfPages = readPDF(source_url=pdf_path)
                    # col3.write(str(len(pdfPages)))

                    st.session_state['pdfPages'] = pdfPages

                    tab1, tab2 = col3.tabs(["Reference Book", "Lecture Script"])
                    
                    # Opening file from file path
                    with open(pdf_path, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

                        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700" type="application/pdf"></iframe>'
                        # print(pdf_display)

                        # Displaying File
                        tab1.markdown(pdf_display, unsafe_allow_html=True)

                    st.session_state['refbooksclicked'] = True


                if st.session_state['refbooksclicked']:
                     
                    col2.write('###')                   
                    
                    col2.write('<div><b>Chapters</b></div>',unsafe_allow_html=True)                 

                    col2_1, col2_2, col2_3, col2_4, col2_5 = col2.columns([10,10,10,10,10])                    
                    btn_chapter_1 = col2_1.button(label='Chapter - 1', key='btn_chapter_1')                    
                    btn_chapter_2 = col2_2.button(label='Chapter - 2', key='btn_chapter_2')
                    btn_chapter_3 = col2_3.button(label='Chapter - 3', key='btn_chapter_3')
                    btn_chapter_4= col2_4.button(label='Chapter - 4', key='btn_chapter_4')                    
                    btn_chapter_5= col2_5.button(label='Chapter - 5', key='btn_chapter_5')
        
                    chapters = []
                    if btn_chapter_1:
                            chapters = st.session_state['chapters']
                            if 'Chapter - 1' not in chapters:
                                chapters.append('Chapter - 1')
                            st.session_state['chapters'] = chapters                        

                    if btn_chapter_2:
                            chapters = st.session_state['chapters']
                            if 'Chapter - 2' not in chapters:
                                chapters.append('Chapter - 2')
                            st.session_state['chapters'] = chapters                        

                    if btn_chapter_3:
                            chapters = st.session_state['chapters']
                            if 'Chapter - 3' not in chapters:
                                chapters.append('Chapter - 3')
                            st.session_state['chapters'] = chapters  

                    if btn_chapter_4:
                            chapters = st.session_state['chapters']
                            if 'Chapter - 4' not in chapters:
                                chapters.append('Chapter - 4')
                            st.session_state['chapters'] = chapters  

                    if btn_chapter_5:
                            chapters = st.session_state['chapters']
                            if 'Chapter - 5' not in chapters:
                                chapters.append('Chapter - 5')
                            st.session_state['chapters'] = chapters  

                chapters = st.session_state['chapters']
                # print(f'chapters:{chapters}')
                if len(chapters) > 0:

                    # print('In len(chapters) > 0')

                    chapter_names = ''
                    for chapter_name in chapters:
                         chapter_names+= chapter_name + ', '

                    chapter_names = chapter_names[:-2]
                    # col2.write(chapter_names)
                    col2.write(f'<div style="font-size:16px; color:black;background-color:#e6eaed;border:1px solid #93bfe6;border-bottom-left-radius:5px;border-bottom-right-radius:5px;border-top-right-radius:5px;border-top-left-radius:5px;padding-left:5px;padding-right:5px;padding-top:5px;padding-bottom:5px">{chapter_names}</div>',unsafe_allow_html=True) 
                    col2.write('###')

                    col2.write('<div><b>Education Copilot</b></div>',unsafe_allow_html=True)
                    col2_11, col2_22, col2_33 = col2.columns([33,33,33])                    
                    btn_generate_lecture_script = col2_11.button(label='Generate lecture script', key='btn_generate_lecture_script') 

                    if btn_generate_lecture_script or st.session_state['generatescriptclicked']:

                        user_input_list = []
                        assistant_output_list = []
                        lecture_script = ''

                        progress_bar_location = col2_11.empty()
                        progress_bar = progress_bar_location.progress(0,'')

                        if len(st.session_state['lecturescript']) > 0:
                             lecture_script = st.session_state['lecturescript']    
                        else:                
                            pdfPages = st.session_state['pdfPages']
                            print(f'len(pdfPages):{len(pdfPages)}')                                                        
                                
                            for pdfPage in pdfPages:     
                                
                                #Only process pages in demo scope
                                if len(pdfPage) > 0:
                                    page_no = pdfPage[1]                    
                                    # print(f'page_no:{str(page_no)}')
                                    progress_bar.progress((page_no/len(pdfPages)),'Processing')

                                    if not page_no in pdf_page_nos:
                                        continue

                                chat_gpt_query = 'Reply with - no reference book content supplied.'
                                if len(pdfPage) > 0:
                                    chat_gpt_query = cleanseText(input_text=pdfPage[0])
                            
                                user_input_list.append(chat_gpt_query)    

                                print('Calling getChatCompletion()')                        

                                assistant_output = ''
                                assistant_output = getChatCompletion(system_init_text = system_init_text, #+ content,
                                                user_input_list=user_input_list,
                                                assistant_output_list=assistant_output_list, 
                                                aoai_chat_model=aoai_chat_model_deployment, 
                                                aoai_chat_model_temperature=aoai_chat_model_temperature, 
                                                aoai_chat_model_max_tokens=aoai_chat_model_max_tokens, 
                                                aoai_chat_model_top_p=aoai_chat_model_top_p)
                                
                                assistant_output_list.append(assistant_output)
                                lecture_script=lecture_script +'.'+assistant_output
                                # print(f'assistant_output:{assistant_output}')

                                #Only keep last N conversation history                                
                                aoai_chat_model_max_conversations = aoai_chat_model_max_conversations-1

                                if len(user_input_list) > aoai_chat_model_max_conversations:
                                    user_input_list = user_input_list[-aoai_chat_model_max_conversations:]
                                    print('user_input_list trimmed.')
                                if len(assistant_output_list) > aoai_chat_model_max_conversations:
                                    assistant_output_list = assistant_output_list[-aoai_chat_model_max_conversations:]
                                    print('assistant_output_list trimmed.')

                        if lecture_script[0:1] == '.':  
                            lecture_script = lecture_script[1:] #Remove first dot.
                        
                        # tab2.write(lecture_script)                        
                        #e6eaed
                        tab2.write(f'<div style="font-size:16px; color:black;background-color:#ffffb3;border:1px solid #3498db;border-bottom-left-radius:5px;border-bottom-right-radius:5px;border-top-right-radius:5px;border-top-left-radius:5px;padding-left:5px;padding-right:5px;padding-top:5px;padding-bottom:5px;font-family:Consolas ">{lecture_script}</div>',unsafe_allow_html=True) 

                        progress_bar.progress(100,'Completed')
                        time.sleep(1)
                        progress_bar_location.empty()
                        st.session_state['lecturescript'] = lecture_script
                         
                        st.session_state['generatescriptclicked'] = True

                        btn_generate_recording = col2_22.button(label='Generate recording', key='btn_generate_recording')

                        # #Remove space at top of dropdown
                        # st.markdown(
                        #     """
                        #     <style>
                        #     [data-baseweb="select"] {
                        #         margin-top: -32px;
                        #     }
                        #     </style>
                        #     """,
                        #     unsafe_allow_html=True,
                        # )
                         

                        speaker_radio = col2_22.radio("Select speaker", ('Bella', 'Darren'), label_visibility='visible')
                        # selectbox_speaker = col2_22.selectbox('Select speaker', ('Amber', 'Ana', 'Brandon'), 
                        #                                       key='selectbox_speaker', label_visibility='hidden')

                        speech_synthesis_voice_name = 'en-GB-BellaNeural'
                        if speaker_radio == 'Bella':
                             speech_synthesis_voice_name = 'en-GB-BellaNeural'                        
                        elif speaker_radio == 'Darren':
                            speech_synthesis_voice_name = 'en-AU-DarrenNeural'
                             

                        if btn_generate_recording:                        

                            if len(lecture_script) >= first_n_chars_to_speech:   
                                # col2_33.write('Playing..')                             
                                textToSpeech(text=lecture_script[:first_n_chars_to_speech], speech_synthesis_voice_name=speech_synthesis_voice_name)   
