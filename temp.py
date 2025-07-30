from crewai import Agent, Task, Crew, LLM
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()
os.environ['SERPER_API_KEY']=os.getenv('SERPER_API_KEY')
from crewai_tools import SerperDevTool
from pydantic import BaseModel, HttpUrl
from typing import List
from pydantic import Field

class SingleTreatment(BaseModel):
    diagnosis_name: str
    treatment_name: str
    dosage: str
    reference_links: List[HttpUrl]

class Diagnosis_1(BaseModel):
    diagnosis_name: str
class Diagnosis_main(BaseModel):
    diagnosis_name: List[Diagnosis_1] = Field(..., min_length=3, max_length=3)

diagnosis_data = Diagnosis_main(
    diagnosis_name=[
        Diagnosis_1(diagnosis_name="..."),
        Diagnosis_1(diagnosis_name="..."),
        Diagnosis_1(diagnosis_name="...")
    ]
)

# 2. Convert to JSON string
diagnosis_json_str = diagnosis_data.model_dump_json()

class Treatment(BaseModel):
    treatments: List[SingleTreatment] = Field(..., min_items=3, max_items=3)

treatment_data = Treatment(
    treatments=[
        SingleTreatment(
            diagnosis_name="...",
            treatment_name="...",
            dosage="...",
            reference_links=["https://example.com/salbutamol"]
        ),
        SingleTreatment(
            diagnosis_name="...",
            treatment_name="...",
            dosage="...",
            reference_links=["https://example.com/salbutamol"]
        ),
        SingleTreatment(
            diagnosis_name="...",
            treatment_name="...",
            dosage="...",
            reference_links=["https://example.com/salbutamol"]
        )
    ]
)

# Convert to JSON string (CrewAI expects string for expected_output)
treatment_json_str = treatment_data.model_dump_json()

tool=SerperDevTool()
os.environ['GEMINI_API_KEY'] = os.getenv("GOOGLE_API_KEY")
raw_results={
    "status": "success",
    "filename": "Right_thumb_big_gallery.jpeg",
    "analysis": {
        "detailed_analysis": "The radiograph shows a right hand in a posterior-anterior (PA) projection.  There is a significant abnormality present in the distal phalanx of the thumb.  Specifically, there is evidence of a comminuted fracture of the distal phalanx.  The fracture is characterized by multiple fracture fragments, suggesting a high-energy impact. The articular surface of the distal phalanx appears involved, indicating an intra-articular fracture.  The remaining bones of the hand appear normal, with no other fractures, dislocations, or significant degenerative changes observed.  Soft tissue swelling is not overtly apparent, but this may be limited by the projection used.",
        "analysis_report": "Based on the radiographic findings, there is a clear indication of a fracture.\nCondition: Comminuted intra-articular fracture of the distal phalanx of the right thumb.",
        "recommendations": "1.  *Further Imaging:*  Obtain lateral and oblique radiographs of the right thumb to better assess the fracture fragments and the extent of articular involvement.\n2.  *Clinical Examination:* A thorough clinical examination of the right thumb should be performed to assess the range of motion, tenderness, and any associated soft tissue injuries.\n3.  *Hand Surgery Consultation:* A consultation with a hand surgeon is recommended for definitive management of the fracture.",
        "treatments": "Treatment will depend on the specifics of the fracture as determined by the clinical examination and additional imaging. Options may include:\n1. *Closed Reduction and Immobilization:*  If the fracture fragments are minimally displaced, closed reduction (manipulation to realign the bones) and immobilization with a splint or cast may be sufficient.\n2. *Open Reduction and Internal Fixation (ORIF):* If the fracture is significantly displaced, comminuted, or involves the articular surface, ORIF may be necessary.  This involves surgical intervention to realign the bone fragments and stabilize them with pins, screws, or plates.\n3. *Pain Management:* Analgesics (pain medication) will be necessary to manage pain and inflammation.\n4. *Physical Therapy:* Post-operative or post-immobilization physical therapy will be crucial for regaining range of motion and strength in the thumb.\nConsult with a doctor before making medical decisions.",
        "diagnosed_condition": "Comminuted intra-articular fracture of the distal phalanx of the right thumb"
    },
    "web_search": {
        "query": "Comminuted intra-articular fracture of the distal phalanx of the right thumb",
        "results": [
            {
                "title": "Comminuted Fracture: Causes, Symptoms, and Recovery - Healthline",
                "snippet": "A comminuted fracture is when a bone breaks into three or more pieces. These typically require surgery and take longer to heal than other fractures. A comminuted fracture happens when you break a",
                "url": "https://www.healthline.com/health/comminuted-fracture"
            },
            {
                "title": "Broken wrist - Diagnosis and treatment - Mayo Clinic",
                "snippet": "Whatever your treatment, it's important to move your fingers regularly while the fracture is healing to keep them from stiffening. Ask your doctor about the best ways to move them. If you smoke, quit. Smoking can delay or prevent bone healing. Immobilization. Restricting the movement of a broken bone in your wrist is critical to proper healing.",
                "url": "https://www.mayoclinic.org/diseases-conditions/broken-wrist/diagnosis-treatment/drc-20353175"
            },
            {
                "title": "What Is a Comminuted Fracture? - WebMD",
                "snippet": "There are a few different types of broken bones, or fractures. One kind is a comminuted fracture. This injury happens when your bone breaks into three or more pieces. Find out how doctors diagnose",
                "url": "https://www.webmd.com/a-to-z-guides/comminuted-fracture-overview"
            },
            {
                "title": "Broken arm - Diagnosis and treatment - Mayo Clinic",
                "snippet": "Care at Mayo Clinic   Patient-Centered Care  About Mayo Clinic  Request Appointment  Find a Doctor  Locations  Clinical Trials      Connect to Support Groups  Patient & Visitor Guide  Billing & Insurance  Departments & Centers  International Services  Contact Us      Patient & Visitor Guide     Image 3             Health Library   Diseases & Conditions  Symptoms  Tests & Procedures      Drugs & Supplements  Healthy Lifestyle  Mayo Clinic Health Letter & Books      Mayo Clinic Health Letter &Books     Image 4             For Medical Professionals   Medical Professional Resources  Refer a Patient  Continuing Medical Education  AskMayoExpert      Mayo Clinic Laboratories  Video Center  Journals & Publications  Mayo Clinic Alumni Association      Continuing Medical Education     Image 5             Mayo Clinic and our partners use technologies such as cookies to collect information from your browser to deliver relevant advertising on our site, in emails and across the Internet, personalize content and perform site analytics.",
                "url": "https://www.mayoclinic.org/diseases-conditions/broken-arm/diagnosis-treatment/drc-20353266"
            },
            {
                "title": "Broken arm - Symptoms and causes - Mayo Clinic",
                "snippet": "The immobilization required to heal a fracture in the upper arm bone can sometimes result in painfully limited range of motion of the elbow or shoulder. Bone infection. If a part of your broken bone protrudes through your skin, it can be exposed to germs that can cause infection. Prompt treatment of this type of fracture is critical.",
                "url": "https://www.mayoclinic.org/diseases-conditions/broken-arm/symptoms-causes/syc-20353260"
            }
        ],
        "answer": "A comminuted fracture of the distal phalanx of the right thumb involves bone shattering into multiple pieces. Treatment typically includes surgery and immobilization. Symptoms include severe pain, swelling, and inability to move the thumb.",
        "total_results": 5
    },
    "disclaimer": "This analysis is for informational purposes only. Always consult with a qualified healthcare professional before making medical decisions."
}



