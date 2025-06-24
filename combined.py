from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import google.generativeai as genai
from crewai import Agent, Task, Crew, LLM
import aiofiles
import os
import re
import logging
import tempfile
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from PIL import Image
import io
from datetime import datetime
from dotenv import load_dotenv
import platform

# Try different imports for CrewAI tools based on version
try:
    from crewai_tools import SerperDevTool
    SEARCH_TOOL_AVAILABLE = True
except ImportError:
    try:
        from crewai.tools import SerperDevTool
        SEARCH_TOOL_AVAILABLE = True
    except ImportError:
        try:
            # Alternative approach - create a basic search tool
            from langchain_community.utilities import GoogleSerperAPIWrapper
            from langchain.tools import Tool
            SEARCH_TOOL_AVAILABLE = True
        except ImportError:
            SEARCH_TOOL_AVAILABLE = False
            logger.warning("No search tool available. Web search functionality will be limited.")

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Medical Image Analysis API", description="Complete medical analysis with AI agents and PDF reporting")

# Configure APIs
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SERPER_API_KEY = os.getenv('SERPER_API_KEY')

if not GOOGLE_API_KEY:
    print(GOOGLE_API_KEY)
    raise ValueError("GOOGLE_API_KEY environment variable not set")

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)
os.environ['GEMINI_API_KEY'] = GOOGLE_API_KEY

# Initialize search tool based on availability
search_tool = None
if SEARCH_TOOL_AVAILABLE and SERPER_API_KEY:
    try:
        os.environ['SERPER_API_KEY'] = SERPER_API_KEY
        if 'SerperDevTool' in globals():
            search_tool = SerperDevTool()
        else:
            # Fallback to basic search wrapper
            search = GoogleSerperAPIWrapper()
            search_tool = Tool(
                name="search",
                description="Search the web for information",
                func=search.run,
            )
        logger.info("Search tool initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize search tool: {e}")
        search_tool = None
else:
    logger.warning("Search tool not available - check SERPER_API_KEY and crewai_tools installation")

# Gemini configuration
generation_config = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 2048
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

