from fastapi import FastAPI,HTTPException,File,UploadFile
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field
from agents_main import main
import uvicorn

api=FastAPI()


api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (Not secure for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Info(BaseModel):
   detailed_analysis:str=Field(...,description='Description of detailed analysis')

@api.post('/get-treatment-diagnosis/')
def get_output(request:Info):
   try:
    description=request.detailed_analysis
    ans=main(description)
    return {"answer":ans}
   except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8080)
   