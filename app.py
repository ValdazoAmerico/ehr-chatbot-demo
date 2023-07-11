import streamlit as st

from utils import db

import streamlit as st
from streamlit_chat import message
import streamlit_scrollable_textbox as stx

from langchain.chains import ConversationChain
from langchain.prompts.prompt import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
import datetime
import os

if 'patient_uid' not in st.session_state:
	st.session_state['patient_uid'] = []

if 'ai' not in st.session_state:
        st.session_state['ai'] = []

today = datetime.datetime.now()
today = today.strftime("%Y-%m-%d")

def ask_patient_hc(context, question):

	default_template = f"""Eres un asistente médico inteligente encargado de proporcionar información relevante sobre la historia clínica de un paciente. Las consultas se encuentran organizadas en orden cronológico, de la más antigua a la más reciente, separadas por '###'. Ten en cuenta que las fechas siguen el formato YYYY-MM-DD y que la fecha de hoy es {today}. En la historia clínica, 'Nota médica' refiere a las anotaciones del médico que atendió la consulta, 'Diagnóstico' es el diagnóstico proporcionado por el médico, 'Motivos de consulta' son los síntomas o problemas mencionados por el paciente antes de su atención, 'Tratamiento' son las recomendaciones brindadas por el médico, 'Medicación / Prescripción médica' son los medicamentos recetados y 'Reposo' indica las horas recomendadas de descanso para el paciente. Si la pregunta no está relacionada con el paciente, responde con 'No lo sé'.
				Historia clínica:
				{context}"""

	chat_template = default_template + """Historial de chat:
											{history}
											Human: {input}
											AI:"""

	prompt = PromptTemplate(input_variables=["history", "input"], template=chat_template)
	chat = ChatOpenAI(temperature=0, max_tokens=1500, model="gpt-4")
	memory = ConversationBufferWindowMemory(k=2)
	if len(st.session_state.ai) == 1:
		memory.save_context({"input": st.session_state.past[-1]}, {"output": st.session_state.ai[0]})
	if len(st.session_state.ai) > 1:
		memory.save_context({"input": st.session_state.past[-2]}, {"output": st.session_state.ai[-2]})
		memory.save_context({"input": st.session_state.past[-1]}, {"output": st.session_state.ai[-1]})
	
	prompt = PromptTemplate(input_variables=["history", "input"], template=chat_template)

	conversation = ConversationChain(
		llm=chat,
		verbose=True,
		memory=memory,
		prompt=prompt)
	response = conversation.predict(input=question)
	st.session_state.ai.append(response)
	return response




def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == 'uma2023':
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():

	col1, col2 = st.columns(2)
	# Create the navigation bar for switching between tabs
	with col1:
			st.title("ÜmaBot 👩‍⚕️\nOpenAI GPT-3.5 🤖 + Langchain ⛓️ + Streamlit ")
		
			if 'generated' not in st.session_state:
				st.session_state['generated'] = []
		
			if 'past' not in st.session_state:
				st.session_state['past'] = []
		
			if 'patient_uid' not in st.session_state:
				st.session_state['patient_uid'] = []
				
			if 'patient_data' not in st.session_state:
				st.session_state['patient_data'] = []
		
			if "temp" not in st.session_state:
				st.session_state["temp"] = ""
			if "user_input" not in st.session_state:
				st.session_state["user_input"] = []
		
			def clear_text():
				st.session_state["temp"] = st.session_state["text"]
				st.session_state["text"] = ""
		
		
			def get_text():
				input_text = st.text_input("You: ", "", key="text",on_change=clear_text)
				st.session_state['user_input'].append(input_text)
				if st.session_state['temp'] == "":
					return "Hola!"
				else:
					return st.session_state['temp']
		
			user_input = get_text()
		
			if user_input:
				if user_input == 'Hola!':
					st.session_state['past'] = []
					st.session_state['generated'] = []
					st.session_state.past.append("Hola")
					st.session_state['generated'].append('¡Hola! Soy ÜmaBot. Por favor, ingresa un número del 1 al 5 como ID de usuario.')
				else:
					try:
						if st.session_state['generated'][-1] == '¡Hola! Soy ÜmaBot. Por favor, ingresa un número del 1 al 5 como ID de usuario.':
							st.session_state.patient_uid.append(user_input) 
							st.session_state.past.append(user_input)
							st.session_state['generated'].append("Haz una consulta sobre la historia clínica del paciente")
							
						else:
							# output = generate_response(user_input)
							uid = st.session_state.patient_uid[0]
							output = ask_patient_hc(st.session_state.patient_data[0], user_input)
							st.session_state.past.append(user_input)
							st.session_state['generated'].append(output)
					except:
						pass
		
			if st.session_state['generated']:
				for i in range(len(st.session_state['generated']) - 1, -1, -1):
					message(st.session_state["generated"][i], key=str(i))
					message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
		
	with col2:
		st.title("EHR Patient Data")
		# Example EHR patient data

		# Open txt file and read lines
		
		def opener_txt(number):
			with open('./patient_data/patient' + str(number) + '.txt', 'r') as file:
				patient_data = file.readlines()
			return patient_data
				
		patient_data = None

		if st.session_state['patient_uid'] and st.session_state['patient_uid'][0]:
			data = opener_txt(st.session_state['patient_uid'][0])
			st.session_state.patient_data.append(data)
			patient_data = data

		# Display the EHR patient data
		if patient_data:
			st.subheader(f"Patient '{st.session_state['patient_uid'][0]}' Information")
			stx.scrollableTextbox(patient_data,height = 350)


COMMENT_TEMPLATE_MD = """{} - {}
> {}"""


def space(num_lines=1):
	"""Adds empty lines to the Streamlit app."""
	for _ in range(num_lines):
		st.write("")



conn = db.connect()
comments = db.collect(conn)

with st.expander("💬 Abrir comentarios"):
		st.write("**Comentarios:**")
		for index, entry in enumerate(comments.itertuples()):
			st.markdown(COMMENT_TEMPLATE_MD.format(entry.name, entry.date, entry.comment))

			is_last = index == len(comments) - 1
			is_new = "just_posted" in st.session_state and is_last
			if is_new:
				st.success("☝️ Tu comentario fue guardado exitosamente.")
	
		space(2)

		# Insert comment

		st.write("**Dejá tu comentario:**")
		form = st.form("comment")
		name = form.text_input("Nombre")
		comment = form.text_area("Comentario")
		submit = form.form_submit_button("Guardar")

		if submit:
			#date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			db.insert(conn, [[name, today, comment]])
			if "just_posted" not in st.session_state:
				st.session_state["just_posted"] = True
			st.experimental_rerun()