system_prompts = """
You are a highly skilled medical analyst specializing in image-based diagnosis. Carefully analyze the provided medical image 
following this EXACT format:

**Detailed Analysis**: Provide an in-depth examination of abnormalities, patterns, or findings present.

**Analysis Report**: Offer a structured summary of your observations, including the specific disease or condition identified. If you identify a specific condition, clearly state: "Condition: [condition name]"

**Recommendations**: List further tests, consultations, or imaging requirements.

**Initial Treatment Notes**: Brief initial treatment suggestions.

Important:
1. Always include the disclaimer: "Consult with a doctor before making medical decisions."
2. If you identify a specific medical condition, clearly state it in the Analysis Report section using the format "Condition: [condition name]"
3. Be specific about any abnormalities you observe.
4. Use the EXACT section headers as shown above with double asterisks.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings
)

def extract_condition_from_text(text: str) -> str:
    """Extract medical condition from analysis text."""
    if not text:
        return ""
    
    # Strategy 1: Look for "Condition:" pattern
    condition_match = re.search(r"Condition:\s*([^\n\.]+)", text, re.IGNORECASE)
    if condition_match:
        return condition_match.group(1).strip()
    
    # Strategy 2: Look for medical conditions in common patterns
    patterns = [
        r"(?:diagnosed with|shows signs of|indicates|suggests|consistent with)\s+([a-zA-Z\s]+?)(?:\.|,|\n|$)",
        r"(?:appears to be|likely|probably|possibly)\s+([a-zA-Z\s]+?)(?:\.|,|\n|$)",
        r"(?:evidence of|signs of)\s+([a-zA-Z\s]+?)(?:\.|,|\n|$)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            condition = match.group(1).strip()
            if len(condition) > 3 and len(condition) < 50:
                return condition
    
    return ""

def parse_gemini_response(response_text: str) -> Dict[str, str]:
    """Parse the Gemini response to extract sections."""
    logger.info(f"Parsing Gemini response (first 500 chars): {response_text[:500]}...")
    
    result = {
        "detailed_analysis": "",
        "analysis_report": "",
        "recommendations": "",
        "initial_treatment_notes": "",
        "diagnosed_condition": ""
    }
    
    try:
        sections = {
            "detailed_analysis": "",
            "analysis_report": "",
            "recommendations": "",
            "initial_treatment_notes": ""
        }
        
        current_section = None
        lines = response_text.split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            if "**Detailed Analysis**" in line:
                current_section = "detailed_analysis"
                content = line.split("**Detailed Analysis**")[-1].replace(":", "").strip()
                if content:
                    sections[current_section] = content
            elif "**Analysis Report**" in line:
                current_section = "analysis_report"
                content = line.split("**Analysis Report**")[-1].replace(":", "").strip()
                if content:
                    sections[current_section] = content
            elif "**Recommendations**" in line:
                current_section = "recommendations"
                content = line.split("**Recommendations**")[-1].replace(":", "").strip()
                if content:
                    sections[current_section] = content
            elif "**Initial Treatment Notes**" in line:
                current_section = "initial_treatment_notes"
                content = line.split("**Initial Treatment Notes**")[-1].replace(":", "").strip()
                if content:
                    sections[current_section] = content
            elif current_section and line:
                if sections[current_section]:
                    sections[current_section] += "\n" + line
                else:
                    sections[current_section] = line
        
        result.update(sections)
        
        # Extract condition
        condition = extract_condition_from_text(result["analysis_report"])
        if not condition:
            condition = extract_condition_from_text(response_text)
        
        result["diagnosed_condition"] = condition
        logger.info(f"Extracted condition: '{condition}'")
        
    except Exception as e:
        logger.error(f"Parsing failed: {str(e)}")
        result["parsing_error"] = f"Could not parse response: {str(e)}"
    
    return result

def run_medical_agents(report_text: str) -> str:
    """Run the medical analysis agents and return detailed report."""
    logger.info("Starting medical agents analysis...")
    
    try:
        # Check if search tool is available
        agent_tools = [search_tool] if search_tool else []
        
        # Agent 1: Medical Diagnostician
        diagnosis_agent = Agent(
            role="General Medical Diagnostician",
            goal="Understand and classify the medical report, then determine top 5 possible diagnoses with reasoning and reference links.",
            backstory=(
                "You're a highly experienced physician with medical knowledge. You understand all types of medical reports—radiology, pathology, lab tests, and summaries. "
                "Provide detailed analysis based on medical knowledge and available search capabilities."
            ),
            verbose=True,
            memory=True,
            llm=LLM(model="gemini/gemini-1.5-flash", temperature=0.5),
            tools=agent_tools,
            allow_delegation=False
        )

        # Agent 2: Treatment Advisor
        treatment_agent = Agent(
            role="Treatment and Prescription Recommender",
            goal="For each diagnosis, suggest relevant medications, ointments, or procedures using clinical knowledge and available search tools.",
            backstory=(
                "You're a medical treatment specialist. You recommend treatment plans (medications, ointments, physiotherapy, etc.) and provide dosage based on diagnosis and established medical protocols."
            ),
            verbose=True,
            memory=True,
            llm=LLM(model="gemini/gemini-1.5-flash", temperature=0.5),
            tools=agent_tools,
            allow_delegation=False,
        )

        # Task 1: Diagnosis
        diagnosis_task = Task(
            description=f"Analyze this medical report, identify the report category, and provide the top 5 most likely diagnoses with reasoning. {('Use web search for additional medical information.' if search_tool else 'Use your medical knowledge for comprehensive analysis.')}",
            expected_output="List of 5 possible diagnoses with supporting explanation for each in detail, including relevant medical references where possible.",
            agent=diagnosis_agent
        )

        # Task 2: Treatment Recommendation
        treatment_task = Task(
            description=f"Based on the diagnoses, recommend medications or therapies with dosage. {('Use web search to support choices and' if search_tool else 'Use established medical protocols to')} provide comprehensive treatment plans.",
            expected_output="Detailed list of medicines/treatments per diagnosis with usage instructions, medicine names, dosages, and reference information for each treatment plan.",
            agent=treatment_agent
        )

        # Create and run crew
        crew = Crew(
            agents=[diagnosis_agent, treatment_agent],
            tasks=[diagnosis_task, treatment_task],
            verbose=True
        )

        result = crew.kickoff(inputs={'report_text': report_text})
        logger.info("Medical agents analysis completed successfully")
        return str(result)
        
    except Exception as e:
        logger.error(f"Medical agents failed: {str(e)}")
        # Fallback to basic analysis if agents fail
        return f"""Medical Analysis Report:

