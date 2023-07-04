import streamlit as st
from streamlit_chat import message
import streamlit_scrollable_textbox as stx

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts.prompt import PromptTemplate
from langchain.chat_models import ChatOpenAI
import datetime


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

    patient_data3 = """Paciente de 50 años, de sexo Masculino.

Fecha: 2022-04-05

Nota médica: paciente cursando con picos febriles, tos seca, congestion nasal, rinorrea hialina, malestar general, en tratamiento con azitromicina. 

Diagnóstico: RESP Gripe (340)

Destino final: En domicilio con instrucciones 

Tratamiento: manejo sintomatico
tratamiento antibiotico 
reposo 24 horas 

Reposo: 24 horas

###

Fecha: 2022-04-07

Nota médica: px confirmado covid-19 positivo se realizo hisopado el dia 06/04 comenzo con sintomas el dia sabado 02/04 actualmente continua con fiebre 

Diagnóstico: INESP confirmado COVID19 x hisopado

Destino final: En domicilio con instrucciones 

Tratamiento: se indica tto y reposo 48 hs 

Reposo: 48 horas

###

Fecha: 2022-04-10

Nota médica: 

Diagnóstico: INESP confirmado COVID19 x hisopado

Destino final: En domicilio con instrucciones 

Reposo: 48 horas

###

Fecha: 2022-04-12

Nota médica: MASCULINO 49 AÑOS
EL FDS CURSO CON COVID19 POSITIVO 
REFIERE CONGESTION NASAL , CANSANCIO

Diagnóstico: INESP confirmado COVID19 x hisopado

Destino final: En domicilio con instrucciones 

Tratamiento: ACEMUK 600MG CADA 12H POR 5 DIAS 
VAPORIZACIONES 
REPOSO 72 HORAS 

Reposo: 72 horas

###

Fecha: 2022-05-02

Nota médica: Paciente refiere tuvo covid19 el 06 de abril cumplio aislamiento por 10, actualmente con cefalea y adinamia post covid19

Diagnóstico: PSICO Otros signos síntomas psicológicos mentales (477)

Destino final: En domicilio con instrucciones 

Tratamiento: Paracetamol: 1 gramo cada 8 horas solo si es necesario.
Valoracion por Neurologia. 

Reposo: 24 horas

###

Fecha: 2022-07-20

Nota médica: PACIENTE CON CUADRO CLINICO DE 03 DIAS DE EVOLUCION CONSISTENTE EN CONGESTION NASAL, ASOCIADO A ODINOFAGIA, MIALGIAS GENERALIZADAS, TOS SECA, CEFALEA GLOBAL, FIEBRE, NO MANEJO. ACTUALMENTE SINTOMATICO.

Diagnóstico: Faringitis aguda

Destino final: En domicilio con instrucciones 

Medicación / Prescripción médica: fexofenadina ALLEGRA 120 mg comp.x 10 Antihistamínico 

Tratamiento: REPOSO
CONTROL CLINICO EN 48 HORAS 
HIDRATACION CONTINUA
TAFIROL COMP 1 GR TOMAR CADA 08 HORAS
FEXOFENADINA COMP 120 MG TOMAR 1 CADA 12 HORAS POR 5 DIAS.
 

Reposo: 48 horas

###

Fecha: 2022-08-22

Nota médica: Paciente con fiebre, cefalea, congestion nasal. 

Diagnóstico: Fiebre

Destino final: En domicilio con instrucciones 

Tratamiento: Tratamiento sintomático y reposo de 48 hs 

###

Fecha: 2022-09-22

Nota médica: Paciente quien refiere FIS hace 12 horas dado por nauseas vómitos, y actualmente con evacuaciones liquidas, cefalea.



Diagnóstico: Gastroenteritis

Destino final: En domicilio con instrucciones 

Tratamiento: Realizar dieta de bajo consumo de azúcares, disminuir el consumo de lácteos, no consumir huevos, pescado, carnes rojas, fiambre, mariscos, no alimentos envasados ni gaseosas.

 
paracetamol 1 gr cada 8 horas por 3 dias.

 

Reposo: 24 horas

###

Fecha: 2022-09-25

Nota médica: PACIENTE CONSULTA POR PRESENTAR DESDE EL 20 DE SEPTIEMBRE POLAQUIURIA, DOLOR EN INGLE IZQUIERDA NIEGA APP, SE DEJAN INDICACIONES


UROCULTIVO
ORINA COMPLETA
LEVOFLOXACINA 1 COMP CADA DIA 5 DIAS (ANTIBIOTICO)
FENAZOPIRIDINA 1 COMP CADA 12H POR 5 DIAS (ANALGESICO)
LIQUIDOS

Diagnóstico: Prostatitis

Destino final: En domicilio con instrucciones 

Medicación / Prescripción médica: cefalexina SINURIT 1000 mg comp.rec.x 16 Antibiótico / fenazopiridina CISTALGINA 200 mg comp.rec.x 10 Analgésico urinario 

Tratamiento: CEFALEXINA 1 COMP CADA 12H POR 7 DIAS
CISTALGINA 1 COMP CADA 12H POR 5 DIAS 

Reposo: 48 horas

###

Fecha: 2022-09-28

Nota médica: Paciente refiere comenzo el 25/09 disuria polaquiuria medicado con ATB continua con sintomas control 

Diagnóstico: Infección urinaria

Destino final: En domicilio con instrucciones 

Tratamiento: Cefalexina Duo 1 c /12 hs 
hidratacion abundante 
Cistalgina 

Reposo: 48 horas

###
"""
    patient_data4 = """Paciente de 41 años, de sexo Femenino.

Fecha: 2022-09-22

Nota médica: ODINOFAGIA

Diagnóstico: Fiebre

Destino final: En domicilio con instrucciones

Motivos de consulta: Dolor de garganta.odinofagia.Tos.Tiene moco.Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales 

Reposo: 24 horas

###

Fecha: 2022-10-17

Nota médica: paciente refiere que ayer en la noche su perrito de dos meses la mordio en la mano derecha . se indica concurrir a una guardia para revision y envio de atb orales. se da reposo por 24 horas . 

Diagnóstico: Dolor en miembro superior

Destino final: Indico concurrir a guardia externa 

Tratamiento: se indica concurrir a una guardia para revision y envio de atb orales. se da reposo por 24 horas . 

Reposo: 24 horas

###

Fecha: 2023-03-06

Nota médica: Paciente con síndrome gripal, se indican pautas de tratamiento y reposo de 24 horas.

Diagnóstico: Gripe

Destino final: En domicilio con instrucciones

Motivos de consulta: Fiebre.Fiebre o escalofríos.Tos.Tiene moco.Menos de 48 horas. .Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales 

Reposo: 24 horas

###

Fecha: 2023-03-13

Nota médica: DIARREA

Diagnóstico: Diarrea

Destino final: En domicilio con instrucciones

Motivos de consulta: Fiebre.Diarrea.Congestión Nasal.Fiebre o escalofríos.diarrea.Tos.Tiene moco.Menos de 48 horas 

Reposo: 24 horas

###

Fecha: 2023-04-03

Nota médica: Paciente quien refiere que presenta cefalea, congestión nasal, tos, mialgia y malestar general 

Diagnóstico: Gripe

Destino final: En domicilio con instrucciones 

Tratamiento: Se indica tratamiento sintomático hidratación oral abundante pautas de alarma control y seguimiento 

Reposo: 72 horas

###

Fecha: 2023-05-09

Nota médica: PACIENTE FEMENINO DE 41 AÑOS
APP NIEGA
NIEGA ALERGIA A MEDICAMENTOS
CONSULTA POR PRESENTAR CUADRO CLINICO CARACTERIZADO POR CONGESTION NASAL, TOS SECA, DISFONIA, TEMP 38.7

Diagnóstico: RESP Infeccion respiratoria aguda del tracto superior (348)

Destino final: En domicilio con instrucciones

Motivos de consulta: Tos.Fiebre.Congestión Nasal.Tos.Fiebre o escalofríos.odinofagia.cefalea.Tiene moco.Tos seca.Tos aguda 

Medicación / Prescripción médica: acetilcisteína ACEMUK 600 mg tab.efer.x 10 Mucolítico / sodio,cloruro+carragenina NASITRAL spray nasal est. x 10ml Fluidificante de las vías aéreas / desloratadina+betametasona FRENALER CORT comp.rec.x 10 Antialérgico Antiinflamatorio 

Tratamiento: SE INDICAN PAUTAS DE ALARMA
ABUNDANTES LIQUIDOS
PARACETAMOL 1 GR CADA 8 HORAS SI DOLOR O FIEBRE >37,5°
NASITRAL SPRAY APLICAR 2 PULSACIONES CADA 8 HRS POR 5 DIAS
ACEMUK 600 MG DILUIR EN AGUA Y TOMAR 1 COMP CADA 12 HRS POR 5 DIAS
FRENALER CORT TOMAR 1 COMP CADA 12 HRS POR 5 DIAS
NC 10/05/23 SEGUIMIENTO CLINICO (ÜMA CARE). 

Reposo: 24 horas

###

Fecha: 2023-05-15

Nota médica: Paciente de 41 años presenta congestion nasal moco amarillo , dolor en senos frontal. cefalea, astenia,disfonia y tos perruna esto inicia hace 7dias.Afebril .fue medicada con acemuk.

Diagnóstico: RESP Laringitis traqueitis aguda (353)

Destino final: En domicilio con instrucciones

Motivos de consulta: Tos.Dolor de garganta.Dolor de cabeza.Congestión Nasal.Tos.odinofagia.cefalea.Fiebre o escalofríos.Tiene moco.Tos seca 

Tratamiento: corteroid 0.6mg cc 30 ( 1 y2 cada 8hs+3 y4 cada 12hs +5 dia por unica vez)+ amoxicilina-acido clavulanico 1gramo cada 12h s por 
 7 dias+ mucoltic 150 ml ( 10 ml cada 8hs por 3 dias)+reposo de 72 horas 

Reposo: 72 horas

###
"""
    patient_data5 = """Paciente de 38 años, de sexo Masculino.

Fecha: 2023-04-21

Nota médica: REFIERE HACE 24 HS EN SU TRABAJO SE GOLPEO EL PIE DORSO IZQUIERDO. EDEMA, DOLOR LA MARCHA. FUE ALA GUARDIA Y LE REALIZARON RX DE PIE NO TIENE FRACTURA.

Diagnóstico: Podalgia

Destino final: En domicilio con instrucciones

Motivos de consulta: Dolor de pie por golpe 

Medicación / Prescripción médica: meloxicam+betametasona+asoc. BRONAX CORT comp.rec.x 20 Analgésico Antiinflam. 

Reposo: 24 horas

###

Fecha: 2023-04-23

Nota médica: PACIENTE MASCULINO DE 38 AÑOS DE EDAD CON CUADRO CLINICO DE 1 SEMANA DE TOS HUMEDA, SIN FIEBRE.

Diagnóstico: RESP Infeccion respiratoria aguda del tracto superior (348)

Destino final: En domicilio con instrucciones

Motivos de consulta: Tos.Congestión Nasal.Tos.Tiene moco.Tos con moco.Tos aguda.Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales 

Medicación / Prescripción médica: ambroxol+butamirato+clorfeniram. MUCO DOSODOS jbe.x 150 ml Antitusivo Expectorante / acetilcisteína TOFLUX 600 mg sob.x 10 Mucolítico 

Tratamiento: MUCOLITICO, ANTITUSIVO 

###

Fecha: 2023-05-03

Nota médica: TOS 

Diagnóstico: Tos

Destino final: En domicilio con instrucciones

Motivos de consulta: Tos.Dolor de garganta.Congestión Nasal.Tos.odinofagia.Tos con moco.Tos subaguda.Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales 

Tratamiento: NEBU CON BUDESONIDE HIPERSOL CONTROL SEGUN EVOLUCION 

Reposo: 24 horas

###

Fecha: 2023-05-04

Nota médica: REFIERE ODINOFAGIA DE 1 DIA DE EVOLUCION

Diagnóstico: Amigdalitis

Destino final: En domicilio con instrucciones

Motivos de consulta: Dolor de garganta.odinofagia.Tos.Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales 

Medicación / Prescripción médica: desloratadina+betametasona FRENALER CORT comp.rec.x 10 Antialérgico Antiinflamatorio 

Tratamiento: FRENALER CORT IBU600 MG 

Reposo: 24 horas

###

Fecha: 2023-05-05

Nota médica: Paciente de 38 años que consulta por tos, dolor de garganta y odinofagia. No refiere fiebre. Se encuentra en BEG. Lucido y vigil. Colabora con interrogatorio. No se entrecorta la voz ni refiere dificultad respiratoria. No refiere perdida de gusto ni olfato. Vacunado para COVID

Diagnóstico: Infección aguda de vías respiratorias superiores

Destino final: En domicilio con instrucciones

Motivos de consulta: Tos.Dolor de garganta.Tos.odinofagia.Tos seca.Tos aguda.Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales 

Tratamiento: Se indica si
-Fiebre/dolores: Paracetamol 1 g c/8 hs
-Tos: Bisolvon jarabe 5 ml c/8 hs 
-Congestión nasal: Acemuk 600 mg 1 tab c/24 hs
Se dan pautas claras de cuidado y de alarma para consulta por guardia: empeoramiento o persistencia de los síntomas, dificultad respiratoria, palabra entrecortada. 
 

Reposo: 24 horas

###

Fecha: 2023-05-05

Nota médica: Paciente de sexo masculino de 38 años de edad que refiere presentar tos y odinofagia de < 24 hs de evolución. Indico tratamiento sintomático y reposo con pautas de alarma por 48 hs.

Diagnóstico: RESP Infeccion respiratoria aguda del tracto superior (348)

Destino final: En domicilio con instrucciones

Motivos de consulta: Tos.Dolor de garganta.Tos.odinofagia.Tos seca.Tos aguda.Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales.Tos.odinofagia.Tos seca.Tos aguda.Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales 

Tratamiento: - Tos: Athos jarabe 7,5 ml c/8 hs
- Dolor de garganta: Ernex spray 2 aplicaciones cada 2 hs
 

Reposo: 48 horas

###

Fecha: 2023-05-11

Nota médica: Paciente refiere congestion nasal, tos y fiebre de reciente aparicion. 

Diagnóstico: RESP Infeccion respiratoria aguda del tracto superior (348)

Destino final: En domicilio con instrucciones

Motivos de consulta: Tos.Fiebre.Congestión Nasal.Tos.Fiebre o escalofríos.Tiene moco.Tos con moco.Tos subaguda.Sin antecedentes coronarios 

Tratamiento: Sintomatico / Reposo 48 hs / Pautas higienico dieteticas / Pautas de alarma 
Control en 24 - 48 hs 

Reposo: 48 horas

###

Fecha: 2023-06-12

Nota médica: padre consulta por menor quien refiere tos y congestion

Diagnóstico: RES Rinofaringitis aguda

Destino final: En domicilio con instrucciones

Motivos de consulta: Tos.Congestión Nasal.Tos.odinofagia.Tiene moco.Tos con moco.Tos aguda.Sin antecedentes coronarios.no refiere antecedentes respiratorios.no refiere antecedentes renales 

Medicación / Prescripción médica: hedera helix ATHOS jbe.x 100 ml Antitusivo Mucolítico / desloratadina+betametasona HEXALER CORT comp.rec.x 10 Antialérgico Antiinflamatorio / paracetamol TAFIROL comp.x 30 Analgésico Antifebril 

Tratamiento: reposo en domicilio, tafirol cada 8 horas, hexaler cort cada 8 horas, athos 5ml cada 8 horas 

Reposo: 48 horas

###

Fecha: 2023-06-29

Nota médica: Paciente de sexo masculino de 38 años de edad que refiere presentar vómitos y diarrea de < 24 hs de evolución. Indico tratamiento sintomático y reposo con pautas de alarma por 24 hs.


Diagnóstico: Gastroenteritis

Destino final: En domicilio con instrucciones

Motivos de consulta: Diarrea.Vómitos.nauseas/vómitos.diarrea.No tiene tos.Sin antecedentes coronarios.Tiene nauseas o vómitos desede hace menos de 1 semana.tolera liquidos.diarrea menos de 1 semana de evolución.Menos de 6 deposiciones diarias.materia fecal sin sangre.deposiciones líquidas.no refiere antecedentes respiratorios.no refiere antecedentes renales 

Tratamiento: - Mantener buena hidratación tomando mucha agua en pequeñas cantidades (hasta 3L por día).
- Dieta: EVITAR fritos, grasas, salsas, picantes, mate, cafe, alcohol, gaseosas, chocolates. COMER pollo a la plancha, arroz, verduras hervidas, gelatina, tostadas. 
- Dolor abdominal: buscapina o sertal simple 1 comp c/8 hs
- Diarrea: Crema de bismuto 2 cucharadas soperas c/4 hs
- Náuseas: Reliveran 1 comp sublingual c/8 hs
 

Reposo: 24 horas

###

Fecha: 2023-06-30

Nota médica: PACIENTE DE 38 AÑOS. NO SE VE LA IMAGEN.
CONSULTA POR DOLOR ABDOMINAL TIPO RETORCIJÓN, DIARREA 5 EPISODIOS. NIEGA OTROS SÍNTOMAS.
BUEN ESTADO GENERAL.
INICIO HACE APROX 36 HS. SE ENCUENTRA EN TRATAMIENTO CON BUSCAPINA.
NIEGA COMIDA COPIOSA PREVIA.
APP: NIEGA. MEDIC HABITUAL: NIEGA. NIEGA ALERGIAS.


Diagnóstico: Dolor abdominal

Destino final: En domicilio con instrucciones

Motivos de consulta: Dolor de abdomen.Diarrea.diarrea.No tiene tos.Sin antecedentes coronarios.diarrea menos de 1 semana de evolución.Menos de 6 deposiciones diarias.materia fecal sin sangre.deposiciones líquidas.no refiere antecedentes respiratorios.no refiere antecedentes renales 

Tratamiento: CONTINUAR IGUAL MEDICACIÓN.
HIDRATACIÓN ABUNDANTE CON AGUA MINERAL.
DIETA ASTRINGENTE HIPOGRASA.
REPOSO 24 HS
NUEVA CONSULTA EN 24 HS
PAUTAS DE ALARMA. 

Reposo: 24 horas

###

"""
    patient_data = "No hay datos del paciente"
    if st.session_state['patient_uid'] == ['1']:
        st.session_state.patient_data.append(patient_data1)
        patient_data = patient_data1
        
    if st.session_state['patient_uid'] == ['2']:
        st.session_state.patient_data.append(patient_data2)
        patient_data = patient_data2
	    
    if st.session_state['patient_uid'] == ['3']:
        st.session_state.patient_data.append(patient_data3)
        patient_data = patient_data3
	    
    if st.session_state['patient_uid'] == ['4']:
        st.session_state.patient_data.append(patient_data4)
        patient_data = patient_data4
	    
    if st.session_state['patient_uid'] == ['5']:
        st.session_state.patient_data.append(patient_data5)
        patient_data = patient_data5
	    
    # Display the EHR patient data
    if patient_data:
        st.subheader(f"Patient '{st.session_state['patient_uid'][0]}' Information")
        stx.scrollableTextbox(patient_data,height = 350)


	
