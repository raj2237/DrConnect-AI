import psycopg2
import os
from dotenv import load_dotenv
from datetime import date
class DataBase:
    def __init__(self):
        load_dotenv()
        self.conn = psycopg2.connect(
                    database=os.getenv("DB"),
                    user=os.getenv("DB_USERNAME"),
                    password=os.getenv("DB_PASSWORD"),
                    host=os.getenv("DB_HOST"),
                    port=os.getenv("DB_PORT")
                )
    def sample(self):
        # creating a cursor object
        cursor = self.conn.cursor()
        # creating table
        sql = '''CREATE TABLE employee(
        id  SERIAL NOT NULL,
        name varchar(20) not null,
        state varchar(20) not null
        )'''


        # list that contain records to be inserted into table
        data = [('Babita', 'Bihar'), ('Anushka', 'Hyderabad'), 
                ('Anamika', 'Banglore'), ('Sanaya', 'Pune'),
                ('Radha', 'Chandigarh')]

        # inserting record into employee table
        for d in data:
            cursor.execute("INSERT into employee(name, state) VALUES (%s, %s)", d)


        print("List has been inserted to employee table successfully...")

        # Commit your changes in the database
        self.conn.commit()
    def client_db(self,client_id,visit_id,doctor_id,first_name,last_name,age,gender,contact_no,visit_date,symptoms):
        try:
            cursor = self.conn.cursor()
            sql_query='''
                        INSERT into patient(client_id, visit_id,doctor_id,first_name,last_name,age,gender,contact_no,visit_date,symptoms) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        '''
            values=(client_id,visit_id,doctor_id,first_name,last_name,age,gender,contact_no,visit_date,symptoms)
            cursor.execute(sql_query,values)
            print("inserted successfullyy")
            self.conn.commit()
        except Exception as e:
            print("an exception occured: ",e)
        

    def doctor_db(self,doctor_id,first_name,last_name):
        try:
            cursor = self.conn.cursor()
            sql_query='''
                        INSERT into doctor(doctor_id,first_name,last_name) VALUES (%s, %s, %s)
                        '''
            values=(doctor_id,first_name,last_name)
            cursor.execute(sql_query,values)
            print("inserted successfullyy")
            self.conn.commit()
        except Exception as e:
            print("an exception occured: ",e)
        

    def treatment_diagnosis_db(self,client_id,doctor_id,visit_id,ai_diagnosed_condition,ai_detailed_analysis,ai_treatment_diagnosiswise,doctor_analysis,image_data):
        try:
            cursor = self.conn.cursor()
            sql_query='''
                        INSERT into diagnosis_treatment_info(client_id,doctor_id,visit_id,ai_diagnosed_condition,ai_detailed_analysis,ai_treatment_diagnosiswise,doctor_analysis,image_data) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        '''
            values=(client_id,doctor_id,visit_id,ai_diagnosed_condition,ai_detailed_analysis,ai_treatment_diagnosiswise,doctor_analysis,psycopg2.Binary(image_data))
            cursor.execute(sql_query,values)
            print("inserted successfullyy")
            self.conn.commit()
        except Exception as e:
            print("an exception occured: ",e)
        




        