DIAGNOSIS ANALYSIS:
Based on the provided medical report, here are the key findings:

{report_text}

TREATMENT RECOMMENDATIONS:
1. Consult with a healthcare professional for proper diagnosis
2. Follow standard medical protocols for the identified condition
3. Consider appropriate medications as prescribed by a physician
4. Monitor symptoms and follow up as recommended

Note: This is a basic analysis due to technical limitations. For comprehensive analysis, please ensure all dependencies are properly installed.

ERROR DETAILS: {str(e)}"""

def create_pdf_report(image_path: str, initial_analysis: Dict[str, Any], agents_report: str, filename: str) -> str:
    """Create a comprehensive PDF report."""
    logger.info("Creating PDF report...")
    
    try:
        # Create temporary PDF file - handle Windows paths
        if platform.system() == "Windows":
            temp_dir = tempfile.gettempdir()
            pdf_path = os.path.join(temp_dir, f"medical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        else:
            pdf_path = f"/tmp/medical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # Title
        story.append(Paragraph("Medical Image Analysis Report", title_style))
        story.append(Spacer(1, 20))
        
        # Report info
        story.append(Paragraph(f"<b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"<b>Original Filename:</b> {filename}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Add image
        try:
            # Resize image for PDF
            with Image.open(image_path) as img:
                img.thumbnail((400, 400), Image.Resampling.LANCZOS)
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                # Save resized image temporarily
                if platform.system() == "Windows":
                    temp_img_path = os.path.join(temp_dir, f"resized_img_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                else:
                    temp_img_path = f"/tmp/resized_img_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                
                with open(temp_img_path, 'wb') as f:
                    f.write(img_buffer.getvalue())
                
                story.append(Paragraph("Medical Image", heading_style))
                story.append(RLImage(temp_img_path, width=4*inch, height=4*inch))
                story.append(Spacer(1, 20))
        except Exception as e:
            logger.error(f"Failed to add image to PDF: {str(e)}")
            story.append(Paragraph("Image could not be displayed", styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Initial Analysis Section
        story.append(Paragraph("Initial AI Analysis", heading_style))
        
        if initial_analysis.get("diagnosed_condition"):
            story.append(Paragraph(f"<b>Detected Condition:</b> {initial_analysis['diagnosed_condition']}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        if initial_analysis.get("detailed_analysis"):
            story.append(Paragraph("<b>Detailed Analysis:</b>", styles['Heading3']))
            story.append(Paragraph(initial_analysis["detailed_analysis"], styles['Normal']))
            story.append(Spacer(1, 12))
        
        if initial_analysis.get("analysis_report"):
            story.append(Paragraph("<b>Analysis Report:</b>", styles['Heading3']))
            story.append(Paragraph(initial_analysis["analysis_report"], styles['Normal']))
            story.append(Spacer(1, 12))
        
        if initial_analysis.get("recommendations"):
            story.append(Paragraph("<b>Initial Recommendations:</b>", styles['Heading3']))
            story.append(Paragraph(initial_analysis["recommendations"], styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Page break before agents report
        story.append(PageBreak())
        
        # Comprehensive Analysis Section
        story.append(Paragraph("Comprehensive Medical Analysis", heading_style))
        story.append(Paragraph("Generated by specialized medical AI agents with web research", styles['Italic']))
        story.append(Spacer(1, 20))
        
        # Add agents report
        if agents_report:
            # Split agents report into paragraphs for better formatting
            report_paragraphs = agents_report.split('\n\n')
            for para in report_paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), styles['Normal']))
                    story.append(Spacer(1, 8))
        
        # Disclaimer
        story.append(Spacer(1, 30))
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.red,
            borderWidth=1,
            borderColor=colors.red,
            borderPadding=10
        )
        story.append(Paragraph(
            "<b>IMPORTANT DISCLAIMER:</b> This analysis is for informational purposes only. "
            "Always consult with a qualified healthcare professional before making medical decisions. "
            "This AI-generated report should not replace professional medical advice, diagnosis, or treatment.",
            disclaimer_style
        ))
        
        # Build PDF
        doc.build(story)
        logger.info(f"PDF report created successfully: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logger.error(f"PDF creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF creation failed: {str(e)}")

@app.post("/analyze-medical-image", summary="Complete medical image analysis with PDF report")
async def analyze_medical_image(file: UploadFile = File(...)):
    """
    Complete medical analysis workflow:
    1. Analyze image with Gemini AI
    2. Run specialized medical agents for comprehensive analysis
    3. Generate PDF report with image and findings
    """
    logger.info(f"Starting analysis for file: {file.filename}")
    
    # Validate file type
    valid_types = ["image/png", "image/jpeg", "image/jpg"]
    if file.content_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Only PNG, JPG, JPEG allowed.")
    
    try:
        # Step 1: Read and analyze image with Gemini
        image_data = await file.read()
        if not image_data:
            raise HTTPException(status_code=400, detail="Empty image file")
        
        logger.info(f"Image data size: {len(image_data)} bytes")
        
        # Save image temporarily
        if platform.system() == "Windows":
            temp_dir = tempfile.gettempdir()
            temp_image_path = os.path.join(temp_dir, f"uploaded_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        else:
            temp_image_path = f"/tmp/uploaded_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        async with aiofiles.open(temp_image_path, 'wb') as f:
            await f.write(image_data)
        
        # Analyze with Gemini
        image_parts = [{"mime_type": file.content_type, "data": image_data}]
        prompt_parts = [image_parts[0], system_prompts]
        
        logger.info("Analyzing image with Gemini AI...")
        response = model.generate_content(prompt_parts)
        
        if not response or not hasattr(response, "text") or not response.text:
            raise HTTPException(status_code=500, detail="Failed to generate analysis from Gemini AI")
        
        # Parse initial analysis
        initial_analysis = parse_gemini_response(response.text)
        logger.info("Initial analysis completed")
        
        # Step 2: Run medical agents for comprehensive analysis
        logger.info("Starting comprehensive analysis with medical agents...")
        
        # Prepare report text for agents
        report_text = f"""
        Medical Image Analysis Report:
        
        Detected Condition: {initial_analysis.get('diagnosed_condition', 'Not specified')}
        
        Detailed Analysis: {initial_analysis.get('detailed_analysis', '')}
        
        Analysis Report: {initial_analysis.get('analysis_report', '')}
        
        Initial Recommendations: {initial_analysis.get('recommendations', '')}
        """
        
        agents_report = run_medical_agents(report_text.strip())
        logger.info("Comprehensive analysis completed")
        
        # Step 3: Generate PDF report
        logger.info("Generating PDF report...")
        pdf_path = create_pdf_report(temp_image_path, initial_analysis, agents_report, file.filename)
        
        # Prepare response
        result = {
            "status": "success",
            "filename": file.filename,
            "initial_analysis": initial_analysis,
            "comprehensive_analysis": agents_report[:1000] + "..." if len(agents_report) > 1000 else agents_report,
            "pdf_report_path": pdf_path,
            "message": "Complete medical analysis finished successfully. PDF report generated.",
            "disclaimer": "This analysis is for informational purposes only. Always consult with a qualified healthcare professional before making medical decisions."
        }
        
        logger.info("Analysis completed successfully")
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/download-report/{report_filename}", summary="Download PDF report")
async def download_report(report_filename: str):
    """Download the generated PDF report."""
    if platform.system() == "Windows":
        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, report_filename)
    else:
        pdf_path = f"/tmp/{report_filename}"
    
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"medical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

@app.get("/health", summary="Health check")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Medical Image Analysis API is running",
        "version": "2.0.0",
        "features": ["Image Analysis", "AI Agents", "PDF Reports"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)