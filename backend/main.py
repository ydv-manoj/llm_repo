from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import your GPT model module
from TerraDX_GPT import TerraDX_GPT 
# Replace with your actual function

app = FastAPI()

terra_dx_gpt_instance = TerraDX_GPT()

# Model for receiving prompt from the frontend
class PromptRequest(BaseModel):
    prompt: str
    
    
@app.get("/")
def hello():
    return {
        "response": "TerraDx GPT Server"
    }

# Endpoint to receive prompt and generate response
@app.post("/generate-response")
async def generate_response_endpoint(prompt_request: PromptRequest):
    prompt = prompt_request.prompt
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    # Call your custom GPT model to generate the response
    response = terra_dx_gpt_instance.get_response(prompt)
    # response = "This is a dummy response"  # Implement this function

    return {"response": response}

# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