if __name__=='__main__':
    db=DataBase()
    current_date = date.today()
    # db.client_db(1,1,1,'krishna','barot',19,'female',8320664946,current_date)
    with open("sample.png", "rb") as file:
        binary_data = file.read()
    db.treatment_diagnosis_db(1,1,1,"Suspected Lipoma of the Thenar Eminence","The radiograph shows a right hand in a posteroanterior (PA) projection.  There is a well-defined, radiolucent lesion located in the soft tissues of the thenar eminence, just distal to the first metacarpophalangeal joint. The lesion is round to oval in shape and appears to have well-defined margins. There is no evidence of cortical erosion or periosteal reaction.  The bones of the hand appear normal, with no evidence of fracture, dislocation, or other bony abnormalities.  The joint spaces appear to be of normal width.  Soft tissue swelling is not significantly evident beyond the radiolucency itself.","""{"treatments": [{"diagnosis_name": "Comminuted fracture of the distal phalanx of the thumb", "treatment_name": "Surgical fixation (K-wires, pins, plates, screws) or splinting", "dosage": "Surgical procedure specifics determined by surgeon; splinting duration varies (typically several weeks).", "reference_links": ["https://emedicine.medscape.com/article/98322-treatment", "https://my.clevelandclinic.org/health/diseases/22252-comminuted-fracture", "https://orthoinfo.aaos.org/en/diseases--conditions/thumb-fractures/"]}, {"diagnosis_name": "Intra-articular fracture of the distal phalanx of the thumb", "treatment_name": "Surgical fixation (K-wires, pins, plates, screws) or closed reduction and splinting", "dosage": "Surgical procedure specifics determined by surgeon; splinting duration varies (typically several weeks).", "reference_links": ["https://emedicine.medscape.com/article/98322-treatment", "https://emedicine.medscape.com/article/1287814-treatment", "https://surgeryreference.aofoundation.org/orthopedic-trauma/adult-trauma/thumb/distal-phalanx-distal-and-shaft-multifragmentary/definition"]}, {"diagnosis_name": "Distal phalanx fracture with displacement", "treatment_name": "Surgical fixation (K-wires, pins, plates, screws) or closed reduction and splinting", "dosage": "Surgical procedure specifics determined by surgeon; splinting duration varies (typically several weeks).", "reference_links": ["https://surgeryreference.aofoundation.org/orthopedic-trauma/adult-trauma/thumb/distal-phalanx-distal-and-shaft-multifragmentary/definition", "https://emedicine.medscape.com/article/1287814-treatment", "https://www.orthobullets.com/hand/6114/phalanx-fractures"]}, {"diagnosis_name": "Thumb fracture (unspecified type)", "treatment_name": "Splinting or surgical fixation (K-wires, pins, plates, screws)", "dosage": "Splinting duration varies (typically several weeks); surgical procedure specifics determined by surgeon.", "reference_links": ["https://orthoinfo.aaos.org/en/diseases--conditions/thumb-fractures/", "https://www.rch.org.au/clinicalguide/guideline_index/fractures/Phalangeal_Finger_Fractures/", "https://www.hey.nhs.uk/patient-leaflet/hand-therapy-phalangeal-fractures-of-the-fingers-or-thumb-pifu/"]}, {"diagnosis_name": "Crush injury to the thumb", "treatment_name": "Wound care, pain management (analgesics), potential surgical debridemg.au/clinicalguide/guideline_index/fractures/Phalangeal_Finger_Fractures/", "https://www.hey.nhs.uk/patient-leaflet/hand-therapy-phalangeal-fractures-of-the-fingers-or-thumb-pifu/"]}, {"diagnog.au/clinicalguide/guideline_index/fractures/Phalangeal_Finger_Fg.au/clinicalguide/guideline_index/fractures/Phalangeal_Finger_Fractures/", "https://www.hey.nhs.uk/patient-leaflet/hand-therapyg.au/clinicalguide/guideline_index/fractures/Phalangeal_Finger_Fractures/", "https://www.hey.nhs.uk/patient-leaflet/hand-therapy-phalangeal-fractures-of-the-fingers-or-thumb-pifu/"]}, {"diagnosis_name": "Crush injury to the thumb", "treatment_name": "Woundg.au/clinicalguide/guideline_index/fractures/Phalangeal_Finger_Fractures/", "https://www.hey.nhs.uk/patient-leaflet/hand-therapy-phalangeal-fractures-of-the-fingers-or-thumb-pifu/"]}, {"diagnog.au/clinicalguide/guideline_index/fractures/Phalangeal_Finger_Fractures/", "https://www.hey.nhs.uk/patient-leaflet/hand-therapyg.au/clinicalguide/guideline_index/fractures/Phalangeal_Finger_Fractures/", "https://www.hey.nhs.uk/patient-leaflet/hand-therapy-phalangeal-fractures-of-the-fingers-or-thumb-pifu/"]}, {"diagnoractures/", "https://www.hey.nhs.uk/patient-leaflet/hand-therapy-phalangeal-fractures-of-the-fingers-or-thumb-pifu/"]}, {"diagno-phalangeal-fractures-of-the-fingers-or-thumb-pifu/"]}, {"diagnosis_name": "Crush injury to the thumb", "treatment_name": "Wound care, pain management (analgesics), potential surgical debridement or fixation depending on severity", "dosage": "Analgesics asent or fixation depending on severity", "dosage": "Analgesics as prescribed by physician; surgical procedure specifics determined by surgeon.", "reference_links": ["https://www.ncbi.nlm.nih.go prescribed by physician; surgical procedure specifics determined by surgeon.", "reference_links": ["https://www.ncbi.nlm.nih.god by surgeon.", "reference_links": ["https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2684218/", "https://emedicine.medscape.com/article/1287814-treatment", "https://orthoinfo.aaos.org/en/diseasesv/pmc/articles/PMC2684218/", "https://emedicine.medscape.com/article/1287814-treatment", "https://orthoinfo.aaos.org/en/diseasesicle/1287814-treatment", "https://orthoinfo.aaos.org/en/diseases--conditions/thumb-fractures/"]}]}""","hello doctor analysis will come here",binary_data)
    # db.doctor_db(1,'krishna','barot')
        