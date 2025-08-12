from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import google.generativeai as genai
from google_api_key import google_api_key
import aiohttp
import re
from typing import Dict, Any
import logging
import asyncio

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Medical Image Analysis API", description="API for analyzing medical images using Gemini AI and Tavily search")

# Configure Google Generative AI
genai.configure(api_key=google_api_key)

generation_config = {
    "temperature": 0.7,  # Reduced for more consistent medical analysis
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 2048  # Increased for detailed responses
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

**Treatments**: Suggest comprehensive treatment plans and methods for faster recovery.

Important:
1. Always include the disclaimer: "Consult with a doctor before making medical decisions."
2. If you identify a specific medical condition, clearly state it in the Analysis Report section using the format "Condition: [condition name]"
3. Be specific about any abnormalities you observe.
4. Use the EXACT section headers as shown above with double asterisks.
"""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings
)

# Tavily API Key (replace with your actual Tavily API key)
TAVILY_API_KEY = "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"

async def web_search(query: str) -> Dict[str, Any]:
    """
    Perform a web search using Tavily API to gather additional information about the diagnosed condition.
    """
    logger.info(f"Performing Tavily search for query: {query}")
    
    # Create a timeout for the HTTP request
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tavily_url = "https://api.tavily.com/search"
        
        # Simplified payload - removed complex site restrictions that might cause issues
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": f"{query} medical condition treatment symptoms",
            "search_depth": "basic",
            "include_answer": True,  # Changed to True for better results
            "include_images": False,
            "max_results": 5,  # Increased for better coverage
            "include_domains": ["mayoclinic.org", "webmd.com", "healthline.com", "medlineplus.gov"]
        }
        
        try:
            logger.info(f"Sending request to Tavily with payload: {payload}")
            
            async with session.post(tavily_url, json=payload) as response:
                response_text = await response.text()
                logger.info(f"Tavily response status: {response.status}")
                logger.info(f"Tavily response text: {response_text[:500]}...")
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract results with better error handling
                    results = []
                    if "results" in data and data["results"]:
                        for item in data["results"]:
                            result_item = {
                                "title": item.get("title", "No title"),
                                "snippet": item.get("content", item.get("snippet", "No content available")),
                                "url": item.get("url", "No URL")
                            }
                            results.append(result_item)
                    
                    search_result = {
                        "query": query,
                        "results": results,
                        "answer": data.get("answer", "No direct answer available"),
                        "total_results": len(results)
                    }
                    
                    logger.info(f"Successful search results: {len(results)} items found")
                    return search_result
                else:
                    error_msg = f"Tavily search failed with status: {response.status}, Response: {response_text}"
                    logger.error(error_msg)
                    return {"error": error_msg, "query": query}
                    
        except asyncio.TimeoutError:
            error_msg = "Tavily search timed out"
            logger.error(error_msg)
            return {"error": error_msg, "query": query}
        except Exception as e:
            error_msg = f"Tavily search failed: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg, "query": query}

def extract_condition_from_text(text: str) -> str:
    """
    Enhanced condition extraction with multiple strategies.
    """
    if not text:
        return ""
    
  
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
            if len(condition) > 3 and len(condition) < 50:  # Reasonable length
                return condition
    
    # Strategy 3: Look for common medical terms
    medical_terms = [
        r"\b(pneumonia|bronchitis|asthma)\b",
        r"\b(fracture|break|crack)\b",
        r"\b(infection|inflammatory|inflammation)\b",
        r"\b(tumor|mass|lesion|nodule)\b",
        r"\b(arthritis|osteoarthritis)\b",
        r"\b(stenosis|blockage|obstruction)\b",
        r"\b(abnormality|anomaly)\b"
    ]
    
    for term_pattern in medical_terms:
        match = re.search(term_pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    
    return ""

def parse_response(response_text: str) -> Dict[str, str]:
    """
    Parse the Gemini response to extract sections and identify the diagnosed condition.
    Enhanced with better parsing and condition extraction.
    """
    logger.info(f"Raw response from Gemini (first 500 chars): {response_text[:500]}...")
    
    result = {
        "detailed_analysis": "",
        "analysis_report": "",
        "recommendations": "",
        "treatments": "",
        "diagnosed_condition": ""
    }
    
    try:
        # Initialize sections
        sections = {
            "detailed_analysis": "",
            "analysis_report": "",
            "recommendations": "",
            "treatments": ""
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
                # Extract content after the header
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
            elif "**Treatments**" in line:
                current_section = "treatments"
                content = line.split("**Treatments**")[-1].replace(":", "").strip()
                if content:
                    sections[current_section] = content
            elif current_section and line:
                # Add content to current section
                if sections[current_section]:
                    sections[current_section] += "\n" + line
                else:
                    sections[current_section] = line
        
        # Update result with parsed sections
        result.update(sections)
        
        # Enhanced condition extraction
        full_text = response_text
        condition = extract_condition_from_text(result["analysis_report"])
        
        # If no condition found in analysis report, check the full text
        if not condition:
            condition = extract_condition_from_text(full_text)
        
        result["diagnosed_condition"] = condition
        
        # Log the extraction results
        logger.info(f"Extracted condition: '{condition}'")
        logger.info(f"Parsed sections - Analysis Report length: {len(result['analysis_report'])}")
        
        # Validation
        if not any(result[key].strip() for key in ["detailed_analysis", "analysis_report", "recommendations", "treatments"]):
            logger.warning("All sections are empty after parsing")
            result["parsing_warning"] = "Response structure may not match expected format"
    
    except Exception as e:
        logger.error(f"Parsing failed: {str(e)}")
        result["parsing_error"] = f"Could not parse response: {str(e)}"
    
    return result

@app.post("/analyze-image", summary="Analyze a medical image")
async def analyze_image(file: UploadFile = File(..., description="Medical image file (PNG, JPG, JPEG)")):
    """
    API endpoint to upload a medical image, analyze it with Gemini AI, and perform a web search on the diagnosed condition.
    """
    logger.info(f"Received file: {file.filename}, Content-Type: {file.content_type}")
    
    # Validate file type
    valid_types = ["image/png", "image/jpeg", "image/jpg"]
    if file.content_type not in valid_types:
        logger.error(f"Invalid file type: {file.content_type}")
        raise HTTPException(status_code=400, detail=f"Invalid file type. Only PNG, JPG, JPEG allowed. Received: {file.content_type}")
    
    try:
        # Read image data
        image_data = await file.read()
        if not image_data:
            logger.error("Empty image data")
            raise HTTPException(status_code=400, detail="Empty image file")
        
        logger.info(f"Image data size: {len(image_data)} bytes")
        
        # Prepare image for Gemini
        image_parts = [{"mime_type": file.content_type, "data": image_data}]
        prompt_parts = [image_parts[0], system_prompts]
        
        # Generate content from Gemini
        logger.info("Sending request to Gemini API")
        try:
            response = model.generate_content(prompt_parts)
            
            if not response or not hasattr(response, "text") or not response.text:
                logger.error("Invalid response from Gemini API")
                raise HTTPException(status_code=500, detail="Failed to generate analysis. Response was empty or invalid.")
            
            logger.info("Received response from Gemini API")
            
        except Exception as gemini_error:
            logger.error(f"Gemini API error: {str(gemini_error)}")
            raise HTTPException(status_code=500, detail=f"Gemini API error: {str(gemini_error)}")
        
        # Parse the response
        parsed_response = parse_response(response.text)
        logger.info(f"Parsed response completed. Condition found: '{parsed_response.get('diagnosed_condition', 'None')}'")
        
        # Perform web search if a condition was identified
        web_results = {}
        condition = parsed_response.get("diagnosed_condition", "").strip()
        
        if condition and len(condition) > 2:
            logger.info(f"Performing web search for condition: '{condition}'")
            web_results = await web_search(condition)
        else:
            logger.info("No specific condition identified for web search")
            web_results = {
                "message": "No specific medical condition identified for web search",
                "query": "",
                "results": []
            }
        
        # Log final results
        logger.info(f"Web search completed. Results count: {len(web_results.get('results', []))}")
        
        # Combine results
        result = {
            "status": "success",
            "filename": file.filename,
            "analysis": parsed_response,
            "web_search": web_results,
            "disclaimer": "This analysis is for informational purposes only. Always consult with a qualified healthcare professional before making medical decisions."
        }
        
        logger.info("Analysis completed successfully")
        return JSONResponse(content=result)
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/health", summary="Check API health")
async def health_check():
    """
    Health check endpoint to verify API status.
    """
    return {
        "status": "healthy",
        "message": "Medical Image Analysis API is running",
        "version": "1.0.0"
    }

@app.get("/test-search/{condition}", summary="Test web search functionality")
async def test_search(condition: str):
    """
    Test endpoint to verify web search functionality independently.
    """
    logger.info(f"Testing web search for condition: {condition}")
    try:
        results = await web_search(condition)
        return JSONResponse(content={
            "status": "success",
            "search_results": results
        })
    except Exception as e:
        logger.error(f"Test search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test search failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)