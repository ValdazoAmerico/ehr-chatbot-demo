import streamlit as st
from streamlit_chat import message
import streamlit_scrollable_textbox as stx

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts.prompt import PromptTemplate
from langchain.chat_models import ChatOpenAI
import datetime
import os

key = st.secrets["OPENAI_API_KEY"]
os.environ["OPENAI_API_KEY"] = key

today = datetime.datetime.now()
today = today.strftime("%Y-%m-%d")

def ask_patient_hc(context, question):
  memory = ConversationBufferWindowMemory(k=2)

  default_template = f"""Eres un asistente médico inteligente encargado de proporcionar información relevante sobre la historia clínica de un paciente. Las consultas se encuentran organizadas en orden cronológico, de la más antigua a la más reciente, separadas por '###'. Ten en cuenta que las fechas siguen el formato YYYY-MM-DD y que la fecha de hoy es {today}. En la historia clínica, 'Nota médica' refiere a las anotaciones del médico que atendió la consulta, 'Diagnóstico' es el diagnóstico proporcionado por el médico, 'Motivos de consulta' son los síntomas o problemas mencionados por el paciente antes de su atención, 'Tratamiento' son las recomendaciones brindadas por el médico, 'Medicación / Prescripción médica' son los medicamentos recetados y 'Reposo' indica las horas recomendadas de descanso para el paciente. Si la pregunta no está relacionada con el paciente, responde con 'No lo sé'.

Historia clínica:
{context}
"""

  chat_template = default_template + """Historial de chat:
{history}
Human: {input}
AI:"""

  prompt = PromptTemplate(input_variables=["history", "input"], template=chat_template)
  chat = ChatOpenAI(temperature=0,model_name="gpt-3.5-turbo", max_tokens=200)
  conversation = ConversationChain(
    llm=chat,
    memory=memory,
    verbose=True,
    prompt=prompt
)
  response = conversation.predict(input=question)

  return response



