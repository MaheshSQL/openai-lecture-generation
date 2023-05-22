#------------Imports---------------
import os
from dotenv import load_dotenv
import openai
from pypdf import PdfReader
import requests
import json
import logging
import azure.cognitiveservices.speech as speechsdk


'''
Initialise environment variables
'''
def setEnv():
    try:
        openai.api_type = os.getenv('OPENAI_API_TYPE')
        openai.api_base = os.getenv('OPENAI_API_BASE')
        openai.api_version = os.getenv('API_VERSION')
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        return True
    except Exception as e:
        logging.error(f'Error setEnv(): {e}')    
        return False

'''
documentPath: Path to document (pdf/word/etc.)
'''
def getDocumentExtension(documentPath):
    try:
        return os.path.basename(documentPath).split('.')[len(os.path.basename(documentPath).split('.'))-1]
    except Exception as e:
        logging.error(f'Error getDocumentExtension(): {e}')    
        return None

'''
Read PDF documents and return the list of page content
'''
def readPDF(source_url):
    try:
        document_pages = []
        reader  = PdfReader(source_url)

        for i, page in enumerate(reader.pages):
            document_pages.append([page.extract_text(),i+1, source_url]) #text, page_no, doc_path

        return document_pages
    
    except Exception as e:
        logging.error(f'Error readPDF(): {e}')
        return []
    
def getUnitCurriculum(id):

    try:
        description = None
        outcome = None

        if id ==3024:
            description = '''
            <b>Description:</b> <br/>
            This unit is about thermodynamics from an engineering perspective. It covers definitions of properties, forms of energy, and systems.<br/>
It discusses the behavior of ideal gases and liquid-vapor systems. The 1st and 2nd laws of thermodynamics are applied to typical systems such as internal combustion engines.
Issues regarding the use of thermodynamic systems are analyzed, such as fuel sources, thermal efficiency, pollution, and emissions.
            '''

            outcome = '''
            <b>Outcome:</b> <br/>
             (1) Decipher inquiries, predicaments, and directives inscribed in the parlance of engineering thermodynamics; <br/>
             (2) Establish systems, categories of energy, substances' states, and properties; <br/>
             (3) Employ the ideal gas equations, acknowledging their restrictions; <br/>
             (4) Acquire pertinent information from thermodynamic property tables and charts; <br/>
             (5) Scrutinize uncomplicated systems, unvarying-state processes, and cycles utilizing the 1st and 2nd Laws of thermodynamics; and <br/>
             (6) Explicate the societal and ecological repercussions of typical thermodynamic systems.
            '''

        return description, outcome
    
    except Exception as e:
        logging.error(f'Error getUnitCurriculum(): {e}')
        return None, None

'''
Get Chat completion.
'''
def getChatCompletion(system_init_text,user_input_list,assistant_output_list, aoai_chat_model, aoai_chat_model_temperature, aoai_chat_model_max_tokens, aoai_chat_model_top_p):
    try:
        #Create ChatML
        prompt = ''
        prompt += '<|im_start|>system\n' + system_init_text + '\n<|im_end|>\n'

        for i, item in enumerate(user_input_list):
            if i < (len(user_input_list) - 1):
                 prompt += '<|im_start|>user\n' + user_input_list[i] + '\n<|im_end|>\n'
                 prompt += '<|im_start|>assistant\n' + assistant_output_list[i] + '\n<|im_end|>\n'
            else:
                prompt += '<|im_start|>user\n' + user_input_list[i] + '\n<|im_end|>\n'
                prompt += '<|im_start|>assistant\n' 

        # print(f'IM prompt:{prompt}')

        response = openai.Completion.create(
            engine=aoai_chat_model, # The deployment name you chose when you deployed the ChatGPT model
            prompt=prompt,
            temperature=aoai_chat_model_temperature,
            max_tokens=aoai_chat_model_max_tokens,
            top_p=aoai_chat_model_top_p,
            stop=["<|im_end|>"])
        
        query_result = response['choices'][0]['text']        
        # print(f'response:{response}')
        return query_result
    
    except Exception as e:        
        logging.error(f'Error getChatCompletion(): {e}')        
        return None                         

'''
Removes new line characters, double spaces
input_text: Piece of text
'''
def cleanseText(input_text):
    try:
        input_text_cleansed = None
        input_text_cleansed = input_text.replace('\n',' ') #Remove new line characters
        input_text_cleansed = input_text_cleansed.replace('  ',' ') #Remove double space

        return input_text_cleansed
    except Exception as e:
        logging.error(f'Error cleanseText(): {e}')
        return None

def textToSpeech(text, speech_synthesis_voice_name):
    try:
        speech_key = os.getenv('SPEECH_KEY')
        service_region = os.getenv('SPEECH_SERVICE_REGION')

        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        
        # Set the voice name, refer to https://aka.ms/speech/voices/neural for full list.
        speech_config.speech_synthesis_voice_name = speech_synthesis_voice_name

        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

        #The synthesized speech is expected to be heard on the speaker with below line executed.
        result = speech_synthesizer.speak_text_async(text).get()
        # result = speech_synthesizer.speak_text(text).get()

        #Check the synthesis result.
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized to speaker for text [{}]".format(text))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
            print("Did you update the subscription info?")


    except Exception as e:
        logging.error(f'Error textToSpeech(): {e}')
        return None

#-----------------------------------

aoai_deployed_models = {

    "text-search-ada-doc-001":{
        "version":{
            "1":{
                "deployment_name": "text-search-ada-doc-001-v1",
                "dim": 1024    
                }
            }    
        },

    "text-search-babbage-doc-001":{
        "version":{
            "1":{
                "deployment_name": "text-search-babbage-doc-001-v1",
                "dim": 2048    
                }
            }    
        },

    "text-search-curie-doc-001":{
        "version":{
            "1":{
                "deployment_name": "text-search-curie-doc-001-v1",
                "dim": 4096    
                }
            }    
        },

    "text-search-davinci-doc-001":{
        "version":{
            "1":{
                "deployment_name": "text-search-davinci-doc-001-v1",
                "dim": 12288    
                }
            }    
        },

    "text-embedding-ada-002":{
        "version":{
            "1":{
                "deployment_name": "text-embedding-ada-002-v1",
                "dim": 1536    
                }
            }    
        },

    "text-davinci-003":{
        "version":{
            "1":{
                "deployment_name": "text-davinci-003-v1"                
                }
            }    
        },

    "gpt-35-turbo":{
        "version":{
            "0301":{
                "deployment_name": "gpt-35-turbo-v0301"                
                }
            }    
        }

    }