# Or use direct input
# report_text = raw_results['analysis']['detailed_analysis']

# Web search tool
# search_tool = TavilySearchResults()
def main(report_text):
    # Agent 1: Medical Diagnostician
    diagnosis_agent = Agent(
        role="General Medical Diagnostician",
        goal="Understand and classify the medical report {report_text}, then determine top 5 possible diagnoses with reasoning and reference links.",
        backstory=(
            "You're a highly experienced physician with access to web search. You understand all types of medical reports—radiology, pathology, lab tests, and summaries."
        ),
        verbose=True,
        memory=True,
        llm=LLM(model="gemini/gemini-1.5-flash",
                            temperature=0.5),
        tools=[tool],
        allow_delegation=False,
        output_pydantic=Treatment
    )

    # Agent 2: Prescription & Treatment Advisor
    treatment_agent = Agent(
        role="Treatment and Prescription Recommender",
        goal="For each diagnosis, suggest relevant medications, ointments, or procedures using web search and clinical knowledge.",
        backstory=(
            "You're a medical treatment specialist. You recommend treatment plans (medications, ointments, physiotherapy, etc.) and provide dosage based on diagnosis."
        ),
        verbose=True,
        memory=True,
        llm=LLM(model="gemini/gemini-1.5-flash",
                            temperature=0.5),
        tools=[tool],
        allow_delegation=False,
         output_pydantic=Treatment
    )

    # Task 1: Diagnosis
    diagnosis_task = Task(
        description="Analyze this medical report (of any type), identify the report category, and provide the top 5 most likely diagnoses with reasoning. Use web search.",
        # expected_output="List of 5 possible diagnoses with supporting explanation for each in detail.",
        expected_output=diagnosis_json_str,
        agent=diagnosis_agent,
        input=str(report_text)
    )

    # Task 2: Treatment Recommendation
    treatment_task = Task(
        description="Based on the diagnoses, recommend medications or therapies with dosage. Use web search to support choices.",
        # expected_output="List of medicines/treatments per diagnosis with usage instructions , name of medicines/tubes and dosage.Also provide reference links with each treatment plan.",
        expected_output=treatment_json_str,
        agent=treatment_agent,
        input=str(diagnosis_task.output)
    )

    # Crew Runner
    crew = Crew(
        agents=[diagnosis_agent, treatment_agent],
        tasks=[diagnosis_task, treatment_task],
        verbose=True
    )


    result = crew.kickoff(inputs={'report_text': report_text})
    result=str(result)
    result=result.replace("```json","")
    result=result.replace("```","")
    print("result: ",result)
    print("--------")
    # print(result.tasks[0].output)
    # print("---------")
    return result

if __name__=='__main__':
    main("The radiograph shows a right hand in a posterior-anterior (PA) projection.  There is a significant abnormality present in the distal phalanx of the thumb.  Specifically, there is evidence of a comminuted fracture of the distal phalanx.  The fracture is characterized by multiple fracture fragments, suggesting a high-energy impact. The articular surface of the distal phalanx appears involved, indicating an intra-articular fracture.  The remaining bones of the hand appear normal, with no other fractures, dislocations, or significant degenerative changes observed.  Soft tissue swelling is not overtly apparent, but this may be limited by the projection used.")