# This function uses the OpenAI Completion API to generate a 
# response based on the given prompt. The temperature parameter controls 
# the randomness of the generated response. A higher temperature will result 
# in more random responses, 
# while a lower temperature will result in more predictable responses.

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

    def get_text():
        input_text = st.text_input("You: ", "Hola!", key="input")
        return input_text 

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
                    print("CONTEXT", st.session_state.patient_data[0])
                    print("QUESTION", user_input)
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
    patient_data1 = """Paciente de 49 años, de sexo Femenino.

Fecha: 2021-05-15

Nota médica: 48 años, previamente sana. 
refiere cuadro clínico de 12 horas con cefalea y diarrea. refire que esta asintomatica a la hora de la consulta. 

Diagnóstico: NEURO Cefalea (306)

Destino final: En domicilio con instrucciones 

Tratamiento: solicita certificado por 24 horas ya que ayer no fue a trabajar por cefalea y no alimentacion por todo el dia. indica que tiene mal patron de alimentacion y que ayer no comio nada. 

Reposo: 24 horas

###

Fecha: 2021-06-29

Nota médica: EL DIA 28/6/21 SE COLOCA LA VACUNA DEL COVID 19 , EVOLUCIONA CON FIEBRE, ESCALOFRIOS, MALESTAR GENERAL . 
SE INDICA ANALGESICOS.

Diagnóstico: INESP Fiebre (338)

Destino final: En domicilio con instrucciones 

Tratamiento: PARACETAMOL 1 GR C6H 
IBUPROFENO 400 C12H . 
 

Reposo: 24 horas

###

Fecha: 2021-06-30

Nota médica: Paciente femenina de 48 años con clinica de dos dias de evolucion caracterizado por cefalea holocraneana, fiebre cuantificada en 38°c, refiere aparicion de los sintomas posterior a la aplicacion de la vacuna Astrazeneca 

Diagnóstico: INESP Fiebre (338)

Destino final: En domicilio con instrucciones 

Medicación / Prescripción médica: ibuprofeno 400 mg ibupirac 400 mg analgesico antiinflam. comp.x 100 Analgésico Antiinflam. 

Reposo: 48 horas

###

Fecha: 2023-04-28

Nota médica: refiere diarrea y vomitos de un dia de evolucion. en beg.hde. se dan pautas de alarma 
ap no refiere 

Diagnóstico: Gastroenteritis

Destino final: En domicilio con instrucciones 

Tratamiento: hidratacion 
dieta astringente
loperamida un comp cada ocho horas 
reliveran un comp cada ocho horas
 

Reposo: 24 horas

###
"""
    
    patient_data2 = """Paciente de 24 años, de sexo Femenino.

Fecha: 2022-07-06

Nota médica: Paciente refiere dolor lumbar de 24 hs de evolucion. Niega alergias. 

Diagnóstico: LOCOM Signos sintomas lumbares (495)

Destino final: En domicilio con instrucciones

Motivos de consulta: Dolor de espalda.lumbalgia.lumbalgia de menos de 24hs de evolución.empeora con el movimiento o cambio de posición.tomo algún analgésico o desinflamatorio 

Medicación / Prescripción médica: meloxicam+pridinol MIO VIROBRON comp.x 10 Antiinflam.Analgésico.Miorrelaja 

Tratamiento: Indico Meloxicam con pridinol cada 12 hs. Aplicación de calor en la zona. Pautas de alarma. En caso de persistir el dolor interconsulta con traumatología. 
Reposo de 24 hs. 
 

Reposo: 24 horas

###

Fecha: 2022-08-04

Nota médica: PACIENTE DE 47 AÑOS.
CONSULTA POR DOLOR DE GARGANTA, ODINOFAGIA, CONGESTIÓN NASAL. NIEGA OTROS SÍNTOMAS.
INICIO HACE 72 HS.
BUEN ESTADO GENERAL.
NIEGA FAUCES ERITEMATOSAS.
VACUNACIÓN COVID19 COMPLETA.
APP: NIEGA. MEDIC HABITUAL: NIEGA. NIEGA ALERGIAS.

Diagnóstico: Faringitis

Destino final: En domicilio con instrucciones

Motivos de consulta: Dolor de garganta.odinofagia.No tiene tos.Tiene moco.Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales 

Medicación / Prescripción médica: desloratadina+betametasona FRENALER CORT comp.rec.x 10 Antialérgico Antiinflamatorio / bencidamina,clorhidrato ERNEX sol.spray x 30 ml Antiinflam.tópico 

Tratamiento: FRENALER CORT 1 COMP X DIA X 3 DIAS.
ERNEX SPRAY 3 VECES POR DIA.
VAPOR DE AGUA.
REPOSO 24 HS
NUEVA CONSULTA EN 24 HS
PAUTAS DE ALARMA. 

Reposo: 24 horas

###

Fecha: 2022-09-14

Nota médica: Paciente refiere vómitos y dolor abdominal de 24 hrs de evolución 

Diagnóstico: Vómitos

Destino final: En domicilio con instrucciones

Motivos de consulta: Vómitos.nauseas/vómitos.No tiene tos.Tiene nauseas o vómitos de 1 dia.tolera liquidos.Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales 

Tratamiento: 1.- dieta astringente e hidratacion 
2.- recomendaciones y pautas de alarma. 

Reposo: 24 horas

###

Fecha: 2022-09-17

Nota médica: paciente quien cursa con cuadro de entorsis de tobillo derecho , posterior a esto con edema , se indica reposo, y manejo manejo analgesico

Diagnóstico: Esguince de tobillo

Destino final: En domicilio con instrucciones

Motivos de consulta: Inflamacion en el tobillo 

Reposo: 24 horas

###

Fecha: 2022-09-19

Nota médica: PACIENTE EN SEGUIMIENTO TRAUMATOLOGICO POR ESGUINCE DE TOBILLO DERECHO DE 2 DIAS DE EVOLUCION, PERSISTE CON DOLOR LOCAL.

Diagnóstico: Esguince de tobillo

Destino final: Indico seguimiento por consultorio externo

Motivos de consulta: Esguince 

Tratamiento: SE INDICA TTO ANALGESICO-REPOSO 48 HS- SE DAN PAUTAS DE ALARMA-CONTROL EVOLUTIVO CON ESPECIALIDAD 

Reposo: 48 horas

###

Fecha: 2022-10-03

Nota médica: paciente quien ursa con cuadro de deposiciones diarreicas de un dia de evolucion , malestra general, seextiende certifiado de reposo

Diagnóstico: Diarrea

Destino final: En domicilio con instrucciones

Motivos de consulta: Diarrea.diarrea.No tiene tos.Fiebre o escalofríos.diarrea 24 de evoución.Menos de 6 deposiciones diarias.materia fecal sin sangre.deposiciones líquidas.Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales 

Medicación / Prescripción médica: trimebutina ALTRIP 200 comp.x 30 Antiespasmódico / saccharomyces boulardii FLORATIL 200 mg caps.x 10 Antidiarreico 

Reposo: 24 horas

###

Fecha: 2022-11-01

Nota médica: Paciente masculino con cuadro de amigdalitis aguda se indica manejo analgesico y cubrimiento antibiotico empirico, se sugiere reposo por 24 horas. 

Diagnóstico: Amigdalitis

Destino final: En domicilio con instrucciones

Motivos de consulta: Fiebre.Dolor de cabeza.Dolor de garganta.Fiebre o escalofríos.odinofagia.cefalea.se siente mareado.No tiene tos.Menos de 48 horas 

Medicación / Prescripción médica: paracetamol TAFIROL 1 G comp.ran.x 24 Analgésico Antifebril / amoxicilina AMOXIDAL 500 mg comp.rec.x 21 Antibiótico 

Tratamiento: Amoxicilina
Paracetamol 

Reposo: 24 horas

###

Fecha: 2022-11-14

Nota médica: pte masculino, madre refiere que desde ayer esta con tos y expectoracion mas fiebre que cede con paracetamol. se indica pautas de alarma y reposo

Diagnóstico: RESP Infeccion respiratoria aguda del tracto superior (348)

Destino final: En domicilio con instrucciones

Motivos de consulta: Fiebre.Tos.Tos.Fiebre o escalofríos.Tiene moco.Tos con moco.Tos aguda.Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales.Menos de 48 horas.Tos.Fiebre o escalofríos.Tiene moco.Tos con moco.Tos aguda.Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales.Menos de 48 horas 

Tratamiento: paracetamol
hidratacion
nebulizacion con sc fisiol 

Reposo: 24 horas

###
"""
    patient_data = None
    if st.session_state['patient_uid'] == ['1']:
        st.session_state.patient_data.append(patient_data1)
        patient_data = patient_data1
        
    if st.session_state['patient_uid'] == ['2']:
        st.session_state.patient_data.append(patient_data2)
        patient_data = patient_data2
    # Display the EHR patient data
    if patient_data:
        print(st.session_state)
        st.subheader(f"Patient '{st.session_state['patient_uid'][0]}' Information")
        stx.scrollableTextbox(patient_data,height = 350)


	